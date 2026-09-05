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
DIAGNOSES_FILE = OUTPUT_DIR / "diagnoses.csv"
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

    with PATIENTS_FILE.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:
            row["date_of_birth"] = datetime.strptime(
                row["date_of_birth"],
                "%Y-%m-%d",
            ).replace(
                hour=0,
                minute=0,
                second=0,
            )

            patients.append(row)

    return patients


def load_encounters():
    encounters = []

    with ENCOUNTERS_FILE.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:
            row["encounter_id"] = int(
                row["encounter_id"]
            )

            row["encounter_date"] = datetime.fromisoformat(
                row["encounter_date"]
            )

            encounters.append(row)

    return encounters


def load_diagnoses():
    diagnoses = []

    with DIAGNOSES_FILE.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:
            diagnoses.append(row)

    return diagnoses


def build_diagnosis_index(diagnoses):
    diagnosis_by_patient = {}

    for row in diagnoses:
        research_id = row["research_id"]

        diagnosis_by_patient.setdefault(
            research_id,
            set(),
        ).add(
            row["diagnosis_code"]
        )

    return diagnosis_by_patient


def get_patient_diseases(
    research_id,
    diagnosis_by_patient,
):
    codes = diagnosis_by_patient.get(
        research_id,
        set(),
    )

    diseases = set()

    if DISEASE_CODES["diabetes"] in codes:
        diseases.add("diabetes")

    if DISEASE_CODES["hypertension"] in codes:
        diseases.add("hypertension")

    if DISEASE_CODES["hyperlipidemia"] in codes:
        diseases.add("hyperlipidemia")

    if DISEASE_CODES["ckd"] in codes:
        diseases.add("ckd")

    if DISEASE_CODES["ascvd"] in codes:
        diseases.add("ascvd")

    return diseases


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
        test_count,
    )


def choose_measurement_date(
    patient_encounters,
    date_of_birth,
):
    """
    Prefer encounter-linked measurements.

    Approximately 65% of lab events will be associated with an
    existing encounter. Otherwise, generate an independent measurement
    date between the patient's date of birth and the study end date.
    """

    if patient_encounters and random.random() < 0.65:
        encounter = random.choice(
            patient_encounters
        )

        return (
            encounter["encounter_id"],
            encounter["encounter_date"],
        )

    earliest_valid_date = max(
        STUDY_START_DATE,
        date_of_birth,
    )

    random_seconds = random.randint(
        0,
        int(
            (
                STUDY_END_DATE
                - earliest_valid_date
            ).total_seconds()
        ),
    )

    result_date = (
        earliest_valid_date
        + timedelta(seconds=random_seconds)
    )

    return None, result_date


