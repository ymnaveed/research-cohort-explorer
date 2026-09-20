-- ============================================================
-- Research Cohort Explorer
-- Cohort Infrastructure: Execution Audit Log
-- ============================================================

CREATE TABLE cohort_execution_log (
    execution_id BIGSERIAL PRIMARY KEY,

    cohort_definition_id BIGINT NOT NULL
        REFERENCES cohort_definitions(cohort_definition_id),

    cohort_version INTEGER NOT NULL,

    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMP,

    status VARCHAR(20) NOT NULL DEFAULT 'running',

    member_count BIGINT,

    error_message TEXT,

    CONSTRAINT cohort_execution_version_valid
        CHECK (
            cohort_version >= 1
        ),

    CONSTRAINT cohort_execution_status_valid
        CHECK (
            status IN ('running', 'succeeded', 'failed')
        ),

    CONSTRAINT cohort_execution_member_count_valid
        CHECK (
            member_count IS NULL
            OR member_count >= 0
        ),

    CONSTRAINT cohort_execution_completed_at_valid
        CHECK (
            completed_at IS NULL
            OR completed_at >= started_at
        )
);
