import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from config import SEED

random.seed(SEED)

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"

PATIENTS_FILE = OUTPUT_DIR / "patients.csv"
ENCOUNTERS_FILE = OUTPUT_DIR / "encounters.csv"
OUTPUT_FILE = OUTPUT_DIR / "labs.csv"

STUDY_START_DATE = datetime(2015, 1, 1)
STUDY_END_DATE = datetime(2025, 12, 31, 23, 59, 59)


LAB_TESTS = {
    "BP_SYS": {
        "unit": "mmHg",
        "baseline_mean": 118,
        "baseline_sd": 12,
        "min": 85,
        "max": 210,
    },
    "GLUCOSE": {
        "unit": "mg/dL",
        "baseline_mean": 92,
        "baseline_sd": 12,
        "min": 55,
        "max": 350,
    },
    "HBA1C": {
        "unit": "%",
        "baseline_mean": 5.4,
        "baseline_sd": 0.35,
        "min": 3.5,
        "max": 15.0,
    },
    "CREAT": {
        "unit": "mg/dL",
        "baseline_mean": 0.9,
        "baseline_sd": 0.18,
        "min": 0.3,
        "max": 8.0,
    },
    "LDL": {
        "unit": "mg/dL",
        "baseline_mean": 105,
        "baseline_sd": 22,
        "min": 30,
        "max": 300,
    },
    "HDL": {
        "unit": "mg/dL",
        "baseline_mean": 55,
        "baseline_sd": 10,
        "min": 15,
        "max": 120,
    },
}


# Disease codes used by the diagnosis generator.
DISEASE_CODES = {
    "diabetes": "E11.9",
    "hypertension": "I10",
    "hyperlipidemia": "E78.5",
    "ckd": "N18.3",
    "ascvd": "I25.10",
}


def load_patients():
    patients = []

    with PATIENTS_FILE.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            patients.append(row)

    return patients


def load_encounters():
    encounters = []

    with ENCOUNTERS_FILE.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            row["encounter_id"] = int(row["encounter_id"])
            row["encounter_date"] = datetime.fromisoformat(
                row["encounter_date"]
            )

            encounters.append(row)

    return encounters


def choose_lab_tests():
    """
    Select 1-4 tests for a laboratory event.

    This creates a mixture of routine and clinically targeted testing.
    """
    test_count = random.choices(
        [1, 2, 3, 4],
        weights=[0.30, 0.35, 0.25, 0.10],
        k=1,
    )[0]

    return random.sample(
        list(LAB_TESTS.keys()),
        k=test_count,
    )


def choose_measurement_date(patient_encounters):
    """
    Prefer encounter-linked measurements.

    Approximately 65% of lab events will be associated with an
    existing encounter. Otherwise, generate an independent measurement
    date inside the study period.
    """

    if patient_encounters and random.random() < 0.65:
        encounter = random.choice(patient_encounters)

        return (
            encounter["encounter_id"],
            encounter["encounter_date"],
        )

    random_seconds = random.randint(
        0,
        int(
            (
                STUDY_END_DATE
                - STUDY_START_DATE
            ).total_seconds()
        ),
    )

    result_date = STUDY_START_DATE + timedelta(
        seconds=random_seconds
    )

    return None, result_date


def get_patient_diseases(patient_id, diagnosis_by_patient):
    """
    Return the synthetic disease profile for a patient.
    """

    return diagnosis_by_patient.get(patient_id, set())


