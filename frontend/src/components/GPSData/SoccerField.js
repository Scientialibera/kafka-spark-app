import React, { useState, useEffect } from "react";
import "../../styles/SoccerField.css";
import soccerFieldBg from "../../icons/soccer-field.jpg"; // Ensure correct path and extension

const SoccerField = () => {
  const FIELD_WIDTH = 600; // Width of the soccer field
  const FIELD_HEIGHT = 400; // Height of the soccer field
  const GOAL_AREA_PADDING = 50; // Padding to avoid players entering the goal areas

  const [players, setPlayers] = useState([
    {
      id: 1,
      x: 100,
      y: 50,
      metrics: {
        heartRate: "120 BPM",
        speed: "22 KM/H",
        acceleration: "1.2 M/S²",
        temperature: "37°C",
      },
    },
    {
      id: 2,
      x: 150,
      y: 100,
      metrics: {
        heartRate: "115 BPM",
        speed: "20 KM/H",
        acceleration: "1.1 M/S²",
        temperature: "36.8°C",
      },
    },
    {
      id: 3,
      x: 200,
      y: 150,
      metrics: {
        heartRate: "130 BPM",
        speed: "23 KM/H",
        acceleration: "1.3 M/S²",
        temperature: "37.1°C",
      },
    },
    {
      id: 4,
      x: 250,
      y: 200,
      metrics: {
        heartRate: "110 BPM",
        speed: "18 KM/H",
        acceleration: "1.0 M/S²",
        temperature: "36.5°C",
      },
    },
    {
      id: 5,
      x: 300,
      y: 250,
      metrics: {
        heartRate: "140 BPM",
        speed: "25 KM/H",
        acceleration: "1.4 M/S²",
        temperature: "37.5°C",
      },
    },
    {
      id: 6,
      x: 350,
      y: 100,
      metrics: {
        heartRate: "112 BPM",
        speed: "19 KM/H",
        acceleration: "1.1 M/S²",
        temperature: "36.9°C",
      },
    },
    {
      id: 7,
      x: 400,
      y: 150,
      metrics: {
        heartRate: "125 BPM",
        speed: "21 KM/H",
        acceleration: "1.2 M/S²",
        temperature: "37.2°C",
      },
    },
    {
      id: 8,
      x: 450,
      y: 200,
      metrics: {
        heartRate: "118 BPM",
        speed: "20 KM/H",
        acceleration: "1.1 M/S²",
        temperature: "36.6°C",
      },
    },
    {
      id: 9,
      x: 500,
      y: 250,
      metrics: {
        heartRate: "135 BPM",
        speed: "24 KM/H",
        acceleration: "1.3 M/S²",
        temperature: "37.3°C",
      },
    },
    {
      id: 10,
      x: 350,
      y: 300,
      metrics: {
        heartRate: "122 BPM",
        speed: "22 KM/H",
        acceleration: "1.2 M/S²",
        temperature: "37°C",
      },
    },
    {
      id: 11,
      x: 250,
      y: 350,
      metrics: {
        heartRate: "120 BPM",
        speed: "21 KM/H",
        acceleration: "1.2 M/S²",
        temperature: "37.1°C",
      },
    },
  ]);

  const [live, setLive] = useState(false);

  const [tooltip, setTooltip] = useState({ visible: false, x: 0, y: 0, player: null });

  // Utility to constrain player positions within boundaries
  const constrainPosition = (x, y) => {
    return {
      x: Math.max(GOAL_AREA_PADDING, Math.min(FIELD_WIDTH - GOAL_AREA_PADDING, x)),
      y: Math.max(0, Math.min(FIELD_HEIGHT, y)),
    };
  };

  const handleMouseEnter = (event, player) => {
    const rect = event.target.getBoundingClientRect();
    setTooltip({
      visible: true,
      x: rect.x + rect.width / 2,
      y: rect.y - 10,
      player,
    });
  };

  const handleMouseLeave = () => {
    setTooltip({ visible: false, x: 0, y: 0, player: null });
  };

  // Mock GPS updates
  useEffect(() => {
    let interval;
    if (live) {
      interval = setInterval(() => {
        setPlayers((prevPlayers) =>
          prevPlayers.map((player) => {
            const newX = player.x + (Math.random() * 20 - 10); // Random horizontal movement
            const newY = player.y + (Math.random() * 20 - 10); // Random vertical movement
            return { ...player, ...constrainPosition(newX, newY) };
          })
        );
      }, 1000); // Updates every second
    }
    return () => clearInterval(interval); // Cleanup
  }, [live]);

  const toggleLive = () => {
    setLive((prevState) => !prevState);
  };

  return (
    <div className="soccer-field-container">
      <button className="button" onClick={toggleLive}>
        {live ? "Stop Live Stream" : "Start Live Stream"}
      </button>
      <div className="soccer-field">
        {players.map((player) => (
          <div
            key={player.id}
            className="player-marker"
            style={{
              left: `${player.x}px`,
              top: `${player.y}px`,
            }}
            onMouseEnter={(event) => handleMouseEnter(event, player)}
            onMouseLeave={handleMouseLeave}
          >
            {player.id}
          </div>
        ))}
        {tooltip.visible && tooltip.player && (
          <div
            class
            className="tooltip"
            style={{
              left: `${tooltip.x}px`,
              top: `${tooltip.y}px`,
            }}
          >
            <p><strong>Player {tooltip.player.id}</strong></p>
            <p>Heart Rate: {tooltip.player.metrics.heartRate}</p>
            <p>Speed: {tooltip.player.metrics.speed}</p>
            <p>Acceleration: {tooltip.player.metrics.acceleration}</p>
            <p>Temperature: {tooltip.player.metrics.temperature}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SoccerField;
