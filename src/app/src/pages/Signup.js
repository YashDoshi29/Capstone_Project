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
  const [userName, setUserName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const validateForm = () => {
    if (!userName || !email || !password || !confirmPassword) {
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
      navigate("/profile");
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
      navigate("/profile");
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
                  label="Name"
                  variant="outlined"
                  value={userName}
                  onChange={(e) => setUserName(e.target.value)}
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
                  onClick={handleSignUp}
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : "Sign Up"}
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