import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage"; // Import the HomePage component
import DashboardPage from "./pages/DashboardPage"; // Import the Dashboard page
// Removed Header import because the homepage has its own dynamic design

const App = () => {
  return (
    <Router>
      <Routes>
        {/* Render HomePage as the default route */}
        <Route path="/" element={<HomePage />} />
        {/* Render DashboardPage on the /dashboard route */}
        <Route path="/dashboard" element={<DashboardPage />} />
      </Routes>
    </Router>
  );
};

export default App;


