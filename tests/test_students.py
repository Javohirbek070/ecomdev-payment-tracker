def test_create_student_success(client):
    """Test 1: Creating a student successfully."""
    payload = {
        "name": "Ali Valiyev",
        "phone": "+998901234567",
        "group_name": "Python Backend",
        "monthly_fee": 500000.0,
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == "Ali Valiyev"
    assert data["phone"] == "+998901234567"
    assert data["group_name"] == "Python Backend"
    assert data["monthly_fee"] == 500000.0
    assert "created_at" in data
    assert "updated_at" in data


def test_list_and_retrieve_students(client):
    """Test 2: Listing and retrieving students."""
    # Create two students
    s1 = client.post(
        "/students",
        json={
            "name": "Student One",
            "phone": "+998901111111",
            "group_name": "Group A",
            "monthly_fee": 300000,
        },
    ).json()
    s2 = client.post(
        "/students",
        json={
            "name": "Student Two",
            "phone": "+998902222222",
            "group_name": "Group B",
            "monthly_fee": 450000,
        },
    ).json()

    # List students
    list_res = client.get("/students")
    assert list_res.status_code == 200
    students = list_res.json()
    assert len(students) >= 2
    student_ids = [s["id"] for s in students]
    assert s1["id"] in student_ids
    assert s2["id"] in student_ids

    # Retrieve one student
    retrieve_res = client.get(f"/students/{s1['id']}")
    assert retrieve_res.status_code == 200
    retrieved = retrieve_res.json()
    assert retrieved["id"] == s1["id"]
    assert retrieved["name"] == "Student One"


def test_update_student(client):
    """Test 3: Updating a student."""
    created = client.post(
        "/students",
        json={
            "name": "Original Name",
            "phone": "+998901234567",
            "group_name": "Group Original",
            "monthly_fee": 400000,
        },
    ).json()

    patch_payload = {
        "name": "Updated Name",
        "monthly_fee": 600000,
    }
    update_res = client.patch(f"/students/{created['id']}", json=patch_payload)
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["name"] == "Updated Name"
    assert updated["monthly_fee"] == 600000
    assert updated["phone"] == "+998901234567"  # Unchanged
    assert updated["group_name"] == "Group Original"  # Unchanged


def test_handle_nonexistent_student(client):
    """Test 4: Handling a nonexistent student."""
    nonexistent_id = 99999
    # GET
    get_res = client.get(f"/students/{nonexistent_id}")
    assert get_res.status_code == 404
    assert f"Student with id {nonexistent_id} not found" in get_res.json()["detail"]

    # PATCH
    patch_res = client.patch(f"/students/{nonexistent_id}", json={"name": "New Name"})
    assert patch_res.status_code == 404
    assert f"Student with id {nonexistent_id} not found" in patch_res.json()["detail"]

    # DELETE
    del_res = client.delete(f"/students/{nonexistent_id}")
    assert del_res.status_code == 404
    assert f"Student with id {nonexistent_id} not found" in del_res.json()["detail"]


def test_reject_invalid_monthly_fees(client):
    """Test 5: Rejecting invalid monthly fees (negative or zero)."""
    # Negative fee
    res_neg = client.post(
        "/students",
        json={
            "name": "Test User",
            "phone": "+998901234567",
            "group_name": "Python",
            "monthly_fee": -1000,
        },
    )
    assert res_neg.status_code == 422

    # Zero fee
    res_zero = client.post(
        "/students",
        json={
            "name": "Test User",
            "phone": "+998901234567",
            "group_name": "Python",
            "monthly_fee": 0,
        },
    )
    assert res_zero.status_code == 422

    # Patch with negative fee
    created = client.post(
        "/students",
        json={
            "name": "Valid Student",
            "phone": "+998901234567",
            "group_name": "Python",
            "monthly_fee": 500000,
        },
    ).json()

    patch_neg = client.patch(f"/students/{created['id']}", json={"monthly_fee": -500})
    assert patch_neg.status_code == 422


def test_reject_empty_required_fields(client):
    """Verify empty or whitespace-only required fields are rejected."""
    res = client.post(
        "/students",
        json={
            "name": "   ",
            "phone": "+998901234567",
            "group_name": "Group A",
            "monthly_fee": 500000,
        },
    )
    assert res.status_code == 422


def test_delete_student_without_payments(client):
    """Test deleting a student with no payment history succeeds."""
    created = client.post(
        "/students",
        json={
            "name": "Student To Delete",
            "phone": "+998901234567",
            "group_name": "Group A",
            "monthly_fee": 500000,
        },
    ).json()

    del_res = client.delete(f"/students/{created['id']}")
    assert del_res.status_code == 204

    # Verify no longer exists
    get_res = client.get(f"/students/{created['id']}")
    assert get_res.status_code == 404


def test_delete_student_with_payment_history_blocked(client):
    """Test 16: Handling student deletion with payment history according to the documented policy."""
    # 1. Create a student
    student = client.post(
        "/students",
        json={
            "name": "Vali Aliyev",
            "phone": "+998909876543",
            "group_name": "DevOps",
            "monthly_fee": 600000,
        },
    ).json()

    # 2. Record a payment for this student
    payment_res = client.post(
        "/payments",
        json={
            "student_id": student["id"],
            "amount": 300000,
            "payment_date": "2026-10-10",
        },
    )
    assert payment_res.status_code == 201

    # 3. Attempt to delete the student
    del_res = client.delete(f"/students/{student['id']}")
    assert del_res.status_code == 400
    error_detail = del_res.json()["detail"]
    assert "Cannot delete student" in error_detail
    assert "payment record(s) exist" in error_detail
    assert "accounting integrity" in error_detail

    # 4. Confirm the student is still present in the system
    get_res = client.get(f"/students/{student['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == student["id"]
