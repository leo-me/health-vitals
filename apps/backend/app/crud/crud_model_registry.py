from uuid import UUID

from sqlalchemy.orm import Session

from app.models.model_registry import ModelRegistry
from app.models.model_version import ModelStage, ModelVersion
from app.schemas.model_registry import ModelRegistryCreate


def get_model_registry(db: Session, registry_id: UUID) -> ModelRegistry | None:
  return db.query(ModelRegistry).filter(ModelRegistry.id == registry_id).first()


def list_model_registries(
  db: Session,
  *,
  model_name: str | None = None,
  stage: ModelStage | None = None,
  limit: int = 100,
) -> list[ModelRegistry]:
  q = db.query(ModelRegistry)
  if model_name is not None:
    q = q.filter(ModelRegistry.model_name == model_name)
  if stage is not None:
    q = q.filter(ModelRegistry.stage == stage)
  return q.order_by(ModelRegistry.created_at.desc()).limit(limit).all()


def get_current_production(
  db: Session,
  *,
  model_name: str | None = None,
) -> ModelRegistry | None:
  """Most recently registered row tagged as production."""
  q = db.query(ModelRegistry).filter(ModelRegistry.stage == ModelStage.PRODUCTION)
  if model_name is not None:
    q = q.filter(ModelRegistry.model_name == model_name)
  return q.order_by(ModelRegistry.created_at.desc()).first()


def create_model_registry(db: Session, data: ModelRegistryCreate) -> ModelRegistry:
  registry = ModelRegistry(**data.model_dump(exclude_none=True))
  # When the new row is itself PRODUCTION, archive any prior PRODUCTION rows
  # of the same model_name in the same transaction. Same invariant as
  # update_stage() below.
  if registry.stage == ModelStage.PRODUCTION and registry.model_name:
    _archive_prior_productions(db, model_name=registry.model_name, except_id=None)
  db.add(registry)
  db.commit()
  db.refresh(registry)
  return registry


def update_stage(
  db: Session,
  registry_id: UUID,
  stage: ModelStage,
) -> ModelRegistry | None:
  registry = get_model_registry(db, registry_id)
  if not registry:
    return None

  # Invariant: at most one row per model_name has stage=PRODUCTION.
  # When promoting, demote any existing PRODUCTION rows of the same name to
  # ARCHIVED in the same transaction before flipping this one.
  if stage == ModelStage.PRODUCTION and registry.model_name:
    _archive_prior_productions(
      db, model_name=registry.model_name, except_id=registry.id
    )

  registry.stage = stage
  db.commit()
  db.refresh(registry)
  return registry


def _archive_prior_productions(
  db: Session,
  *,
  model_name: str,
  except_id: UUID | None,
) -> int:
  """Set stage=ARCHIVED on every PRODUCTION row with the given model_name,
  except (optionally) the row identified by except_id. Cascades the same
  demotion to each row's linked ModelVersion so model_version.stage stays
  consistent with model_registry.stage — the registry table is the source
  of truth for "which model is in production", and the version table just
  mirrors it. Returns the count of registry rows touched. Caller is
  responsible for committing the surrounding transaction."""
  q = (
    db.query(ModelRegistry)
      .filter(ModelRegistry.model_name == model_name)
      .filter(ModelRegistry.stage == ModelStage.PRODUCTION)
  )
  if except_id is not None:
    q = q.filter(ModelRegistry.id != except_id)

  # Snapshot version_ids before the UPDATE collapses them. None entries are
  # possible if a registry row was inserted without a linked version — skip
  # those rather than blowing up the IN-clause.
  version_ids = [r.version_id for r in q.all() if r.version_id is not None]

  n_registries = q.update(
    {ModelRegistry.stage: ModelStage.ARCHIVED},
    synchronize_session=False,
  )

  if version_ids:
    db.query(ModelVersion).filter(ModelVersion.id.in_(version_ids)).update(
      {ModelVersion.stage: ModelStage.ARCHIVED},
      synchronize_session=False,
    )

  return n_registries
