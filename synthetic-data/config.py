# ============================================================
# Research Cohort Explorer
# Synthetic Data Generator Configuration
# ============================================================

SEED = 20260827

# Start small during development.
PATIENT_COUNT = 1_000


# ------------------------------------------------------------
# Patient demographics
# ------------------------------------------------------------

AGE_GROUPS = {
    "0_17": 0.15,
    "18_34": 0.20,
    "35_49": 0.20,
    "50_64": 0.22,
    "65_79": 0.17,
    "80_plus": 0.06,
}

SEX_DISTRIBUTION = {
    "F": 0.51,
    "M": 0.48,
    "O": 0.01,
}


# ------------------------------------------------------------
# Geographic distribution
# Synthetic ZIP3 values only.
# ------------------------------------------------------------

ZIP3_VALUES = [
    "544",
    "545",
    "546",
    "547",
    "548",
    "549",
]


# ------------------------------------------------------------
# Disease base probabilities
#
# These are synthetic modeling assumptions and do not
# represent any real healthcare population.
# ------------------------------------------------------------

BASE_DISEASE_PROBABILITIES = {
    "diabetes": 0.08,
    "hypertension": 0.20,
    "hyperlipidemia": 0.18,
    "ckd": 0.03,
    "asthma": 0.08,
    "ascvd": 0.02,
}


# ------------------------------------------------------------
# Disease age modifiers
# ------------------------------------------------------------

DISEASE_AGE_MODIFIERS = {
    "diabetes": {
        "0_17": -0.08,
        "18_34": -0.04,
        "35_49": 0.04,
        "50_64": 0.10,
        "65_79": 0.14,
        "80_plus": 0.12,
    },

    "hypertension": {
        "0_17": -0.18,
        "18_34": -0.10,
        "35_49": 0.02,
        "50_64": 0.12,
        "65_79": 0.18,
        "80_plus": 0.20,
    },

    "hyperlipidemia": {
        "0_17": -0.12,
        "18_34": -0.08,
        "35_49": 0.02,
        "50_64": 0.10,
        "65_79": 0.14,
        "80_plus": 0.12,
    },

    "ckd": {
        "0_17": -0.03,
        "18_34": -0.02,
        "35_49": 0.01,
        "50_64": 0.04,
        "65_79": 0.08,
        "80_plus": 0.10,
    },

    "asthma": {
        "0_17": 0.04,
        "18_34": 0.03,
        "35_49": 0.01,
        "50_64": 0.00,
        "65_79": -0.01,
        "80_plus": -0.01,
    },

    "ascvd": {
        "0_17": -0.02,
        "18_34": -0.02,
        "35_49": 0.01,
        "50_64": 0.04,
        "65_79": 0.10,
        "80_plus": 0.14,
    },
}


# ------------------------------------------------------------
# Disease-to-disease risk modifiers
# ------------------------------------------------------------

DISEASE_RISK_MODIFIERS = {
    "ckd": {
        "diabetes": 0.06,
        "hypertension": 0.05,
    },

    "ascvd": {
        "diabetes": 0.04,
        "hypertension": 0.05,
        "hyperlipidemia": 0.05,
    },
}


# ------------------------------------------------------------
# Synthetic study period
# ------------------------------------------------------------

STUDY_START_DATE = "2015-01-01"
STUDY_END_DATE = "2025-12-31"

# Patient ages are calculated as of the study end date.
# This ensures generated patients can participate in
# the synthetic study period.
# ------------------------------------------------------------
# Encounter generation
# ------------------------------------------------------------

# Average number of encounters per patient.
# The actual number will vary by patient.
ENCOUNTERS_PER_PATIENT_MIN = 3
ENCOUNTERS_PER_PATIENT_MAX = 20


# Relative frequency of encounter types.
#
# These are synthetic modeling assumptions and do not
# represent any real healthcare population.
ENCOUNTER_TYPE_DISTRIBUTION = {
    "OFFICE": 0.55,
    "ED": 0.10,
    "INPATIENT": 0.08,
    "TELEHEALTH": 0.15,
    "URGENT_CARE": 0.12,
}


# Average duration of encounters in hours.
# These values are only used to generate synthetic
# discharge timestamps.
ENCOUNTER_DURATION_HOURS = {
    "OFFICE": (0.25, 1.5),
    "ED": (1.0, 12.0),
    "INPATIENT": (12.0, 120.0),
    "TELEHEALTH": (0.25, 1.0),
    "URGENT_CARE": (0.5, 3.0),
}


# Probability that an encounter has an assigned facility.
FACILITY_ASSIGNMENT_PROBABILITY = 0.95


# Probability that an encounter has an assigned provider.
PROVIDER_ASSIGNMENT_PROBABILITY = 0.98