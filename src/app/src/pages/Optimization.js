import React, { useEffect, useState } from "react";
import { Box, AppBar, Toolbar, Typography, Button, Grid, Collapse, Card,CardContent, TextField, List, ListItem, Divider } from "@mui/material";
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
  const [expandedCard, setExpandedCard] = useState(null); 
  const [isWarning, setIsWarning] = useState(false);
  const [estimatedSavings, setEstimatedSavings] = useState(null);
  const [savingsRange, setSavingsRange] = useState(""); // Optional: shows the low-high range
    
  const extractEstimatedSavings = (responseText) => {
    const regex = /Estimated Monthly Savings:\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\s*-\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)/gi;
  
    let totalLow = 0;
    let totalHigh = 0;
    let matchCount = 0;
    let match;
  
    while ((match = regex.exec(responseText)) !== null) {
      const low = parseFloat(match[1].replace(/,/g, ""));
      const high = parseFloat(match[2].replace(/,/g, ""));
      totalLow += low;
      totalHigh += high;
      matchCount++;
    }
  
    if (matchCount === 0) return { average: 0, rangeText: "$0 - $0" };
  
    const average = (totalLow + totalHigh) / 2;
    const rangeText = `$${totalLow.toFixed(0)} - $${totalHigh.toFixed(0)}`;
  
    return { average, rangeText };
  };
  

  useEffect(() => {
    const savedSpending = localStorage.getItem("categorizedSpending");
    if (savedSpending) {
      const parsedSpending = JSON.parse(savedSpending);
      setCategorySpending(parsedSpending);

      const totalBudget = Object.values(parsedSpending).reduce((sum, amount) => sum + amount, 0);
      setBudget(totalBudget);
    }
  }, []);

  const optimizeBudget = () => {
    console.log("Optimizing budget...");
    
    if (!categorySpending || Object.keys(categorySpending).length === 0) {
      setSuggestions("No spending data available. Please categorize transactions first.");
      return;
    }
  
    let advice = "\n";
    let flaggedCategories = [];
  
    const income = parseFloat(userDetails.income);
    const children = parseInt(userDetails.children);
    const maritalStatus = userDetails.maritalStatus.toLowerCase();
    const totalSpending = Object.values(categorySpending).reduce((sum, amount) => sum + amount, 0);

    if (income < totalSpending) {
      setIsWarning(true); 
      setChatbotResponse(""); 
      setSuggestions(
        "🚫 Your total monthly spending exceeds your stated income. Please review and adjust your income value before proceeding with optimization."
      );
      return;
    }
    setIsWarning(false); 

  
    let adjustedNeedsThreshold = income * 0.50;
    if (children > 0) adjustedNeedsThreshold += children * 0.02 * income;
    if (maritalStatus === "married") adjustedNeedsThreshold += 0.05 * income;

    let adjustedWantsThreshold = income * 0.30;
    if (maritalStatus === "single" && children === 0) adjustedWantsThreshold += 0.05 * income;

    let adjustedSavingsThreshold = income * 0.20;
    if (children > 2) adjustedSavingsThreshold -= 0.03 * income;
  
    let totalNeeds = 0;
    let totalWants = 0;
    let totalSavings = 0;
  
    Object.entries(categorySpending).forEach(([category, amount]) => {
      if (category === "Food" || category === "Housing" || category === "Transportation" || category === "Utilities" || category === "Insurance") {
        totalNeeds += amount;
        if (totalNeeds > adjustedNeedsThreshold) {
          advice += `⚠️ You are spending too much on Needs: ${category} (${amount.toFixed(2)}). Consider cutting back to stay within the 50% budget.\n`;
          flaggedCategories.push(category);
        } else {
          advice += `✅ Spending on ${category} (${amount.toFixed(2)}) is under control within your "Needs" category.\n`;
        }
      } else if (category === "Entertainment" || category === "Dining Out" || category === "Shopping" || category === "Travel") {
        totalWants += amount;
        if (totalWants > adjustedWantsThreshold) {
          advice += `⚠️ You are spending too much on Wants: ${category} (${amount.toFixed(2)}). Consider cutting back to stay within the 30% budget.\n`;
          flaggedCategories.push(category);
        } else {
          advice += `✅ Spending on ${category} (${amount.toFixed(2)}) is under control within your "Wants" category.\n`;
        }
      } else {
        totalSavings += amount;
        if (totalSavings < adjustedSavingsThreshold) {
          advice += `⚠️ You should increase your savings. Current savings amount: ${amount.toFixed(2)}. Aim for at least 20% of your income in savings.\n`;
          flaggedCategories.push(category);
        } else {
          advice += `✅ You are saving well with ${category} (${amount.toFixed(2)}) within your "Savings" category.\n`;
        }
      }
    });
  
    if (flaggedCategories.length === 0) {
      advice += "\n🎉 Congratulations! You are on track with your spending and savings. Keep up the good work!";
    } else {
      advice += "\n🔔 Consider adjusting your budget to better align with the 50/30/20 rule. By cutting back on non-essential spending and boosting savings, you can achieve a more balanced budget.";
    }
  
    setSuggestions(advice);  
    getChatbotResponse(flaggedCategories);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setUserDetails({ ...userDetails, [name]: value });
  };

  const validateInputs = () => {
    const age = parseInt(userDetails.age);
    const income = parseFloat(userDetails.income);
    const children = parseInt(userDetails.children);
    const maritalStatus = userDetails.maritalStatus.trim().toLowerCase();
  
    if (!/^\d{1,2}$/.test(userDetails.age) || age < 18 || age > 99) {
      setError("Age must be a number between 18 and 99.");
      return false;
    }
  
    if (!/^\d+(\.\d{1,2})?$/.test(userDetails.income) || income <= 0) {
      setError("Income must be a valid number greater than 0.");
      return false;
    }
  
    if (!/^\d+$/.test(userDetails.children) || children < 0 || children > 20) {
      setError("Children must be a positive integer between 0 and 20.");
      return false;
    }
  
    const validStatuses = ["single", "married", "divorced", "widowed"];
    if (!maritalStatus || !validStatuses.includes(maritalStatus)) {
      setError("Marital status must be one of the following: single, married, divorced, widowed.");
      return false;
    }
  
    if (maritalStatus === "single" && children > 3) {
      setError("Single users usually don't have more than 3 children — please confirm.");
      return false;
    }
  
    setError(null);
    return true;
  };
  

  const getChatbotResponse = (flaggedCategories) => {
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
  Monthly Spending Breakdown: ${JSON.stringify(categorySpending)} ${flaggedCategoriesText}.
  
  Based on the user's demographics and spending, provide personalized budget optimization suggestions. 
  
  - In grocery recommendations, include **different store names every time**, selected by you (the assistant), based on affordability and general popularity. Do not repeat the same stores across sessions.
  
  - Suggest specific action steps for groceries, shopping, travel, and other overspending areas. Suggest estimated monthly savings based on the user's profile.
  
  - Tailor recommendations to lifestyle stage and family size (e.g., saving tips for families with children vs. single young professionals).
  
  - End with a motivating and positive message. Ensure every response is **unique** and uses **varied store names** and examples.`,
        },
      ],
      temperature: 0.2,
    };
  
    axios.post(
      "https://api.groq.com/openai/v1/chat/completions",
      requestData,
      {
        headers: {
          Authorization: `Bearer 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`,
          "Content-Type": "application/json",
        },
      }
    )
    .then((response) => {
      if (response.data.choices && response.data.choices.length > 0) {
        const text = response.data.choices[0].message.content.trim();
        setChatbotResponse(text);
    
        // ⬇️ Use new savings extractor
        const { average, rangeText } = extractEstimatedSavings(text);
        if (!isNaN(average)) {
          setEstimatedSavings(average);
          setSavingsRange(rangeText);
        }
      } else {
        setChatbotResponse("No response from the model.");
      }
    })
    
    .catch((error) => {
      console.error("Error interacting with Groq Llama model:", error);
      setError("Sorry, there was an error. Please try again.");
    })
    .finally(() => {
      setIsChatting(false);
    });
  };
  
  const toggleCard = (category) => {
    if (expandedCard === category) {
      setExpandedCard(null); 
    } else {
      setExpandedCard(category); 
    }
  };
   
  const categorySuggestions = {
    Food: {
      under: "You're managing your food expenses well! Meal planning is paying off.",
      over: "Food costs are high. Try meal prepping and using store loyalty programs to cut back.",
    },
    Housing: {
      under: "Great job keeping housing costs stable. That's a solid foundation!",
      over: "Housing costs seem high. Consider negotiating rent or refinancing if possible.",
    },
    Shopping: {
      under: "Your shopping habits are within budget. Keep tracking discretionary spending.",
      over: "Too much on shopping? Try setting a fixed monthly limit or use cashback apps.",
    },
    Travel: {
      under: "You're managing travel costs well. Smart travel planning!",
      over: "Travel is eating into your budget. Try off-season bookings or loyalty points.",
    },
    Utilities: {
      under: "Utility spending is under control. Efficient energy usage helps!",
      over: "Utility bills are high. Consider turning off unused appliances or adjusting thermostat use.",
    },
    Insurance: {
      under: "Insurance expenses are optimized. Great job!",
      over: "Check if bundling policies or switching providers could save you on insurance.",
    },
    Entertainment: {
      under: "You are keeping entertainment costs low — that is a smart leisure balance.",
      over: "Entertainment is over budget. Look for free events or subscription sharing options.",
    },
    DiningOut: {
      under: "Dining out costs are modest. Nice job balancing convenience and savings.",
      over: "Cut back on eating out — try cooking more meals at home to save.",
    },
    Transportation: {
      under: "Transportation costs are efficient. Great use of transit or fuel management!",
      over: "Review transport costs. Carpooling or public transit could help.",
    },
    default: {
      under: "This category is well managed.",
      over: "You may want to review spending in this category.",
    }
  };
  
  
  const generateSummaryCards = () => {
    return Object.entries(categorySpending).map(([category, amount]) => {
      const isUnderControl = amount <= (parseFloat(userDetails.income) * 0.1);
      const cardTitle = `${category} - $${amount.toFixed(2)} (${isUnderControl ? "Under Control" : "Over Budget"})`;
      const cardColor = isUnderControl ? "#4CAF50" : "#FF9800";
      const iconColor = "#ffffff";
  
      const suggestion =
        categorySuggestions[category]?.[isUnderControl ? "under" : "over"] ||
        categorySuggestions["default"][isUnderControl ? "under" : "over"];
  
      return (
        <Grid item xs={12} md={6} key={category}>
          <Card
            sx={{
              backgroundColor: cardColor,
              color: "white",
              marginBottom: "20px",
              borderRadius: "10px",
              boxShadow: "0px 4px 12px rgba(0, 0, 0, 0.2)",
              '&:hover': {
                boxShadow: "0px 6px 18px rgba(0, 0, 0, 0.3)",
                transform: "scale(1.02)",
                transition: "all 0.3s ease-in-out",
              },
            }}
          >
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", cursor: "pointer" }} onClick={() => toggleCard(category)}>
                <Box sx={{ marginRight: "10px" }}>
                  <Typography sx={{ fontSize: "24px", color: iconColor }}>
                    {isUnderControl ? "✔️" : "⚠️"}
                  </Typography>
                </Box>
                <Typography sx={{ fontWeight: "bold", marginLeft: "8px" }} variant="h6">
                  {cardTitle}
                </Typography>
              </Box>
              <Collapse in={expandedCard === category} timeout="auto" unmountOnExit>
                <Typography variant="body2" sx={{ mt: 2, fontSize: "14px" }}>
                  {suggestion}
                </Typography>
              </Collapse>
            </CardContent>
          </Card>
        </Grid>
      );
    });
  };

  const navItems = [
    { name: 'ClassifyBot 💡', path: '/dashboard' },
    { name: 'Optimization', path: '/optimization' },
    { name: 'Investment', path: '/investment' },
    { name: 'News', path: '/FinancialNews' },
  ];

  return (
    <Box
      sx={{
        width: "100%",
        background: "radial-gradient(circle, #888888, #444444, #1c1c1c)",
        color: "white",
        minHeight: "100vh",
      }}
    >
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
              fontFamily: "'Segoe UI Emoji', 'Noto Color Emoji', sans-serif",
              fontWeight: "bold",
              mb: 4,
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
            <span style={{ fontSize: "2.5rem", lineHeight: 1 }}>💸</span>
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
              Budget Optimization
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
              Budget Optimization
            </span>
          </span>
          </Typography>

        </animated.div>

        <Fade triggerOnce>
          <Grid container spacing={3} justifyContent="center">
            <Grid item xs={12} md={6}>
              <Card sx={{ backgroundColor: "#2f2f2f", color: "white" }}>
                <CardContent>
                <Typography
                  variant="h5"
                  sx={{
                    mb: 4,
                    fontWeight: "medium",
                    fontSize: { xs: "1.25rem", md: "1.5rem" },
                    color: "#white",
                    textShadow: "0 0 8px rgba(255, 255, 255, 0.4)",
                    textAlign: "center",
                    letterSpacing: "0.5px",
                    
                  }}
                >
                  📝 Help us tailor your money plan:
                </Typography>
                  {[
                    { label: "Age", key: "age" },
                    { label: "Income", key: "income" },
                    { label: "Children", key: "children" },
                    { label: "Marital Status", key: "maritalStatus" },
                  ].map((field, index) => (
                    <TextField
                      label={field.label}
                      variant="outlined"
                      fullWidth
                      margin="normal"
                      name={field.key}
                      value={userDetails[field.key]}
                      onChange={handleInputChange}
                      InputLabelProps={{
                        sx: { color: "#bbb", fontWeight: "bold", fontSize: "1rem" },
                      }}
                      InputProps={{
                        sx: {
                          color: "white",
                          backgroundColor: "#1e1e1e",
                          borderRadius: "12px",
                          padding: "10px 14px",
                          "& .MuiOutlinedInput-notchedOutline": {
                            borderColor: "#444",
                          },
                          "&:hover .MuiOutlinedInput-notchedOutline": {
                            borderColor: "#888",
                          },
                          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                            borderColor: "#1976d2", 
                          },
                        },
                      }}
                      sx={{ mt: 2 }}
                    />

                  ))}
                  <Button variant="contained" color="primary" 
                  sx={{ 
                    mt: 2,
                    background: "linear-gradient(135deg, #4caf50, #388e3c)",
                    boxShadow: "0 4px 10px rgba(76, 175, 80, 0.3)",
                    borderRadius: "10px",
                    fontWeight: "bold",
                    padding: "10px 16px",
                    transition: "all 0.3s ease-in-out", 
                    '&:hover': {
                      background: "linear-gradient(135deg, #43e97b, #38f9d7)",
                      boxShadow: "0 8px 20px rgba(67, 233, 123, 0.4)",
                      transform: "scale(1.03)",
                    }}} 
                  onClick={optimizeBudget} disabled={isChatting} 
                  >
                    {isChatting ? "Processing..." : "Optimize Budget"}
                  </Button>
                  {isWarning && !chatbotResponse && (
                    <Typography
                      sx={{
                        mt: 3,
                        px: 3,
                        py: 2,
                        backgroundColor: "#ff4444",
                        borderRadius: "10px",
                        color: "#fff",
                        textAlign: "center",
                        fontWeight: "bold",
                        boxShadow: "0 0 10px rgba(255, 68, 68, 0.4)",
                      }}
                    >
                      {suggestions}
                    </Typography> 
                    
                  )}
                  <br></br>

                  {error && <Typography color="error">{error}</Typography>}
                  {chatbotResponse && (
                    <Box sx={{ mt: 3, textAlign: "left" }}>
                      <Typography variant="h5" sx={{ mb: 1, fontWeight: "bold" }}>
                        💡 Chatbot Suggestions:
                      </Typography>
                      <Divider sx={{ mb: 2, backgroundColor: "white" }} />

                      {/* Display Full Response */}
                      <Box sx={{ padding: 3 }}>
                          <List
                            sx={{
                              padding: 5,
                              borderRadius: "10px",
                              background: "radial-gradient(circle, #888888, #444444, #1c1c1c)",
                              backgroundSize: "200% 200%",
                              animation: "gradientFlow 15s ease infinite",
                              position: "relative",
                            }}
                          >
                            {chatbotResponse.split("\n").map((line, index) => (
                              <ListItem key={index} sx={{ display: "flex", alignItems: "center" }}>
                                {line.includes("✅") && (
                                  <Typography sx={{ color: "#4CAF50", fontWeight: "bold", mr: 1 }}>✔️</Typography>
                                )}
                                {line.includes("⚠️") && (
                                  <Typography sx={{ color: "#FF9800", fontWeight: "bold", mr: 1 }}>⚠️</Typography>
                                )}
                                {line.includes("💡") && (
                                  <Typography sx={{ color: "#03A9F4", fontWeight: "bold", mr: 1 }}>💡</Typography>
                                )}
                                <Typography sx={{ color: "#fff", fontSize: "14px" }}>{line}</Typography>
                              </ListItem>
                            ))}
                          </List>
                      </Box>
                    </Box>
                  )}
                  <Grid container spacing={3} justifyContent="center">
                    {suggestions && (generateSummaryCards())}
                  </Grid>
                  {estimatedSavings !== null && (
                  <Typography
                    variant="h5"
                    sx={{
                      mt: 3,
                      px: 3,
                      py: 2,
                      borderRadius: "12px",
                      color: "#4CAF50",
                      fontWeight: "bold",
                      textAlign: "center",
                      boxShadow: "0px 4px 12px rgba(0, 0, 0, 0.3)",
                      width: "fit-content",
                      mx: "auto",
                      fontSize: "1.25rem",
                      background: "radial-gradient(circle, #dfffdc, #a6e4a6, #7ed87e)",
                      backgroundSize: "400% 400%",
                      animation: "gradientFlow 6s ease infinite",
                    }}
                  >
                    💰 Estimated Monthly Savings: <span style={{ color: "#2e7d32" }}>${estimatedSavings.toFixed(2)}</span>
                    {savingsRange && <span style={{ color: "#666", fontSize: "0.9rem" }}> ({savingsRange})</span>}
                  </Typography>
                )}

                  <Typography
                    variant="h5"
                    sx={{
                      mt: 5,
                      px: 3,
                      py: 2,
                      borderRadius: "12px",
                      color: "white",
                      fontWeight: "bold",
                      textAlign: "center",
                      boxShadow: "0px 4px 12px rgba(0, 0, 0, 0.3)",
                      width: "fit-content",
                      mx: "auto",
                      fontSize: "1.25rem",
                      background: "radial-gradient(circle, #888888, #444444, #1c1c1c)",
                      backgroundSize: "400% 400%",
                      animation: "gradientFlow 6s ease infinite",
                    }}
                  >
                    💰 Your Current Spending: <span style={{ color: "#FFD700" }}>${budget.toFixed(2)}</span>
                  </Typography>
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
        🧠 Get Financial Advice
        </Button>
      </Box>

      <Box
        component="footer"
        sx={{
          width: "100%",
          padding: "1rem",
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
