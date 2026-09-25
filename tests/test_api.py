from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "research-cohort-explorer-api",
    }
def test_database_health_check():
    response = client.get("/health/database")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["database"] == "research_cohort"
    assert data["patient_count"] == 100000
def test_list_cohorts():
    response = client.get("/cohorts")

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1
    assert data[0]["cohort_definition_id"] == 1
    assert data[0]["cohort_name"] == "Adult Type 2 Diabetes"
    assert data[0]["status"] == "active"
def test_get_cohort():
    response = client.get("/cohorts/1")

    assert response.status_code == 200

    data = response.json()

    assert data["cohort_definition_id"] == 1
    assert data["cohort_name"] == "Adult Type 2 Diabetes"
    assert data["version"] == 1
    assert data["status"] == "active"


def test_get_cohort_not_found():
    response = client.get("/cohorts/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Cohort not found",
    }
def test_get_cohort_criteria():
    response = client.get("/cohorts/1/criteria")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 4

    assert data[0]["criterion_type"] == "inclusion"
    assert data[0]["domain"] == "diagnosis"
    assert data[0]["field_name"] == "diagnosis_code"
    assert data[0]["operator"] == "="
    assert data[0]["value_text"] == "E11.9"
def test_get_cohort_results():
    response = client.get("/cohorts/1/results")

    assert response.status_code == 200

    data = response.json()

    assert data["cohort_definition_id"] == 1
    assert data["cohort_name"] == "Adult Type 2 Diabetes"
    assert data["member_count"] == 6620
def test_execute_cohort():
    response = client.post("/cohorts/1/execute")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "succeeded"
    assert data["cohort_definition_id"] == 1
    assert data["cohort_name"] == "Adult Type 2 Diabetes"
    assert data["member_count"] == 6620
def test_execute_cohort_not_found():
    response = client.post("/cohorts/999/execute")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Cohort not found",
    }    