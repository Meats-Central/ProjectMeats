import React, { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from '../contexts/AuthContext';

const Login: React.FC = () => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Check for success message from signup
  const successMessage = location.state?.message;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!credentials.username.trim() || !credentials.password.trim()) {
      setError('Please enter both username and password');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await login(credentials);
      navigate('/');
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Login failed. Please check your credentials.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCredentials((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (error) setError(null);
  };

  return (
    <LoginContainer>
      <LoginCard>
        <Header>
          <LogoSection>
            <Logo>🥩</Logo>
            <LogoText>Meats Central</LogoText>
          </LogoSection>
          <Title>Sign In</Title>
          <Subtitle>Access your business management dashboard</Subtitle>
        </Header>

        {successMessage && (
          <SuccessMessage>
            <SuccessIcon>✅</SuccessIcon>
            {successMessage}
          </SuccessMessage>
        )}

        {error && (
          <ErrorMessage>
            <ErrorIcon>⚠️</ErrorIcon>
            {error}
          </ErrorMessage>
        )}

        <LoginForm onSubmit={handleSubmit}>
          <FormGroup>
            <Label>Username</Label>
            <Input
              type="text"
              name="username"
              value={credentials.username}
              onChange={handleInputChange}
              placeholder="Enter your username"
              disabled={loading}
              required
            />
            <HintText>Note: Username is case-sensitive</HintText>
          </FormGroup>

          <FormGroup>
            <Label>Password</Label>
            <Input
              type="password"
              name="password"
              value={credentials.password}
              onChange={handleInputChange}
              placeholder="Enter your password"
              disabled={loading}
              required
            />
          </FormGroup>

          <LoginButton type="submit" disabled={loading}>
            {loading ? (
              <>
                <LoadingSpinner />
                Signing In...
              </>
            ) : (
              'Sign In'
            )}
          </LoginButton>
        </LoginForm>

        <Footer>
          <FooterText>
            Don't have an account? <StyledLink to="/signup">Sign up here</StyledLink>
          </FooterText>
          <FooterSubText>Need help? Contact your administrator</FooterSubText>
        </Footer>
      </LoginCard>
    </LoginContainer>
  );
};

const LoginContainer = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
`;

const LoginCard = styled.div`
  background: rgb(var(--color-surface));
  color: rgb(var(--color-surface-foreground));
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 32px;
`;

const LogoSection = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
`;

const Logo = styled.div`
  font-size: 32px;
`;

const LogoText = styled.h1`
  font-size: 24px;
  font-weight: 700;
  color: rgb(var(--color-text-primary));
  margin: 0;
`;

const Title = styled.h2`
  font-size: 28px;
  font-weight: 700;
  color: rgb(var(--color-text-primary));
  margin: 0 0 8px 0;
`;

const Subtitle = styled.p`
  color: rgb(var(--color-text-secondary));
  margin: 0;
  font-size: 16px;
`;

const ErrorMessage = styled.div`
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
`;

const ErrorIcon = styled.span`
  font-size: 16px;
`;

const LoginForm = styled.form`
  margin-bottom: 24px;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
  font-size: 14px;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
  }

  &:disabled {
    background-color: rgb(var(--color-surface-hover));
    cursor: not-allowed;
  }
`;

const LoginButton = styled.button`
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
  }
`;

const LoadingSpinner = styled.div`
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
`;

const Footer = styled.div`
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
`;

const FooterText = styled.p`
  color: rgb(var(--color-text-secondary));
  font-size: 14px;
  margin: 0 0 8px 0;
`;

const FooterSubText = styled.p`
  color: rgb(var(--color-text-secondary));
  font-size: 12px;
  margin: 0;
`;

const StyledLink = styled(Link)`
  color: #667eea;
  text-decoration: none;
  font-weight: 600;

  &:hover {
    text-decoration: underline;
  }
`;

const SuccessMessage = styled.div`
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #16a34a;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
`;

const SuccessIcon = styled.span`
  font-size: 16px;
`;

const HintText = styled.p`
  color: rgb(var(--color-text-secondary));
  font-size: 12px;
  margin: 4px 0 0 0;
  font-style: italic;
`;

export default Login;
