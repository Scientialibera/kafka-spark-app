import React, { useEffect, useState } from "react";
import MetricsCards from "./MetricsCards";
import FatigueLevelDistribution from "./FatigueLevelDistribution";
import TeamStatistics from "./TeamStatistics";
import PlayerOverview from "./PlayerOverview";
import "../styles/Dashboard.css";

const Dashboard = () => {
  const [teamStatistics, setTeamStatistics] = useState(null);
  const [gameStatistics, setGameStatistics] = useState(null);
  const [teamMetrics, setTeamMetrics] = useState(null);
  const [fatigueData, setFatigueData] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        const [
          teamStatResponse,
          gameStatResponse,
          teamMetricsResponse,
          fatigueResponse,
          recommendationsResponse,
        ] = await Promise.all([
          fetch("/api/team-statistics"),
          fetch("/api/game-statistics"),
          fetch("/api/team-metrics"),
          fetch("/api/fatigue-distribution"),
          fetch("/api/recommendations"),
        ]);

        const teamStatData = await teamStatResponse.json();
        const gameStatData = await gameStatResponse.json();
        const teamMetricsData = await teamMetricsResponse.json();
        const fatigueData = await fatigueResponse.json();
        const recommendationsData = await recommendationsResponse.json();

        setTeamStatistics(teamStatData);
        setGameStatistics(gameStatData);
        setTeamMetrics(teamMetricsData);
        setFatigueData(fatigueData);
        setRecommendations(recommendationsData);
      } catch (err) {
        setError("Failed to fetch dashboard data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <button className="button">Start Live Stream</button>
      </div>

      <div className="dashboard-layout">
        <div className="container team-statistics">
          <TeamStatistics data={teamStatistics} />
        </div>

        <div className="container metrics-section">
          <MetricsCards
            wins={gameStatistics.Wins}
            losses={gameStatistics.Losses}
            draws={gameStatistics.Draws}
            totalDistance={teamMetrics["Total Distance Per Game"]["run_001"]}
            avgRecovery={teamMetrics["Average Team Recovery Rate"]}
          />
        </div>

        <div className="container fatigue-level">
          <FatigueLevelDistribution data={fatigueData} />
        </div>

        <div className="container recommendations">
          <h3>Team Recommendations</h3>
          <ul>
            {recommendations["Team Recommendations"].map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
