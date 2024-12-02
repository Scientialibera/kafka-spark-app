import React from "react";
import "../styles/MetricsCards.css";

// Grouped Metrics
const metricsGrouped = [
  {
    group: [
      { title: "Wins", value: "12", percentage: "0.15%", positive: true, directionPositive: true },
      { title: "Losses", value: "5", percentage: "0.35%", positive: true, directionPositive: false },
      { title: "Draws", value: "3", percentage: "0.27%", positive: false, directionPositive: true },
    ],
    background: "#fdf1f5",
  },
];

// Single Metrics
const metricsSingle = [
  {
    title: "Total Distance Covered / Game",
    value: "95 km",
    percentage: "0.65%",
    positive: false,
    directionPositive: false,
    background: "#f2f2fd",
    titleClass: "distance-title",
  },
  {
    title: "Average Team Recovery Time",
    value: "2.5 bpm/s",
    percentage: "2.29%",
    positive: false,
    directionPositive: true,
    background: "#effcfa",
    titleClass: "recovery-title",
  },
];

// Utility function to render arrow and percentage
const renderArrowAndPercentage = (positive, directionPositive, percentage) => {
  const arrowDirection = positive ? "▲" : "▼"; // Direction based on `positive`
  const colorClass = directionPositive ? "positive" : "negative"; // Color based on `directionPositive`
  return (
    <span className={`metrics-arrow-percentage ${colorClass}`}>
      <span className="arrow">{arrowDirection}</span>
      {percentage}
    </span>
  );
};

const MetricsCards = () => {
  return (
    <div className="metrics-container">
      {/* Grouped Metrics Card */}
      {metricsGrouped.map((group, index) => (
        <div
          key={`group-${index}`}
          className="metrics-card grouped-card"
          style={{ background: group.background }}
        >
          <div className="group-content">
            {group.group.map((metric, idx) => (
              <div key={`metric-${idx}`} className="group-item">
                <h4>{metric.title}</h4>
                <div className="metrics-value">{metric.value}</div>
                <div>
                  {renderArrowAndPercentage(metric.positive, metric.directionPositive, metric.percentage)}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Single Metrics Cards */}
      {metricsSingle.map((metric, index) => (
        <div
          key={`single-${index}`}
          className="metrics-card"
          style={{ background: metric.background }}
        >
          <h4 className={metric.titleClass}>{metric.title}</h4>
          <div className="metrics-value">{metric.value}</div>
          <div>
            {renderArrowAndPercentage(metric.positive, metric.directionPositive, metric.percentage)}
          </div>
        </div>
      ))}
    </div>
  );
};

export default MetricsCards;
