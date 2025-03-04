import React, { useState, useEffect } from "react";
import { Box, Typography, AppBar, Toolbar, Button, Grid, Card, CardContent } from "@mui/material";
import { Link } from "react-router-dom";
import { useSpring, animated } from "@react-spring/web";
import { Fade } from "react-awesome-reveal";
import { PieChart, Pie, Cell, Legend } from "recharts";
import Papa from "papaparse";

const COLORS = ["#FF6384", "#36A2EB", "#FFCE56", "#4CAF50", "#9C27B0", "#FF9800"];

const Dashboard = () => {
  const heroAnimation = useSpring({
    from: { opacity: 0, transform: "translateY(-20px)" },
    to: { opacity: 1, transform: "translateY(0)" },
    config: { duration: 1000 },
  });

  const [file, setFile] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const savedTransactions = localStorage.getItem("transactions");
    if (savedTransactions) {
      setTransactions(JSON.parse(savedTransactions));
    }
  }, []);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
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
    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", pdfFile);

    try {
      const response = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Error uploading PDF.");
      }

      const pdfText = await response.text();
      const parsedTransactions = await parseCSV(pdfText);

      const formattedTransactions = formatTransactions(parsedTransactions);
      saveTransactions(formattedTransactions);
    } catch (error) {
      console.error("Error processing file:", error);
      setError("Error processing file: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const formatTransactions = (parsedTransactions) => {
    return parsedTransactions.map((transaction) => ({
      Category: transaction.Category || "Unknown",
      Amount: parseFloat(transaction.Amount) || 0,
      "Transaction Date": new Date(transaction["Transaction Date"]).toLocaleDateString(),
      "Posting Date": new Date(transaction["Posting Date"]).toLocaleDateString(),
    }));
  };

  const saveTransactions = (formattedTransactions) => {
    setTransactions(formattedTransactions);
    localStorage.setItem("transactions", JSON.stringify(formattedTransactions));
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      if (file.type === "text/csv") {
        const csvText = await file.text();
        const parsedTransactions = await parseCSV(csvText);
        const formattedTransactions = formatTransactions(parsedTransactions);
        saveTransactions(formattedTransactions);
      } else if (file.type === "application/pdf") {
        parsePDF(file);
      } else {
        setError("Unsupported file type. Please upload a CSV or PDF.");
      }
    } catch (error) {
      console.error("Error processing file:", error);
      setError("Error processing file: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const categoryData = transactions.reduce((acc, transaction) => {
    const category = transaction.Category;
    const amount = transaction.Amount;

    if (!acc[category]) {
      acc[category] = 0;
    }
    acc[category] += amount;

    return acc;
  }, {});

  const pieData = Object.keys(categoryData).map((key) => ({
    name: key,
    value: categoryData[key],
  }));

  return (
    <Box
      sx={{
        width: "100%",
        background: "radial-gradient(circle, #0f0f0f, #1c1c1c, #2f2f2f)",
        color: "white",
        minHeight: "100vh",
      }}
    >
      <AppBar position="fixed" sx={{ background: "transparent", boxShadow: "none", width: "100%", zIndex: 2, padding: "0.5rem 1rem" }}>
        <Toolbar sx={{ justifyContent: "space-between" }}>
          <Typography variant="h6" sx={{ fontWeight: "bold", color: "white" }}>
            Financial Assistant
          </Typography>
          <Box>
            <Button component={Link} to="/dashboard" variant="text" sx={{ color: "white" }}>
              Home
            </Button>
            <Button component={Link} to="/profile" variant="text" sx={{ color: "white" }}>
              Profile
            </Button>
            <Button component={Link} to="/docs" variant="text" sx={{ color: "white" }}>
              Docs
            </Button>
            <Button component={Link} to="/FinancialNews" variant="text" sx={{ color: "white" }}>
              News
            </Button>
            <Button component={Link} to="/investment" variant="text" sx={{ color: "white" }}>
              Investment
            </Button>
            <Button component={Link} to="/expense-optimization" variant="text" sx={{ color: "white" }}>
              Expense Optimization
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      

      <Box sx={{ pt: "100px", textAlign: "center" }}>
        <animated.div style={heroAnimation}>
          <Typography variant="h3" sx={{ fontWeight: "bold", mb: 2 }}>
            Budget Classification
          </Typography>
        </animated.div>
      
        <Fade triggerOnce>
          <Grid container spacing={3} justifyContent="center">
            <Grid item xs={12} md={6}>
              <Card sx={{ backgroundColor: "#2f2f2f", color: "white" }}>
                <CardContent>
                  <input type="file" accept=".csv, .pdf" onChange={handleFileChange} />
                  <Button onClick={handleUpload} disabled={loading} sx={{ marginLeft: "10px" }}>
                    {loading ? "Uploading..." : "Upload"}
                  </Button>
                  {error && <Typography color="red">{error}</Typography>}
                  {transactions.length > 0 && (
                    <PieChart width={700} height={750}>
                      <Pie
                        data={pieData}
                        cx="53%"
                        cy="49%"
                        outerRadius={200}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, value }) => `${name}: $${value.toFixed(2)}`}
                      >
                        {pieData.map((_, index) => (
                          <Cell key={index} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Legend 
                        layout="horizontal"
                        align="center"
                        verticalAlign="bottom"
                        wrapperStyle={{ marginBottom: "45px" }}
                      />
                    </PieChart>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Fade>
      </Box>
    
    
    {/* Footer */}
    <Box sx={{ textAlign: "center", mt: 4 }}>
    <Button component={Link} to="/investment" variant="contained" color="primary" sx={{ padding: "10px 20px" }}>
      Go to Financial Assistant
    </Button>
    </Box>
  </Box>

    
  );
};

export default Dashboard;
