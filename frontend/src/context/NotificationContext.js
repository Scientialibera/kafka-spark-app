import React, { createContext, useState, useContext } from "react";

// Create a context for notifications
const NotificationContext = createContext();

// Create a provider to wrap the app
export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([
    // Example notifications with expanded fields
    {
      id: 1,
      title: "New Team Message",
      body: "You have a new message from your team manager.",
      sender: "Team Manager",
      to: "Team",
      timestamp: Date.now(),
      isRead: false,
    },
    {
        id: 2,
        title: "Welcome to the App!",
        body: "We're glad to have you here.",
        sender: "Admin",
        to: "User",
        timestamp: Date.now(),
        isRead: false,
      },
  ]);

  // Function to add a new notification
  const addNotification = (notification) => {
    const newNotification = {
      id: Date.now(), // Unique ID based on timestamp
      ...notification,
      isRead: false,
    };
    setNotifications((prev) => [...prev, newNotification]);
  };

  // Function to mark a notification as read
  const markAsRead = (id) => {
    setNotifications((prev) =>
      prev.map((notification) =>
        notification.id === id ? { ...notification, isRead: true } : notification
      )
    );
  };

  // Function to mark all notifications as read
  const markAllAsRead = () => {
    setNotifications((prev) =>
      prev.map((notification) => ({ ...notification, isRead: true }))
    );
  };

  // Function to mark all notifications as unread
  const markAllAsUnread = () => {
    setNotifications((prev) =>
      prev.map((notification) => ({ ...notification, isRead: false }))
    );
  };

  const toggleReadStatus = (id) => {
    console.log("Toggling read status for notification ID:", id); // Add this
    setNotifications((prev) =>
      prev.map((notification) => {
        if (notification.id === id) {
          console.log("Before toggle:", notification.isRead); // Check current state
          const updatedNotification = { ...notification, isRead: !notification.isRead };
          console.log("After toggle:", updatedNotification.isRead); // Check updated state
          return updatedNotification;
        }
        return notification;
      })
    );
  };

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        addNotification,
        markAsRead,
        markAllAsRead,
        markAllAsUnread, 
        toggleReadStatus,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
};

// Hook to use the NotificationContext
export const useNotifications = () => {
  return useContext(NotificationContext);
};
