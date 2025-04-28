import React from "react";
import { Box, Typography, AppBar, Toolbar, Button, Grid, Container, Paper } from "@mui/material";
import { useSpring, animated } from "@react-spring/web"; // For dynamic animations
import { Fade } from "react-awesome-reveal"; // For scroll-triggered animations
import BudgetLineGraph from "../components/BudgetLineGraph";
import BudgetClassification from "../components/BudgetClassification";
import { Link } from "react-router-dom";
import AppFlowDiagram from '../components/AppFlowDiagram';

const HomePage = () => {
  // Fade-in animation for the "Welcome" text
  const textAnimation = useSpring({
    from: { opacity: 0, transform: 'translateY(20px)' },
    to: { opacity: 1, transform: 'translateY(0)' },
    config: { duration: 1200 },
  });

  const buttonAnimation = useSpring({
    from: { scale: 1 },
    to: { scale: 1.05 },
    config: { tension: 300, friction: 10 },
  });

  return (
    <Box
      sx={{
        width: "100%",
        background: "linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%)",
        color: "#ffffff",
        position: "relative",
        minHeight: "100vh",
      }}
    >
      {/* Header */}
      <AppBar
        position="absolute"
        sx={{
          background: "rgba(26, 26, 26, 0.8)",
          backdropFilter: "blur(10px)",
          boxShadow: "0 4px 30px rgba(0, 0, 0, 0.3)",
          width: "100%",
          zIndex: 2,
          padding: "0.5rem 1rem",
          borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
        }}
      >
        <Toolbar sx={{ justifyContent: "space-between" }}>
          <Typography
            variant="h6"
            sx={{
              fontWeight: "bold",
              color: "#ffffff",
              textShadow: "0px 0px 5px rgba(255, 255, 255, 0.3)",
              letterSpacing: "1px",
            }}
          >
            Credge AI
          </Typography>
          <Box>
            <Button
              component={Link}
              to="/signin"
              variant="outlined"
              sx={{
                color: "#ffffff",
                borderColor: "rgba(255, 255, 255, 0.3)",
                marginRight: "1rem",
                backdropFilter: "blur(5px)",
                "&:hover": {
                  backgroundColor: "rgba(255, 255, 255, 0.1)",
                  borderColor: "#ffffff",
                  transform: "translateY(-2px)",
                  transition: "all 0.3s ease",
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
                background: "linear-gradient(45deg, rgba(255, 255, 255, 0.9) 30%, rgba(255, 255, 255, 0.7) 90%)",
                color: "#1a1a1a",
                boxShadow: "0 3px 5px 2px rgba(255, 255, 255, .2)",
                "&:hover": {
                  background: "linear-gradient(45deg, rgba(255, 255, 255, 0.7) 30%, rgba(255, 255, 255, 0.9) 90%)",
                  transform: "translateY(-2px)",
                  transition: "all 0.3s ease",
                },
              }}
            >
              Sign Up
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Box sx={{ pt: 15 }}>
        {/* Hero Section */}
        <Box
          sx={{
            minHeight: "100vh",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            px: { xs: 2, md: 4 },
            position: "relative",
            "&::before": {
              content: '""',
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: "radial-gradient(circle at center, rgba(255, 255, 255, 0.1) 0%, transparent 70%)",
              pointerEvents: "none",
            }
          }}
        >
          <Container maxWidth="lg">
            <Grid container spacing={4} alignItems="center">
              <Grid item xs={12} md={6}>
                <Fade triggerOnce direction="left">
                  <Box>
                    <Typography
                      variant="h1"
                      sx={{
                        fontWeight: "bold",
                        color: "#ffffff",
                        fontSize: { xs: "3rem", md: "4.5rem" },
                        mb: 3,
                        lineHeight: 1.2,
                        textShadow: "0px 0px 10px rgba(255, 255, 255, 0.3)",
                      }}
                    >
                      Your Financial Future, Powered by AI
                    </Typography>
                    <Typography
                      variant="h5"
                      sx={{
                        color: "#b3b3b3",
                        mb: 4,
                        lineHeight: 1.6,
                        fontSize: { xs: "1.2rem", md: "1.5rem" },
                      }}
                    >
                      Experience the next generation of personal finance management. Our AI analyzes your spending patterns, optimizes your budget, and guides your investments.
                    </Typography>
                    <Box sx={{ display: "flex", gap: 2 }}>
                      <Button
                        variant="contained"
                        sx={{
                          background: "linear-gradient(45deg, rgba(255, 255, 255, 0.9) 30%, rgba(255, 255, 255, 0.7) 90%)",
                          color: "#1a1a1a",
                          boxShadow: "0 3px 5px 2px rgba(255, 255, 255, .2)",
                          "&:hover": {
                            background: "linear-gradient(45deg, rgba(255, 255, 255, 0.7) 30%, rgba(255, 255, 255, 0.9) 90%)",
                            transform: "translateY(-2px)",
                            transition: "all 0.3s ease",
                          },
                        }}
                      >
                        Get Started
                      </Button>
                      <Button
                        variant="outlined"
                        sx={{
                          color: "#ffffff",
                          borderColor: "rgba(255, 255, 255, 0.3)",
                          "&:hover": {
                            backgroundColor: "rgba(255, 255, 255, 0.1)",
                            borderColor: "#ffffff",
                            transform: "translateY(-2px)",
                            transition: "all 0.3s ease",
                          },
                        }}
                      >
                        Learn More
                      </Button>
                    </Box>
                  </Box>
                </Fade>
              </Grid>
              <Grid item xs={12} md={6}>
                <Fade triggerOnce direction="right">
                  <Paper
                    elevation={0}
                    sx={{
                      background: "rgba(26, 26, 26, 0.8)",
                      backdropFilter: "blur(10px)",
                      borderRadius: "20px",
                      padding: "2rem",
                      border: "1px solid rgba(255, 255, 255, 0.1)",
                      boxShadow: "0 8px 32px 0 rgba(0, 0, 0, 0.3)",
                      height: "500px",
                    }}
                  >
                    <BudgetLineGraph />
                  </Paper>
                </Fade>
              </Grid>
            </Grid>
          </Container>
        </Box>

        {/* Budget Classification Section */}
        <Box
          sx={{
            minHeight: "100vh",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            px: { xs: 2, md: 4 },
            background: "rgba(26, 26, 26, 0.5)",
            py: 8,
            position: "relative",
            "&::before": {
              content: '""',
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: "radial-gradient(circle at center, rgba(255, 255, 255, 0.05) 0%, transparent 70%)",
              pointerEvents: "none",
            }
          }}
        >
          <Container maxWidth="lg">
            <Grid container spacing={4} alignItems="center">
              <Grid item xs={12} md={6}>
                <Fade triggerOnce direction="left">
                  <Box>
                    <Typography
                      variant="h2"
                      sx={{
                        fontWeight: "bold",
                        color: "#ffffff",
                        fontSize: { xs: "2.5rem", md: "3.5rem" },
                        mb: 3,
                        textShadow: "0px 0px 10px rgba(255, 255, 255, 0.2)",
                      }}
                    >
                      Smart Budget Classification
                    </Typography>
                    <Typography
                      variant="h5"
                      sx={{
                        color: "#b3b3b3",
                        mb: 4,
                        lineHeight: 1.6,
                      }}
                    >
                      Our AI automatically categorizes your expenses, helping you understand your spending patterns and identify areas for optimization.
                    </Typography>
                    <Typography
                      variant="body1"
                      sx={{
                        color: "#b3b3b3",
                        mb: 2,
                        lineHeight: 1.8,
                      }}
                    >
                      • Automatic transaction categorization<br />
                      • Visual spending patterns<br />
                      • Easy-to-understand budget breakdown<br />
                      • Smart savings opportunities
                    </Typography>
                  </Box>
                </Fade>
              </Grid>
              <Grid item xs={12} md={6}>
                <Fade triggerOnce direction="right">
                  <Paper
                    elevation={0}
                    sx={{
                      background: "rgba(26, 26, 26, 0.8)",
                      backdropFilter: "blur(10px)",
                      borderRadius: "20px",
                      padding: "2rem",
                      border: "1px solid rgba(255, 255, 255, 0.1)",
                      boxShadow: "0 8px 32px 0 rgba(0, 0, 0, 0.3)",
                      height: "500px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <BudgetClassification />
                  </Paper>
                </Fade>
              </Grid>
            </Grid>
          </Container>
        </Box>

        {/* AI-Powered Recommendations Section */}
        <Box
          sx={{
            minHeight: "100vh",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            px: { xs: 2, md: 4 },
            background: "rgba(26, 26, 26, 0.5)",
            py: 8,
            position: "relative",
            "&::before": {
              content: '""',
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: "radial-gradient(circle at center, rgba(255, 255, 255, 0.05) 0%, transparent 70%)",
              pointerEvents: "none",
            }
          }}
        >
          <Container maxWidth="lg">
            <Grid container spacing={4} alignItems="center">
              <Grid item xs={12} md={6}>
                <Fade triggerOnce direction="left">
                  <Box>
                    <Typography
                      variant="h2"
                      sx={{
                        fontWeight: "bold",
                        color: "#ffffff",
                        fontSize: { xs: "2.5rem", md: "3.5rem" },
                        mb: 3,
                        textShadow: "0px 0px 10px rgba(255, 255, 255, 0.2)",
                      }}
                    >
                      AI-Powered Financial Insights
                    </Typography>
                    <Typography
                      variant="h5"
                      sx={{
                        color: "#b3b3b3",
                        mb: 4,
                        lineHeight: 1.6,
                      }}
                    >
                      Chat with our AI to get personalized financial advice and real-time budget optimization recommendations.
                    </Typography>
                    <Typography
                      variant="body1"
                      sx={{
                        color: "#b3b3b3",
                        mb: 2,
                        lineHeight: 1.8,
                      }}
                    >
                      • Personalized financial advice<br />
                      • Real-time budget optimization<br />
                      • Smart spending recommendations<br />
                      • Progress tracking and insights
                    </Typography>
                    <Button
                      variant="contained"
                      sx={{
                        mt: 4,
                        background: "linear-gradient(45deg, rgba(255, 255, 255, 0.9) 30%, rgba(255, 255, 255, 0.7) 90%)",
                        color: "#1a1a1a",
                        boxShadow: "0 3px 5px 2px rgba(255, 255, 255, .2)",
                        "&:hover": {
                          background: "linear-gradient(45deg, rgba(255, 255, 255, 0.7) 30%, rgba(255, 255, 255, 0.9) 90%)",
                          transform: "translateY(-2px)",
                          transition: "all 0.3s ease",
                        },
                      }}
                    >
                      Start Chatting with AI
                    </Button>
                  </Box>
                </Fade>
              </Grid>
              <Grid item xs={12} md={6}>
                <Fade triggerOnce direction="right">
                  <Paper
                    elevation={0}
                    sx={{
                      background: "rgba(26, 26, 26, 0.8)",
                      backdropFilter: "blur(10px)",
                      borderRadius: "20px",
                      padding: "2rem",
                      border: "1px solid rgba(255, 255, 255, 0.1)",
                      boxShadow: "0 8px 32px 0 rgba(0, 0, 0, 0.3)",
                      height: "500px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexDirection: "column",
                    }}
                  >
                    <Box
                      sx={{
                        width: "100%",
                        height: "100%",
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: 2,
                      }}
                    >
                      <Typography
                        variant="h4"
                        sx={{
                          color: "#ffffff",
                          textAlign: "center",
                          mb: 2,
                          textShadow: "0px 0px 10px rgba(255, 255, 255, 0.2)",
                        }}
                      >
                        Chat with Credge AI
                      </Typography>
                      <Typography
                        variant="body1"
                        sx={{
                          color: "#b3b3b3",
                          textAlign: "center",
                          mb: 4,
                        }}
                      >
                        Ask our AI assistant about your budget, get personalized recommendations, and receive actionable insights to improve your financial health.
                      </Typography>
                      <Button
                        variant="outlined"
                        sx={{
                          color: "#ffffff",
                          borderColor: "rgba(255, 255, 255, 0.3)",
                          "&:hover": {
                            backgroundColor: "rgba(255, 255, 255, 0.1)",
                            borderColor: "#ffffff",
                            transform: "translateY(-2px)",
                            transition: "all 0.3s ease",
                          },
                        }}
                      >
                        Try it now
                      </Button>
                    </Box>
                  </Paper>
                </Fade>
              </Grid>
            </Grid>
          </Container>
        </Box>

        {/* Smart Investment Advisor Section */}
        <Box
          sx={{
            minHeight: "100vh",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            px: { xs: 2, md: 4 },
            background: "rgba(26, 26, 26, 0.5)",
            py: 8,
            position: "relative",
            "&::before": {
              content: '""',
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: "radial-gradient(circle at center, rgba(255, 255, 255, 0.05) 0%, transparent 70%)",
              pointerEvents: "none",
            }
          }}
        >
          <Container maxWidth="lg">
            <Grid container spacing={4} alignItems="center">
              <Grid item xs={12} md={6}>
                <Fade triggerOnce direction="left">
                  <Box>
                    <Typography
                      variant="h2"
                      sx={{
                        fontWeight: "bold",
                        color: "#ffffff",
                        fontSize: { xs: "2.5rem", md: "3.5rem" },
                        mb: 3,
                        textShadow: "0px 0px 10px rgba(255, 255, 255, 0.2)",
                      }}
                    >
                      Smart Investment Advisor
                    </Typography>
                    <Typography
                      variant="h5"
                      sx={{
                        color: "#b3b3b3",
                        mb: 4,
                        lineHeight: 1.6,
                      }}
                    >
                      Get personalized investment recommendations based on your savings and risk profile. Our AI analyzes market trends and news to suggest the best investment opportunities.
                    </Typography>
                    <Typography
                      variant="body1"
                      sx={{
                        color: "#b3b3b3",
                        mb: 2,
                        lineHeight: 1.8,
                      }}
                    >
                      • AI-powered stock recommendations<br />
                      • Real-time market analysis<br />
                      • Risk assessment based on news sentiment<br />
                      • Personalized investment strategies<br />
                      • Portfolio optimization suggestions
                    </Typography>
                    <Button
                      variant="contained"
                      sx={{
                        mt: 4,
                        background: "linear-gradient(45deg, rgba(255, 255, 255, 0.9) 30%, rgba(255, 255, 255, 0.7) 90%)",
                        color: "#1a1a1a",
                        boxShadow: "0 3px 5px 2px rgba(255, 255, 255, .2)",
                        "&:hover": {
                          background: "linear-gradient(45deg, rgba(255, 255, 255, 0.7) 30%, rgba(255, 255, 255, 0.9) 90%)",
                          transform: "translateY(-2px)",
                          transition: "all 0.3s ease",
                        },
                      }}
                    >
                      Get Investment Advice
                    </Button>
                  </Box>
                </Fade>
              </Grid>
              <Grid item xs={12} md={6}>
                <Fade triggerOnce direction="right">
                  <Paper
                    elevation={0}
                    sx={{
                      background: "rgba(26, 26, 26, 0.8)",
                      backdropFilter: "blur(10px)",
                      borderRadius: "20px",
                      padding: "2rem",
                      border: "1px solid rgba(255, 255, 255, 0.1)",
                      boxShadow: "0 8px 32px 0 rgba(0, 0, 0, 0.3)",
                      height: "500px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexDirection: "column",
                    }}
                  >
                    <Box
                      sx={{
                        width: "100%",
                        height: "100%",
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: 2,
                      }}
                    >
                      <Typography
                        variant="h4"
                        sx={{
                          color: "#ffffff",
                          textAlign: "center",
                          mb: 2,
                          textShadow: "0px 0px 10px rgba(255, 255, 255, 0.2)",
                        }}
                      >
                        Investment Analysis Flow
                      </Typography>
                      <Box
                        sx={{
                          width: "100%",
                          display: "flex",
                          flexDirection: "column",
                          gap: 2,
                          p: 2,
                        }}
                      >
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 2,
                            p: 2,
                            background: "rgba(255, 255, 255, 0.1)",
                            borderRadius: "10px",
                            border: "1px solid rgba(255, 255, 255, 0.2)",
                          }}
                        >
                          <Typography variant="body1" sx={{ color: "#ffffff" }}>
                            1. Analyze your savings and risk profile
                          </Typography>
                        </Box>
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 2,
                            p: 2,
                            background: "rgba(255, 255, 255, 0.1)",
                            borderRadius: "10px",
                            border: "1px solid rgba(255, 255, 255, 0.2)",
                          }}
                        >
                          <Typography variant="body1" sx={{ color: "#ffffff" }}>
                            2. Scan market trends and news sentiment
                          </Typography>
                        </Box>
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 2,
                            p: 2,
                            background: "rgba(255, 255, 255, 0.1)",
                            borderRadius: "10px",
                            border: "1px solid rgba(255, 255, 255, 0.2)",
                          }}
                        >
                          <Typography variant="body1" sx={{ color: "#ffffff" }}>
                            3. Identify low-risk investment opportunities
                          </Typography>
                        </Box>
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 2,
                            p: 2,
                            background: "rgba(255, 255, 255, 0.1)",
                            borderRadius: "10px",
                            border: "1px solid rgba(255, 255, 255, 0.2)",
                          }}
                        >
                          <Typography variant="body1" sx={{ color: "#ffffff" }}>
                            4. Generate personalized recommendations
                          </Typography>
                        </Box>
                      </Box>
                      <Button
                        variant="outlined"
                        sx={{
                          color: "#ffffff",
                          borderColor: "rgba(255, 255, 255, 0.3)",
                          "&:hover": {
                            backgroundColor: "rgba(255, 255, 255, 0.1)",
                            borderColor: "#ffffff",
                            transform: "translateY(-2px)",
                            transition: "all 0.3s ease",
                          },
                        }}
                      >
                        View Investment Opportunities
                      </Button>
                    </Box>
                  </Paper>
                </Fade>
              </Grid>
            </Grid>
          </Container>
        </Box>

        {/* App Flow Diagram Section */}
        <Box
          sx={{
            minHeight: "100vh",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            px: { xs: 2, md: 4 },
            background: "rgba(26, 26, 26, 0.5)",
            py: 8,
            position: "relative",
            "&::before": {
              content: '""',
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: "radial-gradient(circle at center, rgba(255, 255, 255, 0.05) 0%, transparent 70%)",
              pointerEvents: "none",
            }
          }}
        >
          <Container maxWidth="lg">
            <Grid container spacing={4} alignItems="center">
              <Grid item xs={12}>
                <Fade triggerOnce direction="up">
                  <Box>
                    <Typography
                      variant="h2"
                      sx={{
                        fontWeight: "bold",
                        color: "#ffffff",
                        fontSize: { xs: "2.5rem", md: "3.5rem" },
                        mb: 3,
                        textAlign: "center",
                        textShadow: "0px 0px 10px rgba(255, 255, 255, 0.2)",
                      }}
                    >
                      How It Works
                    </Typography>
                    <Typography
                      variant="h5"
                      sx={{
                        color: "#b3b3b3",
                        mb: 4,
                        lineHeight: 1.6,
                        textAlign: "center",
                      }}
                    >
                      Our AI-powered platform combines advanced data generation, budget optimization, and investment analysis to provide comprehensive financial insights.
                    </Typography>
                  </Box>
                </Fade>
              </Grid>
              <Grid item xs={12}>
                <AppFlowDiagram />
              </Grid>
            </Grid>
          </Container>
        </Box>

        {/* Footer */}
        <Box
          component="footer"
          sx={{
            width: "100%",
            padding: "3rem",
            background: "rgba(26, 26, 26, 0.8)",
            backdropFilter: "blur(10px)",
            color: "#ffffff",
            textAlign: "center",
            marginTop: "2rem",
            borderTop: "1px solid rgba(255, 255, 255, 0.1)",
          }}
        >
          <Container maxWidth="lg">
            <Typography variant="h6" sx={{ mb: 2, color: "#ffffff" }}>
              Made with ❤️ to Empower Your Financial Future
            </Typography>
            <Typography variant="body1" sx={{ color: "#b3b3b3", mb: 2 }}>
              Credge AI is dedicated to helping you make smarter financial decisions and achieve your financial goals.
            </Typography>
            <Typography variant="body2" sx={{ color: "#666666" }}>
              © {new Date().getFullYear()} Credge AI. All rights reserved.
            </Typography>
          </Container>
        </Box>
      </Box>
    </Box>
  );
};

export default HomePage;
