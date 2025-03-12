// DashboardOverview.js
import React from "react";
import { Box, Typography, Grid, Card, CardContent, Button } from "@mui/material";
import { Link } from "react-router-dom";
import { useSpring, animated } from "@react-spring/web";
import { Fade } from "react-awesome-reveal";
import Layout from "../components/Layout";
import DynamicGraphs from "../components/BudgetClassification";
import BudgetSummaryChart from "../components/BudgetSummaryChart";

const Dashboard = () => {
  const heroAnimation = useSpring({
    from: { opacity: 0, transform: "translateY(-20px)" },
    to: { opacity: 1, transform: "translateY(0)" },
    config: { duration: 1000 },
  });

  const currentBudget = "$5,000";
  const totalExpense = "$3,200";

  return (
    <Layout>
      <Box
        sx={{
          width: "100%",
          background: "radial-gradient(circle, #0f0f0f, #1c1c1c, #2f2f2f)",
          color: "white",
          minHeight: "100vh",
          paddingTop: "80px", // Ensures content does not hide behind header
          paddingBottom: "2rem",
        }}
      >
        {/* Animated Hero Section */}
        <animated.div style={heroAnimation}>
          <Typography variant="h3" sx={{ fontWeight: "bold", textAlign: "center", mb: 2 }}>
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

        {/* Visualizations */}
        <Fade triggerOnce>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card sx={{ backgroundColor: "#2f2f2f", color: "white" }}>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
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

            <Grid item xs={12} md={6}>
              <Card sx={{ backgroundColor: "#2f2f2f", color: "white" }}>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
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

        {/* Financial QA Button */}
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

      </Box>
    </Layout>
  );
};

export default Dashboard;
