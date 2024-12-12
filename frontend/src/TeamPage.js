import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import "../styles/TeamPage.css";

const TeamPage = () => {
  const [teamMetrics, setTeamMetrics] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [teamMetricsResponse, recommendationsResponse] = await Promise.all([
          fetch("/api/team-metrics"),
          fetch("/api/recommendations"),
        ]);

        const teamMetricsData = await teamMetricsResponse.json();
        const recommendationsData = await recommendationsResponse.json();

        setTeamMetrics(teamMetricsData);
        setRecommendations(recommendationsData["Team Recommendations"]);
      } catch (err) {
        setError("Failed to fetch team data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  const data = {
    labels: Object.keys(teamMetrics["Total Distance Per Game"]),
    datasets: [
      {
        label: "Total Distance",
        data: Object.values(teamMetrics["Total Distance Per Game"]),
        borderColor: "#636AE8",
        backgroundColor: "rgba(99, 106, 232, 0.2)",
        tension: 0.4,
      },
    ],
  };

  return (
    <div className="team-page">
      <h1>Team Metrics</h1>
      <div className="chart-container">
        <Line data={data} options={{ responsive: true, maintainAspectRatio: false }} />
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

export default TeamPage;
