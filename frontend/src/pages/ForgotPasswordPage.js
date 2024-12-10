import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; // Import useNavigate for redirection
import "../styles/ForgotPasswordPage.css";
import LogoIcon from "../icons/logo.png";


const ForgotPasswordPage = () => {
  const [email, setEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [resetSuccess, setResetSuccess] = useState(false); // New state for tracking success
  const navigate = useNavigate(); // Hook for navigation

  const handleResetPassword = (e) => {
    e.preventDefault();

    const users = JSON.parse(localStorage.getItem("users")) || [];
    const userIndex = users.findIndex((user) => user.email === email);

    if (userIndex === -1) {
      setError("Email not found");
      return;
    }

    users[userIndex].password = newPassword;
    localStorage.setItem("users", JSON.stringify(users));
    setMessage("Password reset successfully! You can now log in.");
    setError("");
    setResetSuccess(true); // Mark the reset as successful
  };

  const handleLoginRedirect = () => {
    navigate("/login"); // Redirect to login page
  };

  return (
    <div className="forgot-password-page">
        <div className="logo-container">
            <img src={LogoIcon} alt="Logo" className="logo-icon" />
            <div className="logo-text">Sports Prophet</div>
        </div>
      <h2>Reset Password</h2>
      <form onSubmit={handleResetPassword}>
        {!resetSuccess && (
          <>
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Enter new password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
          </>
        )}
        {error && <p style={{ color: "red" }}>{error}</p>}
        {message && <p style={{ color: "green" }}>{message}</p>}
        {!resetSuccess ? (
          <button type="submit">Reset Password</button>
        ) : (
          <button type="button" onClick={handleLoginRedirect}>
            Log in
          </button>
        )}
      </form>
    </div>
  );
};

export default ForgotPasswordPage;
