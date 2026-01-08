import React, { useState } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from '../contexts/AuthContext';

interface SignUpFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
  company?: string;
}

const SignUp: React.FC = () => {
  const [formData, setFormData] = useState<SignUpFormData>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    company: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const { signUp } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const validateForm = (): string | null => {
    if (!formData.username.trim()) return 'Username is required';
    if (!formData.email.trim()) return 'Email is required';
    if (!formData.password) return 'Password is required';
    if (!formData.firstName.trim()) return 'First name is required';
    if (!formData.lastName.trim()) return 'Last name is required';

    if (formData.password !== formData.confirmPassword) {
      return 'Passwords do not match';
    }

    if (formData.password.length < 6) {
      return 'Password must be at least 6 characters long';
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      return 'Please enter a valid email address';
    }

    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Use the actual signup service
      await signUp({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        firstName: formData.firstName,
        lastName: formData.lastName,
        company: formData.company,
        token: token || undefined,
      });

      // Show success and redirect to dashboard (user is already logged in)
      setSuccess(true);

      setTimeout(() => {
        navigate('/');
      }, 2000);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Sign up failed. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (error) setError(null);
  };

  if (success) {
    return (
      <SignUpContainer>
        <SignUpCard>
          <SuccessContent>
            <SuccessIcon>✅</SuccessIcon>
            <SuccessTitle>Account Created Successfully!</SuccessTitle>
            <SuccessMessage>
              Welcome to Meats Central! Your account has been created and you're now logged in.
            </SuccessMessage>
            <SuccessSubMessage>Redirecting you to the dashboard...</SuccessSubMessage>
          </SuccessContent>
        </SignUpCard>
      </SignUpContainer>
    );
  }

  return (
    <SignUpContainer>
      <SignUpCard>
        <Header>
          <LogoSection>
            <Logo>🥩</Logo>
            <LogoText>Meats Central</LogoText>
          </LogoSection>
          <Title>Create Account</Title>
          <Subtitle>Join Meats Central to manage your business operations</Subtitle>
        </Header>

        {error && (
          <ErrorMessage>
            <ErrorIcon>⚠️</ErrorIcon>
            {error}
          </ErrorMessage>
        )}

        <SignUpForm onSubmit={handleSubmit}>
          <FormRow>
            <FormGroup>
              <Label>First Name *</Label>
              <Input
                type="text"
                name="firstName"
                value={formData.firstName}
                onChange={handleInputChange}
                placeholder="Enter your first name"
                disabled={loading}
                required
              />
            </FormGroup>
            <FormGroup>
              <Label>Last Name *</Label>
              <Input
                type="text"
                name="lastName"
                value={formData.lastName}
                onChange={handleInputChange}
                placeholder="Enter your last name"
                disabled={loading}
                required
              />
            </FormGroup>
          </FormRow>

          <FormGroup>
            <Label>Username *</Label>
            <Input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              placeholder="Choose a username"
              disabled={loading}
              required
            />
          </FormGroup>

          <FormGroup>
            <Label>Email Address *</Label>
            <Input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="Enter your email address"
              disabled={loading}
              required
            />
          </FormGroup>

          <FormGroup>
            <Label>Company (Optional)</Label>
            <Input
              type="text"
              name="company"
              value={formData.company}
              onChange={handleInputChange}
              placeholder="Your company name"
              disabled={loading}
            />
          </FormGroup>

          <FormRow>
            <FormGroup>
              <Label>Password *</Label>
              <Input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Create a password"
                disabled={loading}
                required
              />
            </FormGroup>
            <FormGroup>
              <Label>Confirm Password *</Label>
              <Input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                placeholder="Confirm your password"
                disabled={loading}
                required
              />
            </FormGroup>
          </FormRow>

          <SignUpButton type="submit" disabled={loading}>
            {loading ? (
              <>
                <LoadingSpinner />
                Creating Account...
              </>
            ) : (
              'Create Account'
            )}
          </SignUpButton>
        </SignUpForm>

        <Footer>
          <FooterText>
            Already have an account? <StyledLink to="/login">Sign in here</StyledLink>
          </FooterText>
          <FooterNote>
            Note: For now, accounts are activated immediately. In the future, admin approval may be
            required.
          </FooterNote>
        </Footer>
      </SignUpCard>
    </SignUpContainer>
  );
};

const SignUpContainer = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
`;

const SignUpCard = styled.div`
  background: rgb(var(--color-surface));
  color: rgb(var(--color-surface-foreground));
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  max-height: 90vh;
  overflow-y: auto;
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
  color: #2c3e50;
  margin: 0;
`;

const Title = styled.h2`
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
`;

const Subtitle = styled.p`
  color: #6c757d;
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

const SignUpForm = styled.form`
  margin-bottom: 24px;
`;

const FormRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;

  @media (max-width: 480px) {
    grid-template-columns: 1fr;
  }
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: #2c3e50;
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

const SignUpButton = styled.button`
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
  color: #6c757d;
  font-size: 14px;
  margin: 0 0 12px 0;
`;

const FooterNote = styled.p`
  color: #8a8a8a;
  font-size: 12px;
  margin: 0;
  font-style: italic;
`;

const StyledLink = styled(Link)`
  color: #667eea;
  text-decoration: none;
  font-weight: 600;

  &:hover {
    text-decoration: underline;
  }
`;

const SuccessContent = styled.div`
  text-align: center;
  padding: 40px 20px;
`;

const SuccessIcon = styled.div`
  font-size: 64px;
  margin-bottom: 24px;
`;

const SuccessTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 16px 0;
`;

const SuccessMessage = styled.p`
  color: #6c757d;
  font-size: 16px;
  margin: 0 0 12px 0;
  line-height: 1.5;
`;

const SuccessSubMessage = styled.p`
  color: #8a8a8a;
  font-size: 14px;
  margin: 0;
  font-style: italic;
`;

export default SignUp;
