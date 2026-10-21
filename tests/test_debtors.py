def test_debt_after_partial_payment(client):
    """Test 9: Calculating debt after a partial payment."""
    # Student fee: 500,000, Paid: 300,000 -> Debt: 200,000
    student = client.post(
        "/students",
        json={
            "name": "Ali Valiyev",
            "phone": "+998901234567",
            "group_name": "Python Beginner",
            "monthly_fee": 500000.0,
        },
    ).json()

    client.post(
        "/payments",
        json={
            "student_id": student["id"],
            "amount": 300000.0,
            "payment_date": "2026-10-10",
        },
    )

    res = client.get("/debtors?month=2026-10")
    assert res.status_code == 200
    data = res.json()
    assert data["month"] == "2026-10"
    assert len(data["debtors"]) == 1
    debtor = data["debtors"][0]
    assert debtor["student_id"] == student["id"]
    assert debtor["name"] == "Ali Valiyev"
    assert debtor["phone"] == "+998901234567"
    assert debtor["group_name"] == "Python Beginner"
    assert debtor["monthly_fee"] == 500000.0
    assert debtor["total_paid"] == 300000.0
    assert debtor["debt"] == 200000.0


def test_exclude_fully_paid_students(client):
    """Test 10: Excluding fully paid students."""
    # Student fee: 400,000, Paid: 400,000 -> Debt: 0 -> Not a debtor
    student = client.post(
        "/students",
        json={
            "name": "Fully Paid Student",
            "phone": "+998901112233",
            "group_name": "Frontend",
            "monthly_fee": 400000.0,
        },
    ).json()

    client.post(
        "/payments",
        json={
            "student_id": student["id"],
            "amount": 400000.0,
            "payment_date": "2026-10-12",
        },
    )

    res = client.get("/debtors?month=2026-10")
    assert res.status_code == 200
    data = res.json()
    assert len(data["debtors"]) == 0


def test_exclude_overpaid_students(client):
    """Test 11: Excluding overpaid students."""
    # Student fee: 400,000, Paid: 500,000 -> Overpaid -> Not a debtor
    student = client.post(
        "/students",
        json={
            "name": "Overpaid Student",
            "phone": "+998902223344",
            "group_name": "Data Science",
            "monthly_fee": 400000.0,
        },
    ).json()

    client.post(
        "/payments",
        json={
            "student_id": student["id"],
            "amount": 500000.0,
            "payment_date": "2026-10-15",
        },
    )

    res = client.get("/debtors?month=2026-10")
    assert res.status_code == 200
    data = res.json()
    assert len(data["debtors"]) == 0


def test_aggregate_multiple_payments_in_one_month(client):
    """Test 12: Aggregating multiple payments in one month."""
    # Student fee: 600,000, Paid 100,000 + 200,000 = 300,000 -> Debt: 300,000
    student = client.post(
        "/students",
        json={
            "name": "Multi Payer",
            "phone": "+998903334455",
            "group_name": "Backend",
            "monthly_fee": 600000.0,
        },
    ).json()

    client.post(
        "/payments",
        json={
            "student_id": student["id"],
            "amount": 100000.0,
            "payment_date": "2026-10-05",
        },
    )
    client.post(
        "/payments",
        json={
            "student_id": student["id"],
            "amount": 200000.0,
            "payment_date": "2026-10-25",
        },
    )

    res = client.get("/debtors?month=2026-10")
    assert res.status_code == 200
    data = res.json()
    assert len(data["debtors"]) == 1
    debtor = data["debtors"][0]
    assert debtor["student_id"] == student["id"]
    assert debtor["total_paid"] == 300000.0
    assert debtor["debt"] == 300000.0


def test_ignore_payments_outside_requested_month(client):
    """Test 13: Ignoring payments outside the requested month."""
    # Student fee: 500,000
    # Payment in September: 500,000
    # Payment in November: 500,000
    # Payments in October: 0
    # Expected in October: Debtor with total_paid: 0, debt: 500,000
    student = client.post(
        "/students",
        json={
            "name": "September Payer",
            "phone": "+998904445566",
            "group_name": "Mobile",
            "monthly_fee": 500000.0,
        },
    ).json()

    # September payment (outside October)
    client.post(
        "/payments",
        json={
            "student_id": student["id"],
            "amount": 500000.0,
            "payment_date": "2026-09-30",
        },
    )
    # November payment (outside October)
    client.post(
        "/payments",
        json={
            "student_id": student["id"],
            "amount": 500000.0,
            "payment_date": "2026-11-01",
        },
    )

    # Check October debtors
    res_oct = client.get("/debtors?month=2026-10")
    assert res_oct.status_code == 200
    oct_debtors = res_oct.json()["debtors"]
    assert len(oct_debtors) == 1
    assert oct_debtors[0]["student_id"] == student["id"]
    assert oct_debtors[0]["total_paid"] == 0.0
    assert oct_debtors[0]["debt"] == 500000.0

    # Check September debtors (should be 0 because fully paid in September)
    res_sep = client.get("/debtors?month=2026-09")
    assert res_sep.status_code == 200
    assert len(res_sep.json()["debtors"]) == 0


def test_handle_month_with_no_payments(client):
    """Test 14: Handling a month with no payments."""
    student = client.post(
        "/students",
        json={
            "name": "No Payment Student",
            "phone": "+998905556677",
            "group_name": "DevOps",
            "monthly_fee": 700000.0,
        },
    ).json()

    # Query a month where no payments have been recorded by anyone
    res = client.get("/debtors?month=2025-01")
    assert res.status_code == 200
    data = res.json()
    assert data["month"] == "2025-01"
    assert len(data["debtors"]) == 1
    debtor = data["debtors"][0]
    assert debtor["student_id"] == student["id"]
    assert debtor["total_paid"] == 0.0
    assert debtor["debt"] == 700000.0


def test_reject_invalid_month_formats(client):
    """Test 15: Rejecting invalid month formats."""
    invalid_formats = [
        "2026-13",    # Invalid month 13
        "2026-00",    # Invalid month 00
        "2026/10",    # Slash separator
        "10-2026",    # Reversed
        "2026-1",     # Missing leading zero
        "2026-10-15", # Full date instead of month
        "invalid",    # Random text
        "",           # Empty string
    ]

    for inv in invalid_formats:
        res = client.get(f"/debtors?month={inv}")
        assert res.status_code == 400, f"Expected 400 for '{inv}', got {res.status_code}"
        assert "Invalid month format" in res.json()["detail"]
