import React, { useState, useEffect } from "react";
import "../styles/DevicesPage.css";
import Sidebar from "../components/Sidebar";

const DevicesPage = () => {
  const [devices, setDevices] = useState([]);
  const [filteredDevices, setFilteredDevices] = useState([]);
  const [newDeviceName, setNewDeviceName] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // Fetch devices from the backend
  const fetchDevices = async () => {
    try {
      const response = await fetch("http://localhost:8000/devices");
      const data = await response.json();
      if (Array.isArray(data.devices)) {
        const sortedDevices = data.devices.sort((a, b) => a.localeCompare(b)); // Sort alphabetically
        setDevices(sortedDevices);
        setFilteredDevices(sortedDevices);
      } else {
        throw new Error("Invalid data format from API");
      }
    } catch (error) {
      console.error("Failed to fetch devices:", error);
      setErrorMessage("Failed to load devices. Please try again.");
    }
  };

  // Initial fetch on component mount
  useEffect(() => {
    fetchDevices();
  }, []);

  // Handle adding a new device
  const handleAddDevice = async (e) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    if (!newDeviceName) {
      setErrorMessage("Device name is required.");
      return;
    }

    const deviceSchema = {
      device_name: newDeviceName,
      schema: {
        latitude: "float",
        longitude: "float",
        timestamp: "string",
      },
    };

    try {
      const response = await fetch("http://localhost:8000/register-device", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(deviceSchema),
      });

      if (!response.ok) {
        throw new Error("Failed to add device.");
      }

      // Refetch devices after adding
      await fetchDevices();
      setSuccessMessage("Device added successfully!");
      setNewDeviceName("");
    } catch (error) {
      console.error("Failed to add device:", error);
      setErrorMessage("Failed to add device. Please try again.");
    }
  };

  // Handle deleting a device
  const handleDeleteDevice = async (deviceName) => {
    setErrorMessage("");
    setSuccessMessage("");

    try {
      const response = await fetch(
        `http://localhost:8000/delete-device/${deviceName}`,
        { method: "DELETE" }
      );

      if (!response.ok) {
        throw new Error("Failed to delete device.");
      }

      // Refetch devices after deleting
      await fetchDevices();
      setSuccessMessage("Device deleted successfully!");
    } catch (error) {
      console.error("Failed to delete device:", error);
      setErrorMessage("Failed to delete device. Please try again.");
    }
  };

  // Handle search functionality
  const handleSearch = (e) => {
    const term = e.target.value.toLowerCase();
    setSearchTerm(term);

    const sortedFilteredDevices = devices
      .filter(
        (device) =>
          typeof device === "string" && device.toLowerCase().includes(term)
      )
      .sort((a, b) => a.localeCompare(b)); // Sort alphabetically after filtering

    setFilteredDevices(sortedFilteredDevices);
  };

  return (
    <div className="devices-page">
      <Sidebar />
      <div className="page-content">
        <h1>Devices</h1>

        <form className="add-device-form" onSubmit={handleAddDevice}>
          <input
            type="text"
            placeholder="Device Name"
            value={newDeviceName}
            onChange={(e) => setNewDeviceName(e.target.value)}
            required
          />
          <button type="submit">Add Device</button>
        </form>

        <input
          type="text"
          placeholder="Search Devices"
          value={searchTerm}
          onChange={handleSearch}
          className="search-input"
        />

        {errorMessage && <p className="error-message">{errorMessage}</p>}
        {successMessage && <p className="success-message">{successMessage}</p>}

        <div className="devices-list">
          {filteredDevices.length === 0 ? (
            <p>No devices found</p>
          ) : (
            <ul>
              {filteredDevices.map((device, index) => (
                <li key={index} className="device-item">
                  <div>
                    <h3>{device}</h3>
                  </div>
                  <button
                    onClick={() => handleDeleteDevice(device)}
                    className="delete-button"
                  >
                    Delete
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default DevicesPage;
