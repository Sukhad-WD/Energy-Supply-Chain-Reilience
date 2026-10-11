import { useState } from "react";
import { runPipeline } from "../services/api";

function Dashboard() {

  const [loading, setLoading] = useState(false);
const [error, setError] = useState("");
const [result, setResult] = useState(null);

const handleRunAnalysis = async () => {
  setLoading(true);
  setError("");

  try {
    const data = await runPipeline();

    console.log("Pipeline result:", data);

    setResult(data);
  } catch (err) {
    console.error(err);

    setError(
      err.message || "Unable to run the analysis."
    );
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="dashboard">

      {/* TOP NAV */}
      <nav className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <span></span>
            <span></span>
            <span></span>
          </div>

          <div>
            <div className="brand-name">ENERGY // RESILIENCE</div>
            <div className="brand-sub">SUPPLY CHAIN INTELLIGENCE</div>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          SYSTEM ONLINE
        </div>
      </nav>


      {/* HERO */}
      <section className="hero">

        <div className="hero-content">

          <div className="eyebrow">
            <span></span>
            AI-DRIVEN ENERGY OPERATIONS
          </div>

          <h1>
            Global Energy
            <br />
            <span>Supply Chain</span>
          </h1>

          <p>
            Detect geopolitical disruptions, model supply-chain impact,
            and generate executable procurement strategies.
          </p>

          <button
  className="run-button"
  onClick={handleRunAnalysis}
  disabled={loading}
>
  <span>{loading ? "◌" : "▶"}</span>

  {loading
    ? "Running AI Analysis..."
    : "Run Risk Analysis"}
</button>

        </div>

        <div className="hero-visual">

          <div className="orbit orbit-one"></div>
          <div className="orbit orbit-two"></div>

          <div className="globe">
            <div className="globe-line horizontal"></div>
            <div className="globe-line horizontal second"></div>
            <div className="globe-line vertical"></div>

            <div className="globe-core">
              ENERGY
            </div>
          </div>

          <div className="route route-one"></div>
          <div className="route route-two"></div>

          <div className="map-node node-one"></div>
          <div className="map-node node-two"></div>
          <div className="map-node node-three"></div>

        </div>

      </section>

      {error && (
  <div className="error-banner">
    <strong>Analysis failed</strong>
    <span>{error}</span>
  </div>
)}

      {/* PIPELINE */}
      <section className="pipeline-section">

        <div className="section-heading">
          <div>
            <span className="section-index">01</span>
            <h2>AI Intelligence Pipeline</h2>
          </div>

          <span className="live-label">
            ● LIVE ARCHITECTURE
          </span>
        </div>


        <div className="pipeline">

          <div className="pipeline-card active">

            <div className="pipeline-top">
              <span className="agent-id">AGENT 01</span>
              <span className="agent-status">READY</span>
            </div>

            <div className="agent-icon">◉</div>

            <h3>Risk Scanner</h3>

            <p>
              Geopolitical events, attacks, disruptions and
              energy supply signals.
            </p>

            <div className="pipeline-footer">
              NEWS INTELLIGENCE
            </div>

          </div>


          <div className="pipeline-connector">
            <span></span>
            <i>→</i>
          </div>


          <div className="pipeline-card">

            <div className="pipeline-top">
              <span className="agent-id">AGENT 02</span>
              <span className="agent-status">READY</span>
            </div>

            <div className="agent-icon">◈</div>

            <h3>Impact Model</h3>

            <p>
              Models supply gaps, price pressure, refinery
              stress and reserve requirements.
            </p>

            <div className="pipeline-footer">
              SCENARIO ENGINE
            </div>

          </div>


          <div className="pipeline-connector">
            <span></span>
            <i>→</i>
          </div>


          <div className="pipeline-card">

            <div className="pipeline-top">
              <span className="agent-id">AGENT 03</span>
              <span className="agent-status">READY</span>
            </div>

            <div className="agent-icon">◆</div>

            <h3>Procurement AI</h3>

            <p>
              Ranks alternative suppliers by cost, speed,
              availability and route risk.
            </p>

            <div className="pipeline-footer">
              DECISION ENGINE
            </div>

          </div>

        </div>

      </section>


      {/* RISK OVERVIEW */}
      <section className="risk-section">

        <div className="section-heading">
          <div>
            <span className="section-index">02</span>
            <h2>Current Supply Risk</h2>
          </div>

          <span className="timestamp">
            AWAITING ANALYSIS
          </span>
        </div>


        <div className="risk-grid">

          <div className="risk-card primary-risk">

            <div className="card-label">
              OVERALL RISK INDEX
            </div>

            <div className="risk-number">
             {result?.impact_report?.risk_score ?? "--"}
             </div>

            <div className="risk-scale">
              <span></span>
            </div>

            <div className="card-foot">
              GLOBAL ENERGY EXPOSURE
            </div>

          </div>


          <div className="risk-card">

            <div className="card-label">
              RISK LEVEL
            </div>

            <div className="metric-placeholder">
  {result?.agent2?.scenario?.risk_level ?? "--"}
</div>

            <div className="metric-note">
              Agent 1 analysis
            </div>

          </div>


          <div className="risk-card">

            <div className="card-label">
              SUPPLY GAP
            </div>

            <div className="metric-placeholder">
  {result?.agent2?.scenario?.supply_gap_percent ?? "--"}
  <small>%</small>
</div>

            <div className="metric-note">
              Agent 2 scenario
            </div>

          </div>


          <div className="risk-card">

            <div className="card-label">
              RESERVE DAYS
            </div>

            <div className="metric-placeholder">
  {result?.impact_report?.reserve_days ?? "--"}
</div>

            <div className="metric-note">
              Strategic reserve
            </div>

          </div>

        </div>

      </section>


      {/* LOWER INTELLIGENCE */}
      <section className="intelligence-grid">

        {/* CORRIDORS */}
        <div className="intel-panel">

          <div className="panel-header">
            <div>
              <span className="panel-tag">LIVE RISK MAP</span>
              <h2>Affected Corridors</h2>
            </div>

            <span className="panel-icon">↗</span>
          </div>

          <div className="corridor-visual">

            <div className="corridor-line line-a"></div>
            <div className="corridor-line line-b"></div>

            <div className="corridor-node n1">
              <span></span>
              ORIGIN
            </div>

            <div className="corridor-node n2 danger">
              <span></span>
              DISRUPTION
            </div>

            <div className="corridor-node n3">
              <span></span>
              REFINERY
            </div>

          </div>

          <div className="empty-message">

  {result?.impact_report?.affected_route ? (
    <>
      <span>●</span>

      Affected route:
      {" "}
      <strong>
        {result.impact_report.affected_route}
      </strong>
    </>
  ) : (
    <>
      <span>◌</span>
      Run analysis to detect vulnerable energy corridors.
    </>
  )}

</div>

        </div>


        {/* PROCUREMENT */}
        <div className="intel-panel">

          <div className="panel-header">
            <div>
              <span className="panel-tag">AGENT 03 OUTPUT</span>
              <h2>Procurement Intelligence</h2>
            </div>

            <span className="panel-icon">↗</span>
          </div>

          <div className="supplier-table">

  <div className="supplier-header">
    <span>SUPPLIER</span>
    <span>COST / BBL</span>
    <span>DELIVERY</span>
  </div>

  {result?.top_suppliers?.length ? (

    result.top_suppliers.map((supplier, index) => (

      <div
        className="supplier-row"
        key={`${supplier.supplier}-${index}`}
      >

        <span className="supplier-name">
          <b>
            {String(index + 1).padStart(2, "0")}
          </b>

          {supplier.supplier}
        </span>

        <span>
          ${supplier.cost_per_barrel}
        </span>

        <span>
          {supplier.delivery_days} days
        </span>

      </div>

    ))

  ) : (

    <>
      <div className="supplier-row">
        <span className="supplier-name">
          <b>01</b>
          Awaiting analysis
        </span>

        <span>--</span>
        <span>--</span>
      </div>

      <div className="supplier-row">
        <span className="supplier-name">
          <b>02</b>
          Awaiting analysis
        </span>

        <span>--</span>
        <span>--</span>
      </div>

      <div className="supplier-row">
        <span className="supplier-name">
          <b>03</b>
          Awaiting analysis
        </span>

        <span>--</span>
        <span>--</span>
      </div>
    </>

  )}

</div>

        </div>

      </section>


      {/* FOOTER */}
      <footer className="dashboard-footer">

        <span>
          ENERGY SUPPLY CHAIN // AI RESILIENCE PLATFORM
        </span>

        <span>
          AGENT 01 · AGENT 02 · AGENT 03
        </span>

      </footer>

    </div>
  );
}

export default Dashboard;