from datetime import date

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from psycopg.rows import dict_row

from backend.app.database import get_connection


class CohortCreate(BaseModel):
    cohort_name: str
    description: str | None = None
    study_start_date: date
    study_end_date: date


class CohortCriterionCreate(BaseModel):
    criterion_order: int
    criterion_type: str = "inclusion"
    domain: str
    field_name: str
    operator: str
    value_text: str


app = FastAPI(
    title="Research Cohort Explorer API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/cohorts/{cohort_id}/members")
def get_cohort_members(
    cohort_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
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

            cursor.execute(
                """
                SELECT
                    p.research_id,
                    p.date_of_birth,
                    p.age_at_study_end,
                    p.sex,
                    p.race,
                    p.ethnicity,
                    p.zip3
                FROM cohort_membership cm
                JOIN vw_patient_demographics p
                  ON p.patient_id = cm.patient_id
                WHERE cm.cohort_definition_id = %s
                ORDER BY p.research_id
                LIMIT %s
                OFFSET %s
                """,
                (
                    cohort_id,
                    limit,
                    offset,
                ),
            )
            members = cursor.fetchall()

    return {
        "cohort_definition_id": cohort["cohort_definition_id"],
        "cohort_name": cohort["cohort_name"],
        "member_count": result["member_count"],
        "limit": limit,
        "offset": offset,
        "members": members,
    }


@app.post("/cohorts/{cohort_id}/execute")
def execute_cohort_endpoint(cohort_id: int):
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
                SELECT execute_cohort(%s) AS member_count
                """,
                (cohort_id,),
            )
            result = cursor.fetchone()

    return {
        "status": "succeeded",
        "cohort_definition_id": cohort["cohort_definition_id"],
        "cohort_name": cohort["cohort_name"],
        "member_count": result["member_count"],
    }


@app.post("/cohorts", status_code=201)
def create_cohort(cohort: CohortCreate):
    if cohort.study_end_date < cohort.study_start_date:
        raise HTTPException(
            status_code=400,
            detail="Study end date cannot be before study start date",
        )

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO cohort_definitions (
                    cohort_name,
                    description,
                    study_start_date,
                    study_end_date
                )
                VALUES (%s, %s, %s, %s)
                RETURNING
                    cohort_definition_id,
                    cohort_name,
                    description,
                    study_start_date,
                    study_end_date,
                    version,
                    status
                """,
                (
                    cohort.cohort_name,
                    cohort.description,
                    cohort.study_start_date,
                    cohort.study_end_date,
                ),
            )
            created_cohort = cursor.fetchone()

    return created_cohort


@app.post("/cohorts/{cohort_id}/criteria", status_code=201)
def create_cohort_criterion(
    cohort_id: int,
    criterion: CohortCriterionCreate,
):
    if criterion.criterion_order < 1:
        raise HTTPException(
            status_code=400,
            detail="Criterion order must be at least 1",
        )

    if criterion.criterion_type not in {"inclusion", "exclusion"}:
        raise HTTPException(
            status_code=400,
            detail="Criterion type must be inclusion or exclusion",
        )

    if (
        criterion.criterion_type == "exclusion"
        and criterion.domain != "diagnosis"
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Cohort Engine v1 supports exclusions only "
                "for diagnosis criteria"
            ),
        )

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

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Cohort not found",
                )

            cursor.execute(
                """
                SELECT
                    criterion_whitelist_id,
                    value_type
                FROM cohort_criterion_whitelist
                WHERE domain = %s
                  AND field_name = %s
                  AND operator = %s
                """,
                (
                    criterion.domain,
                    criterion.field_name,
                    criterion.operator,
                ),
            )

            whitelist_entry = cursor.fetchone()

            if whitelist_entry is None:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported cohort criterion",
                )

            value_type = whitelist_entry["value_type"]

            if value_type != "text":
                postgres_type = {
                    "integer": "integer",
                    "numeric": "numeric",
                    "date": "date",
                }[value_type]

                cursor.execute(
                    """
                    SELECT pg_input_is_valid(%s, %s) AS is_valid
                    """,
                    (
                        criterion.value_text,
                        postgres_type,
                    ),
                )

                value_validation = cursor.fetchone()

                if not value_validation["is_valid"]:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Invalid value for criterion type "
                            f"{value_type}"
                        ),
                    )

            cursor.execute(
                """
                SELECT cohort_criterion_id
                FROM cohort_criteria
                WHERE cohort_definition_id = %s
                  AND criterion_order = %s
                """,
                (
                    cohort_id,
                    criterion.criterion_order,
                ),
            )

            if cursor.fetchone() is not None:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Criterion order already exists "
                        "for this cohort"
                    ),
                )

            cursor.execute(
                """
                INSERT INTO cohort_criteria (
                    cohort_definition_id,
                    criterion_order,
                    criterion_type,
                    domain,
                    field_name,
                    operator,
                    value_text
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING
                    cohort_criterion_id,
                    cohort_definition_id,
                    criterion_order,
                    criterion_type,
                    domain,
                    field_name,
                    operator,
                    value_text
                """,
                (
                    cohort_id,
                    criterion.criterion_order,
                    criterion.criterion_type,
                    criterion.domain,
                    criterion.field_name,
                    criterion.operator,
                    criterion.value_text,
                ),
            )

            created_criterion = cursor.fetchone()

    return created_criterion


@app.delete("/cohorts/{cohort_id}/criteria/{criterion_id}")
def delete_cohort_criterion(
    cohort_id: int,
    criterion_id: int,
):
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

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Cohort not found",
                )

            cursor.execute(
                """
                DELETE FROM cohort_criteria
                WHERE cohort_criterion_id = %s
                  AND cohort_definition_id = %s
                RETURNING cohort_criterion_id
                """,
                (
                    criterion_id,
                    cohort_id,
                ),
            )

            deleted_criterion = cursor.fetchone()

            if deleted_criterion is None:
                raise HTTPException(
                    status_code=404,
                    detail="Cohort criterion not found",
                )

    return {
        "status": "deleted",
        "cohort_definition_id": cohort_id,
        "cohort_criterion_id": criterion_id,
    }