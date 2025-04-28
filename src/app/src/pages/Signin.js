import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { auth, googleProvider } from "../firebaseConfig";
import { signInWithEmailAndPassword, signInWithPopup } from "firebase/auth";
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Divider,
  CircularProgress,
  Alert,
  Fade,
  Zoom
} from "@mui/material";
import GoogleIcon from "@mui/icons-material/Google";

const SignInPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignIn = async () => {
    if (!email || !password) {
      setError("Please fill in all fields");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await signInWithEmailAndPassword(auth, email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(mapAuthError(err.code));
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setLoading(true);
    setError("");

    try {
      await signInWithPopup(auth, googleProvider);
      navigate("/dashboard");
    } catch (err) {
      setError(mapAuthError(err.code));
    } finally {
      setLoading(false);
    }
  };

  const mapAuthError = (code) => {
    switch (code) {
      case "auth/invalid-email":
        return "Invalid email format";
      case "auth/user-disabled":
        return "Account disabled";
      case "auth/user-not-found":
        return "No account found with this email";
      case "auth/wrong-password":
        return "Incorrect password";
      case "auth/popup-closed-by-user":
        return "Google sign-in was canceled";
      default:
        return "Login failed. Please try again.";
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        p: 2,
      }}
    >
      <Zoom in={true} style={{ transitionDelay: '100ms' }}>
        <Paper
          elevation={0}
          sx={{
            maxWidth: 400,
            width: "100%",
            p: 4,
            background: "rgba(26, 26, 26, 0.8)",
            backdropFilter: "blur(10px)",
            color: "white",
            transform: "translateY(0)",
            transition: "transform 0.3s ease",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            boxShadow: "0 8px 32px 0 rgba(0, 0, 0, 0.3)",
            '&:hover': {
              transform: "translateY(-2px)"
            }
          }}
        >
          <Fade in={true} timeout={500}>
            <div>
              <Typography
                variant="h4"
                align="center"
                gutterBottom
                sx={{
                  color: "#ffffff",
                  fontWeight: 700,
                  textShadow: "0px 0px 10px rgba(255, 255, 255, 0.2)",
                }}
              >
                Welcome Back
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              <Box component="form" noValidate autoComplete="off" sx={{ mt: 2 }}>
                <TextField
                  fullWidth
                  label="Email"
                  variant="outlined"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  sx={{
                    mb: 2,
                    "& .MuiOutlinedInput-root": {
                      "& fieldset": { borderColor: "rgba(255, 255, 255, 0.3)" },
                      "&:hover fieldset": { borderColor: "rgba(255, 255, 255, 0.5)" }
                    },
                    "& .MuiInputLabel-root": { color: "rgba(255, 255, 255, 0.7)" },
                    input: { color: "#fff" },
                  }}
                />
                <TextField
                  fullWidth
                  label="Password"
                  variant="outlined"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  sx={{
                    mb: 2,
                    "& .MuiOutlinedInput-root": {
                      "& fieldset": { borderColor: "rgba(255, 255, 255, 0.3)" },
                      "&:hover fieldset": { borderColor: "rgba(255, 255, 255, 0.5)" }
                    },
                    "& .MuiInputLabel-root": { color: "rgba(255, 255, 255, 0.7)" },
                    input: { color: "#fff" },
                  }}
                />
                <Button
                  variant="contained"
                  fullWidth
                  sx={{
                    mb: 2,
                    background: "linear-gradient(45deg, rgba(255, 255, 255, 0.9) 30%, rgba(255, 255, 255, 0.7) 90%)",
                    color: "#1a1a1a",
                    boxShadow: "0 3px 5px 2px rgba(255, 255, 255, .2)",
                    "&:hover": {
                      background: "linear-gradient(45deg, rgba(255, 255, 255, 0.7) 30%, rgba(255, 255, 255, 0.9) 90%)",
                      transform: "scale(1.02)"
                    },
                    transition: "all 0.3s ease"
                  }}
                  onClick={handleSignIn}
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : "Sign In"}
                </Button>

                <Divider sx={{ my: 2, backgroundColor: "rgba(255, 255, 255, 0.1)" }}>OR</Divider>

                <Button
                  variant="outlined"
                  fullWidth
                  sx={{
                    color: "#ffffff",
                    borderColor: "rgba(255, 255, 255, 0.3)",
                    mb: 2,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: 1,
                    "&:hover": {
                      backgroundColor: "rgba(255, 255, 255, 0.1)",
                      borderColor: "#ffffff",
                      transform: "scale(1.02)"
                    },
                    transition: "all 0.3s ease"
                  }}
                  onClick={handleGoogleSignIn}
                  disabled={loading}
                >
                  <GoogleIcon />
                  Sign In with Google
                </Button>

                <Typography
                  align="center"
                  variant="body2"
                  sx={{
                    color: "rgba(255, 255, 255, 0.7)",
                    "& a": {
                      color: "#ffffff",
                      textDecoration: "none",
                      "&:hover": {
                        textDecoration: "underline"
                      }
                    }
                  }}
                >
                  Don't have an account?{' '}
                  <a href="/signup">Create Account</a>
                </Typography>
              </Box>
            </div>
          </Fade>
        </Paper>
      </Zoom>
    </Box>
  );
};

export default SignInPage;