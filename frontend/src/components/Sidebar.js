import React from "react";
import { Link, useLocation } from "react-router-dom";
import "../styles/Sidebar.css";

// Import icons
import LogoIcon from "../icons/logo.png";
import DashboardIcon from "../icons/dashboard.png";
import PlayersIcon from "../icons/players.png";
import TeamIcon from "../icons/team.png";
import LiveDataIcon from "../icons/live-data.png";
import ReportsIcon from "../icons/report.png";
import DevicesIcon from "../icons/devices.png";
import NotificationsIcon from "../icons/notifications.png";

const Sidebar = () => {
  const location = useLocation(); // Get the current route

  return (
    <div className="sidebar">
      {/* Logo Section */}
      <div className="sidebar-logo">
        <img src={LogoIcon} alt="Logo" className="logo-icon" />
        <div>
          <h2>Sports Prophet</h2>
          <p>User Role</p>
        </div>
      </div>

      {/* Menu Section */}
      <div className="menu">
        <Link
          to="/dashboard"
          className={`menu-item ${location.pathname === "/dashboard" ? "selected" : ""}`}
        >
          <img src={DashboardIcon} alt="Dashboard" className="menu-icon" />
          Dashboard
        </Link>
        <Link
          to="/players"
          className={`menu-item ${
            location.pathname === "/players" ? "selected" : ""
          }`}
        >
          <img src={PlayersIcon} alt="Players" className="menu-icon" />
          Players
        </Link>
        <Link
          to="/team"
          className={`menu-item ${location.pathname === "/team" ? "selected" : ""}`}
        >
          <img src={TeamIcon} alt="Team" className="menu-icon" />
          Team
        </Link>
        <Link
          to="/live-data"
          className={`menu-item ${
            location.pathname === "/live-data" ? "selected" : ""
          }`}
        >
          <img src={LiveDataIcon} alt="Live Data" className="menu-icon" />
          Live Data
        </Link>
        <Link
          to="/reports"
          className={`menu-item ${
            location.pathname === "/reports" ? "selected" : ""
          }`}
        >
          <img src={ReportsIcon} alt="Reports" className="menu-icon" />
          Reports
        </Link>
        <Link
          to="/devices"
          className={`menu-item ${
            location.pathname === "/devices" ? "selected" : ""
          }`}
        >
          <img src={DevicesIcon} alt="Devices" className="menu-icon" />
          Devices
        </Link>
        <Link
          to="/notifications"
          className={`menu-item ${
            location.pathname === "/notifications" ? "selected" : ""
          }`}
        >
          <img
            src={NotificationsIcon}
            alt="Notifications"
            className="menu-icon"
          />
          Notifications <span className="badge">9</span>
        </Link>
      </div>

      {/* User Info Section */}
      <div className="user-info">
        <div className="user-avatar">
          <img
            src="https://via.placeholder.com/36"
            alt="User Avatar"
          />
        </div>
        <div>
          <p className="user-name">Lara</p>
          <p className="user-email">company@example.com</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
