from decimal import Decimal
from fastapi.testclient import TestClient


def test_list_all_payments_with_student_name(client: TestClient):
    # Create student
    res = client.post(
        "/students",
        json={
            "name": "Farrux Zokirov",
            "phone": "+998901112233",
            "group_name": "IELTS-5",
            "monthly_fee": 800000.0,
        },
    )
    assert res.status_code == 201
    s_id = res.json()["id"]

    # Record payment
    p_res = client.post(
        "/payments",
        json={"student_id": s_id, "amount": 800000.0, "payment_date": "2026-10-15"},
    )
    assert p_res.status_code == 201

    # List payments
    list_res = client.get("/payments")
    assert list_res.status_code == 200
    payments = list_res.json()
    assert len(payments) >= 1
    found = next((p for p in payments if p["id"] == p_res.json()["id"]), None)
    assert found is not None
    assert found["student_name"] == "Farrux Zokirov"
    assert found["group_name"] == "IELTS-5"
    assert float(found["amount"]) == 800000.0


def test_dashboard_summary_calculations(client: TestClient):
    month = "2026-05"

    # Create 2 students
    s1 = client.post(
        "/students",
        json={
            "name": "Student A",
            "phone": "+998901110001",
            "group_name": "English",
            "monthly_fee": 500000.0,
        },
    ).json()

    s2 = client.post(
        "/students",
        json={
            "name": "Student B",
            "phone": "+998901110002",
            "group_name": "Math",
            "monthly_fee": 600000.0,
        },
    ).json()

    # s1 pays 200,000 (debt = 300,000)
    client.post(
        "/payments",
        json={"student_id": s1["id"], "amount": 200000.0, "payment_date": "2026-05-10"},
    )

    # s2 pays full 600,000 (debt = 0)
    client.post(
        "/payments",
        json={"student_id": s2["id"], "amount": 600000.0, "payment_date": "2026-05-12"},
    )

    resp = client.get(f"/dashboard/summary?month={month}")
    assert resp.status_code == 200
    data = resp.json()

    assert data["month"] == month
    assert data["total_students"] >= 2
    assert float(data["total_collected"]) >= 800000.0
    # s1 is debtor with debt 300,000; s2 is not debtor
    assert data["debtors_count"] >= 1
    assert float(data["total_debt"]) >= 300000.0
    assert len(data["recent_payments"]) >= 2


def test_dashboard_summary_invalid_month(client: TestClient):
    resp = client.get("/dashboard/summary?month=invalid-date")
    assert resp.status_code == 422


def test_frontend_serving_endpoints(client: TestClient):
    # API health check
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    # Root API client
    res_root_json = client.get("/", headers={"Accept": "application/json"})
    assert res_root_json.status_code == 200
    assert res_root_json.json()["status"] == "healthy"

    # Browser visiting /dashboard or /
    res_dash = client.get("/dashboard")
    assert res_dash.status_code == 200
    assert "text/html" in res_dash.headers.get("content-type", "")

