import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
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
import ArrowDownIcon from "../icons/arrow-down.png";

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false); // Modal state

  const handleLogout = () => {
    // Clear user data from localStorage and navigate to login page
    localStorage.removeItem("loggedInUser");
    navigate("/login");
  };

  const handleEditProfile = () => {
    // Redirect to a profile edit page
    navigate("/edit-profile");
  };

  const toggleModal = () => {
    setIsModalOpen(!isModalOpen);
  };

  // Retrieve logged-in user data
  const loggedInUser = JSON.parse(localStorage.getItem("loggedInUser"));

  return (
    <div className="sidebar">
      {/* Logo Section */}
      <div className="sidebar-logo">
        <img src={LogoIcon} alt="Logo" className="logo-icon" />
        <div>
          <h2>Sports Prophet</h2>
          <p>{loggedInUser?.role || "User Role"}</p>
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
          className={`menu-item ${location.pathname === "/players" ? "selected" : ""}`}
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
          className={`menu-item ${location.pathname === "/live-data" ? "selected" : ""}`}
        >
          <img src={LiveDataIcon} alt="Live Data" className="menu-icon" />
          Live Data
        </Link>
        <Link
          to="/reports"
          className={`menu-item ${location.pathname === "/reports" ? "selected" : ""}`}
        >
          <img src={ReportsIcon} alt="Reports" className="menu-icon" />
          Reports
        </Link>
        <Link
          to="/devices"
          className={`menu-item ${location.pathname === "/devices" ? "selected" : ""}`}
        >
          <img src={DevicesIcon} alt="Devices" className="menu-icon" />
          Devices
        </Link>
        <Link
          to="/notifications"
          className={`menu-item ${location.pathname === "/notifications" ? "selected" : ""}`}
        >
          <img src={NotificationsIcon} alt="Notifications" className="menu-icon" />
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
        <div className="user-info-details">
        <p className="user-name">{loggedInUser?.firstName || "User Name"}</p> {/* Display the first name */}
          <p className="user-email">{loggedInUser?.email || "user@example.com"}</p>
        </div>
        <button className="dropdown-toggle" onClick={toggleModal}>
          <img src={ArrowDownIcon} alt="Toggle Modal" className="arrow-icon" />
        </button>
      </div>

      {/* Modal for Profile/Logout */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={toggleModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>User Actions</h3>
            <button onClick={handleEditProfile}>Edit Profile</button>
            <button onClick={handleLogout}>Log Out</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;
