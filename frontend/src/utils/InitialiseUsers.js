// InitialiseUsers.js
const hardcodedUsers = [
    {
      firstName: "Thomas",
      lastName: "Grant",
      role: "Team Manager",
      email: "thomas-grant@gmail.com",
      password: "thomas-manager-1234!",
    },
    {
      firstName: "Sarah",
      lastName: "Reid",
      role: "Physiotherapist",
      email: "sarah-reid@gmail.com",
      password: "sarah-physiotherapist-1234!",
    },
    {
      firstName: "Liam",
      lastName: "Carter",
      role: "Player",
      email: "liam-carter@gmail.com",
      password: "liam-player-1234!",
    },
  ];
  
  export const initialiseUsers = () => {
    const existingUsers = JSON.parse(localStorage.getItem("users")) || [];
    const newUsers = hardcodedUsers.filter(
      (hardcodedUser) => !existingUsers.some((user) => user.email === hardcodedUser.email)
    );
  
    if (newUsers.length > 0) {
      const updatedUsers = [...existingUsers, ...newUsers];
      localStorage.setItem("users", JSON.stringify(updatedUsers));
    }
  };
  