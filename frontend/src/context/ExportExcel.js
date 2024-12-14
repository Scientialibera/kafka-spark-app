import * as XLSX from "xlsx";

export const exportDashboardData = async (setButtonState) => {
  try {
    setButtonState("Exporting...");

    // Fetch data from all required endpoints
    const [
      teamMetricsRes,
      fatigueDistRes,
      gameStatsRes,
      playerOverviewRes
    ] = await Promise.all([
      fetch("http://127.0.0.1:8000/team-metrics"), // Team metrics and statistics
      fetch("http://127.0.0.1:8000/fatigue-distribution"), // Fatigue level distribution
      fetch("http://127.0.0.1:8000/game-statistics"), // Metrics for wins, losses, draws
      fetch("http://127.0.0.1:8000/team-metrics"), // Player overview (reuse team-metrics)
    ]);

    const teamMetricsData = await teamMetricsRes.json();
    const fatigueDistData = await fatigueDistRes.json();
    const gameStatsData = await gameStatsRes.json();
    const playerOverviewData = await playerOverviewRes.json();

    // Prepare workbook
    const workbook = XLSX.utils.book_new();

    // **Team Metrics Data**
    const teamMetricsSheetData = [
      ["Metric", "Value"],
      ["Average Team Distance (km)", (teamMetricsData["Average Team Distance"] / 1000).toFixed(2)],
      ["Average Recovery Rate (bpm/s)", teamMetricsData["Average Team Recovery Rate"]],
    ];

    // Add Total Distance, Average Speed, and Max Speed from "Team Total Distance Per Game"
    const gameMetrics = Object.keys(teamMetricsData["Team Total Distance Per Game"]).map((game, index) => [
      `Game ${index + 1}`,
      (teamMetricsData["Team Total Distance Per Game"][game] / 1000).toFixed(2), // Distance in km
      teamMetricsData["Team Average Speeds per game"][game]?.toFixed(2) || "N/A", // Avg speed
      teamMetricsData["Team Max Speeds per Game"][game]?.toFixed(2) || "N/A", // Max speed
    ]);
    teamMetricsSheetData.push(
      ["Game", "Total Distance (km)", "Avg Speed (km/h)", "Max Speed (km/h)"],
      ...gameMetrics
    );
    const teamMetricsSheet = XLSX.utils.aoa_to_sheet(teamMetricsSheetData);
    XLSX.utils.book_append_sheet(workbook, teamMetricsSheet, "Team Metrics");

    // **Fatigue Distribution Data**
    const totalGames = 15; // Total number of games
    const fatigueDistDataMatches = fatigueDistData["Total Fatigue Levels"].match(
      /Low: (\d+), Medium: (\d+), High: (\d+)/
    );

    const lowFatigueCount = fatigueDistDataMatches ? parseInt(fatigueDistDataMatches[1], 10) : 0;
    const mediumFatigueCount = fatigueDistDataMatches ? parseInt(fatigueDistDataMatches[2], 10) : 0;
    const highFatigueCount = fatigueDistDataMatches ? parseInt(fatigueDistDataMatches[3], 10) : 0;

    const fatigueSheetData = [
      ["Fatigue Level", "Total Count (15 Games)", "Average Number of Players"],
      ["Low", lowFatigueCount, (lowFatigueCount / totalGames).toFixed(1)],
      ["Medium", mediumFatigueCount, (mediumFatigueCount / totalGames).toFixed(1)],
      ["High", highFatigueCount, (highFatigueCount / totalGames).toFixed(1)],
    ];
    const fatigueDistSheet = XLSX.utils.aoa_to_sheet(fatigueSheetData);
    XLSX.utils.book_append_sheet(workbook, fatigueDistSheet, "Fatigue Distribution");

    // **Game Statistics Data (Wins, Losses, Draws)**
    const gameStatsSheetData = [
      ["Metric", "Value"],
      ["Wins", gameStatsData.Wins],
      ["Losses", gameStatsData.Losses],
      ["Draws", gameStatsData.Draws],
    ];
    const gameStatsSheet = XLSX.utils.aoa_to_sheet(gameStatsSheetData);
    XLSX.utils.book_append_sheet(workbook, gameStatsSheet, "Game Statistics");

    // **Player Overview Data**
    const playerOverviewSheetData = [
      ["Game", "Heart Rate Recovery (bpm/s)", "Total Injuries", "Best Player Recommendation", "Worst Player Recommendation"],
    ];

    const totalInjuries = playerOverviewData["Team Total Injuries"];
    const heartRateRecovery = playerOverviewData["Player Average Heart Rate Recovery"];
    const recommendations = playerOverviewData["Best and Worst Recommendations Per Game"];

    const gamesData = Object.keys(totalInjuries).map((key) => {
      const gameNumber = parseInt(key.split("_")[1], 10); // Extract game number
      const avgHeartRateRecovery = Object.values(heartRateRecovery).reduce(
        (acc, playerData) => acc + (playerData[key] || 0),
        0
      ) / 10; // Average across 10 players

      return [
        `Game ${gameNumber}`,
        avgHeartRateRecovery.toFixed(2), // Avg Heart Rate Recovery
        totalInjuries[key], // Total Injuries
        recommendations[key]?.["Best Recommendation"] || "N/A", // Best Recommendation
        recommendations[key]?.["Worst Recommendation"] || "N/A", // Worst Recommendation
      ];
    });

    playerOverviewSheetData.push(...gamesData);
    const playerOverviewSheet = XLSX.utils.aoa_to_sheet(playerOverviewSheetData);
    XLSX.utils.book_append_sheet(workbook, playerOverviewSheet, "Player Overview");

    // **Export the Workbook**
    const now = new Date();
    const formattedDate = now.toISOString().split("T")[0]; // YYYY-MM-DD
    const formattedTime = now.toTimeString().split(" ")[0].replace(/:/g, "-"); // HH-MM-SS
    const fileName = `Dashboard_Data_${formattedDate}_${formattedTime}.xlsx`;
    XLSX.writeFile(workbook, fileName);

    setButtonState("Export Dashboard Data"); // Reset button state
  } catch (err) {
    console.error("Error exporting dashboard data:", err);
    setButtonState("Error Exporting");
    setTimeout(() => setButtonState("Export Dashboard Data"), 3000); // Reset button text after 3 seconds
  }
};
