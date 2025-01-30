import React, { useState } from "react";
import { Box, TextField, Button, Typography, Paper, Divider } from "@mui/material";

const SignUpPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleSignUp = () => {
    // TODO: Add sign-up logic (e.g., call API, handle success/error)
    console.log("Email:", email);
    console.log("Password:", password);
    console.log("Confirm Password:", confirmPassword);
  };

  const handleGoogleSignUp = () => {
    // TODO: Google OAuth flow
    console.log("Signing up with Google...");
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
          Sign Up
        </Typography>
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
            onClick={handleSignUp}
          >
            Sign Up
          </Button>

          <Divider sx={{ my: 2, backgroundColor: "#333" }}>OR</Divider>

          {/* Google Sign-Up Button */}
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
            onClick={handleGoogleSignUp}
          >
            Sign Up with Google
          </Button>

          <Typography align="center" variant="body2">
            Already have an account? <a href="/src/app/src/pages/Signin">Sign In</a>
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default SignUpPage;
