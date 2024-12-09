import React from "react";
import "../styles/RegisterPage.css";

const RegisterPage = () => {
  return (
    <div className="register-page">
      <div className="register-card">
        <h2>Begin your journey</h2>
        <form>
          <div className="form-group">
            <input type="text" placeholder="Input first name" required />
            <input type="text" placeholder="Input last name" required />
          </div>
          <div className="form-group">
            <select required>
              <option value="" disabled selected>
                Select your role
              </option>
              <option value="coach">Coach</option>
              <option value="player">Player</option>
            </select>
          </div>
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
          <div className="terms">
            <input type="checkbox" required />
            <label>
              By signing up, I agree with the <a href="#">Terms of Use</a> &
              <a href="#"> Privacy Policy</a>
            </label>
          </div>
          <button type="submit" className="register-button">
            Register
          </button>
        </form>
        <p>
          Returning user? <a href="/login">Log in here</a>
        </p>
      </div>
      <div className="register-info">
        <h2>Come join us</h2>
        <ul>
          <li>Track your performance and improve with personalized insights</li>
          <li>Manage team data, view analytics, and support player development</li>
          <li>
            Monitor player health, provide recovery recommendations, and access
            medical insights
          </li>
        </ul>
      </div>
    </div>
  );
};

export default RegisterPage;
