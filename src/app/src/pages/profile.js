import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
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
  Paper,
  Tabs,
  Tab,
  IconButton,
  InputAdornment,
  CircularProgress,
  Alert,
  Avatar,
  Container
} from '@mui/material';
import {
  Upload as UploadIcon,
  CloudUpload as CloudUploadIcon,
  Person as PersonIcon,
  AttachMoney as AttachMoneyIcon,
  Home as HomeIcon,
  LocationOn as LocationIcon,
  Male as MaleIcon,
  Female as FemaleIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
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
  const [file, setFile] = useState(null);
  

  const handleUpload = async () => {
    if (!file) return setError("Please select a file first.");
    if (file.type !== "application/pdf" && file.type !== "text/csv") {
      setError("Unsupported file type. Please upload a PDF or CSV only.");
      return;
    }
  
    setLoading(true);
    try {
      let transactions = [];
  
      if (file.type === "text/csv") {
        const csvText = await file.text();
        transactions = await parseCSV(csvText);
      } else if (file.type === "application/pdf") {
        const pdfText = await parsePDF(file);
        transactions = await parseCSV(pdfText);
      }
  
      const formattedTransactions = transactions.map((t) => ({
        Category: t.Category || "Unknown",
        Amount: parseFloat(t.Amount) || 0,
        "Transaction Date": new Date(t["Transaction Date"]).toLocaleDateString(),
      }));
  
      // Save formatted transactions to localStorage
      localStorage.setItem('transactions', JSON.stringify(formattedTransactions));
  
      // Optional: also prepare categorized spending for Pie Chart
      const categoryTotals = formattedTransactions.reduce((acc, transaction) => {
        acc[transaction.Category] = (acc[transaction.Category] || 0) + transaction.Amount;
        return acc;
      }, {});
      localStorage.setItem('categorizedSpending', JSON.stringify(categoryTotals));
  
      // You can navigate to Dashboard or show a success message if you want
      navigate('/dashboard');
  
    } catch (err) {
      console.error(err);
      setError("Failed to upload or parse file.");
    } finally {
      setLoading(false);
    }
  };
  

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
    setFile(e.target.files[0]);
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
      const response = await fetch("http://localhost:5050/upload", {
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
        background: "linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)",
        minHeight: '100vh',
        color: '#ffffff',
        py: 2,
        px: { xs: 2, md: 4 }
      }}
    >
      {/* Hero Section */}
      <Box
        sx={{
          minHeight: '30vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          px: { xs: 2, md: 4 },
          position: 'relative',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'radial-gradient(circle at center, rgba(255, 255, 255, 0.1) 0%, transparent 70%)',
            pointerEvents: 'none',
          }
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center' }}>
            <Typography
              variant="h1"
              sx={{
                fontWeight: 'bold',
                color: '#ffffff',
                fontSize: { xs: '2.5rem', md: '3.5rem' },
                mb: 2,
                lineHeight: 1.2,
                textShadow: '0px 0px 10px rgba(255, 255, 255, 0.3)',
              }}
            >
              Financial Data Management
            </Typography>
            <Typography
              variant="h5"
              sx={{
                color: '#b3b3b3',
                mb: 2,
                lineHeight: 1.6,
                fontSize: { xs: '1.1rem', md: '1.3rem' },
              }}
            >
              Upload your financial statements or generate synthetic data to get started with personalized financial insights and recommendations.
            </Typography>
          </Box>
        </Container>
      </Box>

      {/* Main Content */}
      <Box sx={{ maxWidth: '1200px', mx: 'auto', mt: -4 }}>
        <Grid container spacing={3}>
          {/* Left Side - User Info */}
          <Grid item xs={12} md={4}>
            <Card 
              sx={{ 
                p: 2, 
                background: 'rgba(26, 26, 26, 0.8)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '20px',
                height: '100%',
                boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.3)'
              }}
            >
              <Box sx={{ textAlign: 'center', mb: 2 }}>
                <Avatar
                  sx={{ 
                    width: 80, 
                    height: 80, 
                    mx: 'auto',
                    mb: 1,
                    background: 'linear-gradient(45deg, rgba(255, 255, 255, 0.9) 30%, rgba(255, 255, 255, 0.7) 90%)',
                    color: '#1a1a1a'
                  }}
                >
                  <PersonIcon sx={{ fontSize: 40 }} />
                </Avatar>
                <Typography variant="h6" sx={{ mb: 1, color: '#ffffff' }}>
                  User Profile
                </Typography>
                <Typography variant="body2" sx={{ color: '#b3b3b3' }}>
                  Manage your personal information
                </Typography>
              </Box>

              <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
                <TextField
                  fullWidth
                  label="Age"
                  name="age"
                  value={userData.age}
                  onChange={handleInputChange}
                  sx={{ mb: 2 }}
                  InputLabelProps={{ style: { color: '#ffffff' } }}
                  InputProps={{
                    style: { color: '#ffffff' },
                    startAdornment: (
                      <InputAdornment position="start">
                        <PersonIcon sx={{ color: '#b3b3b3' }} />
                      </InputAdornment>
                    ),
                  }}
                />
                <TextField
                  fullWidth
                  label="Gender"
                  name="gender"
                  value={userData.gender}
                  onChange={handleInputChange}
                  sx={{ mb: 2 }}
                  InputLabelProps={{ style: { color: '#ffffff' } }}
                  InputProps={{
                    style: { color: '#ffffff' },
                    startAdornment: (
                      <InputAdornment position="start">
                        {userData.gender === 'male' ? (
                          <MaleIcon sx={{ color: '#b3b3b3' }} />
                        ) : (
                          <FemaleIcon sx={{ color: '#b3b3b3' }} />
                        )}
                      </InputAdornment>
                    ),
                  }}
                />
                <TextField
                  fullWidth
                  label="Household Size"
                  name="householdSize"
                  value={userData.householdSize}
                  onChange={handleInputChange}
                  sx={{ mb: 2 }}
                  InputLabelProps={{ style: { color: '#ffffff' } }}
                  InputProps={{
                    style: { color: '#ffffff' },
                    startAdornment: (
                      <InputAdornment position="start">
                        <HomeIcon sx={{ color: '#b3b3b3' }} />
                      </InputAdornment>
                    ),
                  }}
                />
                <TextField
                  fullWidth
                  label="Annual Income"
                  name="annualIncome"
                  value={userData.annualIncome}
                  onChange={handleInputChange}
                  sx={{ mb: 2 }}
                  InputLabelProps={{ style: { color: '#ffffff' } }}
                  InputProps={{
                    style: { color: '#ffffff' },
                    startAdornment: (
                      <InputAdornment position="start">
                        <AttachMoneyIcon sx={{ color: '#b3b3b3' }} />
                      </InputAdornment>
                    ),
                  }}
                />
                <TextField
                  fullWidth
                  label="Zipcode"
                  name="zipcode"
                  value={userData.zipcode}
                  onChange={handleInputChange}
                  InputLabelProps={{ style: { color: '#ffffff' } }}
                  InputProps={{
                    style: { color: '#ffffff' },
                    startAdornment: (
                      <InputAdornment position="start">
                        <LocationIcon sx={{ color: '#b3b3b3' }} />
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>
            </Card>
          </Grid>

          {/* Right Side - Data Management */}
          <Grid item xs={12} md={8}>
            <Card 
              sx={{ 
                p: 2, 
                background: 'rgba(26, 26, 26, 0.8)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '20px',
                boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.3)'
              }}
            >
              <Tabs
                value={mode}
                onChange={(e, newValue) => handleModeChange(newValue)}
                sx={{ 
                  mb: 3,
                  '& .MuiTab-root': {
                    color: '#b3b3b3',
                    '&.Mui-selected': {
                      color: '#ffffff',
                    },
                  },
                }}
              >
                <Tab 
                  value="upload" 
                  label="Upload Statement" 
                  icon={<UploadIcon />} 
                  iconPosition="start"
                />
                <Tab 
                  value="generate" 
                  label="Generate Data" 
                  icon={<CloudUploadIcon />} 
                  iconPosition="start"
                />
              </Tabs>

              {error && (
                <Alert severity="error" sx={{ mb: 3, color: '#ffffff' }}>
                  {error}
                </Alert>
              )}

              {mode === 'upload' ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <input
                    accept=".csv,.pdf"
                    style={{ display: 'none' }}
                    id="raised-button-file"
                    type="file"
                    onChange={handleFileChange}
                  />
                  
                  <label htmlFor="raised-button-file">
                    <Button
                                          variant="contained"
                                          component="span"
                                          sx={{
                                            background: "linear-gradient(45deg, rgba(255, 255, 255, 0.9) 30%, rgba(255, 255, 255, 0.7) 90%)",
                                            color: "#1a1a1a",
                                            padding: "10px 22px",
                                            borderRadius: "10px",
                                            fontWeight: "600",
                                            textTransform: "uppercase",
                                            boxShadow: "0 4px 12px rgba(255, 255, 255, 0.2)",
                                            "&:hover": {
                                              background: "linear-gradient(45deg, rgba(255, 255, 255, 0.7) 30%, rgba(255, 255, 255, 0.9) 90%)",
                                              boxShadow: "0 6px 16px rgba(255, 255, 255, 0.3)",
                                            },
                                          }}
                                        >
                                          📁 Choose File
                                        </Button>
                    <Button
                                        onClick={handleUpload}
                                        disabled={loading}
                                        sx={{
                                          background: "linear-gradient(45deg, rgba(255, 255, 255, 0.9) 30%, rgba(255, 255, 255, 0.7) 90%)",
                                          color: "#1a1a1a",
                                          padding: "10px 22px",
                                          borderRadius: "10px",
                                          fontWeight: "600",
                                          textTransform: "uppercase",
                                          boxShadow: "0 4px 12px rgba(255, 255, 255, 0.2)",
                                          "&:hover": {
                                            background: "linear-gradient(45deg, rgba(255, 255, 255, 0.7) 30%, rgba(255, 255, 255, 0.9) 90%)",
                                            boxShadow: "0 6px 16px rgba(255, 255, 255, 0.3)",
                                          },
                                        }}
                                      >
                                        {loading ? "Uploading..." : "Upload"}
                                      </Button>
                  </label>
                  {selectedFile && (
                    <Typography variant="body2" sx={{ mt: 2, color: '#b3b3b3' }}>
                      Selected: {selectedFile.name}
                    </Typography>
                  )}
                </Box>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Button
                    variant="contained"
                    onClick={handleSubmit}
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
                    sx={{
                      background: 'linear-gradient(45deg, rgba(255, 255, 255, 0.9) 30%, rgba(255, 255, 255, 0.7) 90%)',
                      color: '#1a1a1a',
                      boxShadow: '0 3px 5px 2px rgba(255, 255, 255, .2)',
                      '&:hover': {
                        background: 'linear-gradient(45deg, rgba(255, 255, 255, 0.7) 30%, rgba(255, 255, 255, 0.9) 90%)',
                      },
                      '&.Mui-disabled': {
                        background: 'rgba(255, 255, 255, 0.12)',
                      },
                    }}
                  >
                    {loading ? 'Generating...' : 'Generate Data'}
                  </Button>
                </Box>
              )}

              {transactions.length > 0 && (
                <TableContainer component={Paper} sx={{ mt: 3, background: 'rgba(26, 26, 26, 0.8)' }}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ color: '#ffffff' }}>Category</TableCell>
                        <TableCell align="right" sx={{ color: '#ffffff' }}>Amount</TableCell>
                        <TableCell align="right" sx={{ color: '#ffffff' }}>Date</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {transactions.map((transaction, index) => (
                        <TableRow key={index}>
                          <TableCell sx={{ color: '#b3b3b3' }}>{transaction.Category}</TableCell>
                          <TableCell align="right" sx={{ color: '#b3b3b3' }}>${transaction.Amount.toFixed(2)}</TableCell>
                          <TableCell align="right" sx={{ color: '#b3b3b3' }}>{transaction['Transaction Date']}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default Profile;