def generate_value(test_code, diseases):
    """
    Generate a clinically correlated synthetic laboratory result.
    """

    definition = LAB_TESTS[test_code]

    mean = definition["baseline_mean"]
    sd = definition["baseline_sd"]

    # ------------------------------------------------------------
    # Disease-specific shifts
    # ------------------------------------------------------------

    if test_code == "BP_SYS":
        if "I10" in diseases:
            mean += 28

        if "I25.10" in diseases:
            mean += 8

    elif test_code == "GLUCOSE":
        if "E11.9" in diseases:
            mean += 45

        if "N18.3" in diseases:
            mean += 8

    elif test_code == "HBA1C":
        if "E11.9" in diseases:
            mean += 2.2

        if "N18.3" in diseases:
            mean += 0.3

    elif test_code == "CREAT":
        if "N18.3" in diseases:
            mean += 1.4

        if "E11.9" in diseases:
            mean += 0.15

        if "I10" in diseases:
            mean += 0.10

    elif test_code == "LDL":
        if "E78.5" in diseases:
            mean += 45

        if "I25.10" in diseases:
            mean += 20

    elif test_code == "HDL":
        if "E78.5" in diseases:
            mean -= 8

        if "I25.10" in diseases:
            mean -= 5

    value = random.gauss(mean, sd)

    value = max(
        definition["min"],
        min(definition["max"], value),
    )

    # Appropriate decimal precision by test.
    if test_code in {"BP_SYS", "GLUCOSE", "LDL", "HDL"}:
        return round(value, 1)

    if test_code == "HBA1C":
        return round(value, 2)

    if test_code == "CREAT":
        return round(value, 2)

    return round(value, 2)


def generate_lab_results(
    patients,
    encounters,
    diagnosis_by_patient,
):
    """
    Generate synthetic laboratory observations.

    Each patient receives multiple laboratory events based on
    encounter activity, with additional independent measurements.
    """

    encounters_by_patient = {}

    for encounter in encounters:
        encounters_by_patient.setdefault(
            encounter["research_id"],
            [],
        ).append(encounter)

    results = []

    lab_result_id = 1

    for patient in patients:
        research_id = patient["research_id"]

        patient_encounters = encounters_by_patient.get(
            research_id,
            [],
        )

        diseases = get_patient_diseases(
            research_id,
            diagnosis_by_patient,
        )

        # More encounters generally produce more opportunities
        # for laboratory testing.
        encounter_count = len(patient_encounters)

        base_events = max(
            3,
            min(
                12,
                int(encounter_count * 0.35)
            ),
        )

        # Add a small amount of independent testing.
        additional_events = random.randint(1, 4)

        total_events = base_events + additional_events

        for _ in range(total_events):

            encounter_id, result_date = choose_measurement_date(
                patient_encounters
            )

            selected_tests = choose_lab_tests()

            for test_code in selected_tests:

                value = generate_value(
                    test_code,
                    diseases,
                )

                results.append(
                    {
                        "lab_result_id": lab_result_id,
                        "research_id": research_id,
                        "encounter_id": encounter_id,
                        "test_code": test_code,
                        "result_numeric": value,
                        "result_text": "",
                        "unit": LAB_TESTS[test_code]["unit"],
                        "result_date": result_date.isoformat(
                            sep=" "
                        ),
                    }
                )

                lab_result_id += 1

    return results


def load_diagnoses():
    """
    Load diagnoses from diagnoses.csv and build a patient-level
    disease profile.
    """

    diagnoses_file = OUTPUT_DIR / "diagnoses.csv"

    diagnosis_by_patient = {}

    with diagnoses_file.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:
            research_id = row["research_id"]
            diagnosis_code = row["diagnosis_code"]

            diagnosis_by_patient.setdefault(
                research_id,
                set(),
            ).add(diagnosis_code)

    return diagnosis_by_patient


