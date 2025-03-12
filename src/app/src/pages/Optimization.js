import React, { useEffect, useState } from "react";
import { Box, Typography, AppBar, Toolbar, Button, Grid, Card, CardContent, TextField } from "@mui/material";
import { Link } from "react-router-dom";
import { useSpring, animated } from "@react-spring/web";
import { Fade } from "react-awesome-reveal";
import axios from "axios"; // Import axios for API calls

const BudgetOptimization = () => {
  const heroAnimation = useSpring({
    from: { opacity: 0, transform: "translateY(-20px)" },
    to: { opacity: 1, transform: "translateY(0)" },
    config: { duration: 1000 },
  });

  const [userDetails, setUserDetails] = useState({
    age: "",
    income: "",
    children: "",
    maritalStatus: "",
  });
  const [budget, setBudget] = useState(0);
  const [error, setError] = useState("");

  useEffect(() => {
    const savedTransactions = localStorage.getItem("transactions");
    if (savedTransactions) {
      const transactions = JSON.parse(savedTransactions);
      const totalBudget = transactions.reduce((sum, transaction) => sum + transaction.Amount, 0);
      setBudget(totalBudget);
    }
  }, []);

  

  const [chatbotResponse, setChatbotResponse] = useState("");
  const [isChatting, setIsChatting] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setUserDetails({ ...userDetails, [name]: value });
  };

  const handleChatSubmit = async () => {
    setIsChatting(true);

    const requestData = {
      model: "llama3-8b-8192",
      messages: [{ role: "user", content: `User details: Age: ${userDetails.age}, Income: ${userDetails.income}, Children: ${userDetails.children}, Marital Status: ${userDetails.maritalStatus}. Provide budgeting advice.` }],
      temperature: 0.7,
    };

    try {
      const response = await axios.post(
        "https://api.groq.com/openai/v1/chat/completions",
        requestData,
        {
          headers: {
            Authorization: `Bearer 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`,
            "Content-Type": "application/json",
          },
        }
      );

      if (response.data.choices && response.data.choices.length > 0) {
        setChatbotResponse(response.data.choices[0].message.content.trim());
      } else {
        setChatbotResponse("No response from the model.");
      }
    } catch (error) {
      console.error("Error interacting with Groq Llama model:", error);
      setChatbotResponse("Sorry, there was an error. Please try again.");
    } finally {
      setIsChatting(false);
    }
  };

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
            <Button component={Link} to="/dashboard" variant="text" sx={{ color: "white" }}>Home</Button>
            <Button component={Link} to="/profile" variant="text" sx={{ color: "white" }}>Profile</Button>
            <Button component={Link} to="/docs" variant="text" sx={{ color: "white" }}>Docs</Button>
            <Button component={Link} to="/optimization" variant="text" sx={{ color: "white" }}>Optimization</Button>
            <Button component={Link} to="/investment" variant="text" sx={{ color: "white" }}>Investment</Button>
            <Button component={Link} to="/FinancialNews" variant="text" sx={{ color: "white" }}>News</Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Box sx={{ pt: "100px", textAlign: "center" }}>
        <animated.div style={heroAnimation}>
          <Typography variant="h3" sx={{ fontWeight: "bold", mb: 2 }}>
            Budget Optimization
          </Typography>
        </animated.div>

        <Fade triggerOnce>
          <Grid container spacing={3} justifyContent="center">
            <Grid item xs={12} md={6}>
              <Card sx={{ backgroundColor: "#2f2f2f", color: "white" }}>
                <CardContent>
                  <Typography variant="h5" sx={{ mb: 3 }}>
                    Answer these questions to optimize your budget:
                  </Typography>
                  <TextField
                    label="Age"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    name="age"
                    value={userDetails.age}
                    onChange={handleInputChange}
                    sx={{
                      backgroundColor: "#333", 
                      color: "white", 
                      '& .MuiInputBase-root': {
                        color: 'white',
                      },
                    }}
                  />
                  <TextField
                    label="Income Range"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    name="income"
                    value={userDetails.income}
                    onChange={handleInputChange}
                    sx={{
                      backgroundColor: "#333", 
                      color: "white", 
                      '& .MuiInputBase-root': {
                        color: 'white',
                      },
                    }}
                  />
                  <TextField
                    label="Number of Children"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    name="children"
                    value={userDetails.children}
                    onChange={handleInputChange}
                    sx={{
                      backgroundColor: "#333", 
                      color: "white", 
                      '& .MuiInputBase-root': {
                        color: 'white',
                      },
                    }}
                  />
                  <TextField
                    label="Marital Status"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    name="maritalStatus"
                    value={userDetails.maritalStatus}
                    onChange={handleInputChange}
                    sx={{
                      backgroundColor: "#333", 
                      color: "white", 
                      '& .MuiInputBase-root': {
                        color: 'white',
                      },
                    }}
                  />
                  <Button
                    variant="contained"
                    color="primary"
                    sx={{ mt: 2 }}
                    onClick={handleChatSubmit}
                    disabled={isChatting}
                  >
                    {isChatting ? "Processing..." : "Submit"}
                  </Button>

                    {/* Show error if any */}
                    {error && (
                    <Box sx={{ mt: 3 }}>
                        <Typography variant="h6" color="error">
                        Error: {error}
                        </Typography>
                    </Box>
                    )}
                    
                    {chatbotResponse && (
  <Box sx={{ mt: 3 }}>
    <Typography variant="h6" color="primary">
      Chatbot Suggestion:
    </Typography>
    <ul style={{ textAlign: "left", marginLeft: "20px" }}>
      {chatbotResponse.split("\n").map((point, index, arr) => {
        const trimmedPoint = point.trim();

        if (!trimmedPoint) return null;

        const isSubBullet = trimmedPoint.startsWith("-") || trimmedPoint.startsWith("•");

        return isSubBullet ? (
          <ul key={index} style={{ marginLeft: "20px" }}>
            <li>
              <Typography>{trimmedPoint.substring(1).trim()}</Typography>
            </li>
          </ul>
        ) : (
          <li key={index}>
            <Typography>{trimmedPoint}</Typography>
          </li>
        );
      })}
    </ul>
  </Box>
)}



                </CardContent>
                <Typography variant="h5" sx={{ mb: 3 }}>
            Your Current Spending: ${budget.toFixed(2)}
        </Typography>
              </Card>
            </Grid>
          </Grid>
        </Fade>
      </Box>
      <br></br>
      <br></br>
      <br></br>

      <Box sx={{ textAlign: "center", mt: 4 }}>
        <Button component={Link} to="/investment" variant="contained" color="primary" sx={{ padding: "10px 20px" }}>
          Go to Financial Assistant
        </Button>
      </Box>

      <Box
        component="footer"
        sx={{
          width: "100%",
          padding: "1rem",
          backgroundColor: "#1c1c1c",
          color: "white",
          textAlign: "center",
        }}
      >
        <Typography variant="body2">© {new Date().getFullYear()} Financial Assistant. All rights reserved.</Typography>
      </Box>
    </Box>
  );
};

export default BudgetOptimization;
