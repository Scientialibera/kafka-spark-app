import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import { useNotifications } from "../context/NotificationContext"; 
import Modal from "react-modal"; 
import "../styles/TeamPage.css";
import Sidebar from "../components/Sidebar";

// Import Team Logo
import TeamLogo from "../icons/Lakeside_FC_logo.png";

// Import metric icons
import HeartRateIcon from "../icons/heart-rate.png";
import SpeedIcon from "../icons/speed.png";
import AccelerationIcon from "../icons/acceleration.png";
import TemperatureIcon from "../icons/temperature.png";

// Import XLSX for generating Excel files and FileSaver for triggering file downloads
import * as XLSX from "xlsx";
import { saveAs } from "file-saver";

// Modal Styles
const customModalStyles = {
  content: {
    top: "50%",
    left: "55%",
    right: "auto",
    bottom: "auto",
    marginRight: "-50%",
    transform: "translate(-50%, -50%)",
    width: "50%", // Set the width of the modal
    maxHeight: "80%", // Add scroll for overflow
    overflowY: "auto",
    borderRadius: "10px",
    padding: "20px",
  },
};

const ITEMS_PER_PAGE = 3; // Number of items per page for pagination
const STREAM_SECONDS = 100; // Duration for the synthetic data stream

const TeamPageWithBackend = () => {
  // Editable team information
  const [team, setTeam] = useState({
    name: "Lakeside FC",
    manager: "Thomas Grant",
    physiotherapist: "Sarah Reid",
    totalPlayers: 10,
    seasonRecord: "W-L-D: 12-5-3",
    leagueRank: "#2 in League",
  });

  // Toggle between view and edit modes
  const [isEditingAll, setIsEditingAll] = useState(false);
  const [isEditing, setIsEditing] = useState(false);


  // Handle input changes for team fields
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setTeam((prevTeam) => ({
      ...prevTeam,
      [name]: value,
    }));
  };

  // Save button logic
  const handleSave = () => {
    // Save changes (send to backend if needed)
    console.log("Updated team info:", team);
    setIsEditing(false); // Exit edit mode
  };

  // Cancel button logic
  const handleCancel = () => {
    setIsEditing(false); // Exit edit mode without saving
  };

  // Render the team info section
  const renderTeamInfo = () => {
    if (isEditing) {
      return (
        <div className="team-details edit-mode">
          <h2>{team.name}</h2>
          <div className="form-row">
            <label>Manager:</label>
            <input
              type="text"
              name="manager"
              value={team.manager}
              onChange={handleInputChange}
            />
          </div>
          <div className="form-row">
            <label>Physiotherapist:</label>
            <input
              type="text"
              name="physiotherapist"
              value={team.physiotherapist}
              onChange={handleInputChange}
            />
          </div>
          <div className="form-row">
            <label>Players:</label>
            <input
              type="number"
              name="totalPlayers"
              value={team.totalPlayers}
              onChange={handleInputChange}
            />
          </div>
          <div className="form-row">
            <label>Season Record:</label>
            <input
              type="text"
              name="seasonRecord"
              value={team.seasonRecord}
              onChange={handleInputChange}
            />
          </div>
          <div className="form-row">
            <label>League Rank:</label>
            <input
              type="text"
              name="leagueRank"
              value={team.leagueRank}
              onChange={handleInputChange}
            />
          </div>
          <div className="form-buttons">
            <button className="button primary small" onClick={handleSave}>
              Save
            </button>
            <button className="button grey small" onClick={handleCancel}>
              Cancel
            </button>
          </div>
        </div>
      );
    } else {
      return (
        <div className="team-details">
          <h2>{team.name}</h2>
          <p><strong>Manager:</strong> {team.manager}</p>
          <p><strong>Physiotherapist:</strong> {team.physiotherapist}</p>
          <p><strong>Players:</strong> {team.totalPlayers}</p>
          <p><strong>Season Record:</strong> {team.seasonRecord}</p>
          <p><strong>League Rank:</strong> {team.leagueRank}</p>
        </div>
      );
    }
  };

  // Training Timetable State
  const [trainingTimetable, setTrainingTimetable] = useState([
    { date: "2024-12-15", time: "10:00", activity: "Cardio Training", isEditing: false },
    { date: "2024-12-16", time: "14:00", activity: "Strength Training", isEditing: false },
    { date: "2024-12-18", time: "11:00", activity: "Team Strategy Meeting", isEditing: false },
  ]);

  const [isTimetableOpen, setIsTimetableOpen] = useState(false); // Modal visibility

  // Function to toggle modal visibility
  const toggleTimetableModal = () => {
    setIsTimetableOpen(!isTimetableOpen);
  };

  const toggleEditAllSessions = () => {
    if (isEditingAll) {
      // Save logic
      console.log("Saved training sessions:", trainingTimetable);
    }
    setIsEditingAll(!isEditingAll); // Toggle between edit and view modes
  };
  

  // Function to add a new session
  const addTrainingSession = () => {
    const newSession = { date: "", time: "", activity: "", isEditing: true }; // New session with empty fields
    setTrainingTimetable((prev) => [...prev, newSession]);
    setIsEditingAll(true); // Automatically enable edit mode
  };

  // Function to handle edits to a session
  const handleSessionChange = (index, field, value) => {
    const updatedTimetable = [...trainingTimetable];
    updatedTimetable[index][field] = value;
    setTrainingTimetable(updatedTimetable);
  };
  
  // Function to delete a session
  const deleteTrainingSession = (index) => {
    const updatedTimetable = trainingTimetable.filter((_, i) => i !== index);
    setTrainingTimetable(updatedTimetable);
  };
    
  // Render Training Timetable Modal
  const renderTimetableModal = () => (
    <Modal
      isOpen={isTimetableOpen}
      onRequestClose={toggleTimetableModal}
      style={customModalStyles}
      contentLabel="Training Timetable Modal"
    >
      <div className="modal-header">
        <h2>Upcoming Training Sessions</h2>
      </div>
      <div className="modal-body">
        <div className="actions-and-table">
          <div className="button-column">
            <button className="button small primary" onClick={addTrainingSession}>
              Add New Session
            </button>
            <button
              className="button small grey"
              onClick={toggleEditAllSessions}
            >
              {isEditingAll ? "Save" : "Edit"}
            </button>
          </div>
          <div className="table-column">
            {trainingTimetable.length > 0 ? (
              <table className="timetable-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Activity</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {trainingTimetable.map((session, index) => (
                    <tr key={index}>
                      <td>
                        <input
                          type="date"
                          value={session.date}
                          disabled={!isEditingAll}
                          onChange={(e) =>
                            handleSessionChange(index, "date", e.target.value)
                          }
                        />
                      </td>
                      <td>
                        <input
                          type="time"
                          value={session.time}
                          disabled={!isEditingAll}
                          onChange={(e) =>
                            handleSessionChange(index, "time", e.target.value)
                          }
                        />
                      </td>
                      <td>
                        <input
                          type="text"
                          value={session.activity}
                          placeholder="Activity"
                          disabled={!isEditingAll}
                          onChange={(e) =>
                            handleSessionChange(index, "activity", e.target.value)
                          }
                        />
                      </td>
                      <td>
                        <button
                          className="delete-icon"
                          onClick={() => deleteTrainingSession(index)}
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="no-sessions-message">No training sessions scheduled.</p>
            )}
          </div>
        </div>
        <button className="button grey small close-button" onClick={toggleTimetableModal}>
          Close
        </button>
      </div>
    </Modal>
  );

  // Adding state for Send Team Message button
  const [isMessageModalOpen, setIsMessageModalOpen] = useState(false); // State for modal visibility
  const [teamMessage, setTeamMessage] = useState({
    to: "Team", // Default to 'All Players'
    from: `${team.manager} [Team Manager]`, // Default to Manager with role
    subject: "",
    message: "",
  });
  const { addNotification } = useNotifications();

  const [successMessage, setSuccessMessage] = useState(""); // State for displaying success messages

  const handleSendTeamMessage = () => {
    const { to, from, subject, message } = teamMessage;
  
    if (!message.trim()) {
      alert("Message cannot be empty.");
      return;
    }
  
    if (!subject.trim()) {
      alert("Subject cannot be empty.");
      return;
    }
  
    // Add the notification
    addNotification({
      title: subject,
      body: message,
      sender: from,
      to: to === "Team" ? "All Players" : to,
      timestamp: Date.now(),
      isRead: false,
    });

    // Show success message
    setSuccessMessage("Message successfully sent!");
  
    // Close the modal and reset the message
    setIsMessageModalOpen(false);
    setTeamMessage({
      to: "Team",
      from: `${team.manager} [Team Manager]`,
      subject: "",
      message: "",
    });

    // Clear the success message after 3 seconds
    setTimeout(() => setSuccessMessage(""), 3000);
  };
  
  const renderMessageModal = () => (
    <Modal
      isOpen={isMessageModalOpen}
      onRequestClose={() => setIsMessageModalOpen(false)}
      style={customModalStyles}
      contentLabel="Send Team Message"
    >
      <h2>Send Team Message</h2>
      <form style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        {/* To Field (Read-Only) */}
        <div style={{ display: "flex", flexDirection: "column" }}>
          <label htmlFor="to" style={{ fontWeight: "bold" }}>To:</label>
          <input
            id="to"
            type="text"
            value="Team"
            readOnly
            style={{
              width: "97%",
              padding: "10px",
              borderRadius: "5px",
              border: "1px solid #ccc",
              backgroundColor: "#f9f9f9",
              cursor: "not-allowed",
            }}
          />
        </div>
  
        {/* From Field */}
        <div style={{ display: "flex", flexDirection: "column" }}>
          <label htmlFor="from" style={{ fontWeight: "bold" }}>From:</label>
          <select
            id="from"
            value={teamMessage.from}
            onChange={(e) => setTeamMessage({ ...teamMessage, from: e.target.value })}
            style={{
              width: "100%",
              padding: "10px",
              borderRadius: "5px",
              border: "1px solid #ccc",
            }}
          >
            <option value={`${team.manager} [Team Manager]`}>
              {team.manager} [Team Manager]
            </option>
            <option value={`${team.physiotherapist} [Physiotherapist]`}>
              {team.physiotherapist} [Physiotherapist]
            </option>
          </select>
        </div>
  
        {/* Subject Field */}
        <div style={{ display: "flex", flexDirection: "column" }}>
          <label htmlFor="subject" style={{ fontWeight: "bold" }}>Subject:</label>
          <input
            id="subject"
            type="text"
            value={teamMessage.subject || ""}
            onChange={(e) => setTeamMessage({ ...teamMessage, subject: e.target.value })}
            placeholder="Enter the subject"
            style={{
              width: "97%",
              padding: "10px",
              borderRadius: "5px",
              border: "1px solid #ccc",
            }}
          />
        </div>
  
        {/* Message Field */}
        <div style={{ display: "flex", flexDirection: "column" }}>
          <label htmlFor="message" style={{ fontWeight: "bold" }}>Message:</label>
          <textarea
            id="message"
            value={teamMessage.message || ""}
            onChange={(e) => setTeamMessage({ ...teamMessage, message: e.target.value })}
            placeholder="Write your message here..."
            rows="5"
            style={{
              width: "97%",
              padding: "10px",
              borderRadius: "5px",
              border: "1px solid #ccc",
              fontFamily: "Inter, sans-serif",
            }}
          />
        </div>
  
        {/* Buttons */}
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: "20px" }}>
          <button
            type="button"
            className="button grey"
            onClick={() => setIsMessageModalOpen(false)}
            style={{ padding: "10px 20px", borderRadius: "5px", marginLeft: "15px", }}
          >
            Cancel
          </button>
          <button
            type="button"
            className="button primary"
            onClick={handleSendTeamMessage}
            style={{ padding: "10px 20px", borderRadius: "5px" }}
          >
            Send
          </button>
        </div>
      </form>
    </Modal>
  );
 
  // Historical metrics
  const [historicalMetrics, setHistoricalMetrics] = useState({
    averageHeartRate: "N/A",
    averageRecoveryTime: "N/A",
    maxHeartRate: "N/A",
  });

  // Live metrics
  const [liveMetrics, setLiveMetrics] = useState({
    heartRate: "Loading...",
    speed: "Loading...",
    acceleration: "Loading...",
    temperature: "Loading...",
  });

  const [heartbeatData, setHeartbeatData] = useState([]);
  const [games, setGames] = useState([]);

  const [currentPage, setCurrentPage] = useState(1);

  // Streaming state management
  const [isStreaming, setIsStreaming] = useState(false);
  const [buttonText, setButtonText] = useState("Start Live Stream");
  const [statusMessage, setStatusMessage] = useState("");

  const metricTitles = {
    heartRate: "Heart Rate",
    speed: "Speed",
    acceleration: "Acceleration",
    temperature: "Temperature",
  };

  const metricIcons = {
    heartRate: HeartRateIcon,
    speed: SpeedIcon,
    acceleration: AccelerationIcon,
    temperature: TemperatureIcon,
  };

  const heartbeatOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: { grid: { display: false } },
      y: {
        beginAtZero: true,
        ticks: { stepSize: 20 },
      },
    },
    plugins: {
      legend: { display: false },
    },
  };

  const startLiveStream = () => {
    console.log("Initialising live stream...");
    setStatusMessage("");
    console.log("Status message cleared:", statusMessage);
    setButtonText("Starting...");
    fetch(
      `http://localhost:8000/start-synthetic-data?num_players=10&stream_seconds=${STREAM_SECONDS}`,
      {
        method: "POST",
      }
    )
      .then((response) => response.json())
      .then((data) => {
        console.log("Synthetic data stream started:", data);
        setIsStreaming(true);
        setButtonText("Streaming...");
        setStatusMessage("Streaming started...");
        console.log("Status message updated to:", "Streaming started...");
  
        // Wait for 8 seconds before fetching metrics
        setTimeout(() => {
          console.log("Fetching metrics after 8 seconds delay...");
          fetchMetricsAndHeartbeat();
        }, 8000);
  
        // After STREAM_SECONDS, stop streaming
        setTimeout(() => {
          console.log("Stopping live stream after timeout...");
          setIsStreaming(false);
          setButtonText("Start Live Stream");
          setStatusMessage(
            "Streaming ended. Press 'Start Live Stream' again to restart."
          );
          console.log(
            "Status message updated to:",
            "Streaming ended. Press 'Start Live Stream' again to restart."
          );
        }, STREAM_SECONDS * 1000);
      })
      .catch((error) => {
        console.error("Error starting synthetic data:", error);
        setButtonText("Start Live Stream");
        setStatusMessage("Failed to start streaming.");
        console.log("Status message updated to:", "Failed to start streaming.");
      });
  };
  

  const fetchMetricsAndHeartbeat = async () => {
    try {
      const [statsResponse, kafkaResponse] = await Promise.all([
        fetch("http://localhost:8000/get-team-average-stats/10/run_001"),
        fetch("http://localhost:8000/get-team-kafka-stats/10/run_001"),
      ]);

      const statsData = await statsResponse.json();
      const kafkaData = await kafkaResponse.json();

      const roundedHeartRate = parseFloat((kafkaData.team_average_heart_rate || 0).toFixed(1));
      const roundedTemperature = parseFloat((kafkaData.team_average_temperature || 0).toFixed(1));
      const roundedSpeed = parseFloat((statsData.team_average_speed || 0).toFixed(1));
      const roundedAcceleration = parseFloat((statsData.team_average_acceleration || 0).toFixed(1));

      setLiveMetrics({
        heartRate: `${roundedHeartRate} BPM`,
        temperature: `${roundedTemperature} °C`,
        speed: `${roundedSpeed} KM/H`,
        acceleration: `${roundedAcceleration} M/S²`,
      });

      setHeartbeatData((prevData) => [...prevData, roundedHeartRate]);
    } catch (error) {
      console.error("Error fetching metrics and heartbeat data:", error);
    }
  };

  // Fetch historical data (team-metrics & recommendations) on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [teamRes, recRes] = await Promise.all([
          fetch("http://localhost:8000/team-metrics"),
          fetch("http://localhost:8000/recommendations"),
        ]);

        const teamData = await teamRes.json();
        const recData = await recRes.json();

        // Compute overall metrics
        const playerAvgHR = teamData["Player Average Heart Rate"];
        const playerMaxHR = teamData["Player Max Heart Rate"];
        const avgRecovery = teamData["Average Team Recovery Rate"];

        if (playerAvgHR && typeof playerAvgHR === "object") {
          const avgHRValues = Object.values(playerAvgHR);
          const avgHR = avgHRValues.reduce((sum, val) => sum + val, 0) / avgHRValues.length;
          const avgHRStr = `${avgHR.toFixed(1)} bpm`;
          
          const avgRecoveryStr = `${avgRecovery.toFixed(2)} bpm/s`;

          const maxHRValues = Object.values(playerMaxHR);
          const avgMaxHR = maxHRValues.reduce((sum, val) => sum + val, 0) / maxHRValues.length;
          const avgMaxHRStr = `${avgMaxHR.toFixed(0)} bpm`;

          setHistoricalMetrics({
            averageHeartRate: avgHRStr,
            averageRecoveryTime: avgRecoveryStr,
            maxHeartRate: avgMaxHRStr,
          });
        }

        // Prepare games data
        const totalDistanceData = teamData["Team Total Distance Per Game"];
        const heartRateRecoveryData = teamData["Player Average Heart Rate Recovery"];
        const aggregatedRecommendations = recData["Aggregated Team Recommendations"];

        // Sort runs descending by their number
        const runs = Object.keys(totalDistanceData).sort((a, b) => {
          const numA = parseInt(a.split("_")[1]);
          const numB = parseInt(b.split("_")[1]);
          return numB - numA; // descending order
        });

        const updatedGames = runs.map((run_id) => {
          const gameNumber = parseInt(run_id.split("_")[1], 10);
          const distance = totalDistanceData[run_id] / 1000;

          // Compute avg heart rate recovery
          let recoverySum = 0;
          let count = 0;
          for (const playerId in heartRateRecoveryData) {
            const val = heartRateRecoveryData[playerId][run_id];
            if (val !== undefined) {
              recoverySum += val;
              count++;
            }
          }
          const avgHRRecovery = count > 0 ? (recoverySum / count).toFixed(2) : "N/A";
          const aggregatedRecommendation = aggregatedRecommendations[run_id] || "N/A";

          return {
            game: gameNumber,
            totalDistance: `${distance.toFixed(2)} km`,
            avgHeartRateRecovery: `${avgHRRecovery} bpm/s`,
            teamRecommendation: aggregatedRecommendation,
            actionTaken: false,
          };
        });

        setGames(updatedGames);
      } catch (err) {
        console.error("Error fetching team metrics or recommendations:", err);
      }
    };
    fetchData();
  }, []);

  // Update live metrics periodically when streaming
  useEffect(() => {
    let interval;
    if (isStreaming) {
      fetchMetricsAndHeartbeat();
      interval = setInterval(() => {
        fetchMetricsAndHeartbeat();
      }, 5000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isStreaming]);

  const totalPages = Math.ceil(games.length / ITEMS_PER_PAGE);
  const displayedGames = games.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE);

  const handlePageChange = (newPage) => {
    if (newPage > 0 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  const handleExportToExcel = () => {
    // Prepare Team Info Data
    const teamInfoData = [
      ["Field", "Value"],
      ["Team Name", team.name],
      ["Manager", team.manager],
      ["Physiotherapist", team.physiotherapist],
      ["Total Players", team.totalPlayers],
      ["Season Record", team.seasonRecord],
      ["League Rank", team.leagueRank],
    ];

    // Prepare Live Metrics Data
    const liveMetricsData = [
      ["Metric", "Value"],
      ["Heart Rate", liveMetrics.heartRate],
      ["Speed", liveMetrics.speed],
      ["Acceleration", liveMetrics.acceleration],
      ["Temperature", liveMetrics.temperature],
    ];

    // Prepare Chart Data
    const chartData = [["Time Point", "Average Heart Rate"]];
    heartbeatData.forEach((value, index) => {
      chartData.push([index + 1, value]); // Time Point is index + 1
    });

    // Prepare Metrics Cards Data
    const metricsCardsData = [
      ["Metric", "Value"],
      ["Overall Average Heart Rate", historicalMetrics.averageHeartRate],
      ["Overall Average Recovery Time", historicalMetrics.averageRecoveryTime],
      ["Overall Maximum Heart Rate", historicalMetrics.maxHeartRate],
    ];

    // Prepare Health Info Table Data
    const healthInfoData = [
      ["Game", "Total Distance", "Heart Rate Recovery", "Team Recommendation", "Action Taken"],
    ];
    games.forEach((game) => {
      healthInfoData.push([
        game.game,
        game.totalDistance,
        game.avgHeartRateRecovery,
        game.teamRecommendation,
        game.actionTaken ? "Yes" : "No",
      ]);
    });

    // Create WorkSheets for Each Section
    const workbook = XLSX.utils.book_new();
    const teamInfoSheet = XLSX.utils.aoa_to_sheet(teamInfoData);
    const liveMetricsSheet = XLSX.utils.aoa_to_sheet(liveMetricsData);
    const chartSheet = XLSX.utils.aoa_to_sheet(chartData);
    const metricsCardsSheet = XLSX.utils.aoa_to_sheet(metricsCardsData);
    const healthInfoSheet = XLSX.utils.aoa_to_sheet(healthInfoData);

    // Append Sheets to Workbook
    XLSX.utils.book_append_sheet(workbook, teamInfoSheet, "Team Info");
    XLSX.utils.book_append_sheet(workbook, liveMetricsSheet, "Live Metrics");
    XLSX.utils.book_append_sheet(workbook, chartSheet, "Live Heart Rate Data");
    XLSX.utils.book_append_sheet(workbook, metricsCardsSheet, "Metrics Cards");
    XLSX.utils.book_append_sheet(workbook, healthInfoSheet, "Health Info");

    // Export the Workbook as an Excel File
    const excelBuffer = XLSX.write(workbook, { bookType: "xlsx", type: "array" });
    const now = new Date();
    const formattedDate = now.toISOString().split("T")[0]; // YYYY-MM-DD
    const formattedTime = now.toTimeString().split(" ")[0].replace(/:/g, "-"); // HH-MM-SS
    const fileName = `${team.name.replace(" ", "_")}_Team_Data_${formattedDate}_${formattedTime}.xlsx`;
    saveAs(new Blob([excelBuffer], { type: "application/octet-stream" }), fileName);
  };
  
  console.log("Rendering statusMessage:", statusMessage);
  return (
    <div className="team-page">

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
      
      <Sidebar />
      <div className="page-content">
        <div className="team-header">
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start" }}>
            <button className="button" onClick={startLiveStream}>
              {buttonText}
            </button>
            {statusMessage && <div className="status-message">{statusMessage}</div>}
          </div>
        </div>

        <div className="team-section">
          <div className="container team-info">
            <img src={TeamLogo} className="team-avatar" alt="Team Avatar" />
            {renderTeamInfo()}
          </div>

          <div className="action-buttons">
            <button
              className={`button grey ${isEditing ? "disabled" : ""}`}
              onClick={() => setIsEditing(true)}
              disabled={isEditing} /* Disables the button when editing */
            >
              {isEditing ? "Editing..." : "Edit Team Information"}
            </button>
              <button className="button grey"onClick={() => setIsMessageModalOpen(true)}>Send Team Message</button>
              <button className="button grey" onClick={toggleTimetableModal}>View Training Timetable</button>
              <button className="button primary" onClick={handleExportToExcel}>Export Team Data</button>
          </div>
          {renderTimetableModal()}
          {renderMessageModal()}
        </div>

        <div className="metrics-chart-section">
          <div className="live-metrics-container">
            <h3 className="live-metrics-title">Live Metrics</h3>
            <div className="live-metrics">
              {Object.entries(liveMetrics).map(([key, value]) => (
                <div key={key} className="metric-box">
                  <div className={`metric-icon ${key.toLowerCase()}-icon`}>
                    <img src={metricIcons[key]} alt={`${key} icon`} className="icon" />
                  </div>
                  <div className="metric-info">
                    <h4>{metricTitles[key]}</h4>
                    <p>{value}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="heartbeat-chart-container">
            <h3>Average Heart Rate Over Time</h3>
            <div className="chart-wrapper">
              <Line
                data={{
                  labels: Array.from(Array(heartbeatData.length).keys()),
                  datasets: [
                    {
                      label: "Average Heart Rate",
                      data: heartbeatData,
                      borderColor: "#636ae8",
                      backgroundColor: "rgba(99, 106, 232, 0.1)",
                      pointBackgroundColor: "#636ae8",
                      pointBorderColor: "#636ae8",
                      pointRadius: 5,
                      fill: true,
                    },
                  ],
                }}
                options={heartbeatOptions}
              />
            </div>
          </div>
        </div>

        <div className="performance-summary">
          <div className="performance-card">
            <div className="rectangle green"></div>
            <div className="text-container">
              <p className="summary-title">Overall Average Heart Rate</p>
              <p className="summary-value">{historicalMetrics.averageHeartRate}</p>
            </div>
          </div>

          <div className="performance-card">
            <div className="rectangle yellow"></div>
            <div className="text-container">
              <p className="summary-title">Overall Average Recovery Time</p>
              <p className="summary-value">{historicalMetrics.averageRecoveryTime}</p>
            </div>
          </div>

          <div className="performance-card">
            <div className="rectangle red"></div>
            <div className="text-container">
              <p className="summary-title">Overall Maximum Heart Rate</p>
              <p className="summary-value">{historicalMetrics.maxHeartRate}</p>
            </div>
          </div>
        </div>

        <div className="container health-info">
          <h3>Health Information</h3>
          <table>
            <thead>
              <tr>
                <th>Game</th>
                <th>Total Distance</th>
                <th>Heart Rate Recovery</th>
                <th>Team Recommendation</th>
                <th>Action Taken?</th>
              </tr>
            </thead>
            <tbody>
              {displayedGames.map((game, index) => (
                <tr key={index}>
                  <td>{game.game}</td>
                  <td>{game.totalDistance}</td>
                  <td>{game.avgHeartRateRecovery}</td>
                  <td>{game.teamRecommendation}</td>
                  <td>
                    <input
                      type="checkbox"
                      className="action-taken-checkbox"
                      checked={game.actionTaken}
                      onChange={() => {
                        const updatedGames = [...games];
                        updatedGames[(currentPage - 1) * ITEMS_PER_PAGE + index].actionTaken =
                          !game.actionTaken;
                        setGames(updatedGames);
                      }}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="pagination">
            <button
              className={`pagination-btn ${currentPage === 1 ? "disabled" : ""}`}
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </button>
            <div className="pagination-controls">
              {Array.from({ length: totalPages }, (_, index) => (
                <button
                  key={index}
                  className={`pagination-btn ${currentPage === index + 1 ? "active" : ""}`}
                  onClick={() => handlePageChange(index + 1)}
                >
                  {index + 1}
                </button>
              ))}
            </div>
            <button
              className={`pagination-btn ${currentPage === totalPages ? "disabled" : ""}`}
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeamPageWithBackend;
