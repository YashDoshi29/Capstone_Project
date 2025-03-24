import React, { useState, useEffect } from "react";
import { Box, Typography, AppBar, Toolbar, Button, Grid, Card, CardContent} from "@mui/material";
import { Link } from "react-router-dom";
import { useSpring, animated } from "@react-spring/web";
import { Fade } from "react-awesome-reveal";
import Papa from "papaparse";
import {PieChart, Pie, Cell,RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,Tooltip, Legend,ResponsiveContainer} from "recharts";

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
  const [chartType, setChartType] = useState("radar");

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

      if (!response.ok) throw new Error("Error uploading PDF.");

      const pdfText = await response.text();
      const parsedTransactions = await parseCSV(pdfText);
      const formattedTransactions = formatTransactions(parsedTransactions);
      saveTransactions(formattedTransactions);
    } catch (error) {
      console.error("Upload failed:", error);
      setError("Please upload the file again: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const formatTransactions = (parsedTransactions) =>
    parsedTransactions.map((transaction) => ({
      Category: transaction.Category || "Unknown",
      Amount: parseFloat(transaction.Amount) || 0,
      "Transaction Date": new Date(transaction["Transaction Date"]).toLocaleDateString(),
      "Posting Date": new Date(transaction["Posting Date"]).toLocaleDateString(),
    }));

  const saveTransactions = (formattedTransactions) => {
    setTransactions(formattedTransactions);
    localStorage.setItem("transactions", JSON.stringify(formattedTransactions));

    const categoryTotals = formattedTransactions.reduce((acc, transaction) => {
      if (!acc[transaction.Category]) acc[transaction.Category] = 0;
      acc[transaction.Category] += transaction.Amount;
      return acc;
    }, {});

    localStorage.setItem("categorizedSpending", JSON.stringify(categoryTotals));
  };

  const handleUpload = async () => {
    if (!file) return setError("Please select a file first.");
    setLoading(true);
    setError("");

    try {
      if (file.type === "text/csv") {
        const csvText = await file.text();
        const parsedTransactions = await parseCSV(csvText);
        const formattedTransactions = formatTransactions(parsedTransactions);
        saveTransactions(formattedTransactions);
      } else if (file.type === "application/pdf") {
        await parsePDF(file);
      } else {
        setError("Unsupported file type. Please upload a CSV or PDF.");
      }
    } catch (error) {
      console.error("Upload error:", error);
      setError("Please upload the file again: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const categoryData = transactions.reduce((acc, transaction) => {
    const category = transaction.Category;
    const amount = transaction.Amount;
    if (!acc[category]) acc[category] = 0;
    acc[category] += amount;
    return acc;
  }, {});

  const pieData = Object.keys(categoryData).map((key) => ({
    name: key,
    value: categoryData[key],
  }));

  const renderChart = () => {
    switch (chartType) {
      case "donut":
        return (
          <ResponsiveContainer width="100%" height={450}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={90}
                outerRadius={150}
                fill="#8884d8"
                dataKey="value"
                label={({ name, value }) => `${name}: $${parseFloat(value).toFixed(2)}`}
                isAnimationActive={true}
              >
                {pieData.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value) => `$${parseFloat(value).toFixed(2)}`}
                contentStyle={{
                  borderRadius: "12px",
                  color: "#fff",
                }}
                labelStyle={{ display: "none" }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );

      case "radar":
      default:
        return (
          <ResponsiveContainer width="100%" height={500}>
            <RadarChart data={pieData}>
              <PolarGrid stroke="#444" />
              <PolarAngleAxis
                dataKey="name"
                stroke="#00ffe0"
                
              />
              <PolarRadiusAxis stroke="#555" />
              <Radar
                name="💸"
                dataKey="value"
                stroke="#00ffe0"
                fill="#00ffe0"
                fillOpacity={0.6}
                isAnimationActive={true}
              />
              <Tooltip
                formatter={(value) => `$${parseFloat(value).toFixed(2)}`}
                contentStyle={{
                  backgroundColor: "#222",
                  borderRadius: "8px",
                  padding: "6px 10px",
                  color: "#fff",
                  boxShadow: "0 0 10px #00ffe0",
                }}
                labelStyle={{ color: "#00ffe0" }}
              />
            </RadarChart>
          </ResponsiveContainer>
        );
    }
  };

  return (
    <Box sx={{ width: "100%", background: "radial-gradient(circle, #0f0f0f, #1c1c1c, #2f2f2f)", color: "white", minHeight: "100vh" }}>
      <AppBar position="fixed" sx={{ background: "transparent", boxShadow: "none", padding: "0.5rem 1rem" }}>
        <Toolbar sx={{ justifyContent: "space-between" }}>
          <Typography variant="h6" sx={{ fontWeight: "bold", color: "white" }}>
            Financial Assistant
          </Typography>
          <Box>
            <Button component={Link} to="/dashboard" variant="text" sx={{ color: "white" }}>ClassifyBot 💡</Button>
            <Button component={Link} to="/optimization" variant="text" sx={{ color: "white" }}>Optimization</Button>
            <Button component={Link} to="/investment" variant="text" sx={{ color: "white" }}>Investment</Button>
            <Button component={Link} to="/FinancialNews" variant="text" sx={{ color: "white" }}>News</Button>
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
                  {error && <Typography sx={{ color: "red", mt: 2 }}>{error}</Typography>}

                  <Box sx={{ display: "flex", justifyContent: "center", gap: 2, mt: 4, mb: 4 }}>
                    <Button variant={chartType === "donut" ? "contained" : "outlined"} onClick={() => setChartType("donut")}>Donut Chart</Button>
                    <Button variant={chartType === "radar" ? "contained" : "outlined"} onClick={() => setChartType("radar")}>Radar Chart</Button>
                  </Box>

                  {renderChart()}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Fade>
      </Box>

      <Box sx={{ textAlign: "center", mt: 4 }}>
        <Button component={Link} to="/optimization" variant="contained" color="primary" sx={{ padding: "10px 20px" }}>
        🎛️ Fine-Tune Spending
        </Button>
      </Box>

      <Box component="footer" sx={{ width: "100%", padding: "1rem", backgroundColor: "#1c1c1c", color: "white", textAlign: "center" }}>
        <Typography variant="body2">© {new Date().getFullYear()} Financial Assistant. All rights reserved.</Typography>
      </Box>
    </Box>
  );
};

export default Dashboard;
