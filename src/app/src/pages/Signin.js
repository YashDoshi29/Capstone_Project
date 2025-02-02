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
        background: "radial-gradient(circle, #0f0f0f, #1c1c1c, #2f2f2f)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        p: 2,
      }}
    >
      <Zoom in={true} style={{ transitionDelay: '100ms' }}>
        <Paper
          elevation={3}
          sx={{
            maxWidth: 400,
            width: "100%",
            p: 4,
            backgroundColor: "#1c1c1c",
            color: "white",
            transform: "translateY(0)",
            transition: "transform 0.3s ease",
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
                  background: "linear-gradient(45deg, #36A2EB, #4CAF50)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  fontWeight: 700
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
                      "& fieldset": { borderColor: "#ccc" },
                      "&:hover fieldset": { borderColor: "#36A2EB" }
                    },
                    "& .MuiInputLabel-root": { color: "#ccc" },
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
                      "& fieldset": { borderColor: "#ccc" },
                      "&:hover fieldset": { borderColor: "#36A2EB" }
                    },
                    "& .MuiInputLabel-root": { color: "#ccc" },
                    input: { color: "#fff" },
                  }}
                />
                <Button
                  variant="contained"
                  color="primary"
                  fullWidth
                  sx={{
                    mb: 2,
                    bgcolor: "#36A2EB",
                    "&:hover": {
                      bgcolor: "#2B8CD7",
                      transform: "scale(1.02)"
                    },
                    transition: "all 0.3s ease"
                  }}
                  onClick={handleSignIn}
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : "Sign In"}
                </Button>

                <Divider sx={{ my: 2, backgroundColor: "#333" }}>OR</Divider>

                <Button
                  variant="outlined"
                  fullWidth
                  sx={{
                    color: "#fff",
                    borderColor: "#ccc",
                    mb: 2,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: 1,
                    "&:hover": {
                      borderColor: "#36A2EB",
                      color: "#36A2EB",
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
                    color: "#ccc",
                    "& a": {
                      color: "#36A2EB",
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