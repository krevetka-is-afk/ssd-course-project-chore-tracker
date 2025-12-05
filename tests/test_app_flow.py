from datetime import date


def _register(client, name: str, password: str):
    resp = client.post("/auth/register", json={"name": name, "password": password})
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == name
    return body


def _login(client, username: str, password: str) -> str:
    resp = client.post("/auth/token", data={"username": username, "password": password})
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    return body["access_token"]


def test_full_chore_assignment_flow(client):
    # register two users
    _register(client, "alice", "pwd1")
    user2 = _register(client, "bob", "pwd2")

    token = _login(client, "alice", "pwd1")
    auth = {"Authorization": f"Bearer {token}"}

    # create group and add second user
    g_resp = client.post("/groups/", json={"name": "Family"}, headers=auth)
    assert g_resp.status_code == 201
    group = g_resp.json()
    assert group["user_ids"] == []

    add_resp = client.post(f"/groups/{group['id']}/users/{user2['id']}", headers=auth)
    assert add_resp.status_code == 204

    # create a chore
    c_resp = client.post(
        "/chores/",
        json={"title": "Dishes", "description": "Evening dishes"},
        headers=auth,
    )
    assert c_resp.status_code == 201
    chore = c_resp.json()
    assert chore["title"] == "Dishes"

    # assign the chore to bob
    due_date = date.today().isoformat()
    a_resp = client.post(
        "/assignments/",
        json={
            "chore_id": chore["id"],
            "group_id": group["id"],
            "assigned_to_user_id": user2["id"],
            "due_date": due_date,
        },
        headers=auth,
    )
    assert a_resp.status_code == 201
    assignment = a_resp.json()
    assert assignment["status"] == "pending"
    assert assignment["assigned_to_user_id"] == user2["id"]

    # mark done and check listing filters by user
    done_resp = client.post(f"/assignments/{assignment['id']}/done", headers=auth)
    assert done_resp.status_code == 204

    list_resp = client.get(f"/assignments/?user_id={user2['id']}", headers=auth)
    assert list_resp.status_code == 200
    listed = list_resp.json()
    assert len(listed) == 1
    assert listed[0]["status"] == "done"


def test_auth_invalid_password(client):
    _register(client, "carol", "goodpass")
    resp = client.post("/auth/token", data={"username": "carol", "password": "bad"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Incorrect username or password"
