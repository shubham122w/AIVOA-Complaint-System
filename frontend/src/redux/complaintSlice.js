import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  complaint_source: "",
  customer_name: "",
  product_name: "",
  product_strength: "",
  batch_number: "",
  manufacturing_date: "",
  expiry_date: "",
  quantity_affected: "",
  originating_site: "",
  block_impacted: "",
  npm: "",
  complaint_type: "",
  detailed_description: "",
  initial_severity: "",
  suggested_next_action: "",
  initial_risk_assessment: "",
  priority: "",
};

const complaintSlice = createSlice({
  name: "complaint",
  initialState,
  reducers: {
    setComplaint: (state, action) => {
      return { ...state, ...action.payload };
    },

    updateField: (state, action) => {
      const { field, value } = action.payload;
      state[field] = value;
    },

    resetComplaint: () => {
      return initialState;
    },
  },
});

export const {
  setComplaint,
  updateField,
  resetComplaint,
} = complaintSlice.actions;

export default complaintSlice.reducer;