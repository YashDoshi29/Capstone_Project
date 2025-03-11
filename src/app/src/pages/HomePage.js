import React from "react";
import { Box, Typography, AppBar, Toolbar, Button } from "@mui/material";
import { useSpring, animated } from "@react-spring/web"; // For dynamic animations
import { Fade } from "react-awesome-reveal"; // For scroll-triggered animations
import DynamicGraphs from "../components/DynamicGraphs";
import BarChart from "../components/BarChart";
import DoughnutChart from "../components/DoughnutChart";
import { Link } from "react-router-dom";

const HomePage = () => {
  // Fade-in animation for the "Welcome" text
  const textAnimation = useSpring({
    from: { opacity: 0 },
    to: { opacity: 1 },
    config: { duration: 1200 },
  });

  return (
    <Box
      sx={{
        width: "100%",
        background: "radial-gradient(circle, #0f0f0f, #1c1c1c, #2f2f2f)",
        color: "white",
      }}
    >
      {/* Header (AppBar at the top) */}
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
              component={Link}
              to="/signin"
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
              component={Link}
              to='/signup'
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

      {/*
        Hero Section (full screen).
        - Welcome text at top
        - "Did You Know?" + Graph in the middle
      */}
      <Box
        sx={{
          minHeight: "100vh",            // Full viewport height
          display: "flex",
          flexDirection: "column",
          pt: 10,                        // Padding top (so heading isn't behind AppBar)
        }}
      >
        {/* Heading at the top */}
        <Box sx={{ textAlign: "center", mb: 6 }}>
          <animated.div style={textAnimation}>
            <Typography
              variant="h2"
              sx={{
                fontWeight: "bold",
                textShadow: "0px 0px 5px rgba(255, 255, 255, 0.3)",
                "&:hover": {
                  textShadow: "0px 0px 20px rgba(255, 255, 255, 0.6)",
                },
              }}
            >
              Welcome to Financial Freedom
            </Typography>
          </animated.div>
        </Box>

        {/* Centered container for "Did You Know?" + Graph */}
        <Box
          sx={{
            flex: 1,                     // Takes remaining vertical space
            display: "flex",
            alignItems: "center",        // Center vertically
            justifyContent: "center",    // Center horizontally
          }}
        >
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-around",
              alignItems: "flex-start",
              width: "100%",
              maxWidth: "1200px",
              px: "2rem",
              gap: "2rem",               // Horizontal gap between boxes
            }}
          >
            {/* Budget Fact (Did You Know?) */}
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

            {/* Dynamic Graph */}
            {/*<Fade triggerOnce direction="right">*/}
              <Box sx={{ flex: 2, maxWidth: "900px", width: "100%" }}>
                <DynamicGraphs />
              </Box>
            {/*</Fade>*/}
          </Box>
        </Box>
      </Box>

      {/* Next Section: Budget Optimization */}
      <Box
        sx={{
          width: "90%",
          maxWidth: "800px",
          margin: "4rem auto 0 auto",
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

      {/* Next Section: Investment.js Ideas */}
      <Box
        sx={{
          width: "90%",
          maxWidth: "800px",
          margin: "4rem auto",
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
