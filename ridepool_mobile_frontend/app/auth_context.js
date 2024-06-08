// context/AuthContext.js
import React, { createContext, useState, useEffect } from 'react';
import { saveToken, fetchToken } from './components/token_funcs';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);

  useEffect(() => {
    const loadToken = async () => {
      const storedToken = await fetchToken();
      if (storedToken) {
        setToken(storedToken);
      }
    };
    loadToken();
  }, []);

  const login = async (newToken) => {
    await saveToken(newToken);
    setToken(newToken);
  };

  const logout = async () => {
    await saveToken(null); // Clear the token
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
