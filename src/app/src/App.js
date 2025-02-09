import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import HomePage from "./pages/HomePage";
import DashboardPage from "./pages/DashboardPage";
import SignInPage from "./pages/Signin";
import SignUpPage from "./pages/Signup";
import "./styles/App.css";


const App = () => {
  return (
    <Router>
      <Routes>
        {/* Render HomePage as the default route */}
          <Route path="/index.html" element={<Navigate to="/" replace />} />
        <Route path="/" element={<HomePage />} />
        {/* Render DashboardPage on the /dashboard route */}
        <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/signin" element={<SignInPage />} />
        <Route path="/signup" element={<SignUpPage />} />
      </Routes>
    </Router>
  );
};

export default App;


