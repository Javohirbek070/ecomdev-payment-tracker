def test_record_payment_success(client):
    """Test 6: Recording a payment successfully."""
    # 1. Create student
    student = client.post(
        "/students",
        json={
            "name": "Nodir Karimov",
            "phone": "+998901234567",
            "group_name": "Frontend",
            "monthly_fee": 400000,
        },
    ).json()

    # 2. Record payment
    payment_payload = {
        "student_id": student["id"],
        "amount": 200000.0,
        "payment_date": "2026-10-15",
    }
    response = client.post("/payments", json=payment_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["student_id"] == student["id"]
    assert data["amount"] == 200000.0
    assert data["payment_date"] == "2026-10-15"
    assert "created_at" in data


def test_reject_payment_for_nonexistent_student(client):
    """Test 7: Rejecting payments for nonexistent students."""
    nonexistent_id = 88888
    response = client.post(
        "/payments",
        json={
            "student_id": nonexistent_id,
            "amount": 150000,
            "payment_date": "2026-10-15",
        },
    )
    assert response.status_code == 404
    assert f"Student with id {nonexistent_id} not found" in response.json()["detail"]


def test_reject_invalid_payment_amounts(client):
    """Reject nonpositive or zero payment amounts."""
    student = client.post(
        "/students",
        json={
            "name": "Test Student",
            "phone": "+998901234567",
            "group_name": "QA",
            "monthly_fee": 300000,
        },
    ).json()

    # Negative amount
    res_neg = client.post(
        "/payments",
        json={
            "student_id": student["id"],
            "amount": -50000,
            "payment_date": "2026-10-15",
        },
    )
    assert res_neg.status_code == 422

    # Zero amount
    res_zero = client.post(
        "/payments",
        json={
            "student_id": student["id"],
            "amount": 0,
            "payment_date": "2026-10-15",
        },
    )
    assert res_zero.status_code == 422


def test_list_student_payment_history(client):
    """Test 8: Listing a student's payment history."""
    # 1. Create student
    student = client.post(
        "/students",
        json={
            "name": "Dilshod Rahimov",
            "phone": "+998901234567",
            "group_name": "Mobile",
            "monthly_fee": 500000,
        },
    ).json()

    # 2. Add two payments
    client.post(
        "/payments",
        json={
            "student_id": student["id"],
            "amount": 200000,
            "payment_date": "2026-10-05",
        },
    )
    client.post(
        "/payments",
        json={
            "student_id": student["id"],
            "amount": 300000,
            "payment_date": "2026-10-20",
        },
    )

    # 3. List payments for student
    res = client.get(f"/students/{student['id']}/payments")
    assert res.status_code == 200
    payments = res.json()
    assert len(payments) == 2
    amounts = [p["amount"] for p in payments]
    assert 200000 in amounts
    assert 300000 in amounts


def test_list_payments_nonexistent_student(client):
    """Listing payments for a nonexistent student returns 404."""
    nonexistent_id = 99999
    res = client.get(f"/students/{nonexistent_id}/payments")
    assert res.status_code == 404
    assert f"Student with id {nonexistent_id} not found" in res.json()["detail"]
