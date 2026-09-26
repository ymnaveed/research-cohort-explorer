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
def test_create_cohort_criterion_rejects_duplicate_order():
    cohort_response = client.post(
        "/cohorts",
        json={
            "cohort_name": "Duplicate Criterion Order Test Cohort",
            "description": "Temporary cohort for duplicate order testing",
            "study_start_date": "2020-01-01",
            "study_end_date": "2025-12-31",
        },
    )

    assert cohort_response.status_code == 201

    cohort_id = cohort_response.json()["cohort_definition_id"]

    try:
        first_response = client.post(
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

        assert first_response.status_code == 201

        duplicate_response = client.post(
            f"/cohorts/{cohort_id}/criteria",
            json={
                "criterion_order": 1,
                "criterion_type": "inclusion",
                "domain": "diagnosis",
                "field_name": "diagnosis_code",
                "operator": "=",
                "value_text": "E11.9",
            },
        )

        assert duplicate_response.status_code == 409
        assert duplicate_response.json() == {
            "detail": "Criterion order already exists for this cohort",
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
def test_delete_cohort_criterion():
    cohort_response = client.post(
        "/cohorts",
        json={
            "cohort_name": "Delete Criterion Test Cohort",
            "description": "Temporary cohort for criterion deletion testing",
            "study_start_date": "2020-01-01",
            "study_end_date": "2025-12-31",
        },
    )

    assert cohort_response.status_code == 201

    cohort_id = cohort_response.json()["cohort_definition_id"]

    try:
        criterion_response = client.post(
            f"/cohorts/{cohort_id}/criteria",
            json={
                "criterion_order": 1,
                "criterion_type": "inclusion",
                "domain": "diagnosis",
                "field_name": "diagnosis_code",
                "operator": "=",
                "value_text": "E11.9",
            },
        )

        assert criterion_response.status_code == 201

        criterion_id = criterion_response.json()["cohort_criterion_id"]

        delete_response = client.delete(
            f"/cohorts/{cohort_id}/criteria/{criterion_id}"
        )

        assert delete_response.status_code == 200
        assert delete_response.json() == {
            "status": "deleted",
            "cohort_definition_id": cohort_id,
            "cohort_criterion_id": criterion_id,
        }

        criteria_response = client.get(
            f"/cohorts/{cohort_id}/criteria"
        )

        assert criteria_response.status_code == 200
        assert criteria_response.json() == []

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
def test_delete_cohort_criterion_not_found():
    response = client.delete(
        "/cohorts/1/criteria/999999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Cohort criterion not found",
    }
def test_delete_cohort_criterion_cohort_not_found():
    response = client.delete(
        "/cohorts/999999/criteria/999999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Cohort not found",
    }
def test_get_cohort_members():
    response = client.get("/cohorts/1/members?limit=5&offset=0")

    assert response.status_code == 200

    data = response.json()

    assert data["cohort_definition_id"] == 1
    assert data["cohort_name"] == "Adult Type 2 Diabetes"
    assert data["member_count"] == 6620
    assert data["limit"] == 5
    assert data["offset"] == 0
    assert len(data["members"]) == 5

    first_member = data["members"][0]

    assert first_member == {
        "research_id": "P-000026",
        "date_of_birth": "1961-12-05",
        "age_at_study_end": 64,
        "sex": "M",
        "race": "Asian",
        "ethnicity": "Hispanic or Latino",
        "zip3": "544",
    }


def test_get_cohort_members_offset():
    response = client.get("/cohorts/1/members?limit=1&offset=1")

    assert response.status_code == 200

    data = response.json()

    assert data["limit"] == 1
    assert data["offset"] == 1
    assert len(data["members"]) == 1
    assert data["members"][0]["research_id"] == "P-000034"


def test_get_cohort_members_not_found():
    response = client.get("/cohorts/999999/members")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Cohort not found",
    }


def test_get_cohort_members_rejects_invalid_pagination():
    response = client.get("/cohorts/1/members?limit=101&offset=0")

    assert response.status_code == 422

    response = client.get("/cohorts/1/members?limit=5&offset=-1")

    assert response.status_code == 422
def test_list_patients():
    response = client.get("/patients?limit=5&offset=0")

    assert response.status_code == 200

    data = response.json()

    assert data["patient_count"] == 100000
    assert data["limit"] == 5
    assert data["offset"] == 0
    assert len(data["patients"]) == 5

    first_patient = data["patients"][0]

    assert first_patient == {
        "research_id": "P-000001",
        "date_of_birth": "1988-10-17",
        "age_at_study_end": 37,
        "sex": "M",
        "race": "White",
        "ethnicity": "Not Hispanic or Latino",
        "zip3": "547",
        "death_date": None,
    }
def test_get_patient():
    response = client.get("/patients/P-000001")

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "research_id": "P-000001",
        "date_of_birth": "1988-10-17",
        "age_at_study_end": 37,
        "sex": "M",
        "race": "White",
        "ethnicity": "Not Hispanic or Latino",
        "zip3": "547",
        "death_date": None,
    }


