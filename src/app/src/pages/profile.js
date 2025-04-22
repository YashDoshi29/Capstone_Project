import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  AppBar,
  Toolbar,
  Button,
  Card,
  Grid,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
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

  // Switch between "Upload Statement" and "Generate Data" modes
  const handleModeChange = (newMode) => {
    setMode(newMode);
    setTransactions([]);
    setError('');
  };

  // Handle text input changes (age, gender, etc.)
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setUserData((prev) => ({ ...prev, [name]: value }));
  };

  // Store the selected file in local state
  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setError('');
  };

  // Helper to parse CSV text
  const parseCSV = (csvData) => {
    return new Promise((resolve, reject) => {
      Papa.parse(csvData, {
        header: true,
        skipEmptyLines: true,
        complete: (result) => {
          // Check for parsing errors
          if (result.errors && result.errors.length > 0) {
            reject(result.errors[0]);
          } else {
            resolve(result.data);
          }
        },
        error: (error) => reject(error),
      });
    });
  };

  // Upload PDF to server and get text returned
  const parsePDF = async (pdfFile) => {
    const formData = new FormData();
    formData.append("file", pdfFile);

    // Adjust this URL to match your actual PDF-upload endpoint
    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error("Error uploading PDF.");

      // Expecting the server to return raw CSV text after parsing the PDF
      return await response.text();
    } catch (error) {
      throw error;
    }
  };

  // Submit handler for both "upload" and "generate"
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (mode === 'upload') {
      // Make sure we have a file
      if (!selectedFile) {
        setError("Please select a file first.");
        return;
      }

      setLoading(true);
      try {
        let formattedTransactions = [];

        // Handle CSV
        if (selectedFile.type === "text/csv") {
          const csvText = await selectedFile.text();
          const parsed = await parseCSV(csvText);
          formattedTransactions = parsed.map((t) => ({
            Category: t.Category || "Unknown",
            Amount: parseFloat(t.Amount) || 0,
            "Transaction Date": new Date(t["Transaction Date"]).toLocaleDateString(),
          }));
        }
        // Handle PDF
        else if (selectedFile.type === "application/pdf") {
          const pdfText = await parsePDF(selectedFile);
          const parsed = await parseCSV(pdfText);
          formattedTransactions = parsed.map((t) => ({
            Category: t.Category || "Unknown",
            Amount: parseFloat(t.Amount) || 0,
            "Transaction Date": new Date(t["Transaction Date"]).toLocaleDateString(),
          }));
        } else {
          throw new Error("Unsupported file type. Please upload CSV or PDF.");
        }

        // Optionally store in localStorage for use in /dashboard
        localStorage.setItem('transactions', JSON.stringify(formattedTransactions));

        // If you also want to show them right here, uncomment:
        // setTransactions(formattedTransactions);

        // Navigate to the dashboard (or wherever you want them displayed)
        navigate('/dashboard');
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    } else if (mode === 'generate') {
      // Validate the user form fields
      const { age, gender, householdSize, annualIncome, zipcode } = userData;
      if (!age || !gender || !householdSize || !annualIncome || !zipcode) {
        setError("Please fill in all fields.");
        return;
      }

      setLoading(true);
      try {
        // Adjust the URL to your actual data-generation endpoint
        const response = await fetch("http://localhost:8000/generate", {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            age: Number(age),
            gender,
            household_size: Number(householdSize),
            income: Number(annualIncome),
            zipcode
          }),
        });

        if (!response.ok) throw new Error("Network response was not ok");

        const data = await response.json();
        const newTransactions = data.transactions || data;

        if (Array.isArray(newTransactions)) {
          setTransactions(newTransactions);
          setError('');
        } else {
          throw new Error("Invalid data format received from server");
        }
      } catch (err) {
        setError(err.message);
        console.error("Error generating data:", err);
      } finally {
        setLoading(false);
      }
    }
  };

  // Reset the generated transaction list and clear inputs
  const handleReset = () => {
    setTransactions([]);
    setUserData({
      age: '',
      gender: '',
      householdSize: '',
      annualIncome: '',
      zipcode: '',
    });
  };

  // Navigation items
  const navItems = [
    { name: 'ClassifyBot 💡', path: '/dashboard' },
    { name: 'Optimization', path: '/optimization' },
    { name: 'Investment', path: '/investment' },
    { name: 'Profile', path: '/profile' },
    { name: 'News', path: '/FinancialNews' },
    { name: 'Logout', path: '/' }
  ];

  return (
    <Box
      sx={{
        background: "radial-gradient(circle, #0f0f0f, #1c1c1c, #2f2f2f)",
        minHeight: '100vh',
        color: 'white'
      }}
    >
      {/* App Bar */}
      <AppBar position="fixed" sx={{ backgroundColor: 'transparent', boxShadow: 'none' }}>
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            Financial Assistant
          </Typography>
          <Box>
            {navItems.map((item) => (
              <Button
                key={item.name}
                component="a"
                href={item.path}
                // For a smoother SPA experience, consider using "Link" from react-router-dom instead of "a"
                sx={{
                  color: 'white',
                  '&:hover': {
                    color: '#00c6ff'
                  }
                }}
              >
                {item.name}
              </Button>
            ))}
          </Box>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Box sx={{ pt: 12, px: 4, textAlign: 'center' }}>
        <Typography variant="h3" sx={{ mb: 4, fontWeight: 700, color: '#FFB07C' }}>
          TransactIQ
        </Typography>

        {/* Mode Toggle Buttons */}
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 4, mb: 6 }}>
          <Button
            variant={mode === 'upload' ? 'contained' : 'outlined'}
            onClick={() => handleModeChange('upload')}
            sx={{
              px: 6,
              py: 2,
              borderRadius: 2,
              background: mode === 'upload'
                ? 'linear-gradient(135deg, #00c6ff, #0072ff)'
                : 'transparent',
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
              background: mode === 'generate'
                ? 'linear-gradient(135deg, #6a5acd, #4f9df7)'
                : 'transparent',
              color: mode === 'generate' ? 'white' : '#6a5acd',
            }}
          >
            Generate Data
          </Button>
        </Box>

        {/* Content Card */}
        <Card sx={{ maxWidth: 800, mx: 'auto', p: 4, background: '#2f2f2f' }}>
          <form onSubmit={handleSubmit}>
            {mode === 'upload' ? (
              // Upload Statement Section
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
                {error && (
                  <Typography color="error" sx={{ mb: 2 }}>
                    {error}
                  </Typography>
                )}
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
              // Generate Data Form
              <Grid container spacing={3}>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    label="Age"
                    name="age"
                    type="number"
                    value={userData.age}
                    onChange={handleInputChange}
                    variant="filled"
                    InputLabelProps={{ style: { color: '#fff' } }}
                    InputProps={{ style: { color: '#fff' } }}
                    sx={{ background: '#3a3a3a', borderRadius: 1 }}
                  />
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    label="Gender"
                    name="gender"
                    value={userData.gender}
                    onChange={handleInputChange}
                    variant="filled"
                    InputLabelProps={{ style: { color: '#fff' } }}
                    InputProps={{ style: { color: '#fff' } }}
                    sx={{ background: '#3a3a3a', borderRadius: 1 }}
                  />
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    label="Household Size"
                    name="householdSize"
                    type="number"
                    value={userData.householdSize}
                    onChange={handleInputChange}
                    variant="filled"
                    InputLabelProps={{ style: { color: '#fff' } }}
                    InputProps={{ style: { color: '#fff' } }}
                    sx={{ background: '#3a3a3a', borderRadius: 1 }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Annual Income"
                    name="annualIncome"
                    type="number"
                    value={userData.annualIncome}
                    onChange={handleInputChange}
                    variant="filled"
                    InputLabelProps={{ style: { color: '#fff' } }}
                    InputProps={{ style: { color: '#fff' } }}
                    sx={{ background: '#3a3a3a', borderRadius: 1 }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Zipcode"
                    name="zipcode"
                    value={userData.zipcode}
                    onChange={handleInputChange}
                    variant="filled"
                    InputLabelProps={{ style: { color: '#fff' } }}
                    InputProps={{ style: { color: '#fff' } }}
                    sx={{ background: '#3a3a3a', borderRadius: 1 }}
                  />
                </Grid>
                {error && (
                  <Grid item xs={12}>
                    <Typography color="error">{error}</Typography>
                  </Grid>
                )}
                <Grid item xs={12}>
                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    disabled={loading}
                    sx={{
                      mt: 2,
                      py: 2,
                      background: 'linear-gradient(135deg, #6a5acd, #4f9df7)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #7a6aff, #3a8dff)'
                      }
                    }}
                  >
                    {loading ? 'Generating...' : 'Generate Data'}
                  </Button>
                </Grid>
              </Grid>
            )}
          </form>

          {/* If transactions were generated (mode === 'generate'), display them */}
          {transactions.length > 0 && (
            <Box sx={{ mt: 4 }}>
              <Typography variant="h6" sx={{ mb: 2, color: '#FFB07C' }}>
                Generated Transactions
              </Typography>
              <TableContainer component={Paper} sx={{ background: '#2f2f2f' }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      {Object.keys(transactions[0]).map((key) => (
                        <TableCell key={key} sx={{ color: '#fff !important' }}>
                          {key}
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {transactions.map((transaction, index) => (
                      <TableRow key={index}>
                        {Object.values(transaction).map((value, i) => (
                          <TableCell key={i} sx={{ color: '#ccc !important' }}>
                            {typeof value === 'object' ? JSON.stringify(value) : value}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              {/* Action Buttons after data is generated */}
              <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'center' }}>
                <Button
                  onClick={handleReset}
                  variant="outlined"
                  sx={{ color: '#00c6ff', borderColor: '#00c6ff' }}
                >
                  Generate Again
                </Button>
                <Button
                  onClick={() => navigate('/dashboard')}
                  variant="contained"
                  sx={{
                    background: '#00c6ff',
                    '&:hover': { background: '#33d1ff' }
                  }}
                >
                  Classify Transactions
                </Button>
              </Box>
            </Box>
          )}
        </Card>
      </Box>
    </Box>
  );
};

export default Profile;
