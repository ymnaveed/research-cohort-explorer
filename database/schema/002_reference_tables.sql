-- ============================================================
-- Reference / Master Data
-- ============================================================

-- Diagnosis terminology
CREATE TABLE diagnosis_codes (
    diagnosis_code VARCHAR(20) PRIMARY KEY,
    description TEXT NOT NULL,
    category VARCHAR(100)
);


-- Laboratory test definitions
CREATE TABLE lab_tests (
    test_code VARCHAR(30) PRIMARY KEY,
    test_name VARCHAR(150) NOT NULL,
    default_unit VARCHAR(30)
);


-- Medication definitions
CREATE TABLE medication_codes (
    medication_code VARCHAR(30) PRIMARY KEY,
    medication_name VARCHAR(150) NOT NULL,
    medication_class VARCHAR(100)
);


-- Procedure definitions
CREATE TABLE procedure_codes (
    procedure_code VARCHAR(30) PRIMARY KEY,
    procedure_name VARCHAR(150) NOT NULL,
    category VARCHAR(100)
);


-- Encounter type definitions
CREATE TABLE encounter_types (
    encounter_type_code VARCHAR(30) PRIMARY KEY,
    description VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL
);


-- Healthcare facilities
CREATE TABLE facilities (
    facility_id BIGSERIAL PRIMARY KEY,
    facility_code VARCHAR(30) UNIQUE NOT NULL,
    facility_name VARCHAR(150) NOT NULL,
    facility_type VARCHAR(50) NOT NULL,
    city VARCHAR(100),
    state CHAR(2)
);


-- Healthcare providers
CREATE TABLE providers (
    provider_id BIGSERIAL PRIMARY KEY,
    provider_code VARCHAR(30) UNIQUE NOT NULL,
    provider_type VARCHAR(50) NOT NULL,
    specialty VARCHAR(100)
);


-- Clinical note type definitions
CREATE TABLE note_types (
    note_type_code VARCHAR(30) PRIMARY KEY,
    description VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL
);