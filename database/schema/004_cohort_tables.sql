-- ============================================================
-- Cohort Infrastructure
-- ============================================================


-- ============================================================
-- Cohort Definitions
-- ============================================================

CREATE TABLE cohort_definitions (
    cohort_definition_id BIGSERIAL PRIMARY KEY,

    cohort_name VARCHAR(150) NOT NULL,

    description TEXT,

    study_start_date DATE NOT NULL,

    study_end_date DATE NOT NULL,

    version INTEGER NOT NULL DEFAULT 1,

    status VARCHAR(30) NOT NULL DEFAULT 'draft',

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT cohort_study_dates_valid
        CHECK (
            study_end_date >= study_start_date
        ),

    CONSTRAINT cohort_version_valid
        CHECK (
            version >= 1
        ),

    CONSTRAINT cohort_status_valid
        CHECK (
            status IN ('draft', 'active', 'archived')
        )
);

-- ============================================================
-- Cohort Membership
-- ============================================================

CREATE TABLE cohort_membership (
    cohort_membership_id BIGSERIAL PRIMARY KEY,

    cohort_definition_id BIGINT NOT NULL
        REFERENCES cohort_definitions(cohort_definition_id),

    patient_id BIGINT NOT NULL
        REFERENCES patients(patient_id),

    included_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT cohort_membership_unique
        UNIQUE (
            cohort_definition_id,
            patient_id
        )
);
