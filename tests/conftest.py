import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db
from app.main import app

# Use in-memory SQLite for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def account_a(client):
    res = client.post("/api/v1/accounts", json={
        "user_id": "user1",
        "account_type": "checking",
        "currency": "USD"
    })
    return res.json()


@pytest.fixture()
def account_b(client):
    res = client.post("/api/v1/accounts", json={
        "user_id": "user2",
        "account_type": "savings",
        "currency": "USD"
    })
    return res.json()


@pytest.fixture()
def funded_account(client, account_a):
    client.post("/api/v1/deposits", json={
        "account_id": account_a["id"],
        "amount": 1000,
        "currency": "USD"
    })
    return account_a