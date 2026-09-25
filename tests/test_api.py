from fastapi.testclient import TestClient

from backend.app.main import app

from backend.app.database import get_connection


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
def test_create_cohort_rejects_invalid_dates():
    response = client.post(
        "/cohorts",
        json={
            "cohort_name": "Invalid Date Cohort",
            "study_start_date": "2025-12-31",
            "study_end_date": "2020-01-01",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Study end date cannot be before study start date",
    }
def test_create_cohort():
    response = client.post(
        "/cohorts",
        json={
            "cohort_name": "Automated API Test Cohort",
            "description": "Temporary cohort created by the API test suite",
            "study_start_date": "2020-01-01",
            "study_end_date": "2025-12-31",
        },
    )

    assert response.status_code == 201

    data = response.json()
    cohort_id = data["cohort_definition_id"]

    try:
        assert data["cohort_name"] == "Automated API Test Cohort"
        assert data["description"] == "Temporary cohort created by the API test suite"
        assert data["study_start_date"] == "2020-01-01"
        assert data["study_end_date"] == "2025-12-31"
        assert data["version"] == 1
        assert data["status"] == "draft"
    finally:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM cohort_definitions
                    WHERE cohort_definition_id = %s
                    """,
                    (cohort_id,),
                )    
def test_create_cohort_criterion():
    cohort_response = client.post(
        "/cohorts",
        json={
            "cohort_name": "Criterion API Test Cohort",
            "description": "Temporary cohort for criterion API testing",
            "study_start_date": "2020-01-01",
            "study_end_date": "2025-12-31",
        },
    )

    assert cohort_response.status_code == 201

    cohort_id = cohort_response.json()["cohort_definition_id"]

    try:
        response = client.post(
            f"/cohorts/{cohort_id}/criteria",
            json={
                "criterion_order": 1,
                "criterion_type": "inclusion",
                "domain": "demographics",
                "field_name": "age_at_study_end",
                "operator": ">=",
                "value_text": "18",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["cohort_definition_id"] == cohort_id
        assert data["criterion_order"] == 1
        assert data["criterion_type"] == "inclusion"
        assert data["domain"] == "demographics"
        assert data["field_name"] == "age_at_study_end"
        assert data["operator"] == ">="
        assert data["value_text"] == "18"

    finally:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM cohort_criteria
                    WHERE cohort_definition_id = %s
                    """,
                    (cohort_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM cohort_definitions
                    WHERE cohort_definition_id = %s
                    """,
                    (cohort_id,),
                )
def test_create_cohort_criterion_rejects_invalid_value_type():
    cohort_response = client.post(
        "/cohorts",
        json={
            "cohort_name": "Invalid Criterion Value Test Cohort",
            "description": "Temporary cohort for criterion value validation testing",
            "study_start_date": "2020-01-01",
            "study_end_date": "2025-12-31",
        },
    )

    assert cohort_response.status_code == 201

    cohort_id = cohort_response.json()["cohort_definition_id"]

    try:
        response = client.post(
            f"/cohorts/{cohort_id}/criteria",
            json={
                "criterion_order": 1,
                "criterion_type": "inclusion",
                "domain": "demographics",
                "field_name": "age_at_study_end",
                "operator": ">=",
                "value_text": "abc",
            },
        )

        assert response.status_code == 400
        assert response.json() == {
            "detail": "Invalid value for criterion type integer",
        }

    finally:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM cohort_criteria
                    WHERE cohort_definition_id = %s
                    """,
                    (cohort_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM cohort_definitions
                    WHERE cohort_definition_id = %s
                    """,
                    (cohort_id,),
                )
def test_create_cohort_criterion_rejects_unsupported_criterion():
    cohort_response = client.post(
        "/cohorts",
        json={
            "cohort_name": "Unsupported Criterion Test Cohort",
            "description": "Temporary cohort for whitelist validation testing",
            "study_start_date": "2020-01-01",
            "study_end_date": "2025-12-31",
        },
    )

    assert cohort_response.status_code == 201

    cohort_id = cohort_response.json()["cohort_definition_id"]

    try:
        response = client.post(
            f"/cohorts/{cohort_id}/criteria",
            json={
                "criterion_order": 1,
                "criterion_type": "inclusion",
                "domain": "demographics",
                "field_name": "race",
                "operator": "=",
                "value_text": "White",
            },
        )

        assert response.status_code == 400
        assert response.json() == {
            "detail": "Unsupported cohort criterion",
        }

    finally:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM cohort_criteria
                    WHERE cohort_definition_id = %s
                    """,
                    (cohort_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM cohort_definitions
                    WHERE cohort_definition_id = %s
                    """,
                    (cohort_id,),
                )
def test_create_cohort_criterion_rejects_non_diagnosis_exclusion():
    cohort_response = client.post(
        "/cohorts",
        json={
            "cohort_name": "Exclusion Rule Test Cohort",
            "description": "Temporary cohort for exclusion rule testing",
            "study_start_date": "2020-01-01",
            "study_end_date": "2025-12-31",
        },
    )

    assert cohort_response.status_code == 201

    cohort_id = cohort_response.json()["cohort_definition_id"]

    try:
        response = client.post(
            f"/cohorts/{cohort_id}/criteria",
            json={
                "criterion_order": 1,
                "criterion_type": "exclusion",
                "domain": "medication",
                "field_name": "medication_code",
                "operator": "=",
                "value_text": "TEST",
            },
        )

        assert response.status_code == 400
        assert response.json() == {
            "detail": (
                "Cohort Engine v1 supports exclusions only "
                "for diagnosis criteria"
            ),
        }

    finally:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM cohort_criteria
                    WHERE cohort_definition_id = %s
                    """,
                    (cohort_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM cohort_definitions
                    WHERE cohort_definition_id = %s
                    """,
                    (cohort_id,),
                )
def test_create_cohort_criterion_cohort_not_found():
    response = client.post(
        "/cohorts/999999/criteria",
        json={
            "criterion_order": 1,
            "criterion_type": "inclusion",
            "domain": "demographics",
            "field_name": "age_at_study_end",
            "operator": ">=",
            "value_text": "18",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Cohort not found",
    }