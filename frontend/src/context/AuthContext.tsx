import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { api, setAuthToken, removeAuthToken, getAuthToken } from '../services/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginDemo: () => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const handleUnauthorized = () => {
      setUser(null);
    };
    window.addEventListener('auth:unauthorized', handleUnauthorized);

    const checkAuth = async () => {
      const token = getAuthToken();
      if (token) {
        try {
          const profile = await api.getMe();
          setUser(profile);
        } catch {
          removeAuthToken();
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    checkAuth();
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized);
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await api.login({ email, password });
      setAuthToken(res.access_token);
      const profile = await api.getMe();
      setUser(profile);
    } finally {
      setIsLoading(false);
    }
  };

  const loginDemo = async () => {
    setIsLoading(true);
    try {
      // Alex Mercer (seeded test customer)
      await login('alex.demo@supportflow.ai', 'password123');
    } catch {
      // If demo user password differed, register or fallback
      try {
        await login('alex.demo@supportflow.ai', 'demo123');
      } catch {
        const res = await api.register({
          name: 'Alex Mercer',
          email: 'alex.demo@supportflow.ai',
          password: 'password123',
        });
        setAuthToken(res.access_token);
        setUser(await api.getMe());
      }
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await api.register({ name, email, password });
      setAuthToken(res.access_token);
      setUser(await api.getMe());
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await api.logout();
    } finally {
      removeAuthToken();
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        loginDemo,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
