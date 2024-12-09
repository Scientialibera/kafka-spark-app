import React from "react";
import "../styles/LoginPage.css";

const LoginPage = () => {
  return (
    <div className="login-page">
      <div className="login-card">
        <h2>Sign in</h2>
        <form>
          <div className="form-group">
            <input type="email" placeholder="example.email@gmail.com" required />
          </div>
          <div className="form-group">
            <input
              type="password"
              placeholder="Enter at least 8+ characters"
              required
            />
          </div>
          <div className="remember-me">
            <input type="checkbox" />
            <label>Remember me</label>
            <a href="#">Forgot password?</a>
          </div>
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
