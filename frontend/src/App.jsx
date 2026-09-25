import { useEffect, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [cohorts, setCohorts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
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

    loadCohorts();
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <p className="eyebrow">Research Cohort Explorer</p>
          <h1>Cohort Management</h1>
          <p className="subtitle">
            Define, inspect, and execute research cohorts.
          </p>
        </div>

        <div className="api-status">
          <span className="status-dot" />
          API connected
        </div>
      </header>

      <main className="content">
        <section className="section-header">
          <div>
            <p className="section-eyebrow">Cohorts</p>
            <h2>Available cohorts</h2>
          </div>

          <span className="cohort-count">
            {cohorts.length} cohort{cohorts.length === 1 ? "" : "s"}
          </span>
        </section>

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
              Make sure the FastAPI backend is running on port 8000.
            </p>
          </div>
        )}

        {!loading && !error && cohorts.length === 0 && (
          <div className="state-card">
            <h3>No cohorts found</h3>
            <p>Create a cohort to begin building a research population.</p>
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

                  <span className={`status-badge ${cohort.status}`}>
                    {cohort.status}
                  </span>
                </div>

                <h3>{cohort.cohort_name}</h3>

                <p className="description">
                  {cohort.description || "No description provided."}
                </p>

                <div className="date-range">
                  <div>
                    <span>Study start</span>
                    <strong>{cohort.study_start_date}</strong>
                  </div>

                  <div>
                    <span>Study end</span>
                    <strong>{cohort.study_end_date}</strong>
                  </div>
                </div>

                <div className="card-footer">
                  <span>Version {cohort.version}</span>
                  <button type="button">Open cohort</button>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;