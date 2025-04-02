import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import {
  Box, Button, TextField, Typography, Avatar,
  AppBar, Toolbar, CircularProgress, IconButton,
  Paper, Select, MenuItem, FormControl, InputLabel
} from "@mui/material";
import { Link } from "react-router-dom";
import {
  Send as SendIcon,
  AccountCircle as AccountCircleIcon,
  SmartToy as SmartToyIcon,
  AttachMoney as AttachMoneyIcon,
  Warning as RiskLevelIcon
} from "@mui/icons-material";

const API_BASE_URL = "http://localhost:5001";

const FinancialChatBot = () => {

  const [estimatedSavings, setEstimatedSavings] = useState(() => {
    const savedAmount = localStorage.getItem('estimatedSavings');
    return savedAmount ? parseFloat(savedAmount) : 0; // Default to 0 if nothing saved
  });
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stocks, setStocks] = useState([]);
  const [riskLevels, setRiskLevels] = useState([]);
  // const [estimatedSavings, setEstimatedSavings] = useState(5000);
  const [riskPreference, setRiskPreference] = useState("medium");
  const messagesEndRef = useRef(null);

  // This effect will update localStorage whenever estimatedSavings changes
  useEffect(() => {
    localStorage.setItem('estimatedSavings', estimatedSavings.toString());
  }, [estimatedSavings]);

  // Navigation items array
  const navItems = [
    { name: "ClassifyBot 💡", path: "/dashboard" },
    { name: "Optimization", path: "/optimization" },
    { name: "Investment", path: "/investment" },
    { name: "News", path: "/FinancialNews" },
  ];

  const fetchSupportedStocks = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/stocks`);
      setStocks(response.data.tickers);
      setRiskLevels(response.data.risk_levels);
    } catch (error) {
      console.error("Backend connection failed, using fallback data");
      setStocks(["AAPL", "MSFT", "GOOG"]);
      setRiskLevels(["low", "medium", "high"]);
    }
  }, []);

  useEffect(() => {
    const welcomeMessage = {
      type: "bot",
      text: `Welcome! After optimizing your budget, you have saved $${estimatedSavings.toLocaleString()} to invest. Ask about any stocks or request recommendations.`,
      time: new Date().toLocaleTimeString()
    };
    setMessages([welcomeMessage]);
    fetchSupportedStocks();
  }, [estimatedSavings, fetchSupportedStocks]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const updateInvestmentProfile = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/update_profile`, {
        amount: estimatedSavings,
        risk: riskPreference
      });
      localStorage.setItem("estimatedSavings", estimatedSavings);
      localStorage.setItem("riskPreference", riskPreference);
    } catch (error) {
      console.error("Failed to update profile:", error);
    }
  };

  const analyzeStock = async (ticker) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/analyze`, {
        params: { ticker }
      });
      
      let responseText = `Analysis for ${ticker}:\n`;
      responseText += `- Price: $${response.data.price.toFixed(2)}\n`;
      responseText += `- Trend: ${response.data.prediction.toUpperCase()} `;
      responseText += `(${(response.data.confidence * 100).toFixed(1)}% confidence)\n`;
      
      if (response.data.shares_possible) {
        responseText += `\nBased on the stock price and $${estimatedSavings} available to invest, you could buy around ${response.data.shares_possible} shares of this company`;
      }
      
      return responseText;
    } catch (error) {
      return `Couldn't analyze ${ticker}. Please try again.`;
    }
  };

  const getRecommendations = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/recommend`, {
        params: {
          amount: estimatedSavings,
          risk: riskPreference
        }
      });

      if (response.data.status === 'no_recommendations') {
        return "No strong recommendations for your risk profile currently.";
      }

      let recommendation = `Recommended investments ($${estimatedSavings}):\n\n`;
      response.data.recommendations.forEach((stock, i) => {
        recommendation += `${i+1}. ${stock.ticker} ($${stock.price.toFixed(2)})\n`;
        recommendation += `   Confidence: ${(stock.confidence * 100).toFixed(1)}%\n`;
        recommendation += `   Can buy: ${stock.potential_shares} shares\n\n`;
      });

      recommendation += "Suggested allocation:\n";
      response.data.allocation_plan.forEach(item => {
        recommendation += `- ${item.ticker}: ${item.percentage}% (${item.shares} shares)\n`;
      });

      return recommendation;
    } catch (error) {
      return "Couldn't get recommendations. Please try again.";
    }
  };

  const handleSubmit = async () => {
    if (!input.trim()) return;

    const userMessage = {
      type: "user",
      text: input,
      time: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      let botResponse;
      if (input.toLowerCase().includes("recommend")) {
        botResponse = await getRecommendations();
      } else {
        const tickerMatch = input.match(/\b[A-Z]{2,4}\b/i);
        if (tickerMatch) {
          const ticker = tickerMatch[0].toUpperCase();
          botResponse = stocks.includes(ticker)
            ? await analyzeStock(ticker)
            : `We don't support ${ticker}. Try: ${stocks.join(", ")}`;
        } else {
          botResponse = "Ask about a stock (e.g. AAPL) or say 'recommend investments'";
        }
      }

      setMessages(prev => [...prev, {
        type: "bot",
        text: botResponse,
        time: new Date().toLocaleTimeString()
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        type: "bot",
        text: "Sorry, something went wrong.",
        time: new Date().toLocaleTimeString()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const renderMessage = (message) => (
    <Box sx={{ 
      display: "flex", 
      alignItems: "center", 
      gap: 1, 
      mb: 2,
      flexDirection: message.type === "user" ? "row-reverse" : "row"
    }}>
      <Avatar sx={{
        bgcolor: message.type === "user" ? "primary.main" : "secondary.main",
        width: 32,
        height: 32
      }}>
        {message.type === "user" ? <AccountCircleIcon /> : <SmartToyIcon />}
      </Avatar>

      <Paper
        elevation={3}
        sx={{
          p: 2,
          maxWidth: "75%",
          bgcolor: message.type === "user" ? "primary.main" : "background.paper",
          color: message.type === "user" ? "primary.contrastText" : "text.primary",
          borderRadius: message.type === "user" ? "18px 18px 0 18px" : "18px 18px 18px 0"
        }}
      >
        <Typography whiteSpace="pre-line">{message.text}</Typography>
        <Typography variant="caption" sx={{ 
          display: "block", 
          textAlign: "right", 
          opacity: 0.7,
          color: message.type === "user" ? "primary.contrastText" : "text.secondary"
        }}>
          {message.time}
        </Typography>
      </Paper>
    </Box>
  );

  const clearChat = () => {
    setMessages([{
      type: "bot",
      text: `Chat cleared. You have $${estimatedSavings.toLocaleString()} to invest.`,
      time: new Date().toLocaleTimeString()
    }]);
  };

  return (
    <Box sx={{
      width: "100%",
      background: "radial-gradient(circle, #888888, #444444, #1c1c1c)",
      color: "white",
      minHeight: "100vh"
    }}>
      <AppBar
        position="fixed"
        sx={{
          backgroundColor: "transparent",
          boxShadow: "none",
          padding: "0.5rem 1rem",
        }}
      >
        <Toolbar sx={{ justifyContent: "space-between" }}>
          <Typography variant="h6" sx={{ fontWeight: "bold", color: "white" }}>
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
                  color: "white",
                  position: "relative",
                  "&:hover": {
                    color: "#ADD8E6",
                    "&::after": {
                      content: '""',
                      position: "absolute",
                      width: "100%",
                      height: "2px",
                      bottom: 0,
                      left: 0,
                      backgroundColor: "#ADD8E6",
                      visibility: "visible",
                      transform: "scaleX(1)",
                      transition: "all 0.3s ease-in-out",
                    },
                  },
                  "&::after": {
                    content: '""',
                    position: "absolute",
                    width: "100%",
                    height: "2px",
                    bottom: 0,
                    left: 0,
                    backgroundColor: "#ADD8E6",
                    visibility: "hidden",
                    transform: "scaleX(0)",
                    transition: "all 0.3s ease-in-out",
                  },
                }}
              >
                {item.name}
              </Button>
            ))}
          </Box>
        </Toolbar>
      </AppBar>

      {/* New Investment Portfolio Heading */}
      <Box sx={{ pt: "80px", textAlign: "center" }}>
        <Typography
          variant="h3"
          sx={{
            fontFamily: "'Segoe UI Emoji', 'Noto Color Emoji', sans-serif",
            fontWeight: "bold",
            mb: 2,
            letterSpacing: "1.5px",
            fontSize: { xs: "2rem", md: "3rem" },
            textAlign: "center",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: "12px",
            overflow: "visible", 
          }}
        >
          <span style={{ fontSize: "2.5rem", lineHeight: 1 }}>📈</span>
          <span style={{ position: "relative", display: "inline-block" }}>
            {/* Shadow Layer */}
            <span style={{
              position: "absolute",
              top: 0,
              left: 0,
              color: "#ffffff",
              opacity: 0.2,
              filter: "blur(2px)",
              zIndex: 0,
            }}>
              Investment Assistant
            </span>

            {/* Gradient Text Layer */}
            <span style={{
              background: "linear-gradient(135deg, rgb(255, 255, 255), rgb(140, 161, 211), rgb(116, 136, 173), rgb(255, 255, 255))",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              display: "inline-block",
              lineHeight: "1.4",
              animation: "gradientFlow 6s ease infinite",
              backgroundSize: "600% 600%",
              position: "relative",
              zIndex: 1,
            }}>
              Investment Assistant
            </span>
          </span>
        </Typography>
      </Box>

      {/* Main Content Container */}
      <Box sx={{
        pt: "20px",
        maxWidth: "800px",
        mx: "auto",
        px: 2,
        display: "flex",
        flexDirection: "column",
        minHeight: "calc(100vh - 180px)"
      }}>
        <Box sx={{
          flexGrow: 1,
          overflowY: "auto",
          mb: 2,
          backgroundColor: "#2f2f2f",
          borderRadius: "16px",
          p: 3,
          boxShadow: "0px 6px 16px rgba(0,0,0,0.3)"
        }}>
          {messages.map((msg, i) => (
            <div key={i}>{renderMessage(msg)}</div>
          ))}
          {loading && (
            <Box display="flex" justifyContent="center" alignItems="center" gap={1}>
              <CircularProgress size={20} sx={{ color: "#ccc" }} />
              <Typography sx={{ fontStyle: "italic", color: "#ccc" }}>
                Analyzing...
              </Typography>
            </Box>
          )}
          <div ref={messagesEndRef} />
        </Box>

        <Box sx={{ 
            display: "flex", 
            gap: 2, 
            mb: 2,
            position: 'relative',
          }}>
            {/* Amount Control */}
            <Box sx={{ 
              flexGrow: 1,
              position: 'relative',
              border: '1px solid #555',
              borderRadius: '4px',
              padding: '2px 1px',
              backgroundColor: '#2a2a2a'
            }}>
              <Typography sx={{ 
                position: 'absolute',
                top: '-10px',
                left: '10px',
                backgroundColor: '#1e1e1e',
                padding: '0 6px',
                fontSize: '0.75rem',
                fontWeight: 'bold',
                color: 'white'
              }}>
                Amount
              </Typography>
              <TextField
                type="number"
                value={estimatedSavings}
                onChange={(e) => setEstimatedSavings(parseFloat(e.target.value) || 0)}
                onWheel={(e) => {
                  e.preventDefault();
                  setEstimatedSavings(prev => {
                    const changeAmount = e.deltaY > 0 ? 10 : -10;
                    return Math.max(0, prev + changeAmount);
                  });
                }}
                InputProps={{
                  startAdornment: <AttachMoneyIcon sx={{ color: 'white', mr: 1 }} />,
                  sx: { 
                    color: 'white',
                    padding: '1px'
                  }
                }}
                sx={{
                  width: '100%',
                  "& .MuiOutlinedInput-notchedOutline": { borderColor: "transparent" },
                  "& .MuiOutlinedInput-root": {
                    "&:hover .MuiOutlinedInput-notchedOutline": {
                      borderColor: "transparent"
                    },
                    "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                      borderColor: "transparent"
                    }
                  }
                }}
              />
            </Box>

            {/* Risk Control */}
            <Box sx={{ 
              flexGrow: 1,
              position: 'relative',
              border: '1px solid #555',
              borderRadius: '4px',
              padding: '2px 1px',
              backgroundColor: '#2a2a2a'
            }}>
              <Typography sx={{ 
                position: 'absolute',
                top: '-10px',
                left: '10px',
                backgroundColor: '#1e1e1e',
                padding: '0 6px',
                fontSize: '0.75rem',
                fontWeight: 'bold',
                color: 'white'
              }}>
                Risk
              </Typography>
              <Select
                value={riskPreference}
                onChange={(e) => setRiskPreference(e.target.value)}
                sx={{ 
                  width: '100%',
                  color: 'white',
                  "& .MuiSelect-icon": { color: 'white' },
                  "& .MuiOutlinedInput-notchedOutline": { borderColor: "transparent" }
                }}
              >
                {riskLevels.map(level => (
                  <MenuItem key={level} value={level}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <RiskLevelIcon fontSize="small" />
                      {level.charAt(0).toUpperCase() + level.slice(1)}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </Box>

            {/* Update Button */}
            <Button
              variant="contained"
              onClick={updateInvestmentProfile}
              sx={{ 
                height: '56px',
                alignSelf: 'center',
                backgroundColor: "#00e3ae",
                color: '#1e1e1e',
                fontWeight: 'bold',
                "&:hover": { backgroundColor: "#00c49a" }
              }}
            >
              Update
            </Button>
        </Box>

        <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
          <TextField
            fullWidth
            placeholder="Ask about stocks or request recommendations..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
            disabled={loading}
            sx={{
              input: { color: "white" },
              backgroundColor: "#1e1e1e",
              borderRadius: "10px",
              mr: 2,
              "& .MuiOutlinedInput-notchedOutline": { borderColor: "#444" },
              "&:hover .MuiOutlinedInput-notchedOutline": {
                borderColor: "#888",
              },
            }}
          />
          <IconButton
            onClick={handleSubmit}
            disabled={loading || !input.trim()}
            sx={{ 
              backgroundColor: "#1976d2",
              "&:hover": { backgroundColor: "#1565c0" },
              color: "white"
            }}
          >
            <SendIcon />
          </IconButton>
        </Box>

        <Button
          variant="outlined"
          onClick={clearChat}
          sx={{
            alignSelf: "center",
            mt: 2,
            mb: 3,
            color: "#fff",
            borderColor: "#ccc",
            "&:hover": {
              borderColor: "#f50057",
              backgroundColor: "#ff1744"
            }
          }}
        >
          Clear Chat
        </Button>
      </Box>
    </Box>
  );
};

export default FinancialChatBot;