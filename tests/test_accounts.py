def test_create_account(client):
    res = client.post("/api/v1/accounts", json={
        "user_id": "user1",
        "account_type": "checking",
        "currency": "USD"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["user_id"] == "user1"
    assert data["account_type"] == "checking"
    assert data["status"] == "active"
    assert data["balance"] == "0"


def test_get_account(client, account_a):
    res = client.get(f"/api/v1/accounts/{account_a['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == account_a["id"]


def test_get_account_not_found(client):
    res = client.get("/api/v1/accounts/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 404
    assert res.json()["detail"] == "Account not found"


def test_get_ledger_empty(client, account_a):
    res = client.get(f"/api/v1/accounts/{account_a['id']}/ledger")
    assert res.status_code == 200
    data = res.json()
    assert data["total_entries"] == 0
    assert data["entries"] == []


def test_get_ledger_pagination(client, funded_account, account_b):
    # Make multiple transactions
    for _ in range(5):
        client.post("/api/v1/deposits", json={
            "account_id": funded_account["id"],
            "amount": 10
        })
    res = client.get(f"/api/v1/accounts/{funded_account['id']}/ledger?page=1&page_size=3")
    assert res.status_code == 200
    data = res.json()
    assert len(data["entries"]) == 3
    assert data["total_entries"] == 6  # 1 original + 5 more


def test_get_ledger_filter_by_entry_type(client, funded_account, account_b):
    client.post("/api/v1/transfers", json={
        "source_account_id": funded_account["id"],
        "destination_account_id": account_b["id"],
        "amount": 100
    })
    res = client.get(f"/api/v1/accounts/{funded_account['id']}/ledger?entry_type=debit")
    assert res.status_code == 200
    entries = res.json()["entries"]
    assert all(e["entry_type"] == "debit" for e in entries)