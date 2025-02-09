import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import HomePage from "./pages/HomePage";
import SignInPage from "./pages/Signin";
import SignUpPage from "./pages/Signup";
import "./styles/App.css";
import Dashboard from "./pages/Dashboard";


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
      </Routes>
    </Router>
  );
};

export default App;