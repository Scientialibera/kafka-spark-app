import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { NotificationProvider } from "./context/NotificationContext"; 
import { TeamProvider } from "./context/TeamContext";
import RegisterPage from "./pages/RegisterPage";
import LoginPage from "./pages/LoginPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import ProtectedRoute from "./routes/ProtectedRoute";
import Sidebar from "./components/Sidebar";
import Dashboard from "./components/Dashboard";
import PlayersPage from "./pages/PlayersPageWithBackend";
import TeamPage from "./pages/TeamPageWithBackend";
import LiveDataPage from "./pages/LiveDataPage";
import EditProfile from "./pages/EditProfile";
import DevicesPage from "./pages/DevicesPage";
import NotificationsPage from "./pages/NotificationsPage";
import { initialiseUsers } from "./utils/InitialiseUsers";
import "./App.css";

function App() {

  initialiseUsers();

  // Placeholder: Simulate authentication state
  const isAuthenticated = !!localStorage.getItem("authToken");

  return (
    <NotificationProvider>
      <TeamProvider>
        <Router>
          <Routes>
            {/* Public Routes: Login, Register, and Forgot Password */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />

            {/* Private Routes: Protected by ProtectedRoute */}
            <Route
              path="/*"
              element={
                <ProtectedRoute isAuthenticated={isAuthenticated}>
                  <div className="app-container">
                    <Sidebar />
                    <div className="main-content">
                      <Routes>
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/players" element={<PlayersPage />} />
                        <Route path="/team" element={<TeamPage />} />
                        <Route path="/live-data" element={<LiveDataPage />} />
                        <Route path="/edit-profile" element={<EditProfile />} />
                        <Route path="/devices" element={<DevicesPage />} />
                        <Route path="/notifications" element={<NotificationsPage />} />
                        {/* Fallback Route */}
                        <Route path="*" element={<Navigate to="/dashboard" />} />
                      </Routes>
                    </div>
                  </div>
                </ProtectedRoute>
              }
            />

            {/* Default Route */}
            <Route path="/" element={<Navigate to="/login" />} />
          </Routes>
        </Router>
      </TeamProvider>
    </NotificationProvider>
  );
}

export default App;
