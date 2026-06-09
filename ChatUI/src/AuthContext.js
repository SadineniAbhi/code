// AUTH DISABLED - All authentication logic commented out
// import React, { createContext, useContext, useState, useEffect } from 'react';

// const AuthContext = createContext();

// export const useAuth = () => {
//   const context = useContext(AuthContext);
//   if (!context) {
//     throw new Error('useAuth must be used within an AuthProvider');
//   }
//   return context;
// };

// export const AuthProvider = ({ children }) => {
//   const [isAuthenticated, setIsAuthenticated] = useState(false);
//   const [token, setToken] = useState(null);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     // Check for stored token on app load
//     const storedToken = localStorage.getItem('authToken');
//     if (storedToken) {
//       setToken(storedToken);
//       setIsAuthenticated(true);
//     }
//     setLoading(false);
//   }, []);

//   const login = (authToken) => {
//     setToken(authToken);
//     setIsAuthenticated(true);
//     localStorage.setItem('authToken', authToken);
//   };

//   const logout = () => {
//     setToken(null);
//     setIsAuthenticated(false);
//     localStorage.removeItem('authToken');
//   };

//   const value = {
//     isAuthenticated,
//     token,
//     loading,
//     login,
//     logout
//   };

//   return (
//     <AuthContext.Provider value={value}>
//       {children}
//     </AuthContext.Provider>
//   );
// };
