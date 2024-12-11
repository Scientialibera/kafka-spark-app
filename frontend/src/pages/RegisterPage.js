import React, { useState } from "react"; // Added useState for form handling
import { useNavigate } from "react-router-dom"; // Added for navigation
import "../styles/RegisterPage.css";
import LogoIcon from "../icons/logo.png";

const RegisterPage = () => {
  const [firstName, setFirstName] = useState(""); // State to track first name
  const [lastName, setLastName] = useState(""); // State to track last name
  const [role, setRole] = useState(""); // State to track selected role
  const [email, setEmail] = useState(""); // State to track email
  const [password, setPassword] = useState(""); // State to track password
  const [termsAccepted, setTermsAccepted] = useState(false); // State to track terms checkbox
  const [error, setError] = useState(""); // State to track registration errors
  const navigate = useNavigate(); // Hook to programmatically navigate between routes

  const handleRegister = (e) => {
    e.preventDefault(); // Prevent form submission

    // Check if all fields are filled and terms are accepted
    if (!firstName || !lastName || !role || !email || !password || !termsAccepted) {
      setError("Please fill all the fields and accept the terms.");
      return;
    }

    // Get existing users from localStorage
    const users = JSON.parse(localStorage.getItem("users")) || [];

    // Check if email is already registered
    const userExists = users.some((user) => user.email === email);
    if (userExists) {
      setError("Email is already registered.");
      return;
    }

    // Add new user to localStorage
    const newUser = { firstName, lastName, role, email, password };
    users.push(newUser);
    localStorage.setItem("users", JSON.stringify(users));

    // Navigate to login page
    navigate("/login");
  };

  return (
    <div className="register-page">
      {/* Logo */}
      <div className="logo-container">
        <img src={LogoIcon} alt="Logo" className="logo-icon" />
        <div className="logo-text">Sports Prophet</div>
      </div>
      <div className="register-card">
        <h2>Begin your journey</h2>
        <form onSubmit={handleRegister}> {/* Added onSubmit handler */}
          <div className="form-group">
            <input
              type="text"
              placeholder="Input first name"
              value={firstName} // Controlled input
              onChange={(e) => setFirstName(e.target.value)} // Update state
              required
            />
            <input
              type="text"
              placeholder="Input last name"
              value={lastName} // Controlled input
              onChange={(e) => setLastName(e.target.value)} // Update state
              required
            />
          </div>
          <div className="form-group">
            <select
              value={role} // Controlled select
              onChange={(e) => setRole(e.target.value)} // Update state
              required
            >
              <option value="" disabled>
                Select your role
              </option>
              <option value="player">Player</option>
              <option value="coach">Team Manager</option>
              <option value="physiotherapist">Physiotherapist</option>
            </select>
          </div>
          <div className="form-group">
            <input
              type="email"
              placeholder="example.email@gmail.com"
              value={email} // Controlled input
              onChange={(e) => setEmail(e.target.value)} // Update state
              required
            />
          </div>
          <div className="form-group">
            <input
              type="password"
              placeholder="Enter at least 8+ characters"
              value={password} // Controlled input
              onChange={(e) => setPassword(e.target.value)} // Update state
              required
            />
          </div>
          <div className="terms">
            <input
              type="checkbox"
              checked={termsAccepted} // Controlled checkbox
              onChange={(e) => setTermsAccepted(e.target.checked)} // Update state
              required
            />
            <label>
              By signing up, I agree with the <a href="#">Terms of Use</a> & <a href="#">Privacy Policy</a>
            </label>
          </div>
          {error && <p style={{ color: "red" }}>{error}</p>} {/* Display registration error */}
          <button type="submit" className="register-button">
            Register
          </button>
          <p>
            Returning user? <a href="/login">Log in here</a>
          </p>
        </form>
        
      </div>
      <div className="register-info">
        <h2>Come join us</h2>
        <ul>
          <li>Track your performance and improve with personalised insights</li>
          <li>Manage team data, view analytics and support player development</li>
          <li>
            Monitor player health, provide recovery recommendations and access
            medical insights
          </li>
        </ul>
      </div>
    </div>
  );
};

export default RegisterPage;
