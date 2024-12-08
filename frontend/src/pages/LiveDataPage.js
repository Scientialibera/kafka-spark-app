import React from "react";
import "../styles/LiveDataPage.css";
import Sidebar from "../components/Sidebar";
import SoccerField from "../components/GPSData/SoccerField";

const LiveDataPage = () => {
  return (
    <div className="live-data-page">
      <Sidebar />
      <div className="page-content">
        <h1 className="page-title">Live GPS Data</h1>
        <div className="live-data-content">
          <SoccerField />
        </div>
      </div>
    </div>
  );
};

export default LiveDataPage;
