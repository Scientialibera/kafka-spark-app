import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./components/Dashboard";
import PlayersPage from "./pages/PlayersPage";
import TeamPage from "./pages/TeamPage";
import LiveDataPage from "./pages/LiveDataPage";
import "./App.css";

function App() {
  return (
    <div className="app-container">
      <Router>
        <Sidebar />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/players" element={<PlayersPage />} />
            <Route path="/team" element={<TeamPage />} />
            <Route path="/live-data" element={<LiveDataPage />} />
          </Routes>
        </div>
      </Router>
    </div>
  );
}

export default App;