def generate_value(
    test_code,
    diseases,
):
    """
    Generate a clinically plausible synthetic laboratory value.

    Disease conditions shift the expected value while preserving
    random variation.
    """

    config = LAB_TESTS[test_code]

    mean = config["baseline_mean"]
    sd = config["baseline_sd"]

    if test_code == "BP_SYS":
        if "hypertension" in diseases:
            mean += 25

        if "ckd" in diseases:
            mean += 8

    elif test_code == "GLUCOSE":
        if "diabetes" in diseases:
            mean += 55

        elif "ckd" in diseases:
            mean += 8

    elif test_code == "HBA1C":
        if "diabetes" in diseases:
            mean += 2.5

    elif test_code == "CREAT":
        if "ckd" in diseases:
            mean += 1.5

    elif test_code == "LDL":
        if "hyperlipidemia" in diseases:
            mean += 55

        if "ascvd" in diseases:
            mean += 20

    elif test_code == "HDL":
        if "diabetes" in diseases:
            mean -= 5

        if "ascvd" in diseases:
            mean -= 5

    value = random.gauss(
        mean,
        sd,
    )

    value = max(
        config["min"],
        min(
            config["max"],
            value,
        ),
    )

    return round(
        value,
        2,
    )


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
        ).append(
            encounter
        )

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

        encounter_count = len(
            patient_encounters
        )

        base_events = max(
            3,
            min(
                12,
                int(
                    encounter_count * 0.35
                ),
            ),
        )

        additional_events = random.randint(
            1,
            4,
        )

        total_events = (
            base_events
            + additional_events
        )

        for _ in range(total_events):

            encounter_id, result_date = choose_measurement_date(
                patient_encounters,
                patient["date_of_birth"],
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


def validate_results(
    results,
    patients,
    encounters,
):
    print()
    print("Validation")

    patient_ids = {
        patient["research_id"]
        for patient in patients
    }

    patient_map = {
        patient["research_id"]: patient
        for patient in patients
    }

    encounter_map = {
        encounter["encounter_id"]: encounter
        for encounter in encounters
    }

    duplicate_ids = (
        len(results)
        - len(
            {
                row["lab_result_id"]
                for row in results
            }
        )
    )

    missing_patient_ids = sum(
        1
        for row in results
        if row["research_id"]
        not in patient_ids
    )

    missing_test_codes = sum(
        1
        for row in results
        if row["test_code"]
        not in LAB_TESTS
    )

    invalid_values = 0

    for row in results:

        if row["test_code"] not in LAB_TESTS:
            continue

        value = row["result_numeric"]

        config = LAB_TESTS[
            row["test_code"]
        ]

        if value is None:
            invalid_values += 1
            continue

        if (
            value < config["min"]
            or value > config["max"]
        ):
            invalid_values += 1

    dates_before_study = 0
    dates_after_study = 0
    dates_before_birth = 0

    invalid_encounter_links = 0
    encounter_date_mismatches = 0

    for row in results:

        result_date = datetime.fromisoformat(
            row["result_date"]
        )

        if result_date < STUDY_START_DATE:
            dates_before_study += 1

        if result_date > STUDY_END_DATE:
            dates_after_study += 1

        patient = patient_map.get(
            row["research_id"]
        )

        if (
            patient is not None
            and result_date < patient["date_of_birth"]
        ):
            dates_before_birth += 1

        encounter_id = row["encounter_id"]

        if encounter_id is not None:

            encounter = encounter_map.get(
                encounter_id
            )

            if encounter is None:
                invalid_encounter_links += 1

            else:
                if (
                    result_date
                    != encounter["encounter_date"]
                ):
                    encounter_date_mismatches += 1

    patient_coverage = len(
        {
            row["research_id"]
            for row in results
        }
    )

    print(
        f"Rows: {len(results)}"
    )

    print(
        f"Duplicate lab_result_id: {duplicate_ids}"
    )

    print(
        f"Missing/invalid research_id: "
        f"{missing_patient_ids}"
    )

    print(
        f"Invalid test codes: "
        f"{missing_test_codes}"
    )

    print(
        f"Values outside allowed range: "
        f"{invalid_values}"
    )

    print(
        f"Dates before study start: "
        f"{dates_before_study}"
    )

    print(
        f"Dates after study end: "
        f"{dates_after_study}"
    )

    print(
        f"Result date before patient birth: "
        f"{dates_before_birth}"
    )

    print(
        f"Invalid encounter links: "
        f"{invalid_encounter_links}"
    )

    print(
        f"Encounter date mismatches: "
        f"{encounter_date_mismatches}"
    )

    print(
        f"Patients represented: "
        f"{patient_coverage}"
    )

    assert duplicate_ids == 0
    assert missing_patient_ids == 0
    assert missing_test_codes == 0
    assert invalid_values == 0
    assert dates_before_study == 0
    assert dates_after_study == 0
    assert dates_before_birth == 0
    assert invalid_encounter_links == 0
    assert encounter_date_mismatches == 0

    print()
    print("Validation passed.")


def write_results(results):
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
    print(
        "Generating synthetic laboratory results..."
    )

    print(
        f"Random seed: {SEED}"
    )

    patients = load_patients()

    print(
        f"Patients loaded: {len(patients)}"
    )

    encounters = load_encounters()

    print(
        f"Encounters loaded: {len(encounters)}"
    )

    diagnoses = load_diagnoses()

    print(
        f"Diagnoses loaded: {len(diagnoses)}"
    )

    diagnosis_by_patient = build_diagnosis_index(
        diagnoses
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

    print()
    print("Laboratory distribution")

    distribution = {}

    for row in results:
        test_code = row["test_code"]

        distribution[test_code] = (
            distribution.get(
                test_code,
                0,
            )
            + 1
        )

    for test_code in sorted(distribution):
        print(
            f"{test_code}: "
            f"{distribution[test_code]}"
        )

    linked_results = sum(
        1
        for row in results
        if row["encounter_id"] is not None
    )

    unlinked_results = (
        len(results)
        - linked_results
    )

    print()
    print(
        f"Linked laboratory results: "
        f"{linked_results}"
    )

    print(
        f"Unlinked laboratory results: "
        f"{unlinked_results}"
    )

    write_results(results)

    print()
    print(
        "Generation complete."
    )

    print(
        f"Output file: {OUTPUT_FILE}"
    )

    print(
        f"Laboratory results generated: "
        f"{len(results)}"
    )


if __name__ == "__main__":
    main()