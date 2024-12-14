import React, { useState, useEffect } from "react";
import { useNotifications } from "../context/NotificationContext";
import { useTeam } from "../context/TeamContext";
import Modal from "react-modal";
import { Line } from "react-chartjs-2"; // Import the Line chart component
import "../styles/PlayersPage.css";
import Sidebar from "../components/Sidebar";
import PlayersDropdownWithCheckboxes from "../components/PlayersDropdownWithCheckboxes"; 

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
    width: "58%", // Set the width of the modal
    maxHeight: "80%", // Add scroll for overflow
    overflowY: "auto",
    borderRadius: "10px",
    padding: "20px",
  },
};

const ITEMS_PER_PAGE = 2;
const STREAM_SECONDS = 30; // Duration for live data streaming

const PlayersPageWithBackend = () => {

  const { addNotification } = useNotifications();

  const [players, setPlayers] = useState([
    {
      id: "1",
      name: "Liam Carter",
      age: 25,
      team: "Lakeside FC",
      position: "Central Midfielder",
      metrics: {
        heartRate: "Loading...",
        speed: "Loading...",
        acceleration: "Loading...",
        temperature: "Loading...",
      },
      heartbeatData: [],
    },
    {
      id: "2",
      name: "Ethan Brooks",
      age: 23,
      team: "Lakeside FC",
      position: "Central Defender",
      metrics: {
        heartRate: "Loading...",
        speed: "Loading...",
        acceleration: "Loading...",
        temperature: "Loading...",
      },
      heartbeatData: [],
    },
    {
      id: "3",
      name: "Noah Bennett",
      age: 21,
      team: "Lakeside FC",
      position: "Striker",
      metrics: {
        heartRate: "Loading...",
        speed: "Loading...",
        acceleration: "Loading...",
        temperature: "Loading...",
      },
      heartbeatData: [],
    },
    {
      id: "4",
      name: "Oliver Hayes",
      age: 24,
      team: "Lakeside FC",
      position: "Defensive Midfielder",
      metrics: {
        heartRate: "Loading...",
        speed: "Loading...",
        acceleration: "Loading...",
        temperature: "Loading...",
      },
      heartbeatData: [],
    },
    {
      id: "5",
      name: "William Mason",
      age: 26,
      team: "Lakeside FC",
      position: "Left Back",
      metrics: {
        heartRate: "Loading...",
        speed: "Loading...",
        acceleration: "Loading...",
        temperature: "Loading...",
      },
      heartbeatData: [],
    },
    {
      id: "6",
      name: "Lucas Graham",
      age: 22,
      team: "Lakeside FC",
      position: "Attacking Midfielder",
      metrics: {
        heartRate: "Loading...",
        speed: "Loading...",
        acceleration: "Loading...",
        temperature: "Loading...",
      },
      heartbeatData: [],
    },
    {
      id: "7",
      name: "James Turner",
      age: 27,
      team: "Lakeside FC",
      position: "Right Winger",
      metrics: {
        heartRate: "Loading...",
        speed: "Loading...",
        acceleration: "Loading...",
        temperature: "Loading...",
      },
      heartbeatData: [],
    },
    {
      id: "8",
      name: "Henry Mitchell",
      age: 24,
      team: "Lakeside FC",
      position: "Central Defender",
      metrics: {
        heartRate: "Loading...",
        speed: "Loading...",
        acceleration: "Loading...",
        temperature: "Loading...",
      },
      heartbeatData: [],
    },
    {
      id: "9",
      name: "Jack Coleman",
      age: 22,
      team: "Lakeside FC",
      position: "Left Winger",
      metrics: {
        heartRate: "Loading...",
        speed: "Loading...",
        acceleration: "Loading...",
        temperature: "Loading...",
      },
      heartbeatData: [],
    },
    {
      id: "10",
      name: "Alexander Price",
      age: 28,
      team: "Lakeside FC",
      position: "Striker",
      metrics: {
        heartRate: "Loading...",
        speed: "Loading...",
        acceleration: "Loading...",
        temperature: "Loading...",
      },
      heartbeatData: [],
    },
  ]);

  const [isModalOpen, setIsModalOpen] = useState(false); // For "View All Players" modal
  const [isEditing, setIsEditing] = useState(false); // For editing mode


  // Open and close the modal
  const toggleModal = () => {
    setIsModalOpen(!isModalOpen);
    setIsEditing(false); // Reset editing mode when modal is closed
  };

  // Add a new player
  const addNewPlayer = () => {
    const newPlayer = {
      id: (players.length + 1).toString(),
      name: "",
      age: "",
      team: "Lakeside FC",
      position: "",
      metrics: {
        heartRate: "Loading...",
        speed: "Loading...",
        acceleration: "Loading...",
        temperature: "Loading...",
      },
      heartbeatData: [],
    };
    setPlayers([...players, newPlayer]);
    setIsEditing(true); // Automatically enable editing mode
  };

  // Save changes
  const savePlayers = () => {
    console.log("Saved players:", players);
    setIsEditing(false);
  };

  // Handle edits to player details in the modal
  const handlePlayerEdit = (index, field, value) => {
    const updatedPlayers = [...players];
    updatedPlayers[index][field] = value;
    setPlayers(updatedPlayers);
  };
  
  const deletePlayer = (index) => {
    const updatedPlayers = players.filter((_, i) => i !== index);
    setPlayers(updatedPlayers);
  };

  // Updated renderPlayersModal function
  const renderPlayersModal = () => (
    <Modal
      isOpen={isModalOpen}
      onRequestClose={toggleModal}
      style={customModalStyles}
      contentLabel="View All Players Modal"
    >
      <div className="modal-header">
        <h2>List of Players</h2>
      </div>
      <div className="modal-body">
        <div className="actions-and-table">
          <div className="button-column">
            <button className="button small primary" onClick={addNewPlayer}>
              Add New Player
            </button>
            <button
              className={`button small ${isEditing ? "primary" : "grey"}`}
              onClick={() => {
                if (isEditing) savePlayers(); // Save when in editing mode
                setIsEditing(!isEditing); // Toggle editing mode
              }}
            >
              {isEditing ? "Save" : "Edit"}
            </button>
          </div>
          <div className="table-column">
            {players.length > 0 ? (
              <table className="players-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Age</th>
                    <th>Position</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {players.map((player, index) => (
                    <tr key={index}>
                      <td>{player.id}</td>
                      <td>
                        <input
                          type="text"
                          value={player.name}
                          disabled={!isEditing}
                          onChange={(e) =>
                            handlePlayerEdit(index, "name", e.target.value)
                          }
                        />
                      </td>
                      <td>
                        <input
                          type="number"
                          value={player.age}
                          disabled={!isEditing}
                          onChange={(e) =>
                            handlePlayerEdit(index, "age", e.target.value)
                          }
                        />
                      </td>
                      <td>
                        <input
                          type="text"
                          value={player.position}
                          disabled={!isEditing}
                          onChange={(e) =>
                            handlePlayerEdit(index, "position", e.target.value)
                          }
                        />
                      </td>
                      <td>
                        <button
                          className="delete-icon"
                          onClick={() => deletePlayer(index)}
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="no-players-message">No players available.</p>
            )}
          </div>
        </div>
        <button className="button grey small close-button" onClick={toggleModal}>
          Close
        </button>
      </div>
    </Modal>
  );

  const { team } = useTeam(); // Access the team context
  const { manager, physiotherapist } = team;

  const [playerMessage, setPlayerMessage] = useState({
    to: [], // Array of selected player names
    from: `${manager} [Team Manager]`,
    subject: "",
    message: "",
  });
  
  const [isMessageModalOpen, setIsMessageModalOpen] = useState(false); // Manage the "Send Player Message" modal visibility
  const [successMessage, setSuccessMessage] = useState(""); // Toast for success notification

  // Send Player Message Handler
  // Send Player Message Handler
  const handleSendPlayerMessage = () => {
    const { to, from, subject, message } = playerMessage;

    if (!subject.trim()) {
      alert("Subject cannot be empty.");
      return;
    }

    if (!message.trim()) {
      alert("Message cannot be empty.");
      return;
    }

    if (to.length === 0) {
      alert("Please select at least one recipient.");
      return;
    }

    // Create individual notifications for each recipient
    to.forEach((recipient) => {
      addNotification({
        id: `${Date.now()}-${recipient}`, // Unique ID for each notification
        title: subject,
        body: message,
        sender: from,
        to: recipient,
        timestamp: Date.now(),
        isRead: false, // Default to unread
      });
    });

    // Show success message
    setSuccessMessage("Message successfully sent!");

    // Reset modal and form
    setIsMessageModalOpen(false);
    setPlayerMessage({
      to: [],
      from: "Coach [Logged In User]",
      subject: "",
      message: "",
    });

    // Clear success message after 3 seconds
    setTimeout(() => setSuccessMessage(""), 3000);
  };

  const renderPlayerMessageModal = () => (
    <Modal
      isOpen={isMessageModalOpen}
      onRequestClose={() => setIsMessageModalOpen(false)}
      style={customModalStyles}
      contentLabel="Send Player Message"
    >
      <h2>Send Player Message</h2>
      <form style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        {/* To Field */}
        <div style={{ display: "flex", flexDirection: "column" }}>
          <label htmlFor="to" style={{ fontWeight: "bold" }}>To:</label>
          <PlayersDropdownWithCheckboxes
            players={players}
            selectedPlayers={playerMessage.to}
            onSelectionChange={(updatedSelection) =>
              setPlayerMessage({
                ...playerMessage,
                to: updatedSelection,
              })
            }
          />
        </div>
  
        {/* From Field */}
        <div style={{ display: "flex", flexDirection: "column" }}>
          <label htmlFor="from" style={{ fontWeight: "bold" }}>From:</label>
          <select
            id="from"
            value={playerMessage.from}
            onChange={(e) =>
              setPlayerMessage({ ...playerMessage, from: e.target.value })
            }
            style={{
              width: "100%",
              padding: "10px",
              borderRadius: "5px",
              border: "1px solid #ccc",
            }}
          >
            <option value={`${manager} [Team Manager]`}>
              {manager} [Team Manager]
            </option>
            <option value={`${physiotherapist} [Physiotherapist]`}>
              {physiotherapist} [Physiotherapist]
            </option>
          </select>
        </div>
  
        {/* Subject Field */}
        <div style={{ display: "flex", flexDirection: "column" }}>
          <label htmlFor="subject" style={{ fontWeight: "bold" }}>Subject:</label>
          <input
            id="subject"
            type="text"
            value={playerMessage.subject}
            onChange={(e) =>
              setPlayerMessage({ ...playerMessage, subject: e.target.value })
            }
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
            value={playerMessage.message}
            onChange={(e) =>
              setPlayerMessage({ ...playerMessage, message: e.target.value })
            }
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
            onClick={handleSendPlayerMessage}
          >
            Send
          </button>
        </div>
      </form>
    </Modal>
  );
  
  

  const [selectedPlayer, setSelectedPlayer] = useState(players[0]);
  const [games, setGames] = useState([]);
  const [historicalMetrics, setHistoricalMetrics] = useState({
    averageHeartRate: "N/A",
    averageRecoveryTime: "N/A",
    maxHeartRate: "N/A",
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [isStreaming, setIsStreaming] = useState(false);
  const [buttonText, setButtonText] = useState("Start Live Stream");
  const [statusMessage, setStatusMessage] = useState("");
  const [fatigueLevels, setFatigueLevels] = useState({});
  const [loading, setLoading] = useState(true);
  
  // Fetch fatigue data
    useEffect(() => {
      const fetchFatigueData = async () => {
        try {
          const response = await fetch("http://localhost:8000/fatigue-distribution");
          const data = await response.json();
          console.log("Fetched fatigue data:", data);
          setFatigueLevels(data["Detailed Fatigue Data"]);
          setLoading(false);
        } catch (error) {
          console.error("Error fetching fatigue data:", error);
          setLoading(false);
        }
      };
  
      fetchFatigueData();
    }, []);
  
    // Get the latest fatigue level for the selected player
    const getLatestFatigueLevel = (playerId) => {
      if (loading) return "Loading...";
      console.log("Player ID:", playerId);
      console.log("Fatigue Data:", fatigueLevels);
      const playerFatigueData = fatigueLevels[playerId];
      if (playerFatigueData) {
        const latestRun = Object.keys(playerFatigueData)
          .map((run) => parseInt(run.split("_")[1])) // Extract run numbers
          .sort((a, b) => b - a)[0]; // Get the highest run number
        const latestRunKey = `run_${String(latestRun).padStart(3, "0")}`; // Zero-pad to 3 digits
        console.log("Latest Run Key:", latestRunKey, "Value:", playerFatigueData[latestRunKey]);
        return playerFatigueData[latestRunKey] || "Unknown";
      }
      console.log("No fatigue data found for player:", playerId);
      return "Unknown";
    };

    // Fetch historical metrics
    const fetchHistoricalMetrics = async (playerId) => {
      try {
        const [metricsRes, fatigueRes, recRes] = await Promise.all([
          fetch("http://localhost:8000/team-metrics"),
          fetch("http://localhost:8000/fatigue-distribution"),
          fetch("http://localhost:8000/recommendations"),
        ]);

        const metricsData = await metricsRes.json();
        const fatigueData = await fatigueRes.json();
        const recommendationsData = await recRes.json();

        // Log the raw data fetched from each endpoint
        console.log("Metrics Data for Player:", playerId, metricsData);
        console.log("Fatigue Data for Player:", playerId, fatigueData);
        console.log("Recommendations Data for Player:", playerId, recommendationsData);

        // Update historical metrics
        const avgHeartRate =
          metricsData["Player Average Heart Rate"]?.[playerId]?.toFixed(1) || "N/A";
        const maxHeartRate = metricsData["Player Max Heart Rate"]?.[playerId] || "N/A";
        const recoveryTimes = Object.values(
          metricsData["Player Average Heart Rate Recovery"]?.[playerId] || {}
        );
        const avgRecoveryTime = recoveryTimes.length
          ? (recoveryTimes.reduce((sum, val) => sum + val, 0) / recoveryTimes.length).toFixed(2)
          : "N/A";

        // Log computed metrics
        console.log("Computed Metrics for Player:", playerId, {
          avgHeartRate,
          maxHeartRate,
          avgRecoveryTime,
        });

        setHistoricalMetrics({
          averageHeartRate: `${avgHeartRate} bpm`,
          averageRecoveryTime: `${avgRecoveryTime} bpm/s`,
          maxHeartRate: `${maxHeartRate} bpm`,
        });

        // Update games (health info table)
        const playerGames = Object.keys(
          metricsData["Player Average Heart Rate Recovery"]?.[playerId] || {}
        ).map((runId) => {
          const gameNumber = parseInt(runId.split("_")[1], 10);
          const heartRateRecovery =
            metricsData["Player Average Heart Rate Recovery"][playerId][runId]?.toFixed(2) || "N/A";
          const fatigueLevel =
            fatigueData["Detailed Fatigue Data"]?.[playerId]?.[runId] || "N/A";
          const recommendation =
            recommendationsData["Player Recommendations Per Game"]?.[runId]?.[playerId] ||
            "No recommendation";
          
          // Log individual game data
          console.log(`Game Data for Player ${playerId}, Run ${runId}:`, {
            gameNumber,
            heartRateRecovery,
            fatigueLevel,
            recommendation,
          });

          return {
            game: gameNumber,
            heartRateRecovery: `${heartRateRecovery} bpm/s`,
            fatigueLevel,
            recommendation,
            actionTaken: false,
          };
        })
        .sort((a, b) => b.game - a.game);

        // Log final sorted game data
        console.log("Final Games List for Player:", playerId, playerGames);

        setGames(playerGames);
      } catch (error) {
        console.error("Error fetching historical metrics:", error);
      }
    };

    const handlePlayerChange = (event) => {
      const selectedId = event.target.value;
      const player = players.find((p) => p.id === selectedId);
      setSelectedPlayer(player);
      setCurrentPage(1); // Reset to the first page when changing the player
      fetchHistoricalMetrics(selectedId); // Fetch historical metrics for new player
    };

    // Fetch metrics for default player on mount
    useEffect(() => {
      fetchHistoricalMetrics(selectedPlayer.id);
    }, [selectedPlayer.id]);

     // Paginated games for health info table
  const displayedGames = games.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const totalPages = Math.ceil(games.length / ITEMS_PER_PAGE);

  const handlePageChange = (newPage) => {
    if (newPage > 0 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

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

  const fetchLiveMetrics = async (player) => {
    const heartRateUrl = `http://localhost:8000/get-stats/player_heart_rate_${player.id}/run_001?agg_type=average`;
    const speedUrl = `http://localhost:8000/get-speed/gps_${player.id}/run_001?type=speed`;
    const accelerationUrl = `http://localhost:8000/get-speed/gps_${player.id}/run_001?type=acceleration`;
    const temperatureUrl = `http://localhost:8000/get-stats/player_temperature_${player.id}/run_001?agg_type=average`;

    // Logs for debugging
    console.log("Fetching metrics for:", player.name);
    console.log("Heart Rate URL:", heartRateUrl);
    console.log("Temperature URL:", temperatureUrl);
    console.log("Speed URL:", speedUrl);
    console.log("Acceleration URL:", accelerationUrl);

    try {
      const [heartRateRes, speedRes, accelerationRes, temperatureRes] = await Promise.all([
        fetch(heartRateUrl),
        fetch(speedUrl),
        fetch(accelerationUrl),
        fetch(temperatureUrl),
      ]);

      const heartRateData = await heartRateRes.json();
      const speedData = await speedRes.json();
      const accelerationData = await accelerationRes.json();
      const temperatureData = await temperatureRes.json();

      const liveMetrics = {
        heartRate: `${heartRateData.average_heart_rate.toFixed(1)} BPM`,
        speed: `${speedData.speed.toFixed(2)} KM/H`,
        acceleration: `${accelerationData.acceleration.toFixed(2)} M/S²`,
        temperature: `${temperatureData.average_temperature.toFixed(1)} °C`,
      };

      setSelectedPlayer((prevPlayer) => ({
        ...prevPlayer,
        metrics: liveMetrics,
        heartbeatData: [...prevPlayer.heartbeatData, heartRateData.average_heart_rate.toFixed(1)],
      }));
    } catch (error) {
      console.error("Error fetching live metrics:", error);
    }
  };

  useEffect(() => {
    let interval;
    if (isStreaming) {
      fetchLiveMetrics(selectedPlayer); // Fetch metrics immediately
      interval = setInterval(() => {
        fetchLiveMetrics(selectedPlayer); // Fetch metrics every 5 seconds
      }, 5000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isStreaming, selectedPlayer]);

  const startLiveStream = () => {
    console.log("Initialising live stream for player:", selectedPlayer.name);
    setStatusMessage("");
    console.log("Status Message reset to empty");
    setButtonText("Starting...");
  
    // Start the synthetic data stream
    fetch(`http://localhost:8000/start-synthetic-data?num_players=10&stream_seconds=${STREAM_SECONDS}`, {
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Synthetic data stream started:", data);
        setIsStreaming(true);
        setButtonText("Streaming...");
        setStatusMessage("Streaming started...");
        console.log("Status Message updated to: Streaming started...");

  
        // Set up live metrics fetching tied to the specific player
        const playerId = selectedPlayer.id; // Store the current player ID
        const interval = setInterval(() => {
          if (selectedPlayer.id === playerId) {
            // Only fetch metrics if the selected player is still the same
            fetchLiveMetrics(selectedPlayer);
          } else {
            clearInterval(interval); // Stop the interval if the player changes
          }
        }, 5000);
  
        // Stop streaming after the specified duration
        setTimeout(() => {
          clearInterval(interval);
          setIsStreaming(false);
          setButtonText("Start Live Stream");
          setStatusMessage("Streaming ended. Press 'Start Live Stream' to restart.");
          console.log("Status Message updated to: Streaming ended. Press 'Start Live Stream' to restart.");
        }, STREAM_SECONDS * 1000);
      })
      .catch((error) => {
        console.error("Error starting synthetic data stream:", error);
        setButtonText("Start Live Stream");
        setStatusMessage("Failed to start streaming.");
      });
  };

  const heartbeatData = {
    labels: Array.from({ length: selectedPlayer.heartbeatData.length }, (_, i) => i + 1),
    datasets: [
      {
        label: "Heart Rate",
        data: selectedPlayer.heartbeatData,
        borderColor: "#636ae8",
        backgroundColor: "rgba(99, 106, 232, 0.1)",
        pointBackgroundColor: "#636ae8",
        pointBorderColor: "#636ae8",
        pointRadius: 5,
        fill: true,
      },
    ],
  };

  const heartbeatOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: { grid: { display: false } },
      y: { beginAtZero: true, ticks: { stepSize: 20 } },
    },
    plugins: { legend: { display: false } },
  };

  const handleExportCurrentPlayerData = () => {
    if (!selectedPlayer) return;
  
    // Data for the selected player
    const currentPlayerData = [
      ["Field", "Value"],
      ["ID", selectedPlayer.id],
      ["Name", selectedPlayer.name],
      ["Age", selectedPlayer.age],
      ["Team", selectedPlayer.team],
      ["Position", selectedPlayer.position],
      ["Fatigue Level", getLatestFatigueLevel(selectedPlayer.id)],
    ];
  
    // Live Metrics Data
    const liveMetricsData = [
      ["Metric", "Value"],
      ["Heart Rate", selectedPlayer.metrics.heartRate],
      ["Speed", selectedPlayer.metrics.speed],
      ["Acceleration", selectedPlayer.metrics.acceleration],
      ["Temperature", selectedPlayer.metrics.temperature],
    ];
  
    // Average heart rate over time (Chart Data)
    const chartData = [["Time Point", "Average Heart Rate"]];
    selectedPlayer.heartbeatData.forEach((value, index) => {
      chartData.push([index + 1, value]); // Time Point is index + 1
    });
  
    // Metrics Cards Info
    const metricsCardsData = [
      ["Metric", "Value"],
      ["Overall Average Heart Rate", historicalMetrics.averageHeartRate],
      ["Overall Average Recovery Time", historicalMetrics.averageRecoveryTime],
      ["Overall Maximum Heart Rate", historicalMetrics.maxHeartRate],
    ];
  
    // Health Information Table
    const healthInfoData = [
      ["Game", "Heart Rate Recovery", "Fatigue Level", "Player Recommendation", "Action Taken"],
    ];
    games.forEach((game) => {
      healthInfoData.push([
        game.game,
        game.heartRateRecovery,
        game.fatigueLevel,
        game.recommendation,
        game.actionTaken ? "Yes" : "No",
      ]);
    });
  
    // Create Workbook and Add Sheets
    const workbook = XLSX.utils.book_new();
    const playerInfoSheet = XLSX.utils.aoa_to_sheet(currentPlayerData);
    const liveMetricsSheet = XLSX.utils.aoa_to_sheet(liveMetricsData); // New Live Metrics sheet
    const chartSheet = XLSX.utils.aoa_to_sheet(chartData);
    const metricsCardsSheet = XLSX.utils.aoa_to_sheet(metricsCardsData);
    const healthInfoSheet = XLSX.utils.aoa_to_sheet(healthInfoData);
  
    XLSX.utils.book_append_sheet(workbook, playerInfoSheet, "Player Info");
    XLSX.utils.book_append_sheet(workbook, liveMetricsSheet, "Live Metrics"); // Append new sheet
    XLSX.utils.book_append_sheet(workbook, chartSheet, "Live Heart Rate Data");
    XLSX.utils.book_append_sheet(workbook, metricsCardsSheet, "Metrics Cards");
    XLSX.utils.book_append_sheet(workbook, healthInfoSheet, "Health Info");
  
    // Format the filename
    const now = new Date();
    const formattedDate = now.toISOString().split("T")[0]; // YYYY-MM-DD
    const formattedTime = now.toTimeString().split(" ")[0].replace(/:/g, "-"); // HH-MM-SS
    const fileName = `${selectedPlayer.name.replace(" ", "_")}_Data_${formattedDate}_${formattedTime}.xlsx`;
  
    // Export as Excel File
    const excelBuffer = XLSX.write(workbook, { bookType: "xlsx", type: "array" });
    saveAs(new Blob([excelBuffer], { type: "application/octet-stream" }), fileName);
  };

  const [isExporting, setIsExporting] = useState(false); // Add this to manage the loading state

  
  const handleExportAllPlayersData = async () => {
    if (!players || players.length === 0) return;
  
    setIsExporting(true); // Set the loading state to true
  
    const workbook = XLSX.utils.book_new(); // Create a new workbook
  
    // Prepare Player Info Sheet
    const playerInfoData = [
      ["ID", "Name", "Age", "Team", "Position", "Fatigue Level"],
    ];
    players.forEach((player) => {
      playerInfoData.push([
        player.id,
        player.name,
        player.age,
        player.team,
        player.position,
        getLatestFatigueLevel(player.id),
      ]);
    });
  
    // Parallel Fetching: Metrics and Health Info for all players
    const fetchDataForPlayers = async () => {
      try {
        const metricsResponses = await Promise.all(
          players.map((player) =>
            fetch(`http://localhost:8000/team-metrics`).then((res) => res.json())
          )
        );
  
        const recommendationsResponses = await Promise.all(
          players.map((player) =>
            fetch(`http://localhost:8000/recommendations`).then((res) => res.json())
          )
        );
  
        const fatigueResponses = await Promise.all(
          players.map((player) =>
            fetch(`http://localhost:8000/fatigue-distribution`).then((res) => res.json())
          )
        );
  
        return { metricsResponses, recommendationsResponses, fatigueResponses };
      } catch (error) {
        console.error("Error fetching data for players:", error);
        throw error;
      }
    };
  
    let metricsResponses = [];
    let recommendationsResponses = [];
    let fatigueResponses = [];
    try {
      ({ metricsResponses, recommendationsResponses, fatigueResponses } =
        await fetchDataForPlayers());
    } catch (error) {
      console.error("Failed to fetch data:", error);
      setIsExporting(false); // Reset loading state if an error occurs
      return; // Exit if there's a problem fetching data
    }
  
    // Prepare Live Metrics Sheet
    const liveMetricsData = [
      ["ID", "Name", "Heart Rate", "Speed", "Acceleration", "Temperature"],
    ];
    players.forEach((player) => {
      liveMetricsData.push([
        player.id,
        player.name,
        player.metrics.heartRate,
        player.metrics.speed,
        player.metrics.acceleration,
        player.metrics.temperature,
      ]);
    });
  
    // Prepare Metrics Cards Sheet
    const metricsCardsData = [
      [
        "Player ID",
        "Player Name",
        "Overall Average Heart Rate",
        "Overall Average Recovery Time",
        "Overall Maximum Heart Rate",
      ],
    ];
    players.forEach((player, index) => {
      const metrics = metricsResponses[index];
      const avgHeartRate =
        metrics["Player Average Heart Rate"]?.[player.id]?.toFixed(1) || "N/A";
      const maxHeartRate = metrics["Player Max Heart Rate"]?.[player.id] || "N/A";
      const recoveryTimes = Object.values(
        metrics["Player Average Heart Rate Recovery"]?.[player.id] || {}
      );
      const avgRecoveryTime = recoveryTimes.length
        ? (
            recoveryTimes.reduce((sum, val) => sum + val, 0) / recoveryTimes.length
          ).toFixed(2)
        : "N/A";
  
      metricsCardsData.push([
        player.id,
        player.name,
        `${avgHeartRate} bpm`,
        `${avgRecoveryTime} bpm/s`,
        `${maxHeartRate} bpm`,
      ]);
    });
  
    // Prepare Health Information Sheet
    const healthInfoData = [
      [
        "Player ID",
        "Player Name",
        "Game",
        "Heart Rate Recovery",
        "Fatigue Level",
        "Player Recommendation",
        "Action Taken",
      ],
    ];
    players.forEach((player, index) => {
      const fatigueData = fatigueResponses[index];
      const recommendationsData = recommendationsResponses[index];
      const metrics = metricsResponses[index];
  
      const playerGames = Object.keys(
        metrics["Player Average Heart Rate Recovery"]?.[player.id] || {}
      ).map((runId) => {
        const gameNumber = parseInt(runId.split("_")[1], 10);
        const heartRateRecovery =
          metrics["Player Average Heart Rate Recovery"]?.[player.id]?.[runId]?.toFixed(
            2
          ) || "N/A";
        const fatigueLevel =
          fatigueData["Detailed Fatigue Data"]?.[player.id]?.[runId] || "N/A";
        const recommendation =
          recommendationsData["Player Recommendations Per Game"]?.[runId]?.[player.id] ||
          "No recommendation";
  
        return {
          game: gameNumber,
          heartRateRecovery: `${heartRateRecovery} bpm/s`,
          fatigueLevel,
          recommendation,
          actionTaken: false,
        };
      });
  
      playerGames.forEach((game) => {
        healthInfoData.push([
          player.id,
          player.name,
          game.game,
          game.heartRateRecovery,
          game.fatigueLevel,
          game.recommendation,
          game.actionTaken ? "Yes" : "No",
        ]);
      });
    });
  
    // Prepare Chart Data Sheet (Average Heart Rate Over Time)
    const chartData = [
      ["Player ID", "Player Name", "Time Point", "Average Heart Rate"],
    ];
    players.forEach((player) => {
      player.heartbeatData.forEach((value, index) => {
        chartData.push([
          player.id,
          player.name,
          index + 1, // Time Point
          value,
        ]);
      });
    });
  
    // Add Sheets to Workbook
    XLSX.utils.book_append_sheet(workbook, XLSX.utils.aoa_to_sheet(playerInfoData), "Player Info");
    XLSX.utils.book_append_sheet(
      workbook,
      XLSX.utils.aoa_to_sheet(liveMetricsData),
      "Live Metrics"
    );
    XLSX.utils.book_append_sheet(
      workbook,
      XLSX.utils.aoa_to_sheet(chartData),
      "Live Heart Rate Data"
    );
    XLSX.utils.book_append_sheet(
      workbook,
      XLSX.utils.aoa_to_sheet(metricsCardsData),
      "Metrics Cards"
    );
    XLSX.utils.book_append_sheet(
      workbook,
      XLSX.utils.aoa_to_sheet(healthInfoData),
      "Health Info"
    );
      
    // Format the filename
    const now = new Date();
    const formattedDate = now.toISOString().split("T")[0]; // YYYY-MM-DD
    const formattedTime = now.toTimeString().split(" ")[0].replace(/:/g, "-"); // HH-MM-SS
    const fileName = `All_Players_Data_${formattedDate}_${formattedTime}.xlsx`;
  
    // Export the Workbook
    const excelBuffer = XLSX.write(workbook, { bookType: "xlsx", type: "array" });
    saveAs(new Blob([excelBuffer], { type: "application/octet-stream" }), fileName);
  
    setIsExporting(false); // Reset loading state after completion
  };

  return (
    <div className="players-page">

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
        <div className="header">
          <select
            className="player-dropdown"
            onChange={handlePlayerChange}
            value={selectedPlayer.id}
          >
            {players.map((player) => (
              <option key={player.id} value={player.id}>
                {player.name}
              </option>
            ))}
          </select>
          <button className="button" onClick={startLiveStream}>
            {buttonText}
          </button>
          {statusMessage && <p className="status-message">{statusMessage}</p>}
        </div>

        <div className="player-section">
          <div className="container player-info">
            <img
              src={`https://via.placeholder.com/133?text=${selectedPlayer.name.charAt(0)}`}
              alt={selectedPlayer.name}
              className="player-avatar"
            />
            <div className="player-details">
              <h2>{selectedPlayer.name}</h2>
              <p>
                #{selectedPlayer.id} | {selectedPlayer.position} | {selectedPlayer.age} years
              </p>
              <span
                className={`badge ${getLatestFatigueLevel(selectedPlayer.id)?.toLowerCase()}-fatigue`}
              >
                {getLatestFatigueLevel(selectedPlayer.id)} Fatigue
              </span>
            </div>
          </div>

          <div className="action-buttons">
            <button className="button grey" onClick={toggleModal}>View Players</button>
            <button className="button grey" onClick={() => setIsMessageModalOpen(true)}>Send Player Message</button>
            <button className="button grey" onClick={handleExportCurrentPlayerData}>Export Current Player Data</button>
            <button
              className={`button ${isExporting ? "grey" : "primary"}`}
              onClick={handleExportAllPlayersData}
              disabled={isExporting}
            >
              {isExporting ? "Exporting..." : "Export All Players Data"}
            </button>
            {renderPlayersModal()}
            {renderPlayerMessageModal()}
          </div>
        </div>

        <div className="metrics-chart-section">
          <div className="live-metrics-container">
            <h3 className="live-metrics-title">Live Metrics</h3>
            <div className="live-metrics">
              {Object.entries(selectedPlayer.metrics).map(([key, value]) => (
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
              <Line data={heartbeatData} options={heartbeatOptions} />
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
                <th>Heart Rate Recovery</th>
                <th>Fatigue Level</th>
                <th>Player Recommendation</th>
                <th>Action Taken?</th>
              </tr>
            </thead>
            <tbody>
              {displayedGames.map((game, index) => (
                <tr key={index}>
                  <td>{game.game}</td>
                  <td>{game.heartRateRecovery}</td>
                  <td>
                    <span className={`fatigue-badge ${game.fatigueLevel.toLowerCase()}`}>
                      {game.fatigueLevel}
                    </span>
                  </td>
                  <td>{game.recommendation}</td>
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

export default PlayersPageWithBackend;

