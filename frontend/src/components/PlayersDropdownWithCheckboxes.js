import React, { useState } from "react";

const PlayersDropdownWithCheckboxes = ({ players, selectedPlayers, onSelectionChange }) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  const handleCheckboxChange = (playerName) => {
    const updatedSelection = selectedPlayers.includes(playerName)
      ? selectedPlayers.filter((name) => name !== playerName) // Remove if already selected
      : [...selectedPlayers, playerName]; // Add if not selected

    onSelectionChange(updatedSelection);
  };

  return (
    <div className="dropdown-container">
      <button
        type="button"
        className="dropdown-button"
        onClick={toggleDropdown}
        style={{
          width: "100%",
          padding: "10px",
          borderRadius: "5px",
          border: "1px solid #ccc",
          backgroundColor: "#f9f9f9",
          textAlign: "left",
        }}
      >
        {selectedPlayers.length > 0
          ? `${selectedPlayers.length} Player(s) Selected`
          : "Select Players"}
        <span style={{ float: "right" }}>{isDropdownOpen ? "▲" : "▼"}</span>
      </button>

      {isDropdownOpen && (
        <div
          className="dropdown-list"
          style={{
            border: "1px solid #ccc",
            borderRadius: "5px",
            maxHeight: "200px",
            overflowY: "auto",
            padding: "10px",
            backgroundColor: "#ffffff",
            position: "absolute",
            zIndex: "1000",
            width: "92.7%",
          }}
        >
          {players.map((player) => (
            <div key={player.id} className="dropdown-item" style={{ display: "flex", alignItems: "center" }}>
              <input
                type="checkbox"
                id={`player-${player.id}`}
                checked={selectedPlayers.includes(player.name)}
                onChange={() => handleCheckboxChange(player.name)}
                style={{ marginRight: "10px" }}
              />
              <label htmlFor={`player-${player.id}`} style={{ cursor: "pointer" }}>
                {player.name}
              </label>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PlayersDropdownWithCheckboxes;
