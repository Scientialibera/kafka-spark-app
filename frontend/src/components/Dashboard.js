import React from "react";
import MetricsCards from "./MetricsCardsWithBackend";
import FatigueLevelDistribution from "./FatigueLevelDistributionWithBackend";
import TeamStatistics from "./TeamStatisticsWithBackend";
import PlayerOverview from "./PlayerOverview";
import "../styles/Dashboard.css";

const Dashboard = () => {
  return (
    <div className="dashboard">
      {/* Dashboard Header */}
      <div className="dashboard-header">
        <h1 className="text">Dashboard</h1>
        <button className="button">Start Live Stream</button>
      </div>

      {/* Containers for Dashboard Sections */}
      <div className="dashboard-layout">
        {/* Team Statistics Container */}
        <div className="container team-statistics">
          <TeamStatistics />
        </div>

        {/* Metrics Cards */}
        <div className="container metrics-section">
          <MetricsCards />
        </div>

        {/* Player Overview Table */}
        <div className="container player-overview">
          <PlayerOverview />
        </div>

        {/* Fatigue Level Distribution Chart */}
        <div className="container fatigue-level">
          <FatigueLevelDistribution />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
