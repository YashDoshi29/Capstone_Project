// DashboardOverview.js
import React from "react";
import { Box, Typography, AppBar, Toolbar, Button, Grid, Card, CardContent } from "@mui/material";
import { Link } from "react-router-dom";
import { useSpring, animated } from "@react-spring/web";
import { Fade } from "react-awesome-reveal";

// Import your chart components (replace these with your actual implementations)
import DynamicGraphs from "../components/BudgetClassification"; // For budget classification visualization
import BudgetSummaryChart from "../components/BudgetSummaryChart"; // For additional budget summary visualization

const Dashboard = () => {
  // Animate the hero header for a smooth entrance effect
  const heroAnimation = useSpring({
    from: { opacity: 0, transform: "translateY(-20px)" },
    to: { opacity: 1, transform: "translateY(0)" },
    config: { duration: 1000 },
  });

  // Example dynamic values (replace these with data from your backend or state)
  const currentBudget = "$5,000";
  const totalExpense = "$3,200";

  return (
    <Box
      sx={{
        width: "100%",
        background: "radial-gradient(circle, #0f0f0f, #1c1c1c, #2f2f2f)",
        color: "white",
        minHeight: "100vh",
      }}
    >
      {/* Navigation Panel */}
      <AppBar
        position="fixed"
        sx={{
          background: "transparent",
          boxShadow: "none",
          width: "100%",
          zIndex: 2,
          padding: "0.5rem 1rem",
        }}
      >
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
            <Button component={Link} to="/investment" variant="text" sx={{ color: "white" }}>
              Investment
            </Button>
            <Button
              component={Link}
              to="/expense-optimization"
              variant="text"
              sx={{ color: "white" }}
            >
              Expense Optimization
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Hero Section and Overview Stats */}
      <Box sx={{ pt: "80px", px: "2rem", pb: "2rem" }}>
        <animated.div style={heroAnimation}>
          <Typography
            variant="h3"
            sx={{ fontWeight: "bold", textAlign: "center", mb: 2 }}
          >
            Dashboard Overview
          </Typography>
        </animated.div>

        {/* Overview Statistics */}
        <Grid container spacing={3} justifyContent="center" sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ backgroundColor: "#2f2f2f", color: "white" }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                  Current Budget
                </Typography>
                <Typography variant="h4">{currentBudget}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ backgroundColor: "#2f2f2f", color: "white" }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                  Total Expense
                </Typography>
                <Typography variant="h4">{totalExpense}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Dynamic Visualization Section */}
        <Fade triggerOnce>
          <Grid container spacing={3}>
            {/* Budget Classification Visualization */}
            <Grid item xs={12} md={6}>
              <Card sx={{ backgroundColor: "#2f2f2f", color: "white" }}>
                <CardContent>
                  <Typography
                    variant="h6"
                    sx={{ fontWeight: "bold", mb: 2 }}
                  >
                    Budget Classification
                  </Typography>
                  <Box
                    sx={{
                      height: "300px",
                      background: "#1c1c1c",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <DynamicGraphs />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Additional Visualization: Budget Summary */}
            <Grid item xs={12} md={6}>
              <Card sx={{ backgroundColor: "#2f2f2f", color: "white" }}>
                <CardContent>
                  <Typography
                    variant="h6"
                    sx={{ fontWeight: "bold", mb: 2 }}
                  >
                    Budget Summary
                  </Typography>
                  <Box
                    sx={{
                      height: "300px",
                      background: "#1c1c1c",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <BudgetSummaryChart />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Fade>
      </Box>

      <Box sx={{ textAlign: "center", mt: 4 }}>
          <Button
            component={Link}
            to="/financial-qa"
            variant="contained"
            color="primary"
            sx={{ padding: "10px 20px" }}
          >
            Go to Financial QA Chatbot
          </Button>
        </Box>
      

      {/* Footer */}
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
        <Typography variant="body2">
          © {new Date().getFullYear()} Financial Assistant. All rights reserved.
        </Typography>
      </Box>
    </Box>
  );
};

export default Dashboard;