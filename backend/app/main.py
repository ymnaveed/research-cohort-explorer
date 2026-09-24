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


@app.get("/cohorts/{cohort_id}/criteria")
def get_cohort_criteria(cohort_id: int):
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT cohort_definition_id
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

            cursor.execute(
                """
                SELECT
                    cohort_criterion_id,
                    criterion_order,
                    criterion_type,
                    domain,
                    field_name,
                    operator,
                    value_text
                FROM cohort_criteria
                WHERE cohort_definition_id = %s
                ORDER BY criterion_order
                """,
                (cohort_id,),
            )
            criteria = cursor.fetchall()

    return criteria


@app.get("/cohorts/{cohort_id}/results")
def get_cohort_results(cohort_id: int):
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    cohort_definition_id,
                    cohort_name
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

            cursor.execute(
                """
                SELECT COUNT(*) AS member_count
                FROM cohort_membership
                WHERE cohort_definition_id = %s
                """,
                (cohort_id,),
            )
            result = cursor.fetchone()

    return {
        "cohort_definition_id": cohort["cohort_definition_id"],
        "cohort_name": cohort["cohort_name"],
        "member_count": result["member_count"],
    }