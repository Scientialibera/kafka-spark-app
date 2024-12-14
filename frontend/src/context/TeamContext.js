import React, { createContext, useContext, useState } from "react";

// Create the context
const TeamContext = createContext();

// Provider component
export const TeamProvider = ({ children }) => {
  const [team, setTeam] = useState({
    name: "Lakeside FC",
    manager: "Thomas Grant",
    physiotherapist: "Sarah Reid",
    totalPlayers: 10,
    seasonRecord: "W-L-D: 12-5-3",
    leagueRank: "#2 in League",
  });

  return (
    <TeamContext.Provider value={{ team, setTeam }}>
      {children}
    </TeamContext.Provider>
  );
};

// Custom hook to use the TeamContext
export const useTeam = () => useContext(TeamContext);
