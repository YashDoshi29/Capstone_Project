import React, { useState } from "react";
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Divider
} from "@mui/material";
import { useNavigate } from "react-router-dom";

const SignInPage = () => {
  const navigate = useNavigate();

  // Form fields
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // For error messages or success states
  const [error, setError] = useState("");

  const handleSignIn = async () => {
    setError(""); // Clear previous errors

    try {
      // Example: Call a backend login endpoint
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        // e.g. 401 means unauthorized
        const msg = await response.json();
        setError(msg.error || "Invalid email or password");
        return;
      }

      // If returning token in JSON: { token: "..." }
      const data = await response.json();
      const { token } = data;

      // Store token in localStorage (or in an HTTP-only cookie on the server)
      localStorage.setItem("authToken", token);

      // Redirect to a protected route, e.g. /dashboard
      navigate("/dashboard");
    } catch (err) {
      // Catch fetch or network errors
      console.error(err);
      setError("Something went wrong. Please try again.");
    }
  };

  const handleGoogleSignIn = () => {
    // TODO: Implement Google OAuth flow
    console.log("Signing in with Google...");
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
      <Paper
        elevation={3}
        sx={{
          maxWidth: 400,
          width: "100%",
          p: 4,
          backgroundColor: "#1c1c1c",
          color: "white",
        }}
      >
        <Typography variant="h4" align="center" gutterBottom>
          Sign In
        </Typography>

        {/* Display any error messages */}
        {error && (
          <Typography
            variant="body2"
            sx={{ color: "red", textAlign: "center", mb: 2 }}
          >
            {error}
          </Typography>
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
                "& fieldset": {
                  borderColor: "#ccc",
                },
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
                "& fieldset": {
                  borderColor: "#ccc",
                },
              },
              "& .MuiInputLabel-root": { color: "#ccc" },
              input: { color: "#fff" },
            }}
          />
          <Button
            variant="contained"
            color="primary"
            fullWidth
            sx={{ mb: 2 }}
            onClick={handleSignIn}
          >
            Sign In
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
            }}
            onClick={handleGoogleSignIn}
          >
            {/* <GoogleIcon sx={{ mr: 1 }} />  optionally include a Google icon */}
            Sign In with Google
          </Button>

          <Typography align="center" variant="body2">
            Don&rsquo;t have an account?{" "}
            <a href="/signup" style={{ color: "#36A2EB" }}>
              Sign Up
            </a>
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default SignInPage;
