import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";
const MEMBER_PAGE_SIZE = 50;
const PATIENT_PAGE_SIZE = 50;

const CRITERION_OPTIONS = {
  demographics: {
    age_at_study_end: [">="],
  },
  diagnosis: {
    diagnosis_code: ["="],
    recorded_date: [">=", "<="],
  },
  encounter: {
    encounter_type_code: ["="],
  },
  laboratory: {
    result_numeric: [">=", "<="],
    test_code: ["="],
  },
  medication: {
    medication_code: ["="],
  },
  procedure: {
    procedure_code: ["="],
  },
};

const PATIENT_TABS = [
  { key: "encounters", label: "Encounters" },
  { key: "diagnoses", label: "Diagnoses" },
  { key: "labs", label: "Labs" },
  { key: "medications", label: "Medications" },
  { key: "procedures", label: "Procedures" },
  { key: "notes", label: "Notes" },
];

function displayValue(value) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  return value;
}

function formatDateTime(value) {
  if (!value) {
    return "—";
  }

  return value.replace("T", " ");
}

function App() {
  const [activeView, setActiveView] = useState("cohorts");

  const [cohorts, setCohorts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [cohortName, setCohortName] = useState("");
  const [cohortDescription, setCohortDescription] = useState("");
  const [cohortStartDate, setCohortStartDate] = useState("");
  const [cohortEndDate, setCohortEndDate] = useState("");
  const [cohortSaving, setCohortSaving] = useState(false);
  const [cohortSaveError, setCohortSaveError] = useState("");
  const [cohortSaveSuccess, setCohortSaveSuccess] = useState("");

  const [selectedCohort, setSelectedCohort] = useState(null);
  const [criteria, setCriteria] = useState([]);
  const [criteriaLoading, setCriteriaLoading] = useState(false);
  const [criteriaError, setCriteriaError] = useState("");

  const [executionLoading, setExecutionLoading] = useState(false);
  const [executionError, setExecutionError] = useState("");
  const [executionResult, setExecutionResult] = useState(null);

  const [criterionType, setCriterionType] = useState("inclusion");
  const [criterionDomain, setCriterionDomain] = useState("diagnosis");
  const [criterionField, setCriterionField] = useState("diagnosis_code");
  const [criterionOperator, setCriterionOperator] = useState("=");
  const [criterionValue, setCriterionValue] = useState("");
  const [criterionSaving, setCriterionSaving] = useState(false);
  const [criterionSaveError, setCriterionSaveError] = useState("");

  const [criterionDeletingId, setCriterionDeletingId] = useState(null);
  const [criterionDeleteError, setCriterionDeleteError] = useState("");

  const [members, setMembers] = useState([]);
  const [memberCount, setMemberCount] = useState(0);
  const [memberOffset, setMemberOffset] = useState(0);
  const [membersLoading, setMembersLoading] = useState(false);
  const [membersError, setMembersError] = useState("");

  const [apiStatus, setApiStatus] = useState("checking");

  const [patients, setPatients] = useState([]);
  const [patientCount, setPatientCount] = useState(0);
  const [patientOffset, setPatientOffset] = useState(0);
  const [patientsLoading, setPatientsLoading] = useState(false);
  const [patientsError, setPatientsError] = useState("");
  const [patientsLoaded, setPatientsLoaded] = useState(false);

  const [patientSearch, setPatientSearch] = useState("");
  const [patientSearchError, setPatientSearchError] = useState("");
  const [patientSearchLoading, setPatientSearchLoading] = useState(false);

  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientData, setPatientData] = useState({
    encounters: [],
    diagnoses: [],
    labs: [],
    medications: [],
    procedures: [],
    notes: [],
  });
  const [patientDataLoading, setPatientDataLoading] = useState(false);
  const [patientDataError, setPatientDataError] = useState("");
  const [activePatientTab, setActivePatientTab] = useState("encounters");

  useEffect(() => {
    async function checkApiHealth() {
      try {
        const response = await fetch(
          `${API_BASE_URL}/health/database`,
        );

        if (!response.ok) {
          throw new Error("API health check failed");
        }

        const data = await response.json();

        setApiStatus(
          data.status === "ok" ? "connected" : "unavailable",
        );
      } catch {
        setApiStatus("unavailable");
      }
    }

    async function loadCohorts() {
      try {
        const response = await fetch(`${API_BASE_URL}/cohorts`);

        if (!response.ok) {
          throw new Error(`API request failed: ${response.status}`);
        }

        const data = await response.json();
        setCohorts(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    checkApiHealth();
    loadCohorts();
  }, []);

  async function createCohort(event) {
    event.preventDefault();

    const trimmedName = cohortName.trim();
    const trimmedDescription = cohortDescription.trim();

    setCohortSaveError("");
    setCohortSaveSuccess("");

    if (!trimmedName) {
      setCohortSaveError("Cohort name is required.");
      return;
    }

    if (!cohortStartDate || !cohortEndDate) {
      setCohortSaveError("Study start and end dates are required.");
      return;
    }

    if (cohortEndDate < cohortStartDate) {
      setCohortSaveError(
        "Study end date cannot be before study start date.",
      );
      return;
    }

    const newCohort = {
      cohort_name: trimmedName,
      description: trimmedDescription || null,
      study_start_date: cohortStartDate,
      study_end_date: cohortEndDate,
    };

    setCohortSaving(true);

    try {
      const response = await fetch(`${API_BASE_URL}/cohorts`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newCohort),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || `API request failed: ${response.status}`,
        );
      }

      const createdCohort = await response.json();

      setCohorts((currentCohorts) => [
        ...currentCohorts,
        createdCohort,
      ]);

      setCohortName("");
      setCohortDescription("");
      setCohortStartDate("");
      setCohortEndDate("");

      setCohortSaveSuccess(
        `${createdCohort.cohort_name} was created successfully.`,
      );
    } catch (err) {
      setCohortSaveError(err.message);
    } finally {
      setCohortSaving(false);
    }
  }

  async function loadMembers(cohortId, offset = 0) {
    setMembersLoading(true);
    setMembersError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/cohorts/${cohortId}/members?limit=${MEMBER_PAGE_SIZE}&offset=${offset}`,
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || `API request failed: ${response.status}`,
        );
      }

      const data = await response.json();

      setMembers(data.members);
      setMemberCount(data.member_count);
      setMemberOffset(data.offset);
    } catch (err) {
      setMembers([]);
      setMemberCount(0);
      setMembersError(err.message);
    } finally {
      setMembersLoading(false);
    }
  }

  async function openCohort(cohort) {
    setSelectedCohort(cohort);
    setCriteria([]);
    setCriteriaError("");
    setCriteriaLoading(true);

    setExecutionResult(null);
    setExecutionError("");

    setCriterionType("inclusion");
    setCriterionDomain("diagnosis");
    setCriterionField("diagnosis_code");
    setCriterionOperator("=");
    setCriterionValue("");
    setCriterionSaveError("");

    setCriterionDeletingId(null);
    setCriterionDeleteError("");

    setMembers([]);
    setMemberCount(0);
    setMemberOffset(0);
    setMembersError("");

    const criteriaRequest = fetch(
      `${API_BASE_URL}/cohorts/${cohort.cohort_definition_id}/criteria`,
    );

    const membersRequest = loadMembers(
      cohort.cohort_definition_id,
      0,
    );

    try {
      const response = await criteriaRequest;

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const data = await response.json();
      setCriteria(data);
    } catch (err) {
      setCriteriaError(err.message);
    } finally {
      setCriteriaLoading(false);
    }

    await membersRequest;
  }

  async function executeCohort() {
    if (!selectedCohort) {
      return;
    }

    setExecutionLoading(true);
    setExecutionError("");
    setExecutionResult(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/cohorts/${selectedCohort.cohort_definition_id}/execute`,
        {
          method: "POST",
        },
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || `API request failed: ${response.status}`,
        );
      }

      const data = await response.json();
      setExecutionResult(data);

      await loadMembers(
        selectedCohort.cohort_definition_id,
        0,
      );
    } catch (err) {
      setExecutionError(err.message);
    } finally {
      setExecutionLoading(false);
    }
  }

  function handleTypeChange(event) {
    const newType = event.target.value;

    setCriterionType(newType);
    setCriterionSaveError("");

    if (newType === "exclusion") {
      setCriterionDomain("diagnosis");
      setCriterionField("diagnosis_code");
      setCriterionOperator("=");
    }
  }

  function handleDomainChange(event) {
    const newDomain = event.target.value;
    const fields = Object.keys(CRITERION_OPTIONS[newDomain]);
    const firstField = fields[0];
    const firstOperator = CRITERION_OPTIONS[newDomain][firstField][0];

    setCriterionDomain(newDomain);
    setCriterionField(firstField);
    setCriterionOperator(firstOperator);
    setCriterionSaveError("");
  }

  function handleFieldChange(event) {
    const newField = event.target.value;
    const firstOperator =
      CRITERION_OPTIONS[criterionDomain][newField][0];

    setCriterionField(newField);
    setCriterionOperator(firstOperator);
    setCriterionSaveError("");
  }

  async function addCriterion(event) {
    event.preventDefault();

    if (!selectedCohort) {
      return;
    }

    const trimmedValue = criterionValue.trim();

    if (!trimmedValue) {
      setCriterionSaveError("Criterion value is required.");
      return;
    }

    const nextOrder =
      criteria.length === 0
        ? 1
        : Math.max(
            ...criteria.map((criterion) => criterion.criterion_order),
          ) + 1;

    const newCriterion = {
      criterion_order: nextOrder,
      criterion_type: criterionType,
      domain: criterionDomain,
      field_name: criterionField,
      operator: criterionOperator,
      value_text: trimmedValue,
    };

    setCriterionSaving(true);
    setCriterionSaveError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/cohorts/${selectedCohort.cohort_definition_id}/criteria`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(newCriterion),
        },
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || `API request failed: ${response.status}`,
        );
      }

      const createdCriterion = await response.json();

      setCriteria((currentCriteria) =>
        [...currentCriteria, createdCriterion].sort(
          (a, b) => a.criterion_order - b.criterion_order,
        ),
      );

      setCriterionValue("");
      setExecutionResult(null);
      setExecutionError("");
    } catch (err) {
      setCriterionSaveError(err.message);
    } finally {
      setCriterionSaving(false);
    }
  }

  async function deleteCriterion(criterionId) {
    if (!selectedCohort) {
      return;
    }

    setCriterionDeletingId(criterionId);
    setCriterionDeleteError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/cohorts/${selectedCohort.cohort_definition_id}/criteria/${criterionId}`,
        {
          method: "DELETE",
        },
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || `API request failed: ${response.status}`,
        );
      }

      setCriteria((currentCriteria) =>
        currentCriteria.filter(
          (criterion) =>
            criterion.cohort_criterion_id !== criterionId,
        ),
      );

      setExecutionResult(null);
      setExecutionError("");
    } catch (err) {
      setCriterionDeleteError(err.message);
    } finally {
      setCriterionDeletingId(null);
    }
  }

  function goToPreviousMemberPage() {
    if (!selectedCohort || memberOffset === 0) {
      return;
    }

    const newOffset = Math.max(
      0,
      memberOffset - MEMBER_PAGE_SIZE,
    );

    loadMembers(
      selectedCohort.cohort_definition_id,
      newOffset,
    );
  }

  function goToNextMemberPage() {
    if (
      !selectedCohort ||
      memberOffset + MEMBER_PAGE_SIZE >= memberCount
    ) {
      return;
    }

    loadMembers(
      selectedCohort.cohort_definition_id,
      memberOffset + MEMBER_PAGE_SIZE,
    );
  }

  async function loadPatients(offset = 0) {
    setPatientsLoading(true);
    setPatientsError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/patients?limit=${PATIENT_PAGE_SIZE}&offset=${offset}`,
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || `API request failed: ${response.status}`,
        );
      }

      const data = await response.json();

      setPatients(data.patients);
      setPatientCount(data.patient_count);
      setPatientOffset(data.offset);
      setPatientsLoaded(true);
    } catch (err) {
      setPatients([]);
      setPatientsError(err.message);
    } finally {
      setPatientsLoading(false);
    }
  }

  function openPatientsView() {
    setActiveView("patients");
    setSelectedPatient(null);
    setPatientSearchError("");

    if (!patientsLoaded) {
      loadPatients(0);
    }
  }

  function openCohortsView() {
    setActiveView("cohorts");
  }

  async function openPatient(patientOrResearchId) {
    const researchId =
      typeof patientOrResearchId === "string"
        ? patientOrResearchId
        : patientOrResearchId.research_id;

    setPatientDataLoading(true);
    setPatientDataError("");
    setPatientSearchError("");
    setActivePatientTab("encounters");

    try {
      const [
        patientResponse,
        encountersResponse,
        diagnosesResponse,
        labsResponse,
        medicationsResponse,
        proceduresResponse,
        notesResponse,
      ] = await Promise.all([
        fetch(`${API_BASE_URL}/patients/${researchId}`),
        fetch(`${API_BASE_URL}/patients/${researchId}/encounters`),
        fetch(`${API_BASE_URL}/patients/${researchId}/diagnoses`),
        fetch(`${API_BASE_URL}/patients/${researchId}/labs`),
        fetch(`${API_BASE_URL}/patients/${researchId}/medications`),
        fetch(`${API_BASE_URL}/patients/${researchId}/procedures`),
        fetch(`${API_BASE_URL}/patients/${researchId}/notes`),
      ]);

      if (patientResponse.status === 404) {
        throw new Error("Patient not found.");
      }

      const responses = [
        patientResponse,
        encountersResponse,
        diagnosesResponse,
        labsResponse,
        medicationsResponse,
        proceduresResponse,
        notesResponse,
      ];

      const failedResponse = responses.find(
        (response) => !response.ok,
      );

      if (failedResponse) {
        throw new Error(
          `API request failed: ${failedResponse.status}`,
        );
      }

      const [
        patient,
        encounters,
        diagnoses,
        labs,
        medications,
        procedures,
        notes,
      ] = await Promise.all(
        responses.map((response) => response.json()),
      );

      setSelectedPatient(patient);
      setPatientData({
        encounters: encounters.encounters,
        diagnoses: diagnoses.diagnoses,
        labs: labs.lab_results,
        medications: medications.medications,
        procedures: procedures.procedures,
        notes: notes.notes,
      });
    } catch (err) {
      setSelectedPatient(null);
      setPatientDataError(err.message);
      throw err;
    } finally {
      setPatientDataLoading(false);
    }
  }

  async function searchPatient(event) {
    event.preventDefault();

    const researchId = patientSearch.trim().toUpperCase();

    setPatientSearchError("");

    if (!researchId) {
      setPatientSearchError("Enter a research ID.");
      return;
    }

    setPatientSearchLoading(true);

    try {
      await openPatient(researchId);
      setPatientSearch(researchId);
    } catch (err) {
      setPatientSearchError(err.message);
    } finally {
      setPatientSearchLoading(false);
    }
  }

  function goToPreviousPatientPage() {
    if (patientOffset === 0) {
      return;
    }

    loadPatients(
      Math.max(0, patientOffset - PATIENT_PAGE_SIZE),
    );
  }

  function goToNextPatientPage() {
    if (
      patientOffset + PATIENT_PAGE_SIZE >= patientCount
    ) {
      return;
    }

    loadPatients(patientOffset + PATIENT_PAGE_SIZE);
  }

  const availableDomains =
    criterionType === "exclusion"
      ? ["diagnosis"]
      : Object.keys(CRITERION_OPTIONS);

  const availableFields = Object.keys(
    CRITERION_OPTIONS[criterionDomain],
  );

  const availableOperators =
    CRITERION_OPTIONS[criterionDomain][criterionField];

  const memberRangeStart =
    memberCount === 0 ? 0 : memberOffset + 1;

  const memberRangeEnd = Math.min(
    memberOffset + members.length,
    memberCount,
  );

  const patientRangeStart =
    patientCount === 0 ? 0 : patientOffset + 1;

  const patientRangeEnd = Math.min(
    patientOffset + patients.length,
    patientCount,
  );

  const apiStatusLabel =
    apiStatus === "connected"
      ? "API connected"
      : apiStatus === "unavailable"
        ? "API unavailable"
        : "Checking API...";

  function renderPatientClinicalData() {
    if (!selectedPatient) {
      return null;
    }

    if (activePatientTab === "encounters") {
      return (
        <div className="patient-table-wrapper">
          <table className="patient-data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Type</th>
                <th>Category</th>
                <th>Facility</th>
                <th>Provider specialty</th>
                <th>Discharge</th>
              </tr>
            </thead>
            <tbody>
              {patientData.encounters.map((encounter) => (
                <tr key={encounter.encounter_id}>
                  <td>{formatDateTime(encounter.encounter_date)}</td>
                  <td>
                    {displayValue(
                      encounter.encounter_type_description,
                    )}
                  </td>
                  <td>
                    {displayValue(encounter.encounter_category)}
                  </td>
                  <td>{displayValue(encounter.facility_name)}</td>
                  <td>
                    {displayValue(encounter.provider_specialty)}
                  </td>
                  <td>
                    {formatDateTime(encounter.discharge_date)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    if (activePatientTab === "diagnoses") {
      return (
        <div className="patient-table-wrapper">
          <table className="patient-data-table">
            <thead>
              <tr>
                <th>Code</th>
                <th>Description</th>
                <th>Category</th>
                <th>Type</th>
                <th>Onset</th>
                <th>Recorded</th>
              </tr>
            </thead>
            <tbody>
              {patientData.diagnoses.map((diagnosis) => (
                <tr key={diagnosis.diagnosis_id}>
                  <td>
                    <strong>{diagnosis.diagnosis_code}</strong>
                  </td>
                  <td>
                    {displayValue(
                      diagnosis.diagnosis_description,
                    )}
                  </td>
                  <td>
                    {displayValue(diagnosis.diagnosis_category)}
                  </td>
                  <td>
                    {displayValue(diagnosis.diagnosis_type)}
                  </td>
                  <td>{formatDateTime(diagnosis.onset_date)}</td>
                  <td>{formatDateTime(diagnosis.recorded_date)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    if (activePatientTab === "labs") {
      return (
        <div className="patient-table-wrapper">
          <table className="patient-data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Test</th>
                <th>Name</th>
                <th>Result</th>
                <th>Unit</th>
              </tr>
            </thead>
            <tbody>
              {patientData.labs.map((lab) => (
                <tr key={lab.lab_result_id}>
                  <td>{formatDateTime(lab.result_date)}</td>
                  <td>
                    <strong>{lab.test_code}</strong>
                  </td>
                  <td>{displayValue(lab.test_name)}</td>
                  <td>
                    {displayValue(
                      lab.result_numeric ?? lab.result_text,
                    )}
                  </td>
                  <td>
                    {displayValue(lab.unit ?? lab.default_unit)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    if (activePatientTab === "medications") {
      return (
        <div className="patient-table-wrapper">
          <table className="patient-data-table">
            <thead>
              <tr>
                <th>Medication</th>
                <th>Class</th>
                <th>Dose</th>
                <th>Route</th>
                <th>Order date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {patientData.medications.map((medication) => (
                <tr key={medication.medication_order_id}>
                  <td>
                    <strong>{medication.medication_name}</strong>
                  </td>
                  <td>
                    {displayValue(medication.medication_class)}
                  </td>
                  <td>{displayValue(medication.dose)}</td>
                  <td>{displayValue(medication.route)}</td>
                  <td>{formatDateTime(medication.order_date)}</td>
                  <td>{displayValue(medication.status)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    if (activePatientTab === "procedures") {
      return (
        <div className="patient-table-wrapper">
          <table className="patient-data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Code</th>
                <th>Procedure</th>
                <th>Category</th>
              </tr>
            </thead>
            <tbody>
              {patientData.procedures.map((procedure) => (
                <tr key={procedure.procedure_id}>
                  <td>{formatDateTime(procedure.procedure_date)}</td>
                  <td>
                    <strong>{procedure.procedure_code}</strong>
                  </td>
                  <td>{displayValue(procedure.procedure_name)}</td>
                  <td>
                    {displayValue(procedure.procedure_category)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    return (
      <div className="notes-list">
        {patientData.notes.map((note) => (
          <article className="note-card" key={note.note_id}>
            <div className="note-card-header">
              <div>
                <strong>
                  {displayValue(note.note_type_description)}
                </strong>
                <span>
                  {displayValue(note.note_category)}
                </span>
              </div>
              <time>{formatDateTime(note.note_date)}</time>
            </div>
            <p>{displayValue(note.note_text)}</p>
          </article>
        ))}
      </div>
    );
  }

  function getActivePatientRecordCount() {
    return patientData[activePatientTab]?.length ?? 0;
  }

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <p className="eyebrow">Research Cohort Explorer</p>
          <h1>
            {activeView === "cohorts"
              ? "Cohort Management"
              : "Patient Explorer"}
          </h1>
          <p className="subtitle">
            {activeView === "cohorts"
              ? "Define, inspect, and execute research cohorts."
              : "Explore synthetic longitudinal patient records."}
          </p>
        </div>

        <div className="header-actions">
          <nav className="main-navigation">
            <button
              type="button"
              className={
                activeView === "cohorts" ? "active" : ""
              }
              onClick={openCohortsView}
            >
              Cohorts
            </button>
            <button
              type="button"
              className={
                activeView === "patients" ? "active" : ""
              }
              onClick={openPatientsView}
            >
              Patients
            </button>
          </nav>

          <div className={`api-status ${apiStatus}`}>
            <span className="status-dot" />
            {apiStatusLabel}
          </div>
        </div>
      </header>

      <main className="content">
        {activeView === "cohorts" && (
          <>
            <section className="create-cohort-section">
              <div className="section-header">
                <div>
                  <p className="section-eyebrow">Cohort builder</p>
                  <h2>Create cohort</h2>
                </div>
              </div>

              <div className="create-cohort-card">
                <form
                  className="create-cohort-form"
                  onSubmit={createCohort}
                >
                  <div className="form-field cohort-name-field">
                    <label htmlFor="cohort-name">
                      Cohort name
                    </label>
                    <input
                      id="cohort-name"
                      type="text"
                      value={cohortName}
                      onChange={(event) => {
                        setCohortName(event.target.value);
                        setCohortSaveError("");
                        setCohortSaveSuccess("");
                      }}
                      placeholder="Enter cohort name"
                    />
                  </div>

                  <div className="form-field cohort-description-field">
                    <label htmlFor="cohort-description">
                      Description
                    </label>
                    <input
                      id="cohort-description"
                      type="text"
                      value={cohortDescription}
                      onChange={(event) => {
                        setCohortDescription(event.target.value);
                        setCohortSaveError("");
                        setCohortSaveSuccess("");
                      }}
                      placeholder="Optional description"
                    />
                  </div>

                  <div className="form-field">
                    <label htmlFor="cohort-start-date">
                      Study start
                    </label>
                    <input
                      id="cohort-start-date"
                      type="date"
                      value={cohortStartDate}
                      onChange={(event) => {
                        setCohortStartDate(event.target.value);
                        setCohortSaveError("");
                        setCohortSaveSuccess("");
                      }}
                    />
                  </div>

                  <div className="form-field">
                    <label htmlFor="cohort-end-date">
                      Study end
                    </label>
                    <input
                      id="cohort-end-date"
                      type="date"
                      value={cohortEndDate}
                      onChange={(event) => {
                        setCohortEndDate(event.target.value);
                        setCohortSaveError("");
                        setCohortSaveSuccess("");
                      }}
                    />
                  </div>

                  <button
                    type="submit"
                    className="create-cohort-button"
                    disabled={cohortSaving}
                  >
                    {cohortSaving
                      ? "Creating..."
                      : "Create cohort"}
                  </button>
                </form>

                {cohortSaveError && (
                  <div className="form-error">
                    {cohortSaveError}
                  </div>
                )}

                {cohortSaveSuccess && (
                  <div className="form-success">
                    {cohortSaveSuccess}
                  </div>
                )}
              </div>
            </section>

            <section className="cohort-list-section">
              <div className="section-header">
                <div>
                  <p className="section-eyebrow">Cohorts</p>
                  <h2>Available cohorts</h2>
                </div>

                <span className="cohort-count">
                  {cohorts.length} cohort
                  {cohorts.length === 1 ? "" : "s"}
                </span>
              </div>

              {loading && (
                <div className="state-card">
                  <p>Loading cohorts...</p>
                </div>
              )}

              {error && (
                <div className="state-card error-card">
                  <h3>Unable to load cohorts</h3>
                  <p>{error}</p>
                  <p>
                    Make sure the FastAPI backend is running on port
                    8000.
                  </p>
                </div>
              )}

              {!loading && !error && cohorts.length === 0 && (
                <div className="state-card">
                  <h3>No cohorts found</h3>
                  <p>
                    Create a cohort to begin building a research
                    population.
                  </p>
                </div>
              )}

              {!loading && !error && cohorts.length > 0 && (
                <div className="cohort-grid">
                  {cohorts.map((cohort) => (
                    <article
                      className="cohort-card"
                      key={cohort.cohort_definition_id}
                    >
                      <div className="card-top">
                        <span className="cohort-id">
                          Cohort #{cohort.cohort_definition_id}
                        </span>

                        <span
                          className={`status-badge ${cohort.status}`}
                        >
                          {cohort.status}
                        </span>
                      </div>

                      <h3>{cohort.cohort_name}</h3>

                      <p className="description">
                        {cohort.description ||
                          "No description provided."}
                      </p>

                      <div className="date-range">
                        <div>
                          <span>Study start</span>
                          <strong>
                            {cohort.study_start_date}
                          </strong>
                        </div>

                        <div>
                          <span>Study end</span>
                          <strong>{cohort.study_end_date}</strong>
                        </div>
                      </div>

                      <div className="card-footer">
                        <span>Version {cohort.version}</span>

                        <button
                          type="button"
                          onClick={() => openCohort(cohort)}
                        >
                          Open cohort
                        </button>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </section>

            {selectedCohort && (
              <section className="criteria-section">
                <div className="section-header">
                  <div>
                    <p className="section-eyebrow">
                      Selected cohort
                    </p>
                    <h2>{selectedCohort.cohort_name}</h2>
                  </div>

                  <div className="selected-cohort-actions">
                    <span className="cohort-count">
                      {criteria.length}{" "}
                      {criteria.length === 1
                        ? "criterion"
                        : "criteria"}
                    </span>

                    <button
                      type="button"
                      className="execute-button"
                      onClick={executeCohort}
                      disabled={executionLoading}
                    >
                      {executionLoading
                        ? "Running..."
                        : "Run cohort"}
                    </button>
                  </div>
                </div>

                {executionError && (
                  <div className="state-card error-card execution-message">
                    <h3>Cohort execution failed</h3>
                    <p>{executionError}</p>
                  </div>
                )}

                {executionResult && (
                  <div className="execution-result">
                    <div>
                      <span className="result-label">
                        Execution status
                      </span>
                      <strong>{executionResult.status}</strong>
                    </div>

                    <div>
                      <span className="result-label">
                        Cohort members
                      </span>
                      <strong className="member-count">
                        {executionResult.member_count.toLocaleString()}
                      </strong>
                    </div>
                  </div>
                )}

                <section className="criterion-form-card">
                  <div className="criterion-form-heading">
                    <div>
                      <h3>Add criterion</h3>
                      <p>
                        Add a supported rule to the selected cohort
                        definition.
                      </p>
                    </div>
                  </div>

                  <form
                    className="criterion-form"
                    onSubmit={addCriterion}
                  >
                    <div className="form-field">
                      <label htmlFor="criterion-type">Type</label>
                      <select
                        id="criterion-type"
                        value={criterionType}
                        onChange={handleTypeChange}
                      >
                        <option value="inclusion">
                          Inclusion
                        </option>
                        <option value="exclusion">
                          Exclusion
                        </option>
                      </select>
                    </div>

                    <div className="form-field">
                      <label htmlFor="criterion-domain">
                        Domain
                      </label>
                      <select
                        id="criterion-domain"
                        value={criterionDomain}
                        onChange={handleDomainChange}
                      >
                        {availableDomains.map((domain) => (
                          <option key={domain} value={domain}>
                            {domain}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="form-field">
                      <label htmlFor="criterion-field">
                        Field
                      </label>
                      <select
                        id="criterion-field"
                        value={criterionField}
                        onChange={handleFieldChange}
                      >
                        {availableFields.map((field) => (
                          <option key={field} value={field}>
                            {field}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="form-field">
                      <label htmlFor="criterion-operator">
                        Operator
                      </label>
                      <select
                        id="criterion-operator"
                        value={criterionOperator}
                        onChange={(event) => {
                          setCriterionOperator(
                            event.target.value,
                          );
                          setCriterionSaveError("");
                        }}
                      >
                        {availableOperators.map((operator) => (
                          <option
                            key={operator}
                            value={operator}
                          >
                            {operator}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="form-field value-field">
                      <label htmlFor="criterion-value">
                        Value
                      </label>
                      <input
                        id="criterion-value"
                        type="text"
                        value={criterionValue}
                        onChange={(event) => {
                          setCriterionValue(event.target.value);
                          setCriterionSaveError("");
                        }}
                        placeholder="Enter criterion value"
                      />
                    </div>

                    <button
                      type="submit"
                      className="add-criterion-button"
                      disabled={criterionSaving}
                    >
                      {criterionSaving
                        ? "Adding..."
                        : "Add criterion"}
                    </button>
                  </form>

                  {criterionType === "exclusion" && (
                    <p className="form-note">
                      Cohort Engine v1 supports exclusion criteria
                      only for the diagnosis domain.
                    </p>
                  )}

                  {criterionSaveError && (
                    <div className="form-error">
                      {criterionSaveError}
                    </div>
                  )}
                </section>

                {criterionDeleteError && (
                  <div className="state-card error-card execution-message">
                    <h3>Unable to delete criterion</h3>
                    <p>{criterionDeleteError}</p>
                  </div>
                )}

                {criteriaLoading && (
                  <div className="state-card">
                    <p>Loading criteria...</p>
                  </div>
                )}

                {criteriaError && (
                  <div className="state-card error-card">
                    <h3>Unable to load criteria</h3>
                    <p>{criteriaError}</p>
                  </div>
                )}

                {!criteriaLoading &&
                  !criteriaError &&
                  criteria.length === 0 && (
                    <div className="state-card">
                      <p>
                        No criteria have been defined for this cohort.
                      </p>
                    </div>
                  )}

                {!criteriaLoading &&
                  !criteriaError &&
                  criteria.length > 0 && (
                    <div className="criteria-table-wrapper">
                      <table className="criteria-table">
                        <thead>
                          <tr>
                            <th>Order</th>
                            <th>Type</th>
                            <th>Domain</th>
                            <th>Field</th>
                            <th>Operator</th>
                            <th>Value</th>
                            <th>Action</th>
                          </tr>
                        </thead>

                        <tbody>
                          {criteria.map((criterion) => (
                            <tr
                              key={
                                criterion.cohort_criterion_id
                              }
                            >
                              <td>
                                {criterion.criterion_order}
                              </td>

                              <td>
                                <span
                                  className={`criterion-type ${criterion.criterion_type}`}
                                >
                                  {criterion.criterion_type}
                                </span>
                              </td>

                              <td>{criterion.domain}</td>
                              <td>{criterion.field_name}</td>

                              <td>
                                <code>{criterion.operator}</code>
                              </td>

                              <td>{criterion.value_text}</td>

                              <td>
                                <button
                                  type="button"
                                  className="delete-criterion-button"
                                  onClick={() =>
                                    deleteCriterion(
                                      criterion.cohort_criterion_id,
                                    )
                                  }
                                  disabled={
                                    criterionDeletingId ===
                                    criterion.cohort_criterion_id
                                  }
                                >
                                  {criterionDeletingId ===
                                  criterion.cohort_criterion_id
                                    ? "Deleting..."
                                    : "Delete"}
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                <section className="members-section">
                  <div className="members-header">
                    <div>
                      <p className="section-eyebrow">
                        Cohort population
                      </p>
                      <h3>Cohort members</h3>
                      <p className="members-description">
                        Patient demographics for the currently stored
                        cohort membership.
                      </p>
                    </div>

                    {!membersLoading && !membersError && (
                      <div className="members-summary">
                        <strong>
                          {memberCount.toLocaleString()}
                        </strong>
                        <span>
                          {memberCount === 1
                            ? "member"
                            : "members"}
                        </span>
                      </div>
                    )}
                  </div>

                  {membersLoading && (
                    <div className="state-card">
                      <p>Loading cohort members...</p>
                    </div>
                  )}

                  {membersError && (
                    <div className="state-card error-card">
                      <h3>Unable to load cohort members</h3>
                      <p>{membersError}</p>
                    </div>
                  )}

                  {!membersLoading &&
                    !membersError &&
                    memberCount === 0 && (
                      <div className="state-card">
                        <h3>No cohort members</h3>
                        <p>
                          Run this cohort to generate its membership.
                        </p>
                      </div>
                    )}

                  {!membersLoading &&
                    !membersError &&
                    memberCount > 0 && (
                      <>
                        <div className="members-table-wrapper">
                          <table className="members-table">
                            <thead>
                              <tr>
                                <th>Research ID</th>
                                <th>Date of birth</th>
                                <th>Age</th>
                                <th>Sex</th>
                                <th>Race</th>
                                <th>Ethnicity</th>
                                <th>ZIP3</th>
                              </tr>
                            </thead>

                            <tbody>
                              {members.map((member) => (
                                <tr key={member.research_id}>
                                  <td>
                                    <strong>
                                      {member.research_id}
                                    </strong>
                                  </td>
                                  <td>
                                    {member.date_of_birth}
                                  </td>
                                  <td>
                                    {member.age_at_study_end}
                                  </td>
                                  <td>{member.sex}</td>
                                  <td>{member.race}</td>
                                  <td>{member.ethnicity}</td>
                                  <td>{member.zip3}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>

                        <div className="members-pagination">
                          <span>
                            Showing{" "}
                            {memberRangeStart.toLocaleString()}–
                            {memberRangeEnd.toLocaleString()} of{" "}
                            {memberCount.toLocaleString()}
                          </span>

                          <div className="pagination-actions">
                            <button
                              type="button"
                              onClick={goToPreviousMemberPage}
                              disabled={
                                memberOffset === 0 ||
                                membersLoading
                              }
                            >
                              Previous
                            </button>

                            <button
                              type="button"
                              onClick={goToNextMemberPage}
                              disabled={
                                memberOffset +
                                  MEMBER_PAGE_SIZE >=
                                  memberCount ||
                                membersLoading
                              }
                            >
                              Next
                            </button>
                          </div>
                        </div>
                      </>
                    )}
                </section>
              </section>
            )}
          </>
        )}

        {activeView === "patients" && (
          <section className="patient-explorer">
            {!selectedPatient && (
              <>
                <div className="patient-explorer-hero">
                  <div>
                    <p className="section-eyebrow">
                      Synthetic clinical database
                    </p>
                    <h2>Patient directory</h2>
                    <p>
                      Browse the complete synthetic patient
                      population and inspect longitudinal clinical
                      records.
                    </p>
                  </div>

                  <div className="patient-total-card">
                    <strong>
                      {patientCount
                        ? patientCount.toLocaleString()
                        : "100,000"}
                    </strong>
                    <span>Synthetic patients</span>
                  </div>
                </div>

                <form
                  className="patient-search"
                  onSubmit={searchPatient}
                >
                  <div className="patient-search-field">
                    <label htmlFor="patient-search">
                      Research ID
                    </label>
                    <input
                      id="patient-search"
                      type="text"
                      value={patientSearch}
                      onChange={(event) => {
                        setPatientSearch(event.target.value);
                        setPatientSearchError("");
                      }}
                      placeholder="Example: P-000001"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={patientSearchLoading}
                  >
                    {patientSearchLoading
                      ? "Searching..."
                      : "Open patient"}
                  </button>
                </form>

                {patientSearchError && (
                  <div className="form-error patient-search-error">
                    {patientSearchError}
                  </div>
                )}

                {patientsLoading && (
                  <div className="state-card">
                    <p>Loading patients...</p>
                  </div>
                )}

                {patientsError && (
                  <div className="state-card error-card">
                    <h3>Unable to load patients</h3>
                    <p>{patientsError}</p>
                  </div>
                )}

                {!patientsLoading &&
                  !patientsError &&
                  patients.length > 0 && (
                    <>
                      <div className="patient-directory-wrapper">
                        <table className="patient-directory-table">
                          <thead>
                            <tr>
                              <th>Research ID</th>
                              <th>Date of birth</th>
                              <th>Age</th>
                              <th>Sex</th>
                              <th>Race</th>
                              <th>Ethnicity</th>
                              <th>ZIP3</th>
                              <th>Death date</th>
                            </tr>
                          </thead>

                          <tbody>
                            {patients.map((patient) => (
                              <tr key={patient.research_id}>
                                <td>
                                  <button
                                    type="button"
                                    className="patient-id-button"
                                    onClick={() =>
                                      openPatient(patient)
                                    }
                                  >
                                    {patient.research_id}
                                  </button>
                                </td>
                                <td>
                                  {displayValue(
                                    patient.date_of_birth,
                                  )}
                                </td>
                                <td>
                                  {displayValue(
                                    patient.age_at_study_end,
                                  )}
                                </td>
                                <td>
                                  {displayValue(patient.sex)}
                                </td>
                                <td>
                                  {displayValue(patient.race)}
                                </td>
                                <td>
                                  {displayValue(
                                    patient.ethnicity,
                                  )}
                                </td>
                                <td>
                                  {displayValue(patient.zip3)}
                                </td>
                                <td>
                                  {displayValue(
                                    patient.death_date,
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      <div className="members-pagination">
                        <span>
                          Showing{" "}
                          {patientRangeStart.toLocaleString()}–
                          {patientRangeEnd.toLocaleString()} of{" "}
                          {patientCount.toLocaleString()}
                        </span>

                        <div className="pagination-actions">
                          <button
                            type="button"
                            onClick={goToPreviousPatientPage}
                            disabled={
                              patientOffset === 0 ||
                              patientsLoading
                            }
                          >
                            Previous
                          </button>

                          <button
                            type="button"
                            onClick={goToNextPatientPage}
                            disabled={
                              patientOffset +
                                PATIENT_PAGE_SIZE >=
                                patientCount ||
                              patientsLoading
                            }
                          >
                            Next
                          </button>
                        </div>
                      </div>
                    </>
                  )}
              </>
            )}

            {patientDataLoading && (
              <div className="state-card patient-loading-card">
                <p>Loading patient record...</p>
              </div>
            )}

            {patientDataError &&
              !patientSearchError &&
              !patientDataLoading && (
                <div className="state-card error-card">
                  <h3>Unable to load patient record</h3>
                  <p>{patientDataError}</p>
                </div>
              )}

            {selectedPatient && !patientDataLoading && (
              <div className="patient-detail">
                <button
                  type="button"
                  className="back-to-patients-button"
                  onClick={() => {
                    setSelectedPatient(null);
                    setPatientDataError("");
                  }}
                >
                  ← Back to patient directory
                </button>

                <div className="patient-detail-header">
                  <div>
                    <p className="section-eyebrow">
                      Patient record
                    </p>
                    <h2>{selectedPatient.research_id}</h2>
                    <p>
                      Longitudinal synthetic clinical record across
                      encounters, diagnoses, laboratory results,
                      medications, procedures, and notes.
                    </p>
                  </div>
                </div>

                <div className="demographics-grid">
                  <div>
                    <span>Date of birth</span>
                    <strong>
                      {displayValue(
                        selectedPatient.date_of_birth,
                      )}
                    </strong>
                  </div>
                  <div>
                    <span>Age</span>
                    <strong>
                      {displayValue(
                        selectedPatient.age_at_study_end,
                      )}
                    </strong>
                  </div>
                  <div>
                    <span>Sex</span>
                    <strong>
                      {displayValue(selectedPatient.sex)}
                    </strong>
                  </div>
                  <div>
                    <span>Race</span>
                    <strong>
                      {displayValue(selectedPatient.race)}
                    </strong>
                  </div>
                  <div>
                    <span>Ethnicity</span>
                    <strong>
                      {displayValue(selectedPatient.ethnicity)}
                    </strong>
                  </div>
                  <div>
                    <span>ZIP3</span>
                    <strong>
                      {displayValue(selectedPatient.zip3)}
                    </strong>
                  </div>
                  <div>
                    <span>Death date</span>
                    <strong>
                      {displayValue(selectedPatient.death_date)}
                    </strong>
                  </div>
                </div>

                <section className="clinical-record-section">
                  <div className="clinical-record-heading">
                    <div>
                      <p className="section-eyebrow">
                        Longitudinal record
                      </p>
                      <h3>Clinical data</h3>
                    </div>

                    <span className="clinical-record-count">
                      {getActivePatientRecordCount().toLocaleString()}{" "}
                      {getActivePatientRecordCount() === 1
                        ? "record"
                        : "records"}
                    </span>
                  </div>

                  <div className="patient-tabs">
                    {PATIENT_TABS.map((tab) => (
                      <button
                        type="button"
                        key={tab.key}
                        className={
                          activePatientTab === tab.key
                            ? "active"
                            : ""
                        }
                        onClick={() =>
                          setActivePatientTab(tab.key)
                        }
                      >
                        {tab.label}
                        <span>
                          {patientData[tab.key].length.toLocaleString()}
                        </span>
                      </button>
                    ))}
                  </div>

                  {getActivePatientRecordCount() === 0 ? (
                    <div className="state-card patient-empty-state">
                      <p>
                        No {activePatientTab} records are available
                        for this patient.
                      </p>
                    </div>
                  ) : (
                    renderPatientClinicalData()
                  )}
                </section>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

export default App;