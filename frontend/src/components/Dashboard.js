import React, { useState } from "react";
import MetricsCards from "./MetricsCardsWithBackend";
import FatigueLevelDistribution from "./FatigueLevelDistributionWithBackend";
import TeamStatistics from "./TeamStatisticsWithBackend";
import PlayerOverview from "./PlayerOverviewWithBackend";
import "../styles/Dashboard.css";
import { exportDashboardData } from "../context/ExportExcel"; // Import the export function

const Dashboard = () => {
  const [buttonState, setButtonState] = useState("Export Dashboard Data"); // State for the export button

  const handleExportToExcel = () => {
    setButtonState("Fetching Data..."); // Temporarily update button text
    exportDashboardData(setButtonState); // Fetch data and export
  };

  return (
    <div className="dashboard">
      {/* Dashboard Header */}
      <div className="dashboard-header">
        <h1 className="text">Dashboard - Lakeside FC</h1>
        <button
          className={`button primary ${buttonState === "Fetching Data..." || buttonState === "Exporting..." ? "disabled" : ""}`}
          onClick={handleExportToExcel}
          disabled={buttonState === "Fetching Data..." || buttonState === "Exporting..."} // Disable button during export
        >
          {buttonState}
        </button>
      </div>

      {/* Dashboard Sections */}
      <div className="dashboard-layout">
        <div className="container team-statistics">
          <TeamStatistics />
        </div>
        <div className="container metrics-section">
          <MetricsCards />
        </div>
        <div className="container player-overview">
          <PlayerOverview />
        </div>
        <div className="container fatigue-level">
          <FatigueLevelDistribution />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
