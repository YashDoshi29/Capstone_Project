import React, { useState } from 'react';

function GrokSynthesizer() {
  // The server requires these EXACT keys:
  const [formData, setFormData] = useState({
    zipcode: '',
    age_group: '',
    family_type: '',
    earners: '',
    household_size: '',
    num_records: 1,
  });

  const [generatedData, setGeneratedData] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // For convenience, define possible categories (from your server model)
  const ageOptions = ['15-24', '25-44', '45-64', '65+'];
  const familyOptions = ['Married-couple families', 'Female householder', 'Male householder'];
  const earnerOptions = ['0', '1', '2', '3+'];
  const sizeOptions = ['2', '3', '4', '5', '6', '7+'];

  // Update a single form field
  const handleChange = (key, value) => {
    setFormData(prev => ({ ...prev, [key]: value }));
  };

  // Submit to FastAPI
  const handleGenerateData = async () => {
    // Validate that all fields are chosen
    const { zipcode, age_group, family_type, earners, household_size } = formData;
    if (!zipcode || !age_group || !family_type || !earners || !household_size) {
      alert("Please fill in all fields (zipcode, age_group, family_type, earners, household_size).");
      return;
    }

    setIsGenerating(true);

    try {
      // Example: calls the /generate_customer endpoint
      // Could also be /predict_customer_income if you prefer
      const response = await fetch("http://localhost:8000/generate_customer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const data = await response.json();
      // data may be a single object or a list. If your server returns a single dict, store it as is.
      // e.g. { "zipcode": "...", "predicted_income": 12345.67, ... }
      setGeneratedData(Array.isArray(data) ? data : [data]);
    } catch (error) {
      console.error("Error generating data:", error);
      alert("Failed to generate data. Check the API connection.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    if (!generatedData) return;
    const jsonString = JSON.stringify(generatedData, null, 2);
    const blob = new Blob([jsonString], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "synthetic_data.json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ maxWidth: 600, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h2>Data Synthesizer</h2>
      <p>Enter parameters to generate or predict income data:</p>

      {/* ZIPCODE */}
      <div style={{ marginBottom: 10 }}>
        <label style={{ display: 'block', marginBottom: 5 }}>Zipcode:</label>
        <input
          type="text"
          value={formData.zipcode}
          onChange={(e) => handleChange('zipcode', e.target.value)}
          placeholder="e.g. 20037"
          style={{ width: '100%', padding: 8 }}
        />
      </div>

      {/* AGE GROUP */}
      <div style={{ marginBottom: 10 }}>
        <label style={{ display: 'block', marginBottom: 5 }}>Age Group:</label>
        <select
          value={formData.age_group}
          onChange={(e) => handleChange('age_group', e.target.value)}
          style={{ width: '100%', padding: 8 }}
        >
          <option value="">--Select Age Group--</option>
          {ageOptions.map((opt) => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>
      </div>

      {/* FAMILY TYPE */}
      <div style={{ marginBottom: 10 }}>
        <label style={{ display: 'block', marginBottom: 5 }}>Family Type:</label>
        <select
          value={formData.family_type}
          onChange={(e) => handleChange('family_type', e.target.value)}
          style={{ width: '100%', padding: 8 }}
        >
          <option value="">--Select Family Type--</option>
          {familyOptions.map((opt) => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>
      </div>

      {/* EARNERS */}
      <div style={{ marginBottom: 10 }}>
        <label style={{ display: 'block', marginBottom: 5 }}>Number of Earners:</label>
        <select
          value={formData.earners}
          onChange={(e) => handleChange('earners', e.target.value)}
          style={{ width: '100%', padding: 8 }}
        >
          <option value="">--Select Earners--</option>
          {earnerOptions.map((opt) => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>
      </div>

      {/* HOUSEHOLD SIZE */}
      <div style={{ marginBottom: 10 }}>
        <label style={{ display: 'block', marginBottom: 5 }}>Household Size:</label>
        <select
          value={formData.household_size}
          onChange={(e) => handleChange('household_size', e.target.value)}
          style={{ width: '100%', padding: 8 }}
        >
          <option value="">--Select Size--</option>
          {sizeOptions.map((opt) => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>
      </div>

        {/* NUMBER OF RECORDS */}
<div style={{ marginBottom: 10 }}>
  <label style={{ display: 'block', marginBottom: 5 }}>Number of Records:</label>
  <input
    type="number"
    min="1"
    value={formData.num_records}
    onChange={(e) => handleChange('num_records', parseInt(e.target.value, 10) || 1)}
    style={{ width: '100%', padding: 8 }}
  />
</div>

      {/* Generate Button */}
      <button
        onClick={handleGenerateData}
        disabled={isGenerating}
        style={{
          backgroundColor: '#007bff',
          color: '#fff',
          border: 'none',
          padding: '10px 16px',
          cursor: 'pointer',
          borderRadius: 4
        }}
      >
        {isGenerating ? "Generating..." : "Generate Data_Synthesizer"}
      </button>

      {/* Results */}
      {generatedData && generatedData.length > 0 && (
        <div style={{ marginTop: 30 }}>
          <h3>Generated / Predicted Result</h3>
          <button
            onClick={handleDownload}
            style={{
              marginBottom: 10,
              backgroundColor: '#28a745',
              color: '#fff',
              border: 'none',
              padding: '8px 16px',
              cursor: 'pointer',
              borderRadius: 4
            }}
          >
            Download as JSON
          </button>

          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              marginBottom: 10
            }}
          >
            <thead style={{ backgroundColor: '#f0f0f0' }}>
              <tr>
                {Object.keys(generatedData[0]).map((col) => (
                  <th
                    key={col}
                    style={{
                      border: '1px solid #ccc',
                      padding: 8,
                      textAlign: 'left'
                    }}
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {generatedData.slice(0, 10).map((row, i) => (
                <tr key={i} style={{ backgroundColor: i % 2 === 0 ? '#fafafa' : '#fff' }}>
                  {Object.keys(row).map((col) => (
                    <td key={col} style={{ border: '1px solid #ccc', padding: 8 }}>
                      {String(row[col])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>

          <p>Records Shown: {Math.min(10, generatedData.length)} of {generatedData.length}</p>
        </div>
      )}
    </div>
  );
}

export default GrokSynthesizer;
