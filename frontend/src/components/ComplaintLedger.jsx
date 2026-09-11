import { useEffect, useState } from "react";
import { getComplaints } from "../services/api";

function ComplaintLedger() {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadComplaints = async () => {
    try {
      setLoading(true);

      const data = await getComplaints();

      setComplaints(data);
    } catch (error) {
      console.error("Failed to load complaints:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadComplaints();
  }, []);

  return (
    <div style={{ padding: "30px" }}>

      <h2>QMS Complaint Ledger</h2>

      <p>
        All complaints committed to the QMS database
      </p>

      {loading ? (
        <p>Loading complaints...</p>
      ) : complaints.length === 0 ? (
        <p>No complaints found.</p>
      ) : (
        <div style={{ overflowX: "auto" }}>

          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              marginTop: "20px",
            }}
          >

            <thead>
              <tr>
                <th style={cellStyle}>ID</th>
                <th style={cellStyle}>Customer</th>
                <th style={cellStyle}>Product</th>
                <th style={cellStyle}>Batch</th>
                <th style={cellStyle}>Severity</th>
                <th style={cellStyle}>Priority</th>
                <th style={cellStyle}>Complaint Type</th>
              </tr>
            </thead>

            <tbody>

              {complaints.map((item) => (
                <tr key={item.id}>

                  <td style={cellStyle}>
                    {item.id}
                  </td>

                  <td style={cellStyle}>
                    {item.customer_name}
                  </td>

                  <td style={cellStyle}>
                    {item.product_name}
                  </td>

                  <td style={cellStyle}>
                    {item.batch_number}
                  </td>

                  <td style={cellStyle}>
                    {item.initial_severity}
                  </td>

                  <td style={cellStyle}>
                    {item.priority}
                  </td>

                  <td style={cellStyle}>
                    {item.complaint_type}
                  </td>

                </tr>
              ))}

            </tbody>

          </table>

        </div>
      )}

      <button
        onClick={loadComplaints}
        style={{
          marginTop: "20px",
          padding: "10px 18px",
          cursor: "pointer",
        }}
      >
        Refresh Ledger
      </button>

    </div>
  );
}

const cellStyle = {
  border: "1px solid #ddd",
  padding: "12px",
  textAlign: "left",
};

export default ComplaintLedger;