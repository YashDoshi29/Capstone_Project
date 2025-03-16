import React, { useEffect, useState } from "react";
import { Box, AppBar, Toolbar, Typography, Button, Grid, Card, CardContent, TextField, List, ListItem, Divider } from "@mui/material";
import { Link } from "react-router-dom";
import { useSpring, animated } from "@react-spring/web";
import { Fade } from "react-awesome-reveal";
import axios from "axios";

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

  const [categorySpending, setCategorySpending] = useState({});
  const [suggestions, setSuggestions] = useState("");
  const [budget, setBudget] = useState(0);
  const [chatbotResponse, setChatbotResponse] = useState("");
  const [isChatting, setIsChatting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const savedSpending = localStorage.getItem("categorizedSpending");
    if (savedSpending) {
      const parsedSpending = JSON.parse(savedSpending);
      setCategorySpending(parsedSpending);

      const totalBudget = Object.values(parsedSpending).reduce((sum, amount) => sum + amount, 0);
      setBudget(totalBudget);
    }
  }, []);

  const optimizeBudget = async () => {
    console.log("Optimizing budget..."); // Debugging log
    if (!categorySpending || Object.keys(categorySpending).length === 0) {
      setSuggestions("No spending data available. Please categorize transactions first.");
      return;
    }
  
    let advice = "\n";
    let flaggedCategories = [];
    Object.entries(categorySpending).forEach(([category, amount]) => {
      if (amount > 300) {
        advice += `⚠️ Consider reducing expenses in ${category} (${amount.toFixed(2)})\n`;
        flaggedCategories.push(category);
      } else {
        advice += `✅ Spending in ${category} (${amount.toFixed(2)}) is under control.\n`;
      }
    });

    setSuggestions(advice);
    await getChatbotResponse(flaggedCategories);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setUserDetails({ ...userDetails, [name]: value });
  };

  const validateInputs = () => {
    if (!/^\d{1,2}$/.test(userDetails.age) || parseInt(userDetails.age) < 18) {
      setError("Age must be a number, between 18 and 99.");
      return false;
    }
  
    if (!/^\d+(\.\d{1,2})?$/.test(userDetails.income)) {
      setError("Income must be a valid number.");
      return false;
    }
  
    if (!/^\d+$/.test(userDetails.children) || parseInt(userDetails.children) < 0) {
      setError("Children must be a positive integer.");
      return false;
    }

    const maritalStatus = userDetails.maritalStatus.trim().toLowerCase(); 
    if (!maritalStatus || !["single", "married", "divorced", "widowed"].includes(maritalStatus)) {
      setError("Marital status must be one of the following: single, married, divorced, widowed.");
      return false;
    }
  
    setError(null);
    return true;
  };

  const getChatbotResponse = async (flaggedCategories) => {
    if (!validateInputs()) return; 
    setIsChatting(true);
    setError(null);

    let flaggedCategoriesText = flaggedCategories.length > 0
      ? `The user is spending too much in these categories: ${flaggedCategories.join(", ")}. Provide recommendations on reducing expenses in these areas.`
      : "The user's spending is generally balanced.";

    const requestData = {
      model: "llama3-8b-8192",
      messages: [
        {
          role: "user",
          content: `User details: Age: ${userDetails.age}, Income: ${userDetails.income}, Children: ${userDetails.children}, Marital Status: ${userDetails.maritalStatus}. 
                    Monthly Spending Breakdown: ${JSON.stringify(categorySpending)}.
                    ${flaggedCategoriesText}
                    Given this data, suggest how the user can optimize their budget.
                    If the age and the children does not make sense, then highlight that part everytime.`,
        },
      ],
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
      setError("Sorry, there was an error. Please try again.");
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
                  {[
                  { label: "Age", key: "age" },
                  { label: "Income", key: "income" },
                  { label: "Children", key: "children" },
                  { label: "Marital Status", key: "maritalStatus" }, 
                ].map((field, index) => (
                  <TextField
                    key={index}
                    label={field.label}
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    name={field.key} 
                    value={userDetails[field.key]} 
                    onChange={handleInputChange}
                    sx={{
                      backgroundColor: "#333",
                      color: "white",
                      '& .MuiInputBase-root': { color: 'white' },
                    }}
                  />
                ))}
                  <Button variant="contained" color="primary" sx={{ mt: 2 }} onClick={optimizeBudget} disabled={isChatting}>
                    {isChatting ? "Processing..." : "Optimize Budget"}
                  </Button>

                  {error && <Typography color="error">{error}</Typography>}
                  {chatbotResponse && (
                    <Box sx={{ mt: 3, textAlign: "left" }}>
                      <Typography variant="h5" sx={{ mb: 1, fontWeight: "bold" }}>
                        💡 Chatbot Suggestions:
                      </Typography>
                      <Divider sx={{ mb: 2, backgroundColor: "white" }} />

                      <List
                        sx={{
                          padding: 5,
                          borderRadius: "10px",
                          background: "linear-gradient(135deg,rgb(12, 18, 29), #1e2a47, #2b3c5b,rgb(75, 96, 128))",
                          backgroundSize: "200% 200%",
                          animation: "gradientFlow 3s ease infinite",
                          position: "relative", 
                        }}
                      >
                        
                        {chatbotResponse.split("\n").map((line, index) => (
                          <ListItem key={index} sx={{ display: "flex", alignItems: "center" }}>
                            {line.includes("✅") && <Typography sx={{ color: "#4CAF50", fontWeight: "bold", mr: 1 }}>✔️</Typography>}
                            {line.includes("⚠️") && <Typography sx={{ color: "#FF9800", fontWeight: "bold", mr: 1 }}>⚠️</Typography>}
                            {line.includes("💡") && <Typography sx={{ color: "#03A9F4", fontWeight: "bold", mr: 1 }}>💡</Typography>}
                            <Typography>{line}</Typography>
                          </ListItem>
                        ))}
                        {suggestions && (
                          <Box sx={{ mt: 3 }}>
                            <Typography variant="h6" color="White">
                            Overall Budget Review:
                            </Typography><br></br>
                            <Box sx={{ paddingLeft: "20px" }}>
                              {Array.isArray(suggestions)
                                ? suggestions
                                    .filter((suggestion) => suggestion.trim() !== "")
                                    .map((suggestion, index) => (
                                      <Typography key={index} sx={{ display: "block", mb: 1 }}>
                                        {suggestion.replace(/\b(\d+(\.\d{1,2})?)\b/g, '$$$1')} {}
                                      </Typography>
                                    ))
                                : suggestions
                                    .split("\n") 
                                    .filter((suggestion) => suggestion.trim() !== "") 
                                    .map((suggestion, index) => (
                                      <Typography key={index} sx={{ display: "block", mb: 1 }}>
                                        {suggestion.replace(/\b(\d+(\.\d{1,2})?)\b/g, '$$$1')} {}
                                      </Typography>
                                    ))}
                            </Box>
                          </Box>
                        )}

                      </List>
                    </Box>
                  )}
                  <Typography variant="h5" sx={{ mt: 3 }}>💰 Your Current Spending: ${budget.toFixed(2)}</Typography>
                </CardContent>
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
