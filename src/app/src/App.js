import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Box } from "@mui/material";
import HomePage from "./pages/HomePage";
import SignIn from "./pages/Signin";
import SignUp from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Optimization from "./pages/Optimization";
import Investment from "./pages/Investment";
import Profile from "./pages/profile";
import FinancialNews from "./pages/FinancialNews";
import Header from "./components/Header";

const App = () => {
  return (
    <Router>
      <Routes>
        {/* Public routes without header */}
        <Route path="/" element={<HomePage />} />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />

        {/* Protected routes with header */}
        <Route
          path="/dashboard"
          element={
            <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
              <Header />
              <Dashboard />
            </Box>
          }
        />
        <Route
          path="/optimization"
          element={
            <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
              <Header />
              <Optimization />
            </Box>
          }
        />
        <Route
          path="/investment"
          element={
            <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
              <Header />
              <Investment />
            </Box>
          }
        />
        <Route
          path="/profile"
          element={
            <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
              <Header />
              <Profile />
            </Box>
          }
        />
        <Route
          path="/FinancialNews"
          element={
            <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
              <Header />
              <FinancialNews />
            </Box>
          }
        />
      </Routes>
    </Router>
  );
};

export default App;