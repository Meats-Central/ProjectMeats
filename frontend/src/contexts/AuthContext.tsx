/**
 * Authentication context for managing user authentication state across the app.
 */
import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { UserProfile } from "../types";
import {
  authService,
  LoginCredentials,
  SignUpCredentials,
} from "../services/authService";

interface AuthContextType {
  user: UserProfile | null;
  loading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  signUp: (credentials: SignUpCredentials) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
  isAdmin: boolean;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
      } catch (error) {
        console.error("Failed to initialize auth:", error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    setLoading(true);
    try {
      const loggedInUser = await authService.login(credentials);
      setUser(loggedInUser);
    } catch (error) {
      setUser(null);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const signUp = async (credentials: SignUpCredentials) => {
    setLoading(true);
    try {
      const newUser = await authService.signUp(credentials);
      setUser(newUser);
    } catch (error) {
      setUser(null);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await authService.logout();
      setUser(null);
    } catch (error) {
      console.error("Logout error:", error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const refreshUser = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error("Failed to refresh user:", error);
      setUser(null);
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    signUp,
    logout,
    isAuthenticated: !!user,
    isAdmin: authService.isAdmin(),
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
