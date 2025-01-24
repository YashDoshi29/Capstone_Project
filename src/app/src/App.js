import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import DashboardPage from "./pages/DashboardPage";

const App = () => {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        {/* Add routes for other pages here */}
      </Routes>
    </Router>
  );
};

export default App;

