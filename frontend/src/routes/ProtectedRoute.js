import React from "react";
import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ children }) => {
  const user = JSON.parse(localStorage.getItem("loggedInUser"));

  return user ? children : <Navigate to="/login" />;
};

export default ProtectedRoute;
