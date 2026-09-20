# ============================================================
# Research Cohort Explorer
# Synthetic Patient Generator
# ============================================================

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from config import (
    AGE_GROUPS,
    PATIENT_COUNT,
    SEED,
    SEX_DISTRIBUTION,
    RACE_DISTRIBUTION,
    ETHNICITY_DISTRIBUTION,
    ZIP3_VALUES,
    STUDY_END_DATE,
)


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

random.seed(SEED)

REFERENCE_DATE = date.fromisoformat(STUDY_END_DATE)

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "patients.csv"

# ------------------------------------------------------------
# Age group ranges
# ------------------------------------------------------------

AGE_RANGES = {
    "0_17": (0, 17),
    "18_34": (18, 34),
    "35_49": (35, 49),
    "50_64": (50, 64),
    "65_79": (65, 79),
    "80_plus": (80, 95),
}


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def choose_age_group():
    groups = list(AGE_GROUPS.keys())
    weights = list(AGE_GROUPS.values())

    return random.choices(groups, weights=weights, k=1)[0]


def generate_date_of_birth(age_group):
    min_age, max_age = AGE_RANGES[age_group]

    age = random.randint(min_age, max_age)

    latest_birth_date = REFERENCE_DATE.replace(
        year=REFERENCE_DATE.year - age
    )

    earliest_birth_date = REFERENCE_DATE.replace(
        year=REFERENCE_DATE.year - age - 1
    ) + timedelta(days=1)

    days_between = (
        latest_birth_date - earliest_birth_date
    ).days

    return earliest_birth_date + timedelta(
        days=random.randint(0, days_between)
    )

def choose_sex():
    sexes = list(SEX_DISTRIBUTION.keys())
    weights = list(SEX_DISTRIBUTION.values())

    return random.choices(
        sexes,
        weights=weights,
        k=1,
    )[0]
def choose_race():
    races = list(RACE_DISTRIBUTION.keys())
    weights = list(RACE_DISTRIBUTION.values())

    return random.choices(
        races,
        weights=weights,
        k=1,
    )[0]


def choose_ethnicity():
    ethnicities = list(ETHNICITY_DISTRIBUTION.keys())
    weights = list(ETHNICITY_DISTRIBUTION.values())

    return random.choices(
        ethnicities,
        weights=weights,
        k=1,
    )[0]

def choose_zip3():
    return random.choice(ZIP3_VALUES)


# ------------------------------------------------------------
# Patient generation
# ------------------------------------------------------------

def generate_patient(patient_number):
    age_group = choose_age_group()

    date_of_birth = generate_date_of_birth(age_group)

    patient = {
        "research_id": f"P-{patient_number:06d}",
        "date_of_birth": date_of_birth.isoformat(),
        "sex": choose_sex(),
        "race": choose_race(),
        "ethnicity": choose_ethnicity(),
        "zip3": choose_zip3(),
    }

    return patient

# ------------------------------------------------------------
# CSV output
# ------------------------------------------------------------

def write_patients(patients):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "research_id",
        "date_of_birth",
        "sex",
        "race",
        "ethnicity",
        "zip3",
    ]

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(patients)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    print("Generating synthetic patients...")
    print(f"Patient count: {PATIENT_COUNT}")
    print(f"Random seed: {SEED}")

    patients = [
        generate_patient(i)
        for i in range(1, PATIENT_COUNT + 1)
    ]

    write_patients(patients)

    print()
    print("Generation complete.")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Patients generated: {len(patients)}")


if __name__ == "__main__":
    main()
