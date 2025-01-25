import React from "react";
import { Box, Typography, AppBar, Toolbar, Button } from "@mui/material";
import { useSpring, animated } from "@react-spring/web"; // For dynamic animations
import { Fade } from "react-awesome-reveal"; // For scroll-triggered animations
import DynamicGraphs from "../components/DynamicGraphs"; // Line graph
import BarChart from "../components/BarChart"; // Bar chart
import DoughnutChart from "../components/DoughnutChart"; // Doughnut chart

const HomePage = () => {
  // Fade-in animation for welcome text
  const textAnimation = useSpring({
    from: { opacity: 0 },
    to: { opacity: 1 },
    config: { duration: 1200 },
  });

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "radial-gradient(circle, #0f0f0f, #1c1c1c, #2f2f2f)",
        color: "white",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        overflowX: "hidden",
        position: "relative",
      }}
    >
      {/* Header */}
      <AppBar
        position="absolute"
        sx={{
          background: "transparent",
          boxShadow: "none",
          width: "100%",
          zIndex: 2,
          padding: "0.5rem 1rem",
        }}
      >
        <Toolbar sx={{ justifyContent: "space-between" }}>
          <Typography
            variant="h6"
            sx={{
              fontWeight: "bold",
              color: "white",
              textShadow: "0px 0px 5px rgba(255, 255, 255, 0.5)",
            }}
          >
            Financial Assistant
          </Typography>
          <Box>
            <Button
              variant="outlined"
              sx={{
                color: "white",
                borderColor: "white",
                marginRight: "1rem",
                "&:hover": {
                  backgroundColor: "rgba(255, 255, 255, 0.1)",
                },
              }}
            >
              Sign In
            </Button>
            <Button
              variant="contained"
              sx={{
                backgroundColor: "#36A2EB",
                "&:hover": {
                  backgroundColor: "#1c82d0",
                },
              }}
            >
              Sign Up
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Welcome Text */}
      <animated.div style={textAnimation}>
        <Typography
          variant="h2"
          sx={{
            fontWeight: "bold",
            textAlign: "center",
            marginTop: "6rem",
            textShadow: "0px 0px 5px rgba(255, 255, 255, 0.3)",
            "&:hover": {
              textShadow: "0px 0px 20px rgba(255, 255, 255, 0.6)",
            },
          }}
        >
          Welcome to Financial Freedom
        </Typography>
      </animated.div>

      {/* Dynamic Line Graph and Budget Fact */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-around",
          alignItems: "center",
          width: "100%",
          marginTop: "4rem",
        }}
      >
        {/* Budget Fact */}
        <Fade triggerOnce direction="left">
          <Box
            sx={{
              flex: 1,
              padding: "2rem",
              textAlign: "left",
              color: "#b0b0b0",
              maxWidth: "400px",
            }}
          >
            <Typography variant="h5" sx={{ marginBottom: "1rem", fontWeight: "bold" }}>
              Did You Know?
            </Typography>
            <Typography variant="body1">
              The average household spends 30% of its income on housing, while
              only 10% is allocated to savings. Optimize your budget with our
              tools!
            </Typography>
          </Box>
        </Fade>

        {/* Dynamic Line Graph */}
        <Fade triggerOnce direction="right">
          <Box sx={{ flex: 2, width: "70%", maxWidth: "800px" }}>
            <DynamicGraphs />
          </Box>
        </Fade>
      </Box>

      {/* Section: Budget Optimization (Hidden Initially) */}
      <Box
        sx={{
          width: "90%",
          maxWidth: "800px",
          marginTop: "10rem", // Ensure it's below the viewport
          textAlign: "center",
        }}
      >
        <Fade triggerOnce>
          <Typography
            variant="h4"
            sx={{
              marginBottom: "1rem",
              "&:hover": {
                textShadow: "0px 0px 15px rgba(54, 162, 235, 0.8)",
              },
            }}
          >
            Budget Optimization Insights
          </Typography>
          <Typography variant="body1" sx={{ marginBottom: "2rem", color: "#b0b0b0" }}>
            Explore how you can optimize your monthly budget and reduce unnecessary
            expenses with these insights.
          </Typography>
          <BarChart />
        </Fade>
      </Box>

      {/* Section: Investment Ideas (Hidden Initially) */}
      <Box
        sx={{
          width: "90%",
          maxWidth: "800px",
          marginTop: "4rem",
          textAlign: "center",
        }}
      >
        <Fade triggerOnce>
          <Typography
            variant="h4"
            sx={{
              marginBottom: "1rem",
              "&:hover": {
                textShadow: "0px 0px 15px rgba(255, 99, 132, 0.8)",
              },
            }}
          >
            Investment Ideas
          </Typography>
          <Typography variant="body1" sx={{ marginBottom: "2rem", color: "#b0b0b0" }}>
            Learn how to grow your wealth by making informed investment decisions.
          </Typography>
          <DoughnutChart />
        </Fade>
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
          marginTop: "2rem",
        }}
      >
        <Typography variant="body2">
          © {new Date().getFullYear()} Financial Assistant. All rights reserved.
        </Typography>
      </Box>
    </Box>
  );
};

export default HomePage;
