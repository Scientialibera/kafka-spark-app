import React, { useState, useEffect } from "react";

const LiveAlarms = ({ numPlayers, runId, players }) => {
  const [alarms, setAlarms] = useState({});
  const [loading, setLoading] = useState(true);
  

  useEffect(() => {
    let interval;

    const fetchAlarms = async () => {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/analyze-heart-rate/${numPlayers}/${runId}`
        );
        const data = await response.json();
        console.log("Fetched data:", data); // Log fetched data

        // Check if we have valid analyzed_data
        if (data.analyzed_data && data.analyzed_data.length > 0) {
          setAlarms((prevAlarms) => {
            const updatedAlarms = data.analyzed_data.reduce((acc, alarm) => {
              const deviceId = alarm.device_id || "";
              // Extract the player ID from the device_id if present
              const parts = deviceId.split("_");
              const playerId = parts.length > 0 ? String(parts.pop()) : null;

              if (playerId) {
                acc[playerId] = {
                  heartRate: alarm.heart_rate,
                  status: alarm.alarm_type,
                };
              }

              return acc;
            }, {});

            // Merge old alarms with new ones
            const newAlarms = { ...prevAlarms, ...updatedAlarms };
            console.log("Updated alarms:", newAlarms);
            return newAlarms;
          });

          if (loading) setLoading(false);
        } else {
          // No analyzed_data returned, assume streaming ended
          console.error("No analyzed_data found in the response. Stopping fetch.");
          if (interval) {
            clearInterval(interval);
          }
        }
      } catch (error) {
        console.error("Error fetching alarms:", error);
      }
    };

    // Start fetching if we have required params
    if (numPlayers && runId) {
      interval = setInterval(fetchAlarms, 5000);
      fetchAlarms();
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [numPlayers, runId, loading]);

  const getPlayerAlarmData = (playerId) => {
    const alarm = alarms[String(playerId)];

    if (alarm) {
      return {
        heartRate: alarm.heartRate ?? "N/A",
        status: alarm.status ?? "N/A",
      };
    }

    // If we are still loading and have no alarms, show loading
    if (loading && Object.keys(alarms).length === 0) {
      return {
        heartRate: "Loading...",
        status: "Loading...",
      };
    }

    // Otherwise, no data available for this player
    return {
      heartRate: "N/A",
      status: "N/A",
    };
  };

  return (
    <div className="live-alarms">
      <h3 className="table-heading">Real-Time Heart Rate Monitoring</h3>
      <table className="live-alarms-table">
        <thead>
          <tr>
            {players.map((player) => (
              <th key={player.id}>Player {player.id}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            {players.map((player) => (
              <td key={player.id}>{player.name}</td>
            ))}
          </tr>
          <tr>
            {players.map((player) => {
              const alarmData = getPlayerAlarmData(player.id);
              return <td key={player.id}>{alarmData.heartRate} BPM</td>;
            })}
          </tr>
          <tr>
            {players.map((player) => {
              const alarmData = getPlayerAlarmData(player.id);
              const isNormal = alarmData.status === "normal";
              const isAbnormal = alarmData.status === "low" || alarmData.status === "high";
              return (
                <td key={player.id}>
                  <span
                    className={`status ${
                      isNormal ? "normal" : isAbnormal ? "abnormal" : "na"
                    }`}
                  >
                    {alarmData.status}
                  </span>
                </td>
              );
            })}
          </tr>
        </tbody>
      </table>
    </div>
  );
};

export default LiveAlarms;
