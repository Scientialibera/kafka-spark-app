import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import RegisterPage from "./pages/RegisterPage";
import LoginPage from "./pages/LoginPage";
import Sidebar from "./components/Sidebar";
import Dashboard from "./components/Dashboard";
import PlayersPage from "./pages/PlayersPage";
import TeamPage from "./pages/TeamPage";
import LiveDataPage from "./pages/LiveDataPage";
import "./App.css";

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes: Login and Register */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Private Routes: Include Sidebar */}
        <Route
          path="/*"
          element={
            <div className="app-container">
              <Sidebar />
              <div className="main-content">
                <Routes>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/players" element={<PlayersPage />} />
                  <Route path="/team" element={<TeamPage />} />
                  <Route path="/live-data" element={<LiveDataPage />} />
                  <Route path="*" element={<Navigate to="/dashboard" />} />
                </Routes>
              </div>
            </div>
          }
        />

        {/* Default Route */}
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}

export default App;
