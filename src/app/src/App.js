import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import HomePage from "./pages/HomePage";
import SignInPage from "./pages/Signin";
import SignUpPage from "./pages/Signup";
import "./styles/App.css";
import Dashboard from "./pages/Dashboard";
import InvestmentPage from "./pages/Investment.js";
import FinancialNews from "./pages/FinancialNews.js";
import Optimization from "./pages/Optimization.js";
import Profile from "./pages/profile.js";
const App = () => {
  return (
    <Router>
      <Routes>
        {/* Render HomePage as the default route */}
          <Route path="/index.html" element={<Navigate to="/" replace />} />
        <Route path="/" element={<HomePage />} />
        {/* Render DashboardPage on the /dashboard route */}
        <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/signin" element={<SignInPage />} />
        <Route path="/signup" element={<SignUpPage />} />
        <Route path="/Investment" element={<InvestmentPage />} />
        <Route path="/financialnews" element={<FinancialNews />} />
        <Route path="/optimization" element={<Optimization />} />
        <Route path="/profile" element={<Profile />} />
        {/* Redirect any other route to the HomePage */}

      </Routes>
    </Router>
  );
};

export default App;