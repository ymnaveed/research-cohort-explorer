-- ============================================================
-- Research Cohort Explorer
-- Criterion Whitelist
-- ============================================================

CREATE TABLE cohort_criterion_whitelist (
    criterion_whitelist_id BIGSERIAL PRIMARY KEY,

    domain VARCHAR(30) NOT NULL,

    field_name VARCHAR(50) NOT NULL,

    operator VARCHAR(20) NOT NULL,

    source_view VARCHAR(100) NOT NULL,

    source_column VARCHAR(100) NOT NULL,

    value_type VARCHAR(20) NOT NULL,

    CONSTRAINT cohort_criterion_whitelist_unique
        UNIQUE (
            domain,
            field_name,
            operator
        ),

    CONSTRAINT cohort_criterion_value_type_valid
        CHECK (
            value_type IN ('text', 'integer', 'numeric', 'date')
        )
);

INSERT INTO cohort_criterion_whitelist
(domain, field_name, operator, source_view, source_column, value_type)
VALUES
('diagnosis', 'diagnosis_code', '=',  'vw_diagnoses',            'diagnosis_code',   'text'),
('diagnosis', 'recorded_date',  '>=', 'vw_diagnoses',            'recorded_date',    'date'),
('diagnosis', 'recorded_date',  '<=', 'vw_diagnoses',            'recorded_date',    'date'),
('demographics', 'age_at_study_end', '>=', 'vw_patient_demographics', 'age_at_study_end', 'integer');
