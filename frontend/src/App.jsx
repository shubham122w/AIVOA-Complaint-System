import { useRef, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import "./App.css";

import {
  setComplaint,
  resetComplaint,
} from "./redux/complaintSlice";

import {
  analyzeComplaint,
  analyzeComplaintPdf,
  correctComplaint,
  createComplaint,
  getComplaints,
  checkComplaintCompleteness,
  recommendRootCause,
  checkDuplicateComplaint,
  recommendCAPA,
  generateComplaintSummary,
  classifyComplaintRisk,
} from "./services/api";

import ComplaintLedger from "./components/ComplaintLedger";



function App() {
  const complaint = useSelector(
    (state) => state.complaint
  );

  const dispatch = useDispatch();

  const fileInputRef = useRef(null);

  // ==================================================
  // LOCAL STATES
  // ==================================================

  const [complaintText, setComplaintText] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [pdfLoading, setPdfLoading] =
    useState(false);

  const [correctionText, setCorrectionText] =
    useState("");

  const [correctionLoading, setCorrectionLoading] =
    useState(false);

  const [completenessResult, setCompletenessResult] =
    useState(null);

  const [rootCauseResult, setRootCauseResult] =
    useState(null);

  const [duplicateResult, setDuplicateResult] =
    useState(null);

  const [capaResult, setCapaResult] =
    useState(null);

  const [summaryResult, setSummaryResult] =
    useState(null);

  const [riskResult, setRiskResult] =
    useState(null);

  const [featureLoading, setFeatureLoading] =
    useState("");

  // ==================================================
  // COMMON FIELD UPDATE
  // ==================================================

  const handleFieldChange = (
    field,
    value
  ) => {
    dispatch(
      setComplaint({
        [field]: value,
      })
    );
  };

  // ==================================================
  // ANALYZE TEXT COMPLAINT
  // ==================================================

  const handleAnalyze = async () => {
    if (!complaintText.trim()) {
      alert("Please enter a complaint first.");
      return;
    }

    try {
      setLoading(true);

      const data = await analyzeComplaint(
        complaintText
      );

      dispatch(
        setComplaint({
          ...data,

          complaint_type:
            data.complaint_type ??
            data.complaint_category ??
            "",

          detailed_description:
            data.detailed_description ??
            data.complaint_description ??
            "",

          initial_severity:
            data.initial_severity ??
            data.severity ??
            "",

          priority:
            data.priority ?? "",
        })
      );

      alert(
        "Complaint analyzed successfully!"
      );
    } catch (error) {
      console.error(
        "Analysis error:",
        error
      );

      alert(
        error.response?.data?.detail ||
          "Failed to analyze complaint. Please make sure the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  // ==================================================
  // PDF UPLOAD
  // ==================================================

  const handlePdfUpload = async (event) => {
    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    if (
      !file.name
        .toLowerCase()
        .endsWith(".pdf")
    ) {
      alert("Please select a PDF file.");
      event.target.value = "";
      return;
    }

    try {
      setPdfLoading(true);

      const data =
        await analyzeComplaintPdf(file);

      dispatch(
        setComplaint({
          ...data,

          complaint_type:
            data.complaint_type ??
            data.complaint_category ??
            "",

          detailed_description:
            data.detailed_description ??
            data.complaint_description ??
            "",

          initial_severity:
            data.initial_severity ??
            data.severity ??
            "",

          priority:
            data.priority ?? "",
        })
      );

      alert(
        "PDF complaint analyzed successfully!"
      );
    } catch (error) {
      console.error(
        "PDF analysis error:",
        error
      );

      alert(
        error.response?.data?.detail ||
          "Failed to analyze PDF."
      );
    } finally {
      setPdfLoading(false);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  // ==================================================
  // AI CORRECTION
  // ==================================================

  const handleCorrection = async () => {
    if (!correctionText.trim()) {
      alert(
        "Please enter a correction first."
      );
      return;
    }

    try {
      setCorrectionLoading(true);

      const updatedData =
        await correctComplaint(
          complaint,
          correctionText
        );

      if (updatedData.error) {
        alert(
          "AI correction failed. Please try again."
        );
        return;
      }

      const normalizedData = {
        ...updatedData,

        complaint_type:
          updatedData.complaint_type ??
          updatedData.complaint_category ??
          complaint.complaint_type,

        detailed_description:
          updatedData.detailed_description ??
          updatedData.complaint_description ??
          complaint.detailed_description,

        initial_severity:
          updatedData.initial_severity ??
          updatedData.severity ??
          complaint.initial_severity,

        priority:
          updatedData.priority ??
          complaint.priority,
      };

      dispatch(
        setComplaint(normalizedData)
      );

      setCorrectionText("");

      alert(
        "AI correction applied successfully!"
      );
    } catch (error) {
      console.error(
        "Correction error:",
        error
      );

      alert(
        error.response?.data?.detail ||
          "Failed to apply AI correction."
      );
    } finally {
      setCorrectionLoading(false);
    }
  };

  // ==================================================
  // COMPLETENESS CHECKER
  // ==================================================

  const handleCompletenessCheck =
    async () => {
      try {
        setFeatureLoading(
          "completeness"
        );

        const result =
          await checkComplaintCompleteness(
            complaint
          );

        setCompletenessResult(result);
      } catch (error) {
        console.error(
          "Completeness error:",
          error
        );

        alert(
          error.response?.data?.detail ||
            "Completeness check failed."
        );
      } finally {
        setFeatureLoading("");
      }
    };

  // ==================================================
  // ROOT CAUSE
  // ==================================================

  const handleRootCause = async () => {
    try {
      setFeatureLoading(
        "root-cause"
      );

      const result =
        await recommendRootCause(
          complaint
        );

      setRootCauseResult(result);
    } catch (error) {
      console.error(
        "Root cause error:",
        error
      );

      alert(
        error.response?.data?.detail ||
          "Root cause recommendation failed."
      );
    } finally {
      setFeatureLoading("");
    }
  };

  // ==================================================
  // DUPLICATE DETECTION
  // ==================================================

  const handleDuplicateCheck =
    async () => {
      try {
        setFeatureLoading(
          "duplicate"
        );

        const existingComplaints =
          await getComplaints();

        const result =
          await checkDuplicateComplaint(
            complaint,
            existingComplaints
          );

        setDuplicateResult(result);
      } catch (error) {
        console.error(
          "Duplicate detection error:",
          error
        );

        alert(
          error.response?.data?.detail ||
            "Duplicate detection failed."
        );
      } finally {
        setFeatureLoading("");
      }
    };

  // ==================================================
  // CAPA
  // ==================================================

  const handleCAPA = async () => {
    try {
      setFeatureLoading("capa");

      const result =
        await recommendCAPA(
          complaint
        );

      setCapaResult(result);
    } catch (error) {
      console.error(
        "CAPA error:",
        error
      );

      alert(
        error.response?.data?.detail ||
          "CAPA recommendation failed."
      );
    } finally {
      setFeatureLoading("");
    }
  };

  // ==================================================
  // SUMMARY
  // ==================================================

  const handleSummary = async () => {
    try {
      setFeatureLoading(
        "summary"
      );

      const result =
        await generateComplaintSummary(
          complaint
        );

      setSummaryResult(result);
    } catch (error) {
      console.error(
        "Summary error:",
        error
      );

      alert(
        error.response?.data?.detail ||
          "Complaint summary generation failed."
      );
    } finally {
      setFeatureLoading("");
    }
  };

  // ==================================================
  // RISK CLASSIFICATION
  // ==================================================

  const handleRiskClassification =
    async () => {
      try {
        setFeatureLoading(
          "risk"
        );

        const result =
          await classifyComplaintRisk(
            complaint
          );

        setRiskResult(result);
      } catch (error) {
        console.error(
          "Risk classification error:",
          error
        );

        alert(
          error.response?.data?.detail ||
            "Risk classification failed."
        );
      } finally {
        setFeatureLoading("");
      }
    };

  // ==================================================
  // COMMIT TO QMS LEDGER
  // ==================================================

  const handleCommit = async () => {
    try {
      // Backend requires complaint_date.
      // Use today's date for the QMS record.
      const today =
        new Date()
          .toISOString()
          .split("T")[0];

      const complaintData = {
        complaint_source:
          complaint.complaint_source ||
          "Customer",

        customer_name:
          complaint.customer_name || "",

        product_name:
          complaint.product_name || "",

        product_strength:
          complaint.product_strength || "",

        batch_number:
          complaint.batch_number || "",

        manufacturing_date:
          complaint.manufacturing_date ||
          null,

        expiry_date:
          complaint.expiry_date ||
          null,

        quantity_affected:
          complaint.quantity_affected || "",

        complaint_type:
          complaint.complaint_type || "",

        complaint_date: today,

        detailed_description:
          complaint.detailed_description ||
          "",

        initial_severity:
          complaint.initial_severity || "",

        priority:
          complaint.priority || "Normal",
      };

      // Basic validation before sending
      const requiredFields = [
        [
          "Customer Name",
          complaintData.customer_name,
        ],
        [
          "Product Name",
          complaintData.product_name,
        ],
        [
          "Product Strength",
          complaintData.product_strength,
        ],
        [
          "Batch Number",
          complaintData.batch_number,
        ],
        [
          "Quantity Affected",
          complaintData.quantity_affected,
        ],
        [
          "Complaint Type",
          complaintData.complaint_type,
        ],
        [
          "Complaint Description",
          complaintData.detailed_description,
        ],
        [
          "Severity",
          complaintData.initial_severity,
        ],
      ];

      const missingFields =
        requiredFields
          .filter(
            ([, value]) =>
              !String(value).trim()
          )
          .map(
            ([name]) => name
          );

      if (
        missingFields.length > 0
      ) {
        alert(
          `Please complete these fields before committing:\n\n${missingFields.join(
            "\n"
          )}`
        );
        return;
      }

      const result =
        await createComplaint(
          complaintData
        );

      // IMPORTANT:
      // Backend returns:
      // {
      //   message: "...",
      //   complaint_id: 8
      // }

      const complaintId =
        result?.complaint_id ??
        result?.id ??
        result?.data?.complaint_id ??
        result?.data?.id;

      if (
        complaintId !==
        undefined
      ) {
        alert(
          `Complaint committed successfully!\n\nComplaint ID: ${complaintId}`
        );
      } else {
        alert(
          "Complaint committed successfully!\n\nComplaint ID could not be read from the server response."
        );
      }

      // Scroll to ledger after commit
      setTimeout(() => {
        const ledger =
          document.getElementById(
            "qms-ledger"
          );

        if (ledger) {
          ledger.scrollIntoView({
            behavior: "smooth",
          });
        }
      }, 300);
    } catch (error) {
      console.error(
        "Commit error:",
        error
      );

      alert(
        error.response?.data?.detail ||
          "Failed to commit complaint to QMS Ledger."
      );
    }
  };

  // ==================================================
  // RESET
  // ==================================================

  const handleReset = () => {
    dispatch(resetComplaint());

    setComplaintText("");
    setCorrectionText("");

    setCompletenessResult(null);
    setRootCauseResult(null);
    setDuplicateResult(null);
    setCapaResult(null);
    setSummaryResult(null);
    setRiskResult(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // ==================================================
  // HELPER
  // ==================================================

  const isLoading =
    (feature) =>
      featureLoading === feature;

  // ==================================================
  // UI
  // ==================================================

  return (
    <div className="app">

      {/* ==================================================
          HEADER
      ================================================== */}

      <header className="header">

        <div>
          <h1>AIVOA</h1>

          <p>
            AI-Powered Complaint Management System
          </p>
        </div>

        <div className="status">
          <span className="status-dot"></span>

          {complaint.initial_severity
            ? "Ready to Commit"
            : "Pending Triage"}
        </div>

      </header>


      {/* ==================================================
          MAIN LAYOUT
      ================================================== */}

      <main className="main-layout">

        {/* ==================================================
            LEFT SIDE
        ================================================== */}

        <section className="complaint-panel">

          {/* PANEL HEADER */}

          <div className="panel-header">

            <div>

              <h2>
                Complaint Details
              </h2>

              <p>
                Review and update extracted complaint information
              </p>

            </div>

          </div>


          {/* ==================================================
              ORIGIN & CUSTOMER
          ================================================== */}

          <div className="form-section">

            <h3>
              Origin & Customer Details
            </h3>

            <div className="form-grid">

              <div className="field">

                <label>
                  Complaint Source
                </label>

                <select
                  value={
                    complaint.complaint_source ||
                    ""
                  }
                  onChange={(e) =>
                    handleFieldChange(
                      "complaint_source",
                      e.target.value
                    )
                  }
                >

                  <option value="">
                    Select source
                  </option>

                  <option value="Pharmacy">
                    Pharmacy
                  </option>

                  <option value="Hospital">
                    Hospital
                  </option>

                  <option value="Distributor">
                    Distributor
                  </option>

                  <option value="Customer">
                    Customer
                  </option>

                  <option value="Email">
                    Email
                  </option>

                  <option value="Phone">
                    Phone
                  </option>

                </select>

              </div>


              <div className="field">

                <label>
                  Customer Name
                </label>

                <input
                  type="text"
                  placeholder="Enter customer name"
                  value={
                    complaint.customer_name ||
                    ""
                  }
                  onChange={(e) =>
                    handleFieldChange(
                      "customer_name",
                      e.target.value
                    )
                  }
                />

              </div>

            </div>

          </div>


          {/* ==================================================
              PRODUCT & BATCH
          ================================================== */}

          <div className="form-section">

            <h3>
              Product & Batch Identification
            </h3>

            <div className="form-grid">

              <div className="field">

                <label>
                  Product Name
                </label>

                <input
                  type="text"
                  placeholder="Product name"
                  value={
                    complaint.product_name ||
                    ""
                  }
                  onChange={(e) =>
                    handleFieldChange(
                      "product_name",
                      e.target.value
                    )
                  }
                />

              </div>


              <div className="field">

                <label>
                  Product Strength / Grade
                </label>

                <input
                  type="text"
                  placeholder="e.g. 500 mg / IP / BP"
                  value={
                    complaint.product_strength ||
                    ""
                  }
                  onChange={(e) =>
                    handleFieldChange(
                      "product_strength",
                      e.target.value
                    )
                  }
                />

              </div>


              <div className="field">

                <label>
                  Batch / Lot Number
                </label>

                <input
                  type="text"
                  placeholder="Batch number"
                  value={
                    complaint.batch_number ||
                    ""
                  }
                  onChange={(e) =>
                    handleFieldChange(
                      "batch_number",
                      e.target.value
                    )
                  }
                />

              </div>


              <div className="field">

                <label>
                  Manufacturing Date
                </label>

                <input
                  type="date"
                  value={
                    complaint.manufacturing_date ||
                    ""
                  }
                  onChange={(e) =>
                    handleFieldChange(
                      "manufacturing_date",
                      e.target.value
                    )
                  }
                />

              </div>


              <div className="field">

                <label>
                  Expiry Date
                </label>

                <input
                  type="date"
                  value={
                    complaint.expiry_date ||
                    ""
                  }
                  onChange={(e) =>
                    handleFieldChange(
                      "expiry_date",
                      e.target.value
                    )
                  }
                />

              </div>


              <div className="field">

                <label>
                  Affected Quantity
                </label>

                <input
                  type="text"
                  placeholder="e.g. 25 kg"
                  value={
                    complaint.quantity_affected ||
                    ""
                  }
                  onChange={(e) =>
                    handleFieldChange(
                      "quantity_affected",
                      e.target.value
                    )
                  }
                />

              </div>

            </div>

          </div>


          {/* ==================================================
              FACILITY
          ================================================== */}

          <div className="form-section">

            <h3>
              Facility & Material Impact
            </h3>

            <div className="form-grid">

              <div className="field">

                <label>
                  Originating Site
                </label>

                <input
                  type="text"
                  placeholder="Manufacturing site"
                  value={
                    complaint.originating_site ||
                    ""
                  }
                  onChange={(e) =>
                    handleFieldChange(
                      "originating_site",
                      e.target.value
                    )
                  }
                />

              </div>


              <div className="field">

                <label>
                  Block Impacted
                </label>

                <input
                  type="text"
                  placeholder="Block / area"
                  value={
                    complaint.block_impacted ||
                    ""
                  }
                  onChange={(e) =>
                    handleFieldChange(
                      "block_impacted",
                      e.target.value
                    )
                  }
                />

              </div>


              <div className="field full">

                <label>
                  Non-Product Materials (NPM)
                </label>

                <input
                  type="text"
                  placeholder="Packaging / material impact"
                  value={
                    complaint.npm ||
                    ""
                  }
                  onChange={(e) =>
                    handleFieldChange(
                      "npm",
                      e.target.value
                    )
                  }
                />

              </div>

            </div>

          </div>


          {/* ==================================================
              DEFECT ANALYSIS
          ================================================== */}

          <div className="form-section">

            <h3>
              Defect Analysis
            </h3>


            <div className="field">

              <label>
                Complaint Category
              </label>

              <input
                type="text"
                placeholder="Complaint category"
                value={
                  complaint.complaint_type ||
                  ""
                }
                onChange={(e) =>
                  handleFieldChange(
                    "complaint_type",
                    e.target.value
                  )
                }
              />

            </div>


            <div className="field">

              <label>
                Complaint Description
              </label>

              <textarea
                rows="5"
                placeholder="Complaint description"
                value={
                  complaint.detailed_description ||
                  ""
                }
                onChange={(e) =>
                  handleFieldChange(
                    "detailed_description",
                    e.target.value
                  )
                }
              />

            </div>

          </div>


          {/* ==================================================
              AI RISK ASSESSMENT
          ================================================== */}

          <div className="form-section risk-section">

            <div className="section-heading-row">

              <div>

                <h3>
                  AI Copilot Risk Assessment
                </h3>

                <p>
                  AI-generated assessment for initial triage
                </p>

              </div>

              <span className="ai-badge">
                AI
              </span>

            </div>


            <div className="form-grid">

              <div className="field">

                <label>
                  Severity (Suggested)
                </label>

                <input
                  type="text"
                  value={
                    complaint.initial_severity ||
                    ""
                  }
                  readOnly
                />

              </div>


              <div className="field">

                <label>
                  Priority
                </label>

                <input
                  type="text"
                  value={
                    complaint.priority ||
                    ""
                  }
                  readOnly
                />

              </div>


              <div className="field full">

                <label>
                  Suggested Next Action
                </label>

                <textarea
                  rows="3"
                  value={
                    complaint.suggested_next_action ||
                    ""
                  }
                  readOnly
                />

              </div>


              <div className="field full">

                <label>
                  Initial Risk Assessment
                </label>

                <textarea
                  rows="4"
                  value={
                    complaint.initial_risk_assessment ||
                    ""
                  }
                  readOnly
                />

              </div>

            </div>

          </div>


          {/* ==================================================
              BONUS FEATURES
          ================================================== */}

          <div className="ai-features">


            {/* COMPLETENESS */}

            <div className="feature-card">

              <div className="feature-header">

                <div>

                  <h3>
                    Complaint Completeness Checker
                  </h3>

                  <p>
                    Check whether all important complaint information is available.
                  </p>

                </div>

                <span className="ai-badge">
                  AI
                </span>

              </div>


              <button
                className="feature-button"
                onClick={
                  handleCompletenessCheck
                }
                disabled={
                  isLoading("completeness")
                }
              >
                {isLoading("completeness")
                  ? "Checking..."
                  : "Check Completeness"}
              </button>


              {completenessResult && (
                <div className="feature-result">

                  <strong>
                    Status:{" "}
                    {completenessResult.status}
                  </strong>

                  {completenessResult
                    .missing_fields
                    ?.length > 0 && (

                    <div>
                      <p>
                        <strong>
                          Missing Fields:
                        </strong>
                      </p>

                      <ul>
                        {completenessResult.missing_fields.map(
                          (item, index) => (
                            <li key={index}>
                              {item}
                            </li>
                          )
                        )}
                      </ul>

                    </div>

                  )}

                  {completenessResult.message && (
                    <p>
                      {
                        completenessResult.message
                      }
                    </p>
                  )}

                </div>
              )}

            </div>


            {/* ROOT CAUSE */}

            <div className="feature-card">

              <div className="feature-header">

                <div>

                  <h3>
                    AI Root Cause Recommendation
                  </h3>

                  <p>
                    AI-generated hypotheses for QA investigation.
                  </p>

                </div>

                <span className="ai-badge">
                  AI
                </span>

              </div>


              <button
                className="feature-button"
                onClick={
                  handleRootCause
                }
                disabled={
                  isLoading("root-cause")
                }
              >
                {isLoading("root-cause")
                  ? "Analyzing..."
                  : "Recommend Root Cause"}
              </button>


              {rootCauseResult && (
                <div className="feature-result">

                  {rootCauseResult.summary && (
                    <p>
                      <strong>
                        Summary:
                      </strong>{" "}
                      {
                        rootCauseResult.summary
                      }
                    </p>
                  )}


                  {rootCauseResult
                    .possible_root_causes
                    ?.length > 0 && (

                    <div>

                      <strong>
                        Possible Root Causes
                      </strong>

                      <ul>

                        {rootCauseResult.possible_root_causes.map(
                          (item, index) => (
                            <li key={index}>

                              <strong>
                                {item.cause}
                              </strong>

                              {item.reason && (
                                <>
                                  {" - "}
                                  {item.reason}
                                </>
                              )}

                            </li>
                          )
                        )}

                      </ul>

                    </div>

                  )}


                  {rootCauseResult
                    .recommended_investigation
                    ?.length > 0 && (

                    <div>

                      <strong>
                        Investigation
                      </strong>

                      <ul>

                        {rootCauseResult.recommended_investigation.map(
                          (item, index) => (
                            <li key={index}>
                              {item}
                            </li>
                          )
                        )}

                      </ul>

                    </div>

                  )}

                </div>
              )}

            </div>


            {/* DUPLICATE */}

            <div className="feature-card">

              <div className="feature-header">

                <div>

                  <h3>
                    Duplicate Complaint Detection
                  </h3>

                  <p>
                    Compare this complaint with existing QMS complaints.
                  </p>

                </div>

                <span className="ai-badge">
                  AI
                </span>

              </div>


              <button
                className="feature-button"
                onClick={
                  handleDuplicateCheck
                }
                disabled={
                  isLoading("duplicate")
                }
              >
                {isLoading("duplicate")
                  ? "Checking..."
                  : "Check for Duplicate"}
              </button>


              {duplicateResult && (
  <div className="feature-result">
    <strong>
      {duplicateResult.duplicate_found
        ? "Potential Duplicate Found"
        : "No Duplicate Found"}
    </strong>

    {duplicateResult.confidence && (
      <p>
        <strong>Confidence:</strong>{" "}
        {duplicateResult.confidence}
      </p>
    )}

    {duplicateResult.duplicate_found &&
      duplicateResult.matching_complaint_id && (
        <p>
          <strong>Matching Complaint ID:</strong>{" "}
          {duplicateResult.matching_complaint_id}
        </p>
      )}

    {duplicateResult.reason && (
      <p>
        <strong>Reason:</strong>{" "}
        {duplicateResult.reason}
      </p>
    )}

    {duplicateResult.recommendation && (
      <p>
        <strong>Recommendation:</strong>{" "}
        {duplicateResult.recommendation}
      </p>
    )}
  </div>
)}

</div>


            {/* CAPA */}

            <div className="feature-card">

              <div className="feature-header">

                <div>

                  <h3>
                    AI CAPA Recommendation
                  </h3>

                  <p>
                    Recommended corrective and preventive actions for QA review.
                  </p>

                </div>

                <span className="ai-badge">
                  AI
                </span>

              </div>


              <button
                className="feature-button"
                onClick={
                  handleCAPA
                }
                disabled={
                  isLoading("capa")
                }
              >
                {isLoading("capa")
                  ? "Generating..."
                  : "Recommend CAPA"}
              </button>


              {capaResult && (
                <div className="feature-result">

                  {capaResult.summary && (
                    <p>
                      <strong>
                        Summary:
                      </strong>{" "}
                      {
                        capaResult.summary
                      }
                    </p>
                  )}


                  <div>

                    <strong>
                      Corrective Actions
                    </strong>

                    <ul>

                      {(
                        capaResult.corrective_actions ||
                        []
                      ).map(
                        (item, index) => (
                          <li key={index}>
                            {item}
                          </li>
                        )
                      )}

                    </ul>

                  </div>


                  <div>

                    <strong>
                      Preventive Actions
                    </strong>

                    <ul>

                      {(
                        capaResult.preventive_actions ||
                        []
                      ).map(
                        (item, index) => (
                          <li key={index}>
                            {item}
                          </li>
                        )
                      )}

                    </ul>

                  </div>


                  <div>

                    <strong>
                      QA Verification
                    </strong>

                    <ul>

                      {(
                        capaResult.qa_verification ||
                        []
                      ).map(
                        (item, index) => (
                          <li key={index}>
                            {item}
                          </li>
                        )
                      )}

                    </ul>

                  </div>


                  {capaResult.responsible_function && (
                    <p>
                      <strong>
                        Responsible Function:
                      </strong>{" "}
                      {
                        capaResult.responsible_function
                      }
                    </p>
                  )}

                </div>
              )}

            </div>


            {/* SUMMARY */}

            <div className="feature-card">

              <div className="feature-header">

                <div>

                  <h3>
                    AI Complaint Summary
                  </h3>

                  <p>
                    Generate a concise QA-ready complaint summary.
                  </p>

                </div>

                <span className="ai-badge">
                  AI
                </span>

              </div>


              <button
                className="feature-button"
                onClick={
                  handleSummary
                }
                disabled={
                  isLoading("summary")
                }
              >
                {isLoading("summary")
                  ? "Generating..."
                  : "Generate Complaint Summary"}
              </button>


              {summaryResult && (
                <div className="feature-result">

                  {summaryResult.summary && (
                    <div>

                      <strong>
                        Complaint Summary
                      </strong>

                      <p>
                        {
                          summaryResult.summary
                        }
                      </p>

                    </div>
                  )}


                  {summaryResult
                    .key_details
                    ?.length > 0 && (

                    <div>

                      <strong>
                        Key Details
                      </strong>

                      <ul>

                        {summaryResult.key_details.map(
                          (item, index) => (
                            <li key={index}>
                              {item}
                            </li>
                          )
                        )}

                      </ul>

                    </div>

                  )}


                  {summaryResult.risk_overview && (
                    <p>
                      <strong>
                        Risk Overview:
                      </strong>{" "}
                      {
                        summaryResult.risk_overview
                      }
                    </p>
                  )}


                  {summaryResult.recommended_action && (
                    <p>
                      <strong>
                        Recommended Action:
                      </strong>{" "}
                      {
                        summaryResult.recommended_action
                      }
                    </p>
                  )}

                </div>
              )}

            </div>


            {/* RISK CLASSIFICATION */}

            <div className="feature-card">

              <div className="feature-header">

                <div>

                  <h3>
                    AI Risk Classification
                  </h3>

                  <p>
                    Detailed AI classification of complaint risk.
                  </p>

                </div>

                <span className="ai-badge">
                  AI
                </span>

              </div>


              <button
                className="feature-button"
                onClick={
                  handleRiskClassification
                }
                disabled={
                  isLoading("risk")
                }
              >
                {isLoading("risk")
                  ? "Classifying..."
                  : "Classify Complaint Risk"}
              </button>


              {riskResult && (
                <div className="feature-result">

                  <div
                    className="risk-result-grid"
                  >

                    <div>
                      <strong>
                        Risk Level
                      </strong>

                      <p>
                        {
                          riskResult.risk_level
                        }
                      </p>
                    </div>


                    <div>
                      <strong>
                        Severity
                      </strong>

                      <p>
                        {
                          riskResult.severity
                        }
                      </p>
                    </div>


                    <div>
                      <strong>
                        Priority
                      </strong>

                      <p>
                        {
                          riskResult.priority
                        }
                      </p>
                    </div>

                  </div>


                  {riskResult
                    .risk_factors
                    ?.length > 0 && (

                    <div>

                      <strong>
                        Risk Factors
                      </strong>

                      <ul>

                        {riskResult.risk_factors.map(
                          (item, index) => (
                            <li key={index}>
                              {item}
                            </li>
                          )
                        )}

                      </ul>

                    </div>

                  )}


                  {riskResult.rationale && (
                    <p>
                      <strong>
                        Classification Rationale:
                      </strong>{" "}
                      {
                        riskResult.rationale
                      }
                    </p>
                  )}


                  {riskResult
                    .immediate_attention_required && (

                    <div className="attention-warning">

                      Immediate QA Attention Required

                    </div>

                  )}

                </div>
              )}

            </div>

          </div>


          {/* ==================================================
              FORM BUTTONS
          ================================================== */}

          <div className="button-row">

            <button
              className="reset-button"
              onClick={
                handleReset
              }
            >
              Reset Form
            </button>


            <button
              className="commit-button"
              onClick={
                handleCommit
              }
            >
              Commit to QMS Ledger
            </button>

          </div>

        </section>


        {/* ==================================================
            RIGHT SIDE - COPILOT
        ================================================== */}

        <aside className="copilot-panel">

          {/* COPILOT HEADER */}

          <div className="copilot-header">

            <div className="copilot-icon">
              ✦
            </div>

            <div>

              <h2>
                AIVOA Copilot
              </h2>

              <p>
                Powered by LangGraph
              </p>

            </div>

            <span className="online-status">
              Online
            </span>

          </div>


          <div className="copilot-body">

            {/* UPLOAD */}

            <div className="upload-box">

              <div className="upload-icon">
                ↑
              </div>

              <h3>
                Upload Complaint File
              </h3>

              <p>
                Upload a customer complaint PDF and let AI extract the complaint details.
              </p>


              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={
                  handlePdfUpload
                }
                style={{
                  display: "none",
                }}
              />


              <button
                className="upload-button"
                onClick={() =>
                  fileInputRef.current?.click()
                }
                disabled={
                  pdfLoading
                }
              >
                {pdfLoading
                  ? "Analyzing PDF..."
                  : "Choose PDF"}
              </button>

            </div>


            {/* TEXT INPUT */}

            <div className="text-input-box">

              <label>
                Or paste complaint text
              </label>

              <textarea
                rows="8"
                placeholder="Paste customer complaint, email or message here..."
                value={
                  complaintText
                }
                onChange={(e) =>
                  setComplaintText(
                    e.target.value
                  )
                }
              />


              <button
                className="analyze-button"
                onClick={
                  handleAnalyze
                }
                disabled={
                  loading
                }
              >
                {loading
                  ? "Analyzing..."
                  : "Analyze with AI"}
              </button>

            </div>


            {/* AI INFORMATION */}

            <div className="ai-welcome">

              <div className="ai-avatar">
                ✦
              </div>

              <div>

                <h3>
                  AI Complaint Intelligence
                </h3>

                <p>
                  Extracts complaint details, classifies severity, identifies risks and recommends the next action.
                </p>

              </div>

            </div>


            {/* CORRECTION */}

            <div className="correction-box">

              <div>

                <h3>
                  Correct the AI
                </h3>

                <p>
                  You can tell the Copilot to change any extracted field using natural language.
                </p>

              </div>


              <textarea
                rows="5"
                placeholder='Example: "Change batch number to BMX260712A and affected quantity to 30 kg."'
                value={
                  correctionText
                }
                onChange={(e) =>
                  setCorrectionText(
                    e.target.value
                  )
                }
              />


              <button
                className="correction-button"
                onClick={
                  handleCorrection
                }
                disabled={
                  correctionLoading
                }
              >
                {correctionLoading
                  ? "Applying..."
                  : "Apply AI Correction"}
              </button>

            </div>


            {/* AI STATUS */}

            {complaint.initial_severity && (
              <div className="ai-analysis-status">

                <strong>
                  AI Analysis Complete
                </strong>

                <p>

                  Severity:{" "}
                  <strong>
                    {
                      complaint.initial_severity
                    }
                  </strong>

                  {" • "}

                  Priority:{" "}
                  <strong>
                    {
                      complaint.priority
                    }
                  </strong>

                </p>

              </div>
            )}

          </div>


          {/* COPILOT FOOTER */}

          <div className="powered">
            Powered by LangGraph + Groq
          </div>

        </aside>

      </main>


      {/* ==================================================
          QMS LEDGER
      ================================================== */}

      <div id="qms-ledger">

        <ComplaintLedger />

      </div>


      {/* ==================================================
          FOOTER
      ================================================== */}

      <footer className="app-footer">

        <p>
          AIVOA AI-Powered Complaint Management System
        </p>

        <span>
          AI recommendations are for initial QA triage and must be reviewed by qualified personnel.
        </span>

      </footer>

    </div>
  );
}


export default App;