import React, { useState } from 'react';

const Profile = () => {
  const [mode, setMode] = useState('upload'); // 'upload' or 'generate'
  const [userData, setUserData] = useState({
    age: '',
    gender: '',
    householdSize: '',
    annualIncome: '',
  });
  const [selectedFile, setSelectedFile] = useState(null);

  // Handle switching between modes
  const handleModeChange = (newMode) => {
    setMode(newMode);
  };

  // Update form field values
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setUserData(prev => ({ ...prev, [name]: value }));
  };

  // Handle file selection for upload mode
  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  // Handle form submission for either mode
  const handleSubmit = (e) => {
    e.preventDefault();
    if (mode === 'generate') {
      const { age, gender, householdSize, annualIncome } = userData;
      if (!age || !gender || !householdSize || !annualIncome) {
        alert("Please fill in all fields.");
        return;
      }
      alert(`Generating transaction data using:
Age: ${age}, Gender: ${gender}, Household Size: ${householdSize}, Annual Income: ${annualIncome}`);
    } else if (mode === 'upload') {
      if (!selectedFile) {
        alert("Please select a file to upload.");
        return;
      }
      alert(`Uploading file: ${selectedFile.name}`);
    }
  };

  // Inline styling for a dark theme with white accents
  const containerStyle = {
    backgroundColor: '#000',
    color: '#fff',
    minHeight: '100vh',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  };

  const heroStyle = {
    textAlign: 'center',
    marginBottom: '40px',
  };

  const buttonStyle = {
    padding: '10px 20px',
    margin: '10px',
    border: 'none',
    cursor: 'pointer',
    fontSize: '16px',
  };

  const activeButtonStyle = {
    ...buttonStyle,
    backgroundColor: '#fff',
    color: '#000',
  };

  const inactiveButtonStyle = {
    ...buttonStyle,
    backgroundColor: '#333',
    color: '#fff',
  };

  const formStyle = {
    maxWidth: '400px',
    margin: '0 auto',
  };

  const inputStyle = {
    width: '100%',
    padding: '10px',
    margin: '10px 0',
    backgroundColor: '#222',
    border: '1px solid #555',
    color: '#fff',
  };

  const submitButtonStyle = {
    ...buttonStyle,
    width: '100%',
    backgroundColor: '#fff',
    color: '#000',
  };

  return (
    <div style={containerStyle}>
      {/* Hero Section */}
      <div style={heroStyle}>
        <h1>FinCOAI</h1>
        <p>Generate personalized transaction data for financial analysis, optimization, and investment planning.</p>
      </div>

      {/* Mode Selection */}
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <button
          style={mode === 'upload' ? activeButtonStyle : inactiveButtonStyle}
          onClick={() => handleModeChange('upload')}
        >
          Upload Transaction Statement
        </button>
        <button
          style={mode === 'generate' ? activeButtonStyle : inactiveButtonStyle}
          onClick={() => handleModeChange('generate')}
        >
          Generate Transaction Data
        </button>
      </div>

      {/* Form Section */}
      <form onSubmit={handleSubmit} style={formStyle}>
        {mode === 'upload' ? (
          <div style={{ textAlign: 'center' }}>
            <input type="file" onChange={handleFileChange} style={{ color: '#fff' }} />
          </div>
        ) : (
          <>
            <input
              type="number"
              name="age"
              placeholder="Age"
              value={userData.age}
              onChange={handleInputChange}
              style={inputStyle}
            />
            <input
              type="text"
              name="gender"
              placeholder="Gender"
              value={userData.gender}
              onChange={handleInputChange}
              style={inputStyle}
            />
            <input
              type="number"
              name="householdSize"
              placeholder="Household Size"
              value={userData.householdSize}
              onChange={handleInputChange}
              style={inputStyle}
            />
            <input
              type="number"
              name="annualIncome"
              placeholder="Annual Income"
              value={userData.annualIncome}
              onChange={handleInputChange}
              style={inputStyle}
            />
          </>
        )}
        <button type="submit" style={submitButtonStyle}>
          {mode === 'upload' ? 'Upload File' : 'Generate Data'}
        </button>
      </form>
    </div>
  );
};

export default Profile;
