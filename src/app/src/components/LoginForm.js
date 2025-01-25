import React, { useState } from "react";
import { Box, TextField, Button, Typography } from "@mui/material";

const LoginForm = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle login logic here
    console.log("Login:", { email, password });
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{
        display: "flex",
        flexDirection: "column",
        gap: "1rem",
        backgroundColor: "white",
        padding: "2rem",
        borderRadius: "10px",
        boxShadow: "0 4px 10px rgba(0,0,0,0.2)",
        width: "100%",
        maxWidth: "400px",
        margin: "auto",
      }}
    >
      <Typography variant="h5" sx={{ textAlign: "center", marginBottom: "1rem" }}>
        Login
      </Typography>
      <TextField
        label="Email"
        type="email"
        variant="outlined"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <TextField
        label="Password"
        type="password"
        variant="outlined"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <Button type="submit" variant="contained" color="primary">
        Login
      </Button>
    </Box>
  );
};

export default LoginForm;
