import React, { useState } from "react";
import { useNotifications } from "../context/NotificationContext"; // Import useNotifications hook
import "../styles/NotificationsPage.css";

const NotificationsPage = () => {
  const { notifications, toggleReadStatus, markAllAsRead, markAllAsUnread, addNotification } =
    useNotifications(); // Access notifications and functions
  const [expandedNotification, setExpandedNotification] = useState(null); // State to track expanded notification
  const [reply, setReply] = useState(""); // State for reply input

  const loggedInUser = "You [Logged In User]"; // Placeholder for the logged-in user info

  // Sort notifications by timestamp (newest first)
  const sortedNotifications = [...notifications].sort(
    (a, b) => b.timestamp - a.timestamp
  );

  const [successMessage, setSuccessMessage] = useState(""); // State for success toast

  // Handle sending a reply
  const handleSendReply = (notification) => {
    if (!reply.trim()) {
      alert("Reply cannot be empty.");
      return;
    }

    addNotification({
      title: `Reply: ${notification.title}`, // Add "Reply" prefix
      body: reply,
      sender: loggedInUser,
      to: notification.sender,
      timestamp: Date.now(),
    });

    setReply(""); // Clear the reply input
    setSuccessMessage("Reply sent!");

    // Hide the success message after 3 seconds
    setTimeout(() => setSuccessMessage(""), 3000);
  };

  return (
    <div className="notifications-page">

        {/* Success Message Toast */}
        {successMessage && (
        <div
            style={{
            position: "fixed",
            top: "10px",
            right: "10px",
            backgroundColor: "#22cc88",
            color: "#ffffff",
            padding: "10px 20px",
            borderRadius: "5px",
            boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
            zIndex: "9999",
            }}
        >
            {successMessage}
        </div>
        )}

        <h1>Notifications</h1>
        {notifications.length === 0 ? (
            <p>No notifications yet.</p>
        ) : (
            <>
            <div className="buttons-container">
                <button onClick={markAllAsRead} className="mark-all-btn">
                Mark All as Read
                </button>
                <button onClick={markAllAsUnread} className="mark-all-btn">
                Mark All as Unread
                </button>
            </div>
            <ul className="notifications-list">
                {sortedNotifications.map((notification) => (
                    <li
                    key={notification.id}
                    className={`notification-item ${notification.isRead ? "read" : "unread"}`}
                    >
                    <div className="notification-summary">
                        <p>
                        <strong>Subject:</strong> {notification.title || "No Subject"}
                        </p>
                        <p>
                        <strong>From:</strong> {notification.sender}
                        </p>
                        <p>
                        <strong>To:</strong> {notification.to}
                        </p>
                        <p>
                        <strong>Sent at:</strong> {new Date(notification.timestamp).toLocaleString()}
                        </p>

                        {/* Mark Read/Unread Button */}
                        <button
                        onClick={() => toggleReadStatus(notification.id)} // Toggle read/unread
                        className={`mark-read-btn ${notification.isRead ? "unread" : "read"}`}
                        >
                        {notification.isRead ? "Mark as Unread" : "Mark as Read"}
                        </button>

                        {/* Read More/Hide Button */}
                        <button
                        onClick={() =>
                            setExpandedNotification(
                            expandedNotification === notification.id ? null : notification.id
                            )
                        }
                        className="read-more-btn"
                        >
                        {expandedNotification === notification.id ? "Hide" : "Read"}
                        </button>
                    </div>

                    {/* Expanded Notification Details */}
                    {expandedNotification === notification.id && (
                        <div className="notification-details">
                        <p>
                            <strong>Message:</strong> {notification.body}
                        </p>
                        <div className="reply-section">
                            <textarea
                            value={reply}
                            onChange={(e) => setReply(e.target.value)}
                            placeholder={`Write a reply to ${notification.sender}...`}
                            rows="3"
                            />
                            <button
                            onClick={() => handleSendReply(notification)}
                            className="send-reply-btn"
                            >
                            Send Reply
                            </button>
                        </div>
                        </div>
                    )}
                    </li>
                ))}
                </ul>
            </>
        )}
        </div>
  );
};

export default NotificationsPage;
