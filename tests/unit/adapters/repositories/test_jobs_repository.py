import psycopg
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.adapters.repositories.jobs_repository import JobRepository
from src.domain.models.job import Job, JobRequest

TEST_DB_URL = "postgresql://postgres:postgres@localhost:5433/"
TEST_DB_NAME = "test_nebula_repo"


@pytest.fixture(scope="session")
def setup_test_db():
    with psycopg.connect(TEST_DB_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')
            cur.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')

    test_db_url = f"{TEST_DB_URL}{TEST_DB_NAME}"
    yield test_db_url

    # Teardown: Drop the test database after the session
    with psycopg.connect(TEST_DB_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')


@pytest.fixture
def db_session(setup_test_db):
    engine = create_engine(setup_test_db)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS jobs CASCADE;"))
        conn.execute(text("""
            CREATE TABLE jobs (
                id SERIAL PRIMARY KEY,
                func_name TEXT NOT NULL,
                args TEXT NOT NULL,
                schedule TEXT NOT NULL,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))

    session = testing_session_local()

    session.execute(text("TRUNCATE TABLE jobs RESTART IDENTITY CASCADE;"))
    session.commit()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def repo(db_session):
    return JobRepository(db_session)


def test_create_job_successfully(repo, db_session):
    # GIVEN
    job_request = JobRequest(
        func_name="fake_func_name",
        args=["arg_1", "arg_2"],
        schedule="1,31 * * * *"
    )

    # WHEN
    job = repo.create(job_request)

    # THEN
    assert job is not None
    assert type(job.id) is int
    assert job.func_name == "fake_func_name"
    assert job.args == ["arg_1", "arg_2"]
    assert job.schedule == "1,31 * * * *"


def test_get_all_returns_jobs(repo, db_session):
    # GIVEN
    db_session.execute(
        text("""
            INSERT INTO jobs (func_name, args, schedule)
            VALUES (:func_name, :args, :schedule)
        """),
        {
            "func_name": "fake_func_name",
            "args": '["arg_1", "arg_2"]',
            "schedule": "1,31 * * * *",
        }
    )
    db_session.execute(
        text("""
            INSERT INTO jobs (func_name, args, schedule)
            VALUES (:func_name, :args, :schedule)
        """),
        {
            "func_name": "fake_func_name_2",
            "args": '["arg_3", "arg_4"]',
            "schedule": "* * * * *",
        }
    )
    db_session.commit()

    # WHEN
    jobs = repo.get_all()

    # THEN
    assert len(jobs) == 2
    assert all(isinstance(s, Job) for s in jobs)


def test_get_all_returns_empty(repo, db_session):
    # WHEN
    jobs = repo.get_all()

    # THEN
    assert len(jobs) == 0
