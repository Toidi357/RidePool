import React, { createContext, useState, useContext } from 'react';

// Create the context object with a default value
const AuthContext = createContext({
  isLoggedIn: false,
  setIsLoggedIn: () => {}  // This will allow updating the context
});

// Export the useAuth custom hook for easy access to the context
export const useAuth = () => useContext(AuthContext);

// Provider component that holds the state and provides it to children
export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  return (
    <AuthContext.Provider value={{ isLoggedIn, setIsLoggedIn }}>
      {children}
    </AuthContext.Provider>
  );
};