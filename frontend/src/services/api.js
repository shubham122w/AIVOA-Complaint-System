import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8001",
  headers: {
    "Content-Type": "application/json",
  },
});

// ==================================================
// ANALYZE COMPLAINT TEXT
// ==================================================

export const analyzeComplaint = async (text) => {
  const response = await api.post(
    "/complaints/parse",
    { text }
  );

  return response.data;
};


// ==================================================
// CORRECT COMPLAINT DATA
// ==================================================

export const correctComplaint = async (
  currentData,
  correctionText
) => {
  const response = await api.post(
    "/complaints/correct",
    {
      current_data: currentData,
      correction_text: correctionText,
    }
  );

  return response.data;
};


// ==================================================
// CREATE / COMMIT COMPLAINT
// ==================================================

export const createComplaint = async (
  complaintData
) => {
  const response = await api.post(
    "/complaints",
    complaintData
  );

  return response.data;
};


// ==================================================
// GET ALL COMPLAINTS
// ==================================================

export const getComplaints = async () => {
  const response = await api.get(
    "/complaints"
  );

  return response.data;
};


// ==================================================
// ANALYZE COMPLAINT PDF
// ==================================================

export const analyzeComplaintPdf = async (
  file
) => {
  const formData = new FormData();

  formData.append("file", file);

  const response = await api.post(
    "/complaints/parse-pdf",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};


// ==================================================
// COMPLETENESS CHECKER
// ==================================================

export const checkComplaintCompleteness =
  async (complaintData) => {

    const response = await api.post(
      "/complaints/check-completeness",
      {
        complaint_data: complaintData,
      }
    );

    return response.data;
  };


// ==================================================
// ROOT CAUSE RECOMMENDATION
// ==================================================

export const recommendRootCause = async (
  complaintData
) => {

  const response = await api.post(
    "/complaints/root-cause",
    {
      complaint_data: complaintData,
    }
  );

  return response.data;
};


// ==================================================
// DUPLICATE COMPLAINT DETECTION
// ==================================================

export const checkDuplicateComplaint = async (
  newComplaint,
  existingComplaints
) => {

  const response = await api.post(
    "/complaints/check-duplicate",
    {
      new_complaint: newComplaint,
      existing_complaints: existingComplaints,
    }
  );

  return response.data;
};


// ==================================================
// CAPA RECOMMENDATION
// ==================================================

export const recommendCAPA = async (
  complaintData
) => {

  const response = await api.post(
    "/complaints/capa",
    {
      complaint_data: complaintData,
    }
  );

  return response.data;
};


// ==================================================
// COMPLAINT SUMMARY
// ==================================================

export const generateComplaintSummary = async (
  complaintData
) => {

  const response = await api.post(
    "/complaints/summary",
    {
      complaint_data: complaintData,
    }
  );

  return response.data;
};


// ==================================================
// AI RISK CLASSIFICATION
// ==================================================

export const classifyComplaintRisk = async (
  complaintData
) => {

  const response = await api.post(
    "/complaints/risk-classification",
    {
      complaint_data: complaintData,
    }
  );

  return response.data;
};


// ==================================================
// DEFAULT API
// ==================================================

export default api;