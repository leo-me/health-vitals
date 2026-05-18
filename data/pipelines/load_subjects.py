"""
Pipeline: load raw Empatica E4 CSV files → sensor_recordings table.

Signal mapping (all 6 E4 signals):
    EDA.csv   → SensorType.EDA         (4 Hz,  single col,  {"value": float})
    BVP.csv   → SensorType.BVP         (64 Hz, single col,  {"value": float})
    ACC.csv   → SensorType.ACC         (32 Hz, 3 cols x/y/z, skip header row)
    HR.csv    → SensorType.HEART_RATE  (1 Hz,  single col,  {"value": float})
    IBI.csv   → SensorType.IBI         (event, 2 cols,      {"offset_s": float, "ibi_s": float})
    TEMP.csv  → SensorType.TEMP        (4 Hz,  single col,  {"value": float})

Prerequisites:
    - Users must exist in DB (run data/pipelines/seed_fixtures.py first)
    - DB migration a1b2c3d4e5f6 must be applied (alembic upgrade head)

Usage:
    DATABASE_URL=postgresql://postgres:0000@localhost:5432/health_db \\
        python data/pipelines/load_subjects.py
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ── paths ─────────────────────────────────────────────────────────────────────
HERE         = Path(__file__).resolve().parent          # data/pipelines/
DATA_ROOT    = HERE.parent / "raw"                      # data/raw/
PROJECT_ROOT = HERE.parent.parent                       # project root

sys.path.insert(0, str(PROJECT_ROOT / "apps" / "backend"))

from app.models.device import Device, DeviceType                        # noqa: E402
from app.models.sensor_recording import SensorRecording, SensorType    # noqa: E402
from app.models.user import User                                        # noqa: E402

# ── DB ────────────────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:0000@localhost:5432/health_db"
)
engine  = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# ── signal configuration ──────────────────────────────────────────────────────
N_SUBJECTS = 29
BATCH_SIZE = 1_000
BASE_TS    = datetime(2026, 1, 1)

# fmt: (sensor_type, hz_or_None, n_cols, skip_header_rows)
#   hz=None  → IBI: event-based, timestamp derived from first column (offset in seconds)
#   skip=1   → ACC: first row is metadata "32,32,32"
SIGNALS: dict[str, tuple] = {
    "EDA":  (SensorType.EDA,        4,    1, 0),
    "BVP":  (SensorType.BVP,       64,    1, 0),
    "ACC":  (SensorType.ACC,       32,    3, 1),
    "HR":   (SensorType.HEART_RATE, 1,    1, 0),
    "IBI":  (SensorType.IBI,       None,  2, 0),
    "TEMP": (SensorType.TEMP,       4,    1, 0),
}


# ── parsers ───────────────────────────────────────────────────────────────────

def _parse_single(raw: str) -> dict:
    try:
        return {"value": round(float(raw.strip()), 4)}
    except ValueError:
        return None


def _parse_acc(raw: str) -> dict:
    x, y, z = raw.strip().split(",")
    return {"x": round(float(x), 4), "y": round(float(y), 4), "z": round(float(z), 4)}


def _parse_ibi(raw: str) -> tuple[float, dict]:
    """Returns (offset_seconds, data_dict)."""
    offset, ibi = raw.strip().split(",")
    try:
        ibi = round(float(ibi), 6)
        return float(offset), {"offset_s": round(float(offset), 6), "ibi_s": ibi}
    except ValueError:
        return float(offset), {"offset_s": round(float(offset), 6), "ibi_s": 0}


# ── device helper ─────────────────────────────────────────────────────────────

def _ensure_device(db, subject_idx: int, users: list[User]) -> Device:
    """Return existing device or create one assigned to a round-robin user."""
    serial = f"E4_subject_{subject_idx:02d}"
    device = db.query(Device).filter(Device.serial_number == serial).first()
    if device:
        return device
    user = users[(subject_idx - 1) % len(users)]
    device = Device(
        id            = uuid.uuid4(),
        serial_number = serial,
        user_id       = user.id,
        type          = DeviceType.SENSOR,
    )
    db.add(device)
    db.flush()
    print(f"    created device {serial} → {user.email}")
    return device


# ── per-signal loader ─────────────────────────────────────────────────────────

def _load_signal(
    db,
    csv_path: Path,
    device: Device,
    sensor_type: SensorType,
    hz,
    n_cols: int,
    skip_rows: int,
) -> int:
    # idempotency: skip if any row already exists for this device+type
    exists = (
        db.query(SensorRecording.id)
        .filter(
            SensorRecording.device_id   == device.id,
            SensorRecording.sensor_type == sensor_type,
        )
        .limit(1)
        .scalar()
    )
    if exists:
        n = (
            db.query(SensorRecording)
            .filter(
                SensorRecording.device_id   == device.id,
                SensorRecording.sensor_type == sensor_type,
            )
            .count()
        )
        print(f"    [skip] {csv_path.name}: {n:,} rows already in DB")
        return n

    batch: list[SensorRecording] = []
    inserted = 0

    with open(csv_path) as f:
        for row_idx, line in enumerate(f):
            if row_idx < skip_rows:
                continue
            raw = line.strip()
            if not raw:
                continue

            data_idx = row_idx - skip_rows

            if sensor_type == SensorType.IBI:
                offset_s, data = _parse_ibi(raw)
                ts = BASE_TS + timedelta(seconds=offset_s)
            elif n_cols == 3:
                data = _parse_acc(raw)
                ts   = BASE_TS + timedelta(seconds=data_idx / hz)
            else:
                data = _parse_single(raw)
                if data is None:
                    continue
                ts = BASE_TS + timedelta(seconds=data_idx / hz)

            batch.append(SensorRecording(
                id          = uuid.uuid4(),
                device_id   = device.id,
                user_id     = device.user_id,
                timestamp   = ts,
                sensor_type = sensor_type,
                data        = data,
            ))

            if len(batch) == BATCH_SIZE:
                db.bulk_save_objects(batch)
                inserted += len(batch)
                batch = []

    if batch:
        db.bulk_save_objects(batch)
        inserted += len(batch)

    print(f"    {csv_path.name}: {inserted:,} rows inserted")
    return inserted


# ── main pipeline ─────────────────────────────────────────────────────────────

def run(db) -> dict[str, int]:
    # Query all existing users; round-robin subjects across them
    users = db.query(User).order_by(User.email).all()
    if not users:
        raise RuntimeError("No users in database — run seed_fixtures.py first")
    print(f"  {len(users)} users found in DB — distributing {N_SUBJECTS} subjects round-robin")

    counts: dict[str, int] = {sig: 0 for sig in SIGNALS}

    for subject_idx in range(1, N_SUBJECTS + 1):
        device = _ensure_device(db, subject_idx, users)

        folder = DATA_ROOT / f"subject_{subject_idx:02d}"
        if not folder.exists():
            print(f"  [skip] {folder.name} not found in data/raw/")
            continue

        print(f"  subject_{subject_idx:02d}  (device {device.id}, user {device.user_id})")
        for sig_name, (sensor_type, hz, n_cols, skip) in SIGNALS.items():
            csv_path = folder / f"{sig_name}.csv"
            if not csv_path.exists():
                continue
            n = _load_signal(db, csv_path, device, sensor_type, hz, n_cols, skip)
            counts[sig_name] += n

        db.commit()   # commit per subject to keep transactions small

    return counts


if __name__ == "__main__":
    print("── Empatica E4 data pipeline ──────────────────────────────")
    db = Session()
    try:
        counts = run(db)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    total = sum(counts.values())
    print("\n── Summary ────────────────────────────────────────────────")
    for sig, n in counts.items():
        sensor_type = SIGNALS[sig][0]
        print(f"  {sig:4s} → SensorType.{sensor_type.name:12s}: {n:>9,}")
    print(f"  {'':4s}   {'total':14s}: {total:>9,}")
    print("────────────────────────────────────────────────────────────")
