/**
 * Authentication service for managing user authentication state.
 */
import axios from 'axios';
import { UserProfile } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  token: string;
  user: UserProfile;
}

export class AuthService {
  private token: string | null = null;
  private user: UserProfile | null = null;

  constructor() {
    // Initialize from localStorage
    this.token = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        this.user = JSON.parse(storedUser);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        localStorage.removeItem('user');
      }
    }
  }

  async login(credentials: LoginCredentials): Promise<UserProfile> {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login/`, credentials);
      const { token, user } = response.data;

      this.token = token;
      this.user = user;

      // Store in localStorage
      localStorage.setItem('authToken', token);
      localStorage.setItem('user', JSON.stringify(user));

      return user;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Login failed');
    }
  }

  async logout(): Promise<void> {
    try {
      if (this.token) {
        await axios.post(`${API_BASE_URL}/auth/logout/`, {}, {
          headers: { Authorization: `Bearer ${this.token}` }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local state and storage regardless of API call success
      this.token = null;
      this.user = null;
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
    }
  }

  async getCurrentUser(): Promise<UserProfile | null> {
    if (!this.token) {
      return null;
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/auth/user/`, {
        headers: { Authorization: `Bearer ${this.token}` }
      });
      
      this.user = response.data;
      localStorage.setItem('user', JSON.stringify(this.user));
      return this.user;
    } catch (error: any) {
      if (error.response?.status === 401) {
        // Token is invalid, clear auth state
        this.logout();
      }
      return null;
    }
  }

  getToken(): string | null {
    return this.token;
  }

  getUser(): UserProfile | null {
    return this.user;
  }

  isAuthenticated(): boolean {
    return !!this.token && !!this.user;
  }

  isAdmin(): boolean {
    return this.user?.is_staff || this.user?.is_superuser || false;
  }
}

// Export singleton instance
export const authService = new AuthService();