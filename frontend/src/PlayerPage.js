import React, { useEffect, useState } from "react";
import "../styles/PlayerPage.css";

const PlayerPage = ({ playerId }) => {
  const [playerData, setPlayerData] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [playerResponse, recommendationsResponse] = await Promise.all([
          fetch(`/api/player-overview/${playerId}`),
          fetch("/api/recommendations"),
        ]);

        const playerData = await playerResponse.json();
        const recommendationsData = await recommendationsResponse.json();

        setPlayerData(playerData);
        setRecommendations(recommendationsData["Player Recommendations"][playerId]);
      } catch (err) {
        setError("Failed to fetch player data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [playerId]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="player-page">
      <h1>Player {playerId}</h1>
      <div className="metrics">
        <p>Fatigue Level: {playerData.FatigueLevel}</p>
        <p>Injuries: {playerData.Injuries}</p>
        <p>Heart Rate Recovery Rate: {playerData["Heart Rate Recovery Rate"] || "N/A"}</p>
      </div>
      <div className="recommendations">
        <h3>Recommendations</h3>
        <ul>
          {recommendations.map((rec, index) => (
            <li key={index}>{rec}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default PlayerPage;
