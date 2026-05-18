"""
Seed test fixtures: 25 users + 29 Empatica E4 devices.

Step 1 : Create 25 users  (user_001 … user_025 @sensors2care.nl)
Step 2 : Create 29 devices (E4_subject_01 … E4_subject_29)
         Round-robin across ALL users currently in the database
Step 3 : Write data/pipelines/user_ids.json — UUIDs of ALL users in DB

Next step: load sensor recordings
    python data/pipelines/load_subjects.py

Usage:
    DATABASE_URL=postgresql://postgres:0000@localhost:5432/health_db \\
        python data/pipelines/seed_fixtures.py
"""

import json
import os
import sys
import uuid
from pathlib import Path

from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ── paths ─────────────────────────────────────────────────────────────────────
HERE         = Path(__file__).resolve().parent   # data/pipelines/
PROJECT_ROOT = HERE.parent.parent                # project root

sys.path.insert(0, str(PROJECT_ROOT / "apps" / "backend"))

from app.models.user import User, UserTypeEnum      # noqa: E402
from app.models.device import Device, DeviceType    # noqa: E402

# ── DB ────────────────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:0000@localhost:5432/health_db"
)
engine  = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
pwd_ctx = CryptContext(schemes=["bcrypt"])

N_USERS    = 25
N_SUBJECTS = 29


def create_users(db) -> tuple[list[User], int]:
    hashed_pw = pwd_ctx.hash("exp1secret")
    users, created = [], 0
    for i in range(1, N_USERS + 1):
        email    = f"user_{i:03d}@sensors2care.nl"
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            users.append(existing)
            continue
        user = User(
            id        = uuid.uuid4(),
            email     = email,
            password  = hashed_pw,
            name      = f"Subject {i:03d}",
            user_type = UserTypeEnum.PATIENT,
        )
        db.add(user)
        users.append(user)
        created += 1
    db.flush()
    return users, created


def create_devices(db, users: list[User]) -> tuple[dict[int, Device], int]:
    devices, created = {}, 0
    for idx in range(1, N_SUBJECTS + 1):
        serial   = f"E4_subject_{idx:02d}"
        existing = db.query(Device).filter(Device.serial_number == serial).first()
        if existing:
            devices[idx] = existing
            continue
        device = Device(
            id            = uuid.uuid4(),
            serial_number = serial,
            user_id       = users[(idx - 1) % len(users)].id,
            type          = DeviceType.SENSOR,
        )
        db.add(device)
        devices[idx] = device
        created += 1
    db.flush()
    return devices, created


def seed():
    db = Session()
    try:
        print("── Step 1: users ──────────────────────────────────────────")
        users, new_u = create_users(db)
        print(f"  {len(users)} total  ({new_u} new, {len(users) - new_u} skipped)")

        print("\n── Step 2: devices ────────────────────────────────────────")
        # Round-robin across ALL users currently in DB (not just the ones we created)
        all_users = db.query(User).order_by(User.email).all()
        devices, new_d = create_devices(db, all_users)
        print(f"  {len(devices)} total  ({new_d} new, {len(devices) - new_d} skipped)")

        db.commit()

        # Step 3: write user_ids.json from ALL users currently in DB
        all_users_after = db.query(User).order_by(User.email).all()
        user_ids = [str(u.id) for u in all_users_after]

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print("\n── Summary ────────────────────────────────────────────────")
    print(f"  Users   : {len(user_ids)}")
    print(f"  Devices : {len(devices)}")

    manifest = {"user_ids": user_ids}
    out = HERE / "user_ids.json"
    with open(out, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  user_ids.json → {out}")
    print("\n  Next: python data/pipelines/load_subjects.py")
    print("────────────────────────────────────────────────────────────")


if __name__ == "__main__":
    seed()
