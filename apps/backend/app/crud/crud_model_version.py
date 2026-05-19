from uuid import UUID

from sqlalchemy.orm import Session

from app.models.model_version import ModelVersion
from app.schemas.model_version import ModelVersionCreate


def get_model_version(db: Session, version_id: UUID) -> ModelVersion | None:
  return db.query(ModelVersion).filter(ModelVersion.id == version_id).first()


def list_model_versions(db: Session, *, limit: int = 100) -> list[ModelVersion]:
  return (
    db.query(ModelVersion)
      .order_by(ModelVersion.created_at.desc())
      .limit(limit)
      .all()
  )


def create_model_version(db: Session, data: ModelVersionCreate) -> ModelVersion:
  version = ModelVersion(**data.model_dump(exclude_none=True))
  db.add(version)
  db.commit()
  db.refresh(version)
  return version
