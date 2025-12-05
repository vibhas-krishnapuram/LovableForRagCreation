import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI } from '../services/api';
import type { LoginRequest, CreateUserRequest } from '../types';

interface AuthContextType {
  token: string | null;
  isAuthenticated: boolean;
  login: (data: LoginRequest) => Promise<void>;
  signup: (data: CreateUserRequest) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }, [token]);

  const login = async (data: LoginRequest) => {
    setLoading(true);
    try {
      const response = await authAPI.login(data);
      setToken(response.access_token);
    } catch (error) {
      throw error; // Re-throw to let the component handle it
    } finally {
      setLoading(false);
    }
  };

  const signup = async (data: CreateUserRequest) => {
    setLoading(true);
    try {
      await authAPI.createUser(data);
      // Auto-login after signup
      await login(data);
    } catch (error) {
      throw error; // Re-throw to let the component handle it
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        isAuthenticated: !!token,
        login,
        signup,
        logout,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

