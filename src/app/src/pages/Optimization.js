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
  const [isSummary, setIsSummary] = useState(true); 
  const [summaryText, setSummaryText] = useState(""); 



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
    console.log("Optimizing budget...");
    
    if (!categorySpending || Object.keys(categorySpending).length === 0) {
      setSuggestions("No spending data available. Please categorize transactions first.");
      return;
    }
  
    let advice = "\n";
    let flaggedCategories = [];
  
    const income = parseFloat(userDetails.income);
    const totalSpending = Object.values(categorySpending).reduce((sum, amount) => sum + amount, 0);

    if (income < totalSpending) {
      setChatbotResponse(""); 
      setSuggestions(
        "🚫 Your total monthly spending exceeds your stated income. Please review and adjust your income value before proceeding with optimization."
      );
      return;
    }
  
    const needsThreshold = income * 0.50;
    const wantsThreshold = income * 0.30; 
    const savingsThreshold = income * 0.20;
  
    let totalNeeds = 0;
    let totalWants = 0;
    let totalSavings = 0;
  
    Object.entries(categorySpending).forEach(([category, amount]) => {
      if (category === "Food" || category === "Housing" || category === "Transportation" || category === "Utilities" || category === "Insurance") {
        totalNeeds += amount;
        if (totalNeeds > needsThreshold) {
          advice += `⚠️ You are spending too much on Needs: ${category} (${amount.toFixed(2)}). Consider cutting back to stay within the 50% budget.\n`;
          flaggedCategories.push(category);
        } else {
          advice += `✅ Spending on ${category} (${amount.toFixed(2)}) is under control within your "Needs" category.\n`;
        }
      } else if (category === "Entertainment" || category === "Dining Out" || category === "Shopping" || category === "Travel") {
        totalWants += amount;
        if (totalWants > wantsThreshold) {
          advice += `⚠️ You are spending too much on Wants: ${category} (${amount.toFixed(2)}). Consider cutting back to stay within the 30% budget.\n`;
          flaggedCategories.push(category);
        } else {
          advice += `✅ Spending on ${category} (${amount.toFixed(2)}) is under control within your "Wants" category.\n`;
        }
      } else {
        totalSavings += amount;
        if (totalSavings < savingsThreshold) {
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
    await getChatbotResponse(flaggedCategories);
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
    Monthly Spending Breakdown: ${JSON.stringify(categorySpending)}${flaggedCategoriesText}.
    
    Based on the user's demographics and spending, provide personalized budget optimization suggestions. 

    - In grocery recommendations, include **different store names every time**, selected by you (the assistant), based on affordability and general popularity. Do not repeat the same stores across sessions.
    
    - Suggest specific action steps for groceries, shopping, travel, and other overspending areas. Suggest estimated monthly savings based on the user's profile.
    
    - Tailor recommendations to lifestyle stage and family size (e.g., saving tips for families with children vs. single young professionals).
    
    - End with a motivating and positive message. Ensure every response is **unique** and uses **varied store names** and examples.`,
        },
      ],
      temperature: 0.6,
    };

    try {
      const response = await axios.post(
        "https://api.groq.com/openai/v1/chat/completions",
        requestData,
        {
          headers: {
            Authorization: `Bearer "YOUR_API_KEY"`,
            "Content-Type": "application/json",
          },
        }
      );

      if (response.data.choices && response.data.choices.length > 0) {
        setChatbotResponse(response.data.choices[0].message.content.trim());
        await summarizeTextWithHuggingFace(response.data.choices[0].message.content.trim()); 
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

  const toggleCard = (category) => {
    if (expandedCard === category) {
      setExpandedCard(null); 
    } else {
      setExpandedCard(category); 
    }
  };

  const summarizeTextWithHuggingFace = async (chatbotResponse) => {
    try {
        const API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn";
        const API_KEY = "YOUR_API_KEY";  

        const prompt = `
        Summarize the following text in a concise and clear manner. Focus on the most important points and avoid unnecessary details. The summary should reflect key aspects such as spending categories (e.g., groceries, shopping, travel), amounts spent in each category, and practical tips for reducing costs.

        Ensure that the summary ends with an actionable recommendation for the user to optimize their budget effectively. The summary should not exceed 40 lines and must be specific, actionable, and directly related to the user's financial situation.

        Text to summarize:
        ${chatbotResponse}`;

        const response = await axios.post(API_URL, 

            {
                inputs: prompt,
                parameters: {
                  max_length: 500,  
                  min_length: 190,  
                  do_sample: false, 
              }
                
            }, 
            {
                headers: {
                    Authorization: `Bearer ${API_KEY}`,
                    "Content-Type": "application/json"
                }
                
            }
        );

        const summary = response.data[0].summary_text;
        console.log("Summary:", summary);
        setSummaryText(summary);  
    } catch (error) {
        console.error("Error while fetching summary:", error);
        setSummaryText("Error fetching summary.");
    }
};

  const toggleSummary = () => {
    setIsSummary(!isSummary);
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
            <span
              style={{
                background: "linear-gradient(135deg, rgb(221, 221, 221),rgb(61, 86, 145), #2b3c5b, rgb(189, 196, 206))",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                display: "inline-block",
                lineHeight: "1.4", 
                animation: "gradientFlow 6s ease infinite",
                backgroundSize: "600% 600%",

              }}
            >
              Budget Optimization
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
                  📝 Answer these questions to optimize your budget:
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
                            borderColor: "#1976d2", // Blue focus border
                          },
                        },
                      }}
                      sx={{ mt: 2 }}
                    />

                  ))}
                  <Button variant="contained" color="primary" sx={{ mt: 2 }} onClick={optimizeBudget} disabled={isChatting}>
                    {isChatting ? "Processing..." : "Optimize Budget"}
                  </Button>
                  {suggestions && !chatbotResponse && (
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
                      
                      {/* Toggle Button for Summary vs Full */}
                      <Box sx={{ textAlign: "center", mb: 2 }}>
                        <Button
                          variant="contained"
                          color="secondary"
                          onClick={toggleSummary}
                        >
                          {isSummary ? "View Summarized Suggestions" : "View Full Suggestions"}
                        </Button>
                      </Box>

                      {/* Display Full or Summarized Response */}
                      <Box sx={{ padding: 3 }}>
                        {isSummary ? (
                          <List
                            sx={{
                              padding: 5,
                              borderRadius: "10px",
                              background: "linear-gradient(135deg, rgb(12, 18, 29), #1e2a47, #2b3c5b, rgb(75, 96, 128))",
                              backgroundSize: "200% 200%",
                              animation: "gradientFlow 3s ease infinite",
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
                        )
                         : (
                          <List
                            sx={{
                              padding: 5,
                              borderRadius: "10px",
                              background: "linear-gradient(135deg, rgb(12, 18, 29), #1e2a47, #2b3c5b, rgb(75, 96, 128))",
                              backgroundSize: "200% 200%",
                              animation: "gradientFlow 3s ease infinite",
                              position: "relative",
                            }}
                          >
                            {summaryText.split("\n").map((line, index) => (
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
                        )}
                      </Box>
                    </Box>
                  )}
                  <Grid container spacing={3} justifyContent="center">
                    {suggestions && (generateSummaryCards())}
                  </Grid>
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
                      background: "linear-gradient(135deg, rgb(12, 18, 29), #1e2a47, #2b3c5b, rgb(75, 96, 128))",
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
