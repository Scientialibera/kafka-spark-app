import React from "react";
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
        <div className="menu-item selected">
          <img src={DashboardIcon} alt="Dashboard" className="menu-icon" />
          Dashboard
        </div>
        <div className="menu-item">
          <img src={PlayersIcon} alt="Players" className="menu-icon" />
          Players
        </div>
        <div className="menu-item">
          <img src={TeamIcon} alt="Team" className="menu-icon" />
          Team
        </div>
        <div className="menu-item">
          <img src={LiveDataIcon} alt="Live Data" className="menu-icon" />
          Live Data
        </div>
        <div className="menu-item">
          <img src={ReportsIcon} alt="Reports" className="menu-icon" />
          Reports
        </div>
        <div className="menu-item">
          <img src={DevicesIcon} alt="Devices" className="menu-icon" />
          Devices
        </div>
        <div className="menu-item">
          <img src={NotificationsIcon} alt="Notifications" className="menu-icon" />
          Notifications <span className="badge">9</span>
        </div>
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
