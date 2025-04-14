import React, { useState, useEffect } from "react";
import { Box, Typography, AppBar, Toolbar, Button, Grid, Card, CardContent} from "@mui/material";
import { Link } from "react-router-dom";
import { useSpring, animated } from "@react-spring/web";
import { Fade } from "react-awesome-reveal";
import {PieChart, Pie, Cell,RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,Tooltip, Legend,ResponsiveContainer, Sector} from "recharts";

const COLORS = [
  "#00C49F", "#FFBB28", "#FF8042", "#8884d8", "#A28FD0",
  "#FF6699", "#33CCFF", "#FF6666", "#FFD700", "#6A5ACD"
];


const Dashboard = () => {
  const heroAnimation = useSpring({
    from: { opacity: 0, transform: "translateY(-20px)" },
    to: { opacity: 1, transform: "translateY(0)" },
    config: { duration: 1000 },
  });

  const CustomTooltip = ({ payload }) => {
    if (!payload || !payload.length) return null;
    const { name, value } = payload[0].payload;
    return (
      <div style={{
        backgroundColor: "#222",
        borderRadius: "10px",
        padding: "10px",
        color: "#fff",
        fontSize: "0.9rem",
        boxShadow: "0 0 10px rgba(0,0,0,0.3)"
      }}>
        <strong>{name}</strong><br />${parseFloat(value).toFixed(2)}
      </div>
    );
  };
  const [file, setFile] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [chartType, setChartType] = useState("radar");

  useEffect(() => {
    if (!sessionStorage.getItem("dashboardLaunched")) {
      localStorage.removeItem("transactions");
      localStorage.removeItem("categorizedSpending");
      sessionStorage.setItem("dashboardLaunched", "true");
    }
  
    const savedTransactions = localStorage.getItem("transactions");
    if (savedTransactions) {
      setTransactions(JSON.parse(savedTransactions));
    }
  }, []);
  

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };


  const parsePDF = async (pdfFile) => {
    setLoading(true);
    setError("");
    const formData = new FormData();
    formData.append("file", pdfFile);
    try {
      const response = await fetch("http://127.0.0.1:5050/upload", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error("Error uploading PDF.");
      const pdfText = await response.text();
      const parsed = await new Response(new Blob([pdfText])).text();
      const lines = parsed.trim().split("\n");
      const headers = lines[0].split(",");
      const transactions = lines.slice(1).map(line => {
        const values = line.split(",");
        const obj = {};
        headers.forEach((h, i) => {
          obj[h] = values[i];
        });
        return obj;
      });
      const formatted = formatTransactions(transactions);
      saveTransactions(formatted);
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
    if (file.type !== "application/pdf") {
      setError("Unsupported file type. Please upload a PDF only.");
      return;
    }
    await parsePDF(file);
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
    const renderActiveShape = (props) => {
      const {
        cx, cy, innerRadius, outerRadius, startAngle, endAngle, fill, payload,
      } = props;
      return (
        <g>
          <text x={cx} y={cy} dy={8} textAnchor="middle" fill="#fff" fontSize={14}>
            {payload.name}
          </text>
          <Sector
            cx={cx}
            cy={cy}
            innerRadius={innerRadius}
            outerRadius={outerRadius + 6}
            startAngle={startAngle}
            endAngle={endAngle}
            fill={fill}
          />
        </g>
      );
    };
    switch (chartType) {
      case "donut":
        
        return (
          <ResponsiveContainer width="100%" height={450}>
          <PieChart>
            <defs>
              {COLORS.map((color, index) => (
                <linearGradient id={`grad${index}`} key={index} x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor={color} stopOpacity={0.6} />
                  <stop offset="100%" stopColor={color} stopOpacity={1} />
                </linearGradient>
              ))}
              <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="2" dy="2" stdDeviation="3" floodColor="#000" floodOpacity="0.4" />
              </filter>
            </defs>

            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={90}
              outerRadius={150}
              dataKey="value"
              isAnimationActive={true}
              activeShape={renderActiveShape}
              label={({ name, value, cx, cy, midAngle, outerRadius, index }) => {
                const RADIAN = Math.PI / 180;
                const radius = outerRadius + 20;
                const x = cx + radius * Math.cos(-midAngle * RADIAN);
                const y = cy + radius * Math.sin(-midAngle * RADIAN);
                return (
                  <text
                    x={x}
                    y={y}
                    fill={COLORS[index % COLORS.length]}
                    textAnchor={x > cx ? "start" : "end"}
                    dominantBaseline="central"
                    fontSize={15}
                  >
                    {`${name}: $${parseFloat(value).toFixed(2)}`}
                  </text>
                );
              }}
              style={{ filter: "url(#shadow)" }}
            >
              {pieData.map((_, index) => (
                <Cell key={index} fill={`url(#grad${index % COLORS.length})`} />
              ))}
            </Pie>

            <Tooltip content={<CustomTooltip />} />
            <Legend
              iconType="circle"
              wrapperStyle={{
                paddingTop: "15px",
                fontSize: "0.9rem"
              }}
            />
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

  const navItems = [
    { name: 'ClassifyBot 💡', path: '/dashboard' },
    { name: 'Optimization', path: '/optimization' },
    { name: 'Investment', path: '/investment' },
      {name: "Profile", path: "/profile"},
    { name: 'News', path: '/FinancialNews' },
    { name: 'Logout', path: '/'}
  ];

  return (
    <Box sx={{ width: "100%", background: "radial-gradient(circle, #0f0f0f, #1c1c1c, #2f2f2f)", color: "white", minHeight: "100vh" }}>
      <AppBar position="fixed" sx={{ backgroundColor: 'transparent', boxShadow: 'none', padding: '0.5rem 1rem' }}>
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'white' }}>
          Financial Assistant
        </Typography>
        <Box>
          {navItems.map((item) => (
            <Button
              key={item.name}
              component={Link}
              to={item.path}
              variant="text"
              sx={{
                color: 'white',
                position: 'relative',
                '&:hover': {
                  color: '#ADD8E6', 
                  '&::after': {
                    content: '""',
                    position: 'absolute',
                    width: '100%',
                    height: '2px',
                    bottom: 0,
                    left: 0,
                    backgroundColor: '#ADD8E6', 
                    visibility: 'visible',
                    transform: 'scaleX(1)',
                    transition: 'all 0.3s ease-in-out',
                  },
                },
                '&::after': {
                  content: '""',
                  position: 'absolute',
                  width: '100%',
                  height: '2px',
                  bottom: 0,
                  left: 0,
                  backgroundColor: '#ADD8E6',
                  visibility: 'hidden',
                  transform: 'scaleX(0)',
                  transition: 'all 0.3s ease-in-out',
                },
              }}
            >
              {item.name}
            </Button>
          ))}
        </Box>
      </Toolbar>
    </AppBar>
    
      <Box sx={{ pt: "100px", textAlign: "center" }}>
      <animated.div style={heroAnimation}>
        <Typography
          variant="h3"
          sx={{
            fontWeight: 700,
            mb: 2,
            fontFamily: "'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif",
            color: "#FFB07C",
            letterSpacing: "1.8px",
            textAlign: "center",
            textShadow: `
              0 1px 2px rgba(0, 0, 0, 0.5),
              0 2px 6px rgba(0, 0, 0, 0.4),
              0 4px 10px rgba(0, 0, 0, 0.3)
            `,
          }}
        >
          💼 Budget Breakdown
        </Typography>
      </animated.div>
        <Fade triggerOnce>
          
        <Grid container spacing={3} justifyContent="center" alignItems="stretch">
        {/* Left Info Block */}
        <Grid item xs={12} md={3}>
          <Fade direction="left" triggerOnce>
            <br></br>
          <Typography sx={{
            fontFamily: '"Pacifico", cursive',
            fontSize: "2.5rem",
            color: "#fff",
            background: "linear-gradient(135deg, #ffb6c1, #87cefa, #dda0dd, #fff176)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            textShadow: `
              2px 2px 4px rgba(0,0,0,0.2),
              4px 4px 8px rgba(0,0,0,0.15)
            `,
            animation: "bounce 3s infinite",
            transform: "rotate(-5deg)",

            textAlign: "center",
            mb: 2
          }}
        > Track Every Penny!
        </Typography>
            <br></br>
            <br></br>
            <br></br>
            <br></br>
            <br></br>
            <br></br>
            <br></br>
            <br></br>
          <Box
            sx={{
              background: "linear-gradient(to bottom right, #232323, #2d2d2d)",
              padding: "28px",
              borderRadius: "14px",
              height: "100%",
              color: "#ddd",
              fontSize: "1.05rem",
              boxShadow: "0 6px 20px rgba(0,0,0,0.4)",
              lineHeight: 1.75,
              border: "1px solid #333",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
            }}
          >
            <Typography
              variant="h6"
              sx={{
                color: "#FFD700",
                mb: 2,
                fontWeight: "bold",
                fontSize: "1.25rem",
                textShadow: "0 1px 4px rgba(0,0,0,0.6)",
              }}
            >
              💡 Ready to Dive In?
            </Typography>

            <Typography
              sx={{
                fontSize: "1.05rem",
                color: "#eee",
                background: "linear-gradient(90deg, #ffecd2, #fcb69f)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                fontWeight: 500,
                textShadow: "0 1px 2px rgba(0,0,0,0.3)"
              }}
            >
              Drop your credit card statement. <br />
              Watch your spending story unfold.
            </Typography>
          </Box>

          </Fade>
        </Grid>

        {/* Center Card (Chart + Upload) */}
        <Grid item xs={12} md={6}>
          <Card sx={{ backgroundColor: "#2f2f2f", color: "white" }}>
            <CardContent>
              <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 2, mt: 2 }}>
                <label htmlFor="file-upload">
                  <input
                    id="file-upload"
                    type="file"
                    accept=".csv, .pdf"
                    style={{ display: "none" }}
                    onChange={handleFileChange}
                  />
                  <Button
                    variant="contained"
                    component="span"
                    sx={{
                      background: "linear-gradient(135deg, #e0cfc1, #c2b4a3)",
                      color: "#1a1a1a",
                      padding: "10px 22px",
                      borderRadius: "10px",
                      fontWeight: "600",
                      textTransform: "uppercase",
                      boxShadow: "0 4px 12px rgba(194, 180, 163, 0.3)",
                      "&:hover": {
                        background: "linear-gradient(135deg, #f2e3d5, #cabaa9)",
                        boxShadow: "0 6px 16px rgba(194, 180, 163, 0.4)",
                      },
                    }}
                  >
                    📁 Choose File
                  </Button>
                </label>
                <Button
                  onClick={handleUpload}
                  disabled={loading}
                  sx={{
                    background: "linear-gradient(135deg, #a6e3e9, #71c9ce)",
                    color: "#1a1a1a",
                    padding: "10px 22px",
                    borderRadius: "10px",
                    fontWeight: "600",
                    textTransform: "uppercase",
                    boxShadow: "0 4px 12px rgba(113, 201, 206, 0.3)",
                    "&:hover": {
                      background: "linear-gradient(135deg, #c3f0f4, #88d4da)",
                      boxShadow: "0 6px 16px rgba(113, 201, 206, 0.4)",
                    },
                  }}
                >
                  {loading ? "Uploading..." : "Upload"}
                </Button>
              </Box>
              {file && (
                <Typography
                  variant="body2"
                  sx={{
                    color: "#ccc",
                    textAlign: "center",
                    fontStyle: "italic",
                    mt: 1,
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    maxWidth: "100%",
                  }}
                >
                  Selected File: {file.name}
                </Typography>
              )}
              {error && <Typography sx={{ color: "red", mt: 2 }}>{error}</Typography>}
              <Box sx={{ display: "flex", justifyContent: "center", gap: 3, mt: 4, mb: 4 }}>
                <Button
                  onClick={() => setChartType("donut")}
                  sx={{
                    background: chartType === "donut" ? "linear-gradient(135deg, #d7b899, #b08c5f)" : "transparent",
                    color: chartType === "donut" ? "white" : "#b08c5f",
                    border: "2px solid #b08c5f",
                    padding: "10px 24px",
                    borderRadius: "10px",
                    fontWeight: "bold",
                    fontSize: "1rem",
                    textTransform: "uppercase",
                    transition: "all 0.3s ease-in-out",
                    boxShadow: chartType === "donut" ? "0px 6px 18px rgba(183, 141, 94, 0.4)" : "none",
                    "&:hover": {
                      background: "linear-gradient(135deg, #e1c4a0, #b89265)",
                      boxShadow: "0px 8px 22px rgba(183, 141, 94, 0.6)",
                      color: "white",
                    },
                  }}
                >
                  🍩 Donut Chart
                </Button>
                <Button
                  onClick={() => setChartType("radar")}
                  sx={{
                    background: chartType === "radar" ? "linear-gradient(135deg, #00c6ff, #0072ff)" : "transparent",
                    color: chartType === "radar" ? "white" : "#00c6ff",
                    border: "2px solid #00c6ff",
                    padding: "10px 24px",
                    borderRadius: "10px",
                    fontWeight: "bold",
                    fontSize: "1rem",
                    textTransform: "uppercase",
                    transition: "all 0.3s ease-in-out",
                    boxShadow: chartType === "radar" ? "0px 6px 18px rgba(0, 198, 255, 0.4)" : "none",
                    "&:hover": {
                      background: "linear-gradient(135deg, #33d1ff, #338eff)",
                      boxShadow: "0px 8px 22px rgba(0, 198, 255, 0.6)",
                      color: "white",
                    },
                  }}
                >
                  📡 Radar Chart
                </Button>
              </Box>
              {renderChart()}
            </CardContent>
          </Card>
        </Grid>

        {/* Right Info Block */}
        <Grid item xs={12} md={3}>
          <Fade direction="right" triggerOnce>
            
          <br></br>
          <br></br>
          <br></br>
          <br></br>
          <br></br>
          <br></br>
          <br></br>
          <br></br>
          <br></br>
          <br></br>
          <br></br>
          <br></br>
          <br></br>
          <Box
          sx={{
            background: "linear-gradient(to bottom right, #232323, #2d2d2d)",
            padding: "28px",
            borderRadius: "14px",
            height: "100%",
            color: "#ddd",
            fontSize: "1.05rem",
            boxShadow: "0 6px 20px rgba(0,0,0,0.4)",
            lineHeight: 1.75,
            border: "1px solid #333",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
          }}
        >
          <Typography
            variant="h6"
            sx={{
              color: "#90ee90",
              mb: 2,
              fontWeight: "bold",
              fontSize: "1.25rem",
              textShadow: "0 1px 4px rgba(0,0,0,0.6)",
              fontFamily: "'Poppins', sans-serif", 
            }}
          >
            Your Next Step 🚀
          </Typography>

          <Typography
            sx={{
              fontSize: "1.05rem",
              color: "#eee",
              background: "linear-gradient(90deg, #c2e9fb, #a1c4fd)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              fontWeight: 500,
              fontFamily: "'Poppins', sans-serif", 
              textShadow: "0 1px 2px rgba(0,0,0,0.3)",
            }}
          >
            Take a peek at your spending patterns.
            <br />
            Hop to Optimization for smart ways to save!
          </Typography>
        </Box>
            <br></br>
            <br></br>
            <br></br>
            <br></br>
            <br></br>
            <br></br>
            <br></br>
            <br></br>
        <Typography
          sx={{
            fontFamily: '"Baloo 2", cursive',
            fontSize: "2.5rem",
            background: "linear-gradient(135deg, #fbc2eb, #a6c1ee, #fda085, #f6d365, #c3cfe2)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            textShadow: "0 0 6px rgba(255,255,255,0.25), 0 0 12px rgba(255,255,255,0.15)"
,
            transform: "rotate(5deg)",
            display: "inline-block",
            textAlign: "center",
            mb: 2,
          }}
        >
          Grow Smarter Habits
        </Typography>
          </Fade>
        </Grid>
      </Grid>
        </Fade>
      </Box>
      <br></br>
      <br></br>
      <br></br>
      <br></br>
      <br></br>
      <br></br>
      <Box sx={{ textAlign: "center", mt: 4 }}>
      <Button
        component={Link}
        to="/optimization"
        variant="contained"
        sx={{
          padding: "12px 28px",
          borderRadius: "999px", 
          fontWeight: "bold",
          fontSize: "1rem",
          textTransform: "uppercase",
          background: "linear-gradient(135deg, #6a5acd, #4f9df7)", 
          boxShadow: "0 4px 12px rgba(79, 157, 247, 0.3)",
          transition: "all 0.3s ease-in-out",
          "&:hover": {
            background: "linear-gradient(135deg, #7a6aff, #3a8dff)",
            boxShadow: "0 6px 20px rgba(79, 157, 247, 0.5)",
            transform: "translateY(-2px)",
          },
        }}
      >
        🎛️ Fine-Tune Spending
      </Button>
    </Box>


      <Box component="footer" sx={{ width: "100%", padding: "1rem", color: "white", textAlign: "center" }}>
        <Typography variant="body2">© {new Date().getFullYear()} Financial Assistant. All rights reserved.</Typography>
      </Box>
    </Box>
  );
};

export default Dashboard;
