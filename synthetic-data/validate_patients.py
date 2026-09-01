# ============================================================
# Research Cohort Explorer
# Synthetic Patient Data Validation
# ============================================================

import csv
from collections import Counter
from datetime import date
from pathlib import Path

from config import PATIENT_COUNT, SEX_DISTRIBUTION, ZIP3_VALUES


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

TODAY = date(2026, 8, 27)

INPUT_FILE = (
    Path(__file__).parent
    / "output"
    / "patients.csv"
)


# ------------------------------------------------------------
# Load data
# ------------------------------------------------------------

def load_patients():
    with INPUT_FILE.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        return list(csv.DictReader(csv_file))


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

def validate_patients(patients):

    errors = []

    # --------------------------------------------------------
    # Patient count
    # --------------------------------------------------------

    if len(patients) != PATIENT_COUNT:
        errors.append(
            f"Expected {PATIENT_COUNT} patients, "
            f"found {len(patients)}."
        )

    # --------------------------------------------------------
    # Research ID uniqueness
    # --------------------------------------------------------

    research_ids = [
        patient["research_id"]
        for patient in patients
    ]

    duplicate_ids = [
        patient_id
        for patient_id, count
        in Counter(research_ids).items()
        if count > 1
    ]

    if duplicate_ids:
        errors.append(
            f"Duplicate research IDs found: {duplicate_ids}"
        )

    # --------------------------------------------------------
    # Sex validation
    # --------------------------------------------------------

    valid_sexes = set(SEX_DISTRIBUTION.keys())

    invalid_sexes = [
        patient["sex"]
        for patient in patients
        if patient["sex"] not in valid_sexes
    ]

    if invalid_sexes:
        errors.append(
            f"Invalid sex values found: {invalid_sexes}"
        )

    # --------------------------------------------------------
    # ZIP3 validation
    # --------------------------------------------------------

    valid_zip3 = set(ZIP3_VALUES)

    invalid_zip3 = [
        patient["zip3"]
        for patient in patients
        if patient["zip3"] not in valid_zip3
    ]

    if invalid_zip3:
        errors.append(
            f"Invalid ZIP3 values found: {invalid_zip3}"
        )

    # --------------------------------------------------------
    # Date of birth validation
    # --------------------------------------------------------

    for patient in patients:

        dob = date.fromisoformat(
            patient["date_of_birth"]
        )

        if dob > TODAY:
            errors.append(
                f"{patient['research_id']} has "
                f"a future date of birth: {dob}"
            )

    return errors


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

def print_summary(patients):

    sex_counts = Counter(
        patient["sex"]
        for patient in patients
    )

    zip_counts = Counter(
        patient["zip3"]
        for patient in patients
    )

    print()
    print("PATIENT DATA SUMMARY")
    print("=" * 40)

    print(f"Total patients: {len(patients)}")

    print()
    print("Sex distribution:")

    for sex, count in sorted(sex_counts.items()):
        percentage = count / len(patients) * 100

        print(
            f"  {sex}: "
            f"{count} "
            f"({percentage:.1f}%)"
        )

    print()
    print("ZIP3 distribution:")

    for zip3, count in sorted(zip_counts.items()):
        percentage = count / len(patients) * 100

        print(
            f"  {zip3}: "
            f"{count} "
            f"({percentage:.1f}%)"
        )


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():

    print("Validating synthetic patient data...")
    print(f"Input: {INPUT_FILE}")

    patients = load_patients()

    errors = validate_patients(patients)

    print_summary(patients)

    print()
    print("VALIDATION")
    print("=" * 40)

    if errors:

        print(
            f"FAILED — {len(errors)} "
            f"validation error(s)"
        )

        for error in errors:
            print(f"  - {error}")

        raise SystemExit(1)

    print("PASSED")
    print("All patient validation checks passed.")


if __name__ == "__main__":
    main()