def validate_results(results, patients, encounters):
    """
    Perform Python-level validation before the CSV is loaded
    into PostgreSQL.
    """

    patient_ids = {
        patient["research_id"]
        for patient in patients
    }

    encounter_map = {
        encounter["encounter_id"]: encounter
        for encounter in encounters
    }

    print()
    print("Validation")

    # ------------------------------------------------------------
    # Basic row validation
    # ------------------------------------------------------------

    print(f"Rows: {len(results)}")

    duplicate_ids = (
        len(results)
        - len(
            {
                row["lab_result_id"]
                for row in results
            }
        )
    )

    print(f"Duplicate lab_result_id: {duplicate_ids}")

    missing_patient_ids = sum(
        1
        for row in results
        if row["research_id"] not in patient_ids
    )

    print(
        f"Missing research_id: {missing_patient_ids}"
    )

    missing_test_codes = sum(
        1
        for row in results
        if row["test_code"] not in LAB_TESTS
    )

    print(
        f"Invalid test_code: {missing_test_codes}"
    )

    # ------------------------------------------------------------
    # Numeric validation
    # ------------------------------------------------------------

    invalid_values = 0

    for row in results:
        definition = LAB_TESTS[row["test_code"]]
        value = row["result_numeric"]

        if not (
            definition["min"]
            <= value
            <= definition["max"]
        ):
            invalid_values += 1

    print(
        f"Values outside configured range: {invalid_values}"
    )

    # ------------------------------------------------------------
    # Date validation
    # ------------------------------------------------------------

    dates_before_study = 0
    dates_after_study = 0

    for row in results:
        result_date = datetime.fromisoformat(
            row["result_date"]
        )

        if result_date < STUDY_START_DATE:
            dates_before_study += 1

        if result_date > STUDY_END_DATE:
            dates_after_study += 1

    print(
        f"Result date before study start: {dates_before_study}"
    )

    print(
        f"Result date after study end: {dates_after_study}"
    )

    # ------------------------------------------------------------
    # Encounter linkage validation
    # ------------------------------------------------------------

    invalid_encounter_links = 0
    encounter_date_mismatches = 0

    for row in results:

        encounter_id = row["encounter_id"]

        if encounter_id is None:
            continue

        encounter = encounter_map.get(
            encounter_id
        )

        if encounter is None:
            invalid_encounter_links += 1
            continue

        result_date = datetime.fromisoformat(
            row["result_date"]
        )

        if result_date != encounter["encounter_date"]:
            encounter_date_mismatches += 1

    print(
        f"Invalid encounter links: {invalid_encounter_links}"
    )

    print(
        f"Encounter date mismatches: {encounter_date_mismatches}"
    )

    # ------------------------------------------------------------
    # Patient coverage
    # ------------------------------------------------------------

    patients_with_labs = len(
        {
            row["research_id"]
            for row in results
        }
    )

    print(
        f"Patients with laboratory results: "
        f"{patients_with_labs}"
    )

    # ------------------------------------------------------------
    # Final validation assertion
    # ------------------------------------------------------------

    assert duplicate_ids == 0
    assert missing_patient_ids == 0
    assert missing_test_codes == 0
    assert invalid_values == 0
    assert dates_before_study == 0
    assert dates_after_study == 0
    assert invalid_encounter_links == 0
    assert encounter_date_mismatches == 0

    print("Validation passed.")


def write_results(results):
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "lab_result_id",
        "research_id",
        "encounter_id",
        "test_code",
        "result_numeric",
        "result_text",
        "unit",
        "result_date",
    ]

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)


def main():

    print("Generating synthetic laboratory data...")
    print(f"Random seed: {SEED}")

    patients = load_patients()
    encounters = load_encounters()
    diagnosis_by_patient = load_diagnoses()

    print(
        f"Patients loaded: {len(patients)}"
    )

    print(
        f"Encounters loaded: {len(encounters)}"
    )

    print(
        f"Patients with diagnoses: "
        f"{len(diagnosis_by_patient)}"
    )

    results = generate_lab_results(
        patients,
        encounters,
        diagnosis_by_patient,
    )

    validate_results(
        results,
        patients,
        encounters,
    )

    write_results(results)

    print()
    print("Generation complete.")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Lab results generated: {len(results)}")

    print()
    print("Results by test:")

    test_counts = {}

    for row in results:
        test_code = row["test_code"]

        test_counts[test_code] = (
            test_counts.get(test_code, 0) + 1
        )

    for test_code in sorted(test_counts):
        print(
            f"{test_code}: "
            f"{test_counts[test_code]}"
        )


if __name__ == "__main__":
    main()