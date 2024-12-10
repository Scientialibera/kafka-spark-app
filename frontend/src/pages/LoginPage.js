import React, { useState } from "react"; // Added useState for form handling
import { useNavigate } from "react-router-dom"; // Added for navigation
import "../styles/LoginPage.css";
import LogoIcon from "../icons/logo.png";

const LoginPage = () => {
  const [email, setEmail] = useState(""); // State to track email input
  const [password, setPassword] = useState(""); // State to track password input
  const [error, setError] = useState(""); // State to track login errors
  const navigate = useNavigate(); // Hook to programmatically navigate between routes

  const handleLogin = (e) => {
    e.preventDefault(); // Prevent form submission

    const users = JSON.parse(localStorage.getItem("users")) || []; // Get users from localStorage
    const user = users.find(
      (user) => user.email === email && user.password === password
    ); // Check if the user exists with matching credentials

    if (!user) {
      setError("Invalid email or password"); // Show error if credentials don't match
      return;
    }

    // Store the logged-in user in localStorage and redirect to dashboard
    localStorage.setItem("loggedInUser", JSON.stringify(user));
    navigate("/dashboard"); // Navigate to the dashboard
  };

  return (
    <div className="login-page">
      {/* Logo */}
      <div className="logo-container">
        <img src={LogoIcon} alt="Logo" className="logo-icon" />
        <div className="logo-text">Sports Prophet</div>
      </div>
      <div className="login-card">
        <h2>Sign in</h2>
        <form onSubmit={handleLogin}> {/* Added onSubmit handler */}
          <div className="form-group">
            <input
              type="email"
              placeholder="example.email@gmail.com"
              value={email} // Controlled input
              onChange={(e) => setEmail(e.target.value)} // Update email state
              required
            />
          </div>
          <div className="form-group">
            <input
              type="password"
              placeholder="Enter at least 8+ characters"
              value={password} // Controlled input
              onChange={(e) => setPassword(e.target.value)} // Update password state
              required
            />
          </div>
          <div className="form-options">
            <div className="remember-me-container">
              <input type="checkbox" id="remember-me" />
              <label htmlFor="remember-me">Remember me</label>
            </div>
            <a href="/forgot-password" className="forgot-password"> {/* Updated link */}
              Forgot password?
            </a>
          </div>
          {error && <p style={{ color: "red" }}>{error}</p>} {/* Display login error */}
          <button type="submit" className="login-button">
            Sign in
          </button>
        </form>
        <p>
          Need to register? <a href="/register">Sign up here</a>
        </p>
      </div>
      <div className="login-info">
        <h2>Great to have you back!</h2>
        <ul>
          <li>Stay on top of your game</li>
          <li>Get insights for each session</li>
          <li>Receive injury risk alerts</li>
          <li>Never miss an update</li>
        </ul>
      </div>
    </div>
  );
};

export default LoginPage;