def test_get_patient_not_found():
    response = client.get("/patients/P-999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Patient not found",
    }    
def test_get_patient_encounters():
    response = client.get("/patients/P-000001/encounters")

    assert response.status_code == 200

    data = response.json()

    assert data["research_id"] == "P-000001"
    assert data["encounter_count"] == 19
    assert len(data["encounters"]) == 19

    first_encounter = data["encounters"][0]

    assert first_encounter["encounter_id"] == 19
    assert first_encounter["encounter_date"] == "2025-10-13T10:24:04"
    assert first_encounter["encounter_type_code"] == "TELEHEALTH"
def test_get_patient_diagnoses():
    response = client.get("/patients/P-000001/diagnoses")

    assert response.status_code == 200

    data = response.json()

    assert data["research_id"] == "P-000001"
    assert data["diagnosis_count"] == 1
    assert len(data["diagnoses"]) == 1

    diagnosis = data["diagnoses"][0]

    assert diagnosis["diagnosis_code"] == "I10"
    assert diagnosis["diagnosis_description"] == "Essential hypertension"
    assert diagnosis["diagnosis_category"] == "Cardiovascular"
    assert diagnosis["diagnosis_type"] == "PRIMARY"
    assert diagnosis["recorded_date"] == "2019-08-07"
def test_get_patient_labs():
    response = client.get("/patients/P-000001/labs")

    assert response.status_code == 200

    data = response.json()

    assert data["research_id"] == "P-000001"
    assert data["lab_result_count"] == 19
    assert len(data["lab_results"]) == 19

    first_lab = data["lab_results"][0]

    assert first_lab["test_code"] == "HDL"
    assert first_lab["test_name"] == "HDL Cholesterol"
    assert first_lab["result_date"] == "2025-03-14T19:48:08"
    assert first_lab["unit"] == "mg/dL"
def test_get_patient_medications():
    response = client.get("/patients/P-000001/medications")

    assert response.status_code == 200

    data = response.json()

    assert data["research_id"] == "P-000001"
    assert data["medication_count"] == 2
    assert len(data["medications"]) == 2

    first_medication = data["medications"][0]

    assert first_medication["medication_code"] == "LISINOPRIL"
    assert first_medication["medication_name"] == "Lisinopril"
    assert first_medication["medication_class"] == "ACE Inhibitor"
    assert first_medication["dose"] == "10 mg"
    assert first_medication["route"] == "ORAL"
    assert first_medication["status"] == "DISCONTINUED"
def test_get_patient_procedures():
    response = client.get("/patients/P-000001/procedures")

    assert response.status_code == 200

    data = response.json()

    assert data["research_id"] == "P-000001"
    assert data["procedure_count"] == 3
    assert len(data["procedures"]) == 3

    first_procedure = data["procedures"][0]

    assert first_procedure["procedure_code"] == "ECG"
    assert first_procedure["procedure_name"] == "Electrocardiogram"
    assert first_procedure["procedure_category"] == "Cardiology"
    assert first_procedure["procedure_date"] == "2025-10-13T07:29:55"
def test_get_patient_notes():
    response = client.get("/patients/P-000001/notes")

    assert response.status_code == 200

    data = response.json()

    assert data["research_id"] == "P-000001"
    assert data["note_count"] == 26
    assert len(data["notes"]) == 26

    first_note = data["notes"][0]

    assert first_note["note_id"] == 26
    assert first_note["encounter_id"] == 19
    assert first_note["note_type_code"] == "PROGRESS"
    assert first_note["note_type_description"] == "Progress Note"
    assert first_note["note_category"] == "Clinical"
    assert first_note["note_date"] == "2025-10-13T12:14:04"