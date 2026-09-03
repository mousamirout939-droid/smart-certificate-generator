from tests.conftest import create_admin, login


def test_login_success(client, db_session):
    create_admin(db_session, email="admin1@example.com")
    r = client.post("/api/auth/login", json={"email": "admin1@example.com", "password": "Password123!"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_invalid_password(client, db_session):
    create_admin(db_session, email="admin2@example.com")
    r = client.post("/api/auth/login", json={"email": "admin2@example.com", "password": "WrongPassword"})
    assert r.status_code == 401


def test_login_nonexistent_user(client):
    r = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "whatever"})
    assert r.status_code == 401


def test_me_requires_auth(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_me_returns_current_user(client, db_session):
    create_admin(db_session, email="admin3@example.com")
    headers = login(client, "admin3@example.com")
    r = client.get("/api/auth/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == "admin3@example.com"
    assert r.json()["role"] == "admin"


def test_learner_can_register(client):
    r = client.post("/api/auth/register", json={
        "full_name": "New Learner", "email": "new.learner@example.com", "password": "StrongPass123!",
    })
    assert r.status_code == 201
    assert "access_token" in r.json()

    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["role"] == "employee"
    assert me.json()["employee_id"] is not None
