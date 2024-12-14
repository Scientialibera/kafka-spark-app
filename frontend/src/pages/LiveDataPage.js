import React from "react";
import "../styles/LiveDataPage.css";
import Sidebar from "../components/Sidebar";
import SoccerField from "../components/GPSData/SoccerField";
import LiveAlarms from "../components/GPSData/LiveAlarms";

const LiveDataPage = () => {

  const runId = "run_001"; // Replace with dynamic run ID if necessary
  const numPlayers = 10; // Total number of players

  const players = [
    { id: "1", name: "Liam Carter" },
    { id: "2", name: "Ethan Brooks" },
    { id: "3", name: "Noah Bennett" },
    { id: "4", name: "Oliver Hayes" },
    { id: "5", name: "William Mason" },
    { id: "6", name: "Lucas Graham" },
    { id: "7", name: "James Turner" },
    { id: "8", name: "Henry Mitchell" },
    { id: "9", name: "Jack Coleman" },
    { id: "10", name: "Alexander Price" },
  ];

  return (
    <div className="live-data-page">
      <Sidebar />
      <div className="page-content">
        <h1 className="page-title">Live Match Data</h1>
        <div className="live-data-content">
          <SoccerField runId={runId} players={players} />
          <LiveAlarms numPlayers={numPlayers} runId={runId} players={players} />
        </div>
      </div>
    </div>
  );
};

export default LiveDataPage;
