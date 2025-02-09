import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
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
import { auth, googleProvider } from "../firebaseConfig";
import { createUserWithEmailAndPassword, signInWithPopup } from "firebase/auth";
import GoogleIcon from "@mui/icons-material/Google";

const SignUpPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const validateForm = () => {
    if (!email || !password || !confirmPassword) {
      setError("All fields are required");
      return false;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return false;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return false;
    }
    return true;
  };

  const handleSignUp = async () => {
    if (!validateForm()) return;

    setLoading(true);
    setError("");

    try {
      await createUserWithEmailAndPassword(auth, email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignUp = async () => {
    setLoading(true);
    setError("");

    try {
      await signInWithPopup(auth, googleProvider);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
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
                Create Account
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

                <TextField
                  fullWidth
                  label="Confirm Password"
                  variant="outlined"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
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
                  onClick={handleSignUp}
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : "Sign Up"}
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
                  onClick={handleGoogleSignUp}
                  disabled={loading}
                >
                  <GoogleIcon />
                  Sign Up with Google
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
                  Already have an account?{' '}
                  <a href="/signin">Sign In</a>
                </Typography>
              </Box>
            </div>
          </Fade>
        </Paper>
      </Zoom>
    </Box>
  );
};

export default SignUpPage;