JD_TEXT = (
    "Need FastAPI and SQLAlchemy backend engineer. PostgreSQL, API testing, "
    "and Docker experience are required."
)
RESUME_TEXT = (
    "Built FastAPI backend services with SQLAlchemy and PostgreSQL. "
    "Wrote API tests for internal systems."
)


def create_successful_analysis(client):
    job = client.post("/api/jobs", json={"title": "Backend Engineer", "raw_text": JD_TEXT}).json()
    resume = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": RESUME_TEXT},
    ).json()
    return client.post("/api/analysis", json={"job_id": job["id"], "resume_id": resume["id"]}).json()


def test_generate_learning_tasks_contract(client):
    analysis_task = create_successful_analysis(client)

    response = client.post(
        "/api/learning/tasks/generate",
        json={"task_id": analysis_task["id"]},
    )

    assert response.status_code == 201
    tasks = response.json()
    assert tasks
    item = tasks[0]
    assert item["schema_version"] == "1"
    assert item["status"] == "not_started"
    assert item["source_report_id"]
    assert item["source_task_id"] == analysis_task["id"]
    assert item["title"]
    assert item["dimension"]
    assert "evidence_refs" in item


def test_generate_learning_tasks_from_report(client):
    analysis_task = create_successful_analysis(client)

    response = client.post(
        "/api/learning/tasks/generate",
        json={"task_id": analysis_task["id"]},
    )

    assert response.status_code == 201
    tasks = response.json()
    assert len(tasks) >= 1
    assert all(task["source_task_id"] == analysis_task["id"] for task in tasks)


def test_generate_learning_tasks_is_idempotent(client):
    analysis_task = create_successful_analysis(client)
    payload = {"task_id": analysis_task["id"]}

    first_response = client.post("/api/learning/tasks/generate", json=payload)
    second_response = client.post("/api/learning/tasks/generate", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    first = first_response.json()
    second = second_response.json()
    assert [item["id"] for item in second] == [item["id"] for item in first]


def test_generate_learning_tasks_rejects_missing_report(client):
    response = client.post("/api/learning/tasks/generate", json={"task_id": 999999})

    assert response.status_code == 404


def test_update_learning_task_status(client):
    analysis_task = create_successful_analysis(client)
    tasks = client.post(
        "/api/learning/tasks/generate",
        json={"task_id": analysis_task["id"]},
    ).json()
    task_id = tasks[0]["id"]

    doing_response = client.patch(f"/api/learning/tasks/{task_id}", json={"status": "doing"})
    done_response = client.patch(f"/api/learning/tasks/{task_id}", json={"status": "done"})

    assert doing_response.status_code == 200
    assert doing_response.json()["status"] == "doing"
    assert done_response.status_code == 200
    assert done_response.json()["status"] == "done"


def test_update_learning_task_status_rejects_invalid_value(client):
    analysis_task = create_successful_analysis(client)
    tasks = client.post(
        "/api/learning/tasks/generate",
        json={"task_id": analysis_task["id"]},
    ).json()
    task_id = tasks[0]["id"]

    response = client.patch(f"/api/learning/tasks/{task_id}", json={"status": "archived"})

    assert response.status_code == 422


def test_update_learning_task_status_rejects_missing_task(client):
    response = client.patch("/api/learning/tasks/999999", json={"status": "doing"})

    assert response.status_code == 404


def test_update_learning_task_status_rejects_done_reopen(client):
    analysis_task = create_successful_analysis(client)
    tasks = client.post(
        "/api/learning/tasks/generate",
        json={"task_id": analysis_task["id"]},
    ).json()
    task_id = tasks[0]["id"]

    assert client.patch(f"/api/learning/tasks/{task_id}", json={"status": "doing"}).status_code == 200
    assert client.patch(f"/api/learning/tasks/{task_id}", json={"status": "done"}).status_code == 200
    response = client.patch(f"/api/learning/tasks/{task_id}", json={"status": "doing"})

    assert response.status_code == 400
