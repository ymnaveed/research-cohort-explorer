-- ============================================================
-- Core Clinical Tables
-- ============================================================


-- ============================================================
-- Patients
-- ============================================================

CREATE TABLE patients (
    patient_id BIGSERIAL PRIMARY KEY,

    research_id VARCHAR(32) UNIQUE NOT NULL,

    date_of_birth DATE NOT NULL,

    sex CHAR(1),

    race VARCHAR(50),

    ethnicity VARCHAR(50),

    zip3 VARCHAR(3),

    death_date DATE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT patient_dates_valid
        CHECK (
            death_date IS NULL
            OR death_date >= date_of_birth
        )
);


-- ============================================================
-- Encounters
-- ============================================================

CREATE TABLE encounters (
    encounter_id BIGSERIAL PRIMARY KEY,

    patient_id BIGINT NOT NULL
        REFERENCES patients(patient_id),

    encounter_date TIMESTAMP NOT NULL,

    encounter_type_code VARCHAR(30) NOT NULL
        REFERENCES encounter_types(encounter_type_code),

    facility_id BIGINT
        REFERENCES facilities(facility_id),

    provider_id BIGINT
        REFERENCES providers(provider_id),

    discharge_date TIMESTAMP,

    CONSTRAINT encounter_dates_valid
        CHECK (
            discharge_date IS NULL
            OR discharge_date >= encounter_date
        )
);


-- ============================================================
-- Diagnoses
-- ============================================================

CREATE TABLE diagnoses (
    diagnosis_id BIGSERIAL PRIMARY KEY,

    patient_id BIGINT NOT NULL
        REFERENCES patients(patient_id),

    encounter_id BIGINT
        REFERENCES encounters(encounter_id),

    diagnosis_code VARCHAR(20) NOT NULL
        REFERENCES diagnosis_codes(diagnosis_code),

    onset_date DATE,

    recorded_date DATE NOT NULL,

    diagnosis_type VARCHAR(30)
);


-- ============================================================
-- Laboratory Results
-- ============================================================

CREATE TABLE lab_results (
    lab_result_id BIGSERIAL PRIMARY KEY,

    patient_id BIGINT NOT NULL
        REFERENCES patients(patient_id),

    encounter_id BIGINT
        REFERENCES encounters(encounter_id),

    test_code VARCHAR(30) NOT NULL
        REFERENCES lab_tests(test_code),

    result_numeric NUMERIC,

    result_text TEXT,

    unit VARCHAR(30),

    result_date TIMESTAMP NOT NULL,

    CONSTRAINT lab_result_has_value
        CHECK (
            result_numeric IS NOT NULL
            OR result_text IS NOT NULL
        )
);


-- ============================================================
-- Medication Orders
-- ============================================================

CREATE TABLE medication_orders (
    medication_order_id BIGSERIAL PRIMARY KEY,

    patient_id BIGINT NOT NULL
        REFERENCES patients(patient_id),

    encounter_id BIGINT
        REFERENCES encounters(encounter_id),

    medication_code VARCHAR(30) NOT NULL
        REFERENCES medication_codes(medication_code),

    order_date DATE,

    start_date DATE NOT NULL,

    end_date DATE,

    dose VARCHAR(50),

    route VARCHAR(30),

    status VARCHAR(30) NOT NULL,

    CONSTRAINT medication_dates_valid
        CHECK (
            end_date IS NULL
            OR end_date >= start_date
        )
);


-- ============================================================
-- Procedures
-- ============================================================

CREATE TABLE procedures (
    procedure_id BIGSERIAL PRIMARY KEY,

    patient_id BIGINT NOT NULL
        REFERENCES patients(patient_id),

    encounter_id BIGINT
        REFERENCES encounters(encounter_id),

    procedure_code VARCHAR(30) NOT NULL
        REFERENCES procedure_codes(procedure_code),

    procedure_date TIMESTAMP NOT NULL
);


-- ============================================================
-- Clinical Notes
-- ============================================================

CREATE TABLE clinical_notes (
    note_id BIGSERIAL PRIMARY KEY,

    patient_id BIGINT NOT NULL
        REFERENCES patients(patient_id),

    encounter_id BIGINT
        REFERENCES encounters(encounter_id),

    note_date TIMESTAMP NOT NULL,

    note_type_code VARCHAR(30) NOT NULL
        REFERENCES note_types(note_type_code),

    note_text TEXT NOT NULL
);