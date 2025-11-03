/**
 * Authentication service for managing user authentication state.
 */
import axios from 'axios';
import { UserProfile } from '../types';

const API_BASE_URL = config.API_BASE_URL;

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface SignUpCredentials {
  username: string;
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  company?: string;
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
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.error || 'Login failed');
      }
      throw new Error('Login failed');
    }
  }

  async signUp(credentials: SignUpCredentials): Promise<UserProfile> {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/signup/`, {
        username: credentials.username,
        email: credentials.email,
        password: credentials.password,
        firstName: credentials.firstName,
        lastName: credentials.lastName,
      });

      const { token, user } = response.data;

      this.token = token;
      this.user = user;

      // Store in localStorage
      localStorage.setItem('authToken', token);
      localStorage.setItem('user', JSON.stringify(user));

      return user;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.error || 'Sign up failed');
      }
      throw new Error('Sign up failed');
    }
  }

  async logout(): Promise<void> {
    try {
      if (this.token) {
        await axios.post(
          `${API_BASE_URL}/auth/logout/`,
          {},
          {
            headers: { Authorization: `Token ${this.token}` },
          }
        );
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

    // If we have a stored user, return it
    if (this.user) {
      return this.user;
    }

    // Try to get user from localStorage if we have a token but no user in memory
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        this.user = JSON.parse(storedUser);
        return this.user;
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        localStorage.removeItem('user');
      }
    }

    // If we have a token but no user data, something went wrong - clear auth state
    console.warn('Token exists but no user data found - clearing auth state');
    await this.logout();
    return null;
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
