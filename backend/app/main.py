from fastapi import FastAPI, HTTPException
from psycopg.rows import dict_row

from backend.app.database import get_connection


app = FastAPI(
    title="Research Cohort Explorer API",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "research-cohort-explorer-api",
    }


@app.get("/health/database")
def database_health_check():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM patients")
            patient_count = cursor.fetchone()[0]

    return {
        "status": "ok",
        "database": "research_cohort",
        "patient_count": patient_count,
    }


@app.get("/cohorts")
def list_cohorts():
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    cohort_definition_id,
                    cohort_name,
                    description,
                    study_start_date,
                    study_end_date,
                    version,
                    status
                FROM cohort_definitions
                ORDER BY cohort_definition_id
                """
            )
            cohorts = cursor.fetchall()

    return cohorts


@app.get("/cohorts/{cohort_id}")
def get_cohort(cohort_id: int):
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    cohort_definition_id,
                    cohort_name,
                    description,
                    study_start_date,
                    study_end_date,
                    version,
                    status
                FROM cohort_definitions
                WHERE cohort_definition_id = %s
                """,
                (cohort_id,),
            )
            cohort = cursor.fetchone()

    if cohort is None:
        raise HTTPException(
            status_code=404,
            detail="Cohort not found",
        )

    return cohort