import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, AppBar, Toolbar, Button, Card, CardContent } from '@mui/material';
import Papa from 'papaparse';

const Profile = () => {
  const navigate = useNavigate();
  const [mode, setMode] = useState('upload');
  const [userData, setUserData] = useState({
    age: '',
    gender: '',
    householdSize: '',
    annualIncome: '',
    zipcode: '',
  });
  const [selectedFile, setSelectedFile] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleModeChange = (newMode) => {
    setMode(newMode);
    setTransactions([]);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setUserData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const parseCSV = (csvData) => {
    return new Promise((resolve, reject) => {
      Papa.parse(csvData, {
        header: true,
        skipEmptyLines: true,
        complete: (result) => resolve(result.data),
        error: (error) => reject(error),
      });
    });
  };

  const parsePDF = async (pdfFile) => {
    const formData = new FormData();
    formData.append("file", pdfFile);

    try {
      const response = await fetch("http://127.0.0.1:5050/upload", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error("Error uploading PDF.");
      return await response.text();
    } catch (error) {
      throw error;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (mode === 'upload') {
      if (!selectedFile) {
        setError("Please select a file first.");
        return;
      }

      setLoading(true);
      setError('');

      try {
        let formattedTransactions = [];
        if (selectedFile.type === "text/csv") {
          const csvText = await selectedFile.text();
          const parsed = await parseCSV(csvText);
          formattedTransactions = parsed.map(t => ({
            Category: t.Category || "Unknown",
            Amount: parseFloat(t.Amount) || 0,
            "Transaction Date": new Date(t["Transaction Date"]).toLocaleDateString(),
          }));
        } else if (selectedFile.type === "application/pdf") {
          const pdfText = await parsePDF(selectedFile);
          const parsed = await parseCSV(pdfText);
          formattedTransactions = parsed.map(t => ({
            Category: t.Category || "Unknown",
            Amount: parseFloat(t.Amount) || 0,
            "Transaction Date": new Date(t["Transaction Date"]).toLocaleDateString(),
          }));
        }

        localStorage.setItem('transactions', JSON.stringify(formattedTransactions));
        navigate('/dashboard');
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    } else {
      // Existing generate functionality
      // ... (keep the original generate code)
    }
  };

  const navItems = [
    { name: 'ClassifyBot 💡', path: '/dashboard' },
    { name: 'Optimization', path: '/optimization' },
    { name: 'Investment', path: '/investment' },
    { name: 'Profile', path: '/profile' },
    { name: 'News', path: '/FinancialNews' },
    { name: 'Logout', path: '/' }
  ];

  return (
    <Box sx={{
      background: "radial-gradient(circle, #0f0f0f, #1c1c1c, #2f2f2f)",
      minHeight: '100vh',
      color: 'white'
    }}>
      <AppBar position="fixed" sx={{ backgroundColor: 'transparent', boxShadow: 'none' }}>
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            Financial Assistant
          </Typography>
          <Box>
            {navItems.map((item) => (
              <Button
                key={item.name}
                component={Link}
                to={item.path}
                sx={{ color: 'white' }}
              >
                {item.name}
              </Button>
            ))}
          </Box>
        </Toolbar>
      </AppBar>

      <Box sx={{ pt: 12, px: 4, textAlign: 'center' }}>
        <Typography variant="h3" sx={{ mb: 4, fontWeight: 700, color: '#FFB07C' }}>
          TransactIQ
        </Typography>

        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 4, mb: 6 }}>
          <Button
            variant={mode === 'upload' ? 'contained' : 'outlined'}
            onClick={() => handleModeChange('upload')}
            sx={{
              px: 6,
              py: 2,
              borderRadius: 2,
              background: mode === 'upload' ? 'linear-gradient(135deg, #00c6ff, #0072ff)' : 'transparent',
              color: mode === 'upload' ? 'white' : '#00c6ff',
            }}
          >
            Upload Statement
          </Button>
          <Button
            variant={mode === 'generate' ? 'contained' : 'outlined'}
            onClick={() => handleModeChange('generate')}
            sx={{
              px: 6,
              py: 2,
              borderRadius: 2,
              background: mode === 'generate' ? 'linear-gradient(135deg, #6a5acd, #4f9df7)' : 'transparent',
              color: mode === 'generate' ? 'white' : '#6a5acd',
            }}
          >
            Generate Data
          </Button>
        </Box>

        <Card sx={{ maxWidth: 600, mx: 'auto', p: 4, background: '#2f2f2f' }}>
          <form onSubmit={handleSubmit}>
            {mode === 'upload' ? (
              <Box sx={{ textAlign: 'center' }}>
                <label htmlFor="file-upload">
                  <input
                    id="file-upload"
                    type="file"
                    accept=".csv,.pdf"
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                  />
                  <Button
                    component="span"
                    variant="contained"
                    sx={{
                      background: 'linear-gradient(135deg, #e0cfc1, #c2b4a3)',
                      color: '#1a1a1a',
                      mb: 2,
                      px: 4,
                      py: 2
                    }}
                  >
                    📁 Choose File
                  </Button>
                </label>
                {selectedFile && (
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 2 }}>
                    Selected: {selectedFile.name}
                  </Typography>
                )}
                {error && <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>}
                <Button
                  type="submit"
                  variant="contained"
                  disabled={loading || !selectedFile}
                  sx={{
                    background: 'linear-gradient(135deg, #a6e3e9, #71c9ce)',
                    color: '#1a1a1a',
                    px: 6,
                    py: 2,
                    width: '100%'
                  }}
                >
                  {loading ? 'Processing...' : 'Upload & Analyze'}
                </Button>
              </Box>
            ) : (
              /* Generate form fields (keep existing) */
            )}
          </form>
        </Card>
      </Box>
    </Box>
  );
};

export default Profile;