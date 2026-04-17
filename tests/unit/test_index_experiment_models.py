"""Unit tests for Index/Experiment/Run/EvalCase/MetricSnapshot/Deployment models and repos."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.deployment import Deployment
from backend.models.eval_case import EvalCase
from backend.models.experiment import Experiment
from backend.models.index import VectorIndex
from backend.models.metric_snapshot import MetricSnapshot
from backend.models.run import Run
from backend.repositories.deployment_repository import DeploymentRepository
from backend.repositories.eval_case_repository import EvalCaseRepository
from backend.repositories.experiment_repository import ExperimentRepository
from backend.repositories.index_repository import IndexRepository
from backend.repositories.metric_snapshot_repository import MetricSnapshotRepository
from backend.repositories.run_repository import RunRepository


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def workspace_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def index(workspace_id: uuid.UUID) -> VectorIndex:
    idx = VectorIndex()
    idx.id = uuid.uuid4()
    idx.workspace_id = workspace_id
    idx.name = "test-index"
    idx.vector_backend = "pinecone"
    idx.namespace = "ns-1"
    idx.config_hash = "hash-abc"
    idx.index_config = {"embed_model": "text-embedding-3-small"}
    idx.status = "building"
    return idx


@pytest.fixture
def experiment(workspace_id: uuid.UUID, index: VectorIndex) -> Experiment:
    exp = Experiment()
    exp.id = uuid.uuid4()
    exp.workspace_id = workspace_id
    exp.index_id = index.id
    exp.name = "baseline-experiment"
    exp.description = "First retrieval experiment"
    exp.experiment_config = {"top_k": 5}
    return exp


@pytest.fixture
def run(experiment: Experiment) -> Run:
    r = Run()
    r.id = uuid.uuid4()
    r.experiment_id = experiment.id
    r.status = "queued"
    r.artifact_uri = None
    r.run_logs = None
    return r


@pytest.fixture
def eval_case(run: Run) -> EvalCase:
    ec = EvalCase()
    ec.id = uuid.uuid4()
    ec.run_id = run.id
    ec.question = "What is RAG?"
    ec.ground_truth = "Retrieval-Augmented Generation"
    ec.predicted = "RAG stands for Retrieval-Augmented Generation"
    ec.case_metrics = {"relevance": 0.95}
    ec.failure_type = None
    return ec


@pytest.fixture
def metric_snapshot(run: Run) -> MetricSnapshot:
    ms = MetricSnapshot()
    ms.id = uuid.uuid4()
    ms.run_id = run.id
    ms.snapshot_metrics = {"faithfulness": 0.9, "latency_ms": 120}
    return ms


@pytest.fixture
def deployment(workspace_id: uuid.UUID, index: VectorIndex) -> Deployment:
    dep = Deployment()
    dep.id = uuid.uuid4()
    dep.workspace_id = workspace_id
    dep.index_id = index.id
    dep.environment = "staging"
    dep.revision = "abc123"
    dep.status = "pending"
    return dep


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock(spec=AsyncSession)
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


# ---------------------------------------------------------------------------
# VectorIndex model structure
# ---------------------------------------------------------------------------


def test_index_table_name():
    assert VectorIndex.__tablename__ == "indexes"


def test_index_columns_exist():
    cols = {c.key for c in VectorIndex.__table__.columns}
    assert cols >= {"id", "workspace_id", "name", "vector_backend", "namespace",
                    "config_hash", "status", "created_at", "updated_at"}


def test_index_config_column_name():
    col = VectorIndex.__table__.c["config"]
    assert col is not None


def test_index_indexes_defined():
    names = {idx.name for idx in VectorIndex.__table__.indexes}
    assert "ix_indexes_workspace_id" in names
    assert "ix_indexes_status" in names


def test_index_workspace_fk():
    fks = {fk.target_fullname for fk in VectorIndex.__table__.foreign_keys}
    assert "workspaces.id" in fks


def test_index_repr(index: VectorIndex):
    r = repr(index)
    assert "test-index" in r
    assert "building" in r


# ---------------------------------------------------------------------------
# Experiment model structure
# ---------------------------------------------------------------------------


def test_experiment_table_name():
    assert Experiment.__tablename__ == "experiments"


def test_experiment_columns_exist():
    cols = {c.key for c in Experiment.__table__.columns}
    assert cols >= {"id", "workspace_id", "index_id", "name", "description",
                    "created_at", "updated_at"}


def test_experiment_config_column_name():
    col = Experiment.__table__.c["config"]
    assert col is not None


def test_experiment_index_fk_nullable():
    col = Experiment.__table__.c["index_id"]
    assert col.nullable is True


def test_experiment_runs_cascade():
    rel = Experiment.runs.property
    assert "delete-orphan" in rel.cascade


def test_experiment_repr(experiment: Experiment):
    r = repr(experiment)
    assert "baseline-experiment" in r


# ---------------------------------------------------------------------------
# Run model structure
# ---------------------------------------------------------------------------


def test_run_table_name():
    assert Run.__tablename__ == "runs"


def test_run_columns_exist():
    cols = {c.key for c in Run.__table__.columns}
    assert cols >= {"id", "experiment_id", "status", "started_at", "finished_at",
                    "artifact_uri"}


def test_run_logs_column_name():
    col = Run.__table__.c["logs"]
    assert col is not None


def test_run_experiment_fk_cascade():
    fk = next(fk for fk in Run.__table__.foreign_keys
              if fk.target_fullname == "experiments.id")
    assert fk.ondelete == "CASCADE"


def test_run_eval_cases_cascade():
    rel = Run.eval_cases.property
    assert "delete-orphan" in rel.cascade


def test_run_metric_snapshots_cascade():
    rel = Run.metric_snapshots.property
    assert "delete-orphan" in rel.cascade


def test_run_repr(run: Run):
    r = repr(run)
    assert "queued" in r


# ---------------------------------------------------------------------------
# EvalCase model structure
# ---------------------------------------------------------------------------


def test_eval_case_table_name():
    assert EvalCase.__tablename__ == "eval_cases"


def test_eval_case_columns_exist():
    cols = {c.key for c in EvalCase.__table__.columns}
    assert cols >= {"id", "run_id", "question", "ground_truth", "predicted",
                    "failure_type"}


def test_eval_case_metrics_column_name():
    col = EvalCase.__table__.c["metrics"]
    assert col is not None


def test_eval_case_run_fk_cascade():
    fk = next(fk for fk in EvalCase.__table__.foreign_keys)
    assert fk.target_fullname == "runs.id"
    assert fk.ondelete == "CASCADE"


def test_eval_case_repr(eval_case: EvalCase):
    r = repr(eval_case)
    assert "EvalCase" in r


# ---------------------------------------------------------------------------
# MetricSnapshot model structure
# ---------------------------------------------------------------------------


def test_metric_snapshot_table_name():
    assert MetricSnapshot.__tablename__ == "metric_snapshots"


def test_metric_snapshot_columns_exist():
    cols = {c.key for c in MetricSnapshot.__table__.columns}
    assert cols >= {"id", "run_id", "created_at"}


def test_metric_snapshot_metrics_column_name():
    col = MetricSnapshot.__table__.c["metrics"]
    assert col is not None


def test_metric_snapshot_run_fk_cascade():
    fk = next(fk for fk in MetricSnapshot.__table__.foreign_keys)
    assert fk.target_fullname == "runs.id"
    assert fk.ondelete == "CASCADE"


def test_metric_snapshot_repr(metric_snapshot: MetricSnapshot):
    r = repr(metric_snapshot)
    assert "MetricSnapshot" in r


# ---------------------------------------------------------------------------
# Deployment model structure
# ---------------------------------------------------------------------------


def test_deployment_table_name():
    assert Deployment.__tablename__ == "deployments"


def test_deployment_columns_exist():
    cols = {c.key for c in Deployment.__table__.columns}
    assert cols >= {"id", "workspace_id", "index_id", "environment", "revision",
                    "status", "created_at"}


def test_deployment_workspace_fk():
    fks = {fk.target_fullname for fk in Deployment.__table__.foreign_keys}
    assert "workspaces.id" in fks


def test_deployment_index_fk_nullable():
    col = Deployment.__table__.c["index_id"]
    assert col.nullable is True


def test_deployment_repr(deployment: Deployment):
    r = repr(deployment)
    assert "staging" in r
    assert "pending" in r


# ---------------------------------------------------------------------------
# IndexRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_index_repo_get(index: VectorIndex, mock_session: AsyncMock):
    mock_session.get = AsyncMock(return_value=index)
    repo = IndexRepository(mock_session)
    result = await repo.get(index.id)
    mock_session.get.assert_awaited_once_with(VectorIndex, index.id)
    assert result is index


@pytest.mark.asyncio
async def test_index_repo_add(index: VectorIndex, mock_session: AsyncMock):
    repo = IndexRepository(mock_session)
    result = await repo.add(index)
    mock_session.add.assert_called_once_with(index)
    mock_session.flush.assert_awaited_once()
    assert result is index


@pytest.mark.asyncio
async def test_index_repo_list_by_workspace(
    index: VectorIndex, workspace_id: uuid.UUID, mock_session: AsyncMock
):
    _setup_scalars_all(mock_session, [index])
    repo = IndexRepository(mock_session)
    results = await repo.list_by_workspace(workspace_id)
    assert results == [index]


@pytest.mark.asyncio
async def test_index_repo_list_by_status(index: VectorIndex, mock_session: AsyncMock):
    _setup_scalars_all(mock_session, [index])
    repo = IndexRepository(mock_session)
    results = await repo.list_by_status("building")
    assert results == [index]


@pytest.mark.asyncio
async def test_index_repo_get_by_config_hash(
    index: VectorIndex, mock_session: AsyncMock
):
    _setup_scalar_first(mock_session, index)
    repo = IndexRepository(mock_session)
    result = await repo.get_by_config_hash("hash-abc")
    assert result is index


@pytest.mark.asyncio
async def test_index_repo_get_by_config_hash_missing(mock_session: AsyncMock):
    _setup_scalar_first(mock_session, None)
    repo = IndexRepository(mock_session)
    result = await repo.get_by_config_hash("nonexistent")
    assert result is None


# ---------------------------------------------------------------------------
# ExperimentRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_experiment_repo_get(experiment: Experiment, mock_session: AsyncMock):
    mock_session.get = AsyncMock(return_value=experiment)
    repo = ExperimentRepository(mock_session)
    result = await repo.get(experiment.id)
    assert result is experiment


@pytest.mark.asyncio
async def test_experiment_repo_add(experiment: Experiment, mock_session: AsyncMock):
    repo = ExperimentRepository(mock_session)
    result = await repo.add(experiment)
    mock_session.add.assert_called_once_with(experiment)
    assert result is experiment


@pytest.mark.asyncio
async def test_experiment_repo_list_by_workspace(
    experiment: Experiment, workspace_id: uuid.UUID, mock_session: AsyncMock
):
    _setup_scalars_all(mock_session, [experiment])
    repo = ExperimentRepository(mock_session)
    results = await repo.list_by_workspace(workspace_id)
    assert results == [experiment]


@pytest.mark.asyncio
async def test_experiment_repo_list_by_index(
    experiment: Experiment, index: VectorIndex, mock_session: AsyncMock
):
    _setup_scalars_all(mock_session, [experiment])
    repo = ExperimentRepository(mock_session)
    results = await repo.list_by_index(index.id)
    assert results == [experiment]


# ---------------------------------------------------------------------------
# RunRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_repo_get(run: Run, mock_session: AsyncMock):
    mock_session.get = AsyncMock(return_value=run)
    repo = RunRepository(mock_session)
    result = await repo.get(run.id)
    assert result is run


@pytest.mark.asyncio
async def test_run_repo_add(run: Run, mock_session: AsyncMock):
    repo = RunRepository(mock_session)
    result = await repo.add(run)
    mock_session.add.assert_called_once_with(run)
    assert result is run


@pytest.mark.asyncio
async def test_run_repo_list_by_experiment(
    run: Run, experiment: Experiment, mock_session: AsyncMock
):
    _setup_scalars_all(mock_session, [run])
    repo = RunRepository(mock_session)
    results = await repo.list_by_experiment(experiment.id)
    assert results == [run]


@pytest.mark.asyncio
async def test_run_repo_list_by_status(run: Run, mock_session: AsyncMock):
    _setup_scalars_all(mock_session, [run])
    repo = RunRepository(mock_session)
    results = await repo.list_by_status("queued")
    assert results == [run]


# ---------------------------------------------------------------------------
# EvalCaseRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_eval_case_repo_add(eval_case: EvalCase, mock_session: AsyncMock):
    repo = EvalCaseRepository(mock_session)
    result = await repo.add(eval_case)
    mock_session.add.assert_called_once_with(eval_case)
    assert result is eval_case


@pytest.mark.asyncio
async def test_eval_case_repo_list_by_run(
    eval_case: EvalCase, run: Run, mock_session: AsyncMock
):
    _setup_scalars_all(mock_session, [eval_case])
    repo = EvalCaseRepository(mock_session)
    results = await repo.list_by_run(run.id)
    assert results == [eval_case]


@pytest.mark.asyncio
async def test_eval_case_repo_list_by_failure_type_empty(
    run: Run, mock_session: AsyncMock
):
    _setup_scalars_all(mock_session, [])
    repo = EvalCaseRepository(mock_session)
    results = await repo.list_by_failure_type(run.id, "hallucination")
    assert results == []


# ---------------------------------------------------------------------------
# MetricSnapshotRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_metric_snapshot_repo_add(
    metric_snapshot: MetricSnapshot, mock_session: AsyncMock
):
    repo = MetricSnapshotRepository(mock_session)
    result = await repo.add(metric_snapshot)
    mock_session.add.assert_called_once_with(metric_snapshot)
    assert result is metric_snapshot


@pytest.mark.asyncio
async def test_metric_snapshot_repo_list_by_run(
    metric_snapshot: MetricSnapshot, run: Run, mock_session: AsyncMock
):
    _setup_scalars_all(mock_session, [metric_snapshot])
    repo = MetricSnapshotRepository(mock_session)
    results = await repo.list_by_run(run.id)
    assert results == [metric_snapshot]


# ---------------------------------------------------------------------------
# DeploymentRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_deployment_repo_add(deployment: Deployment, mock_session: AsyncMock):
    repo = DeploymentRepository(mock_session)
    result = await repo.add(deployment)
    mock_session.add.assert_called_once_with(deployment)
    assert result is deployment


@pytest.mark.asyncio
async def test_deployment_repo_list_by_workspace(
    deployment: Deployment, workspace_id: uuid.UUID, mock_session: AsyncMock
):
    _setup_scalars_all(mock_session, [deployment])
    repo = DeploymentRepository(mock_session)
    results = await repo.list_by_workspace(workspace_id)
    assert results == [deployment]


@pytest.mark.asyncio
async def test_deployment_repo_list_by_status(
    deployment: Deployment, mock_session: AsyncMock
):
    _setup_scalars_all(mock_session, [deployment])
    repo = DeploymentRepository(mock_session)
    results = await repo.list_by_status("pending")
    assert results == [deployment]


@pytest.mark.asyncio
async def test_deployment_repo_list_by_environment(
    deployment: Deployment, workspace_id: uuid.UUID, mock_session: AsyncMock
):
    _setup_scalars_all(mock_session, [deployment])
    repo = DeploymentRepository(mock_session)
    results = await repo.list_by_environment(workspace_id, "staging")
    assert results == [deployment]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _setup_scalar_first(session: AsyncMock, value):
    scalars = MagicMock()
    scalars.first.return_value = value
    result = MagicMock()
    result.scalars.return_value = scalars
    session.execute = AsyncMock(return_value=result)


def _setup_scalars_all(session: AsyncMock, values: list):
    scalars = MagicMock()
    scalars.all.return_value = values
    result = MagicMock()
    result.scalars.return_value = scalars
    session.execute = AsyncMock(return_value=result)
