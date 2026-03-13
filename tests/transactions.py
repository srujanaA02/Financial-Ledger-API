def test_deposit(client, account_a):
    res = client.post("/api/v1/deposits", json={
        "account_id": account_a["id"],
        "amount": 500,
        "currency": "USD",
        "description": "Test deposit"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["transaction_type"] == "deposit"
    assert data["status"] == "completed"
    assert data["amount"] == "500.0000"


def test_deposit_updates_balance(client, account_a):
    client.post("/api/v1/deposits", json={
        "account_id": account_a["id"],
        "amount": 750
    })
    res = client.get(f"/api/v1/accounts/{account_a['id']}")
    assert res.json()["balance"] == "750.0000"


def test_deposit_negative_amount(client, account_a):
    res = client.post("/api/v1/deposits", json={
        "account_id": account_a["id"],
        "amount": -100
    })
    assert res.status_code == 400


def test_transfer_success(client, funded_account, account_b):
    res = client.post("/api/v1/transfers", json={
        "source_account_id": funded_account["id"],
        "destination_account_id": account_b["id"],
        "amount": 300
    })
    assert res.status_code == 201
    assert res.json()["status"] == "completed"


def test_transfer_updates_both_balances(client, funded_account, account_b):
    client.post("/api/v1/transfers", json={
        "source_account_id": funded_account["id"],
        "destination_account_id": account_b["id"],
        "amount": 400
    })
    res_a = client.get(f"/api/v1/accounts/{funded_account['id']}")
    res_b = client.get(f"/api/v1/accounts/{account_b['id']}")
    assert res_a.json()["balance"] == "600.0000"
    assert res_b.json()["balance"] == "400.0000"


def test_transfer_insufficient_funds(client, funded_account, account_b):
    res = client.post("/api/v1/transfers", json={
        "source_account_id": funded_account["id"],
        "destination_account_id": account_b["id"],
        "amount": 9999
    })
    assert res.status_code == 422
    assert res.json()["detail"] == "Insufficient funds"


def test_transfer_source_not_found(client, account_b):
    res = client.post("/api/v1/transfers", json={
        "source_account_id": "00000000-0000-0000-0000-000000000000",
        "destination_account_id": account_b["id"],
        "amount": 100
    })
    assert res.status_code == 404


def test_withdrawal_success(client, funded_account):
    res = client.post("/api/v1/withdrawals", json={
        "account_id": funded_account["id"],
        "amount": 200
    })
    assert res.status_code == 201
    assert res.json()["status"] == "completed"


def test_withdrawal_insufficient_funds(client, funded_account):
    res = client.post("/api/v1/withdrawals", json={
        "account_id": funded_account["id"],
        "amount": 9999
    })
    assert res.status_code == 422


def test_double_entry_creates_two_ledger_entries(client, funded_account, account_b):
    client.post("/api/v1/transfers", json={
        "source_account_id": funded_account["id"],
        "destination_account_id": account_b["id"],
        "amount": 100
    })
    res_a = client.get(f"/api/v1/accounts/{funded_account['id']}/ledger")
    res_b = client.get(f"/api/v1/accounts/{account_b['id']}/ledger")

    a_entries = res_a.json()["entries"]
    b_entries = res_b.json()["entries"]

    # Account A: 1 credit (deposit) + 1 debit (transfer)
    assert any(e["entry_type"] == "debit" for e in a_entries)
    # Account B: 1 credit (transfer received)
    assert any(e["entry_type"] == "credit" for e in b_entries)


def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"