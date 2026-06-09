import React from "react";
// Commented out auth imports - auth disabled
// import { AuthProvider, useAuth } from "./AuthContext";
// import Login from "./Login";
import Chat from "./Chat";
import "./App.css";

// Commented out auth-dependent AppContent - auth disabled
// function AppContent() {
//   const { isAuthenticated, loading } = useAuth();

//   if (loading) {
//     return (
//       <div className="loading-container">
//         <div className="loading-spinner">Loading...</div>
//       </div>
//     );
//   }

//   return isAuthenticated ? <Chat /> : <Login />;
// }

function App() {
  // Auth disabled - directly render Chat component
  return <Chat />;
  
  // Original auth-wrapped version (commented out)
  // return (
  //   <AuthProvider>
  //     <AppContent />
  //   </AuthProvider>
  // );
}

export default App;
