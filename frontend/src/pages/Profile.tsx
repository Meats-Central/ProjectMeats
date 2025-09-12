import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import styled from 'styled-components';

const Profile: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    firstName: user?.first_name || '',
    lastName: user?.last_name || '',
    email: user?.email || '',
    username: user?.username || ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (message) setMessage(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      // For now, simulate the update (since we're using mock auth)
      // In the future, this would call an actual API endpoint
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update local storage with new data (for demo)
      if (user) {
        const updatedUser = {
          ...user,
          first_name: formData.firstName,
          last_name: formData.lastName,
          email: formData.email,
          username: formData.username
        };
        localStorage.setItem('user', JSON.stringify(updatedUser));
        await refreshUser();
      }
      
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
      setIsEditing(false);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to update profile. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      firstName: user?.first_name || '',
      lastName: user?.last_name || '',
      email: user?.email || '',
      username: user?.username || ''
    });
    setIsEditing(false);
    setMessage(null);
  };

  if (!user) {
    return (
      <Container>
        <LoadingMessage>Loading profile...</LoadingMessage>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <Title>My Profile</Title>
        <Subtitle>Manage your account information</Subtitle>
      </Header>

      {message && (
        <Message $type={message.type}>
          <MessageIcon>{message.type === 'success' ? '✅' : '❌'}</MessageIcon>
          {message.text}
        </Message>
      )}

      <ProfileCard>
        <ProfileHeader>
          <Avatar>
            {user.first_name?.[0]?.toUpperCase() || user.username?.[0]?.toUpperCase() || '👤'}
          </Avatar>
          <ProfileInfo>
            <DisplayName>
              {user.first_name && user.last_name 
                ? `${user.first_name} ${user.last_name}` 
                : user.username}
            </DisplayName>
            <UserRole>
              {user.is_superuser ? 'Super Administrator' : 
               user.is_staff ? 'Administrator' : 'User'}
            </UserRole>
          </ProfileInfo>
          <EditButton onClick={() => setIsEditing(!isEditing)}>
            {isEditing ? 'Cancel' : 'Edit Profile'}
          </EditButton>
        </ProfileHeader>

        {isEditing ? (
          <ProfileForm onSubmit={handleSubmit}>
            <FormRow>
              <FormGroup>
                <Label>First Name</Label>
                <Input
                  type="text"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Last Name</Label>
                <Input
                  type="text"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
            </FormRow>

            <FormGroup>
              <Label>Username</Label>
              <Input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                disabled={loading}
              />
            </FormGroup>

            <FormGroup>
              <Label>Email Address</Label>
              <Input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                disabled={loading}
              />
            </FormGroup>

            <FormActions>
              <CancelButton type="button" onClick={handleCancel} disabled={loading}>
                Cancel
              </CancelButton>
              <SaveButton type="submit" disabled={loading}>
                {loading ? 'Saving...' : 'Save Changes'}
              </SaveButton>
            </FormActions>
          </ProfileForm>
        ) : (
          <ProfileDetails>
            <DetailRow>
              <DetailLabel>Username</DetailLabel>
              <DetailValue>{user.username}</DetailValue>
            </DetailRow>
            <DetailRow>
              <DetailLabel>Email</DetailLabel>
              <DetailValue>{user.email || 'Not provided'}</DetailValue>
            </DetailRow>
            <DetailRow>
              <DetailLabel>First Name</DetailLabel>
              <DetailValue>{user.first_name || 'Not provided'}</DetailValue>
            </DetailRow>
            <DetailRow>
              <DetailLabel>Last Name</DetailLabel>
              <DetailValue>{user.last_name || 'Not provided'}</DetailValue>
            </DetailRow>
            <DetailRow>
              <DetailLabel>Account Status</DetailLabel>
              <DetailValue>
                <StatusBadge $active={user.is_active}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </StatusBadge>
              </DetailValue>
            </DetailRow>
          </ProfileDetails>
        )}
      </ProfileCard>

      <AccountInfo>
        <InfoTitle>Account Information</InfoTitle>
        <InfoGrid>
          <InfoCard>
            <InfoIcon>🔐</InfoIcon>
            <InfoContent>
              <InfoLabel>Account Type</InfoLabel>
              <InfoText>
                {user.is_superuser ? 'Super Administrator' : 
                 user.is_staff ? 'Administrator' : 'Standard User'}
              </InfoText>
            </InfoContent>
          </InfoCard>
          <InfoCard>
            <InfoIcon>⚡</InfoIcon>
            <InfoContent>
              <InfoLabel>Status</InfoLabel>
              <InfoText>{user.is_active ? 'Active Account' : 'Inactive Account'}</InfoText>
            </InfoContent>
          </InfoCard>
        </InfoGrid>
      </AccountInfo>
    </Container>
  );
};

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #6c757d;
`;

const Header = styled.div`
  margin-bottom: 30px;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
`;

const Subtitle = styled.p`
  font-size: 16px;
  color: #6c757d;
  margin: 0;
`;

const Message = styled.div<{ $type: 'success' | 'error' }>`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  background: ${props => props.$type === 'success' ? '#f0fdf4' : '#fef2f2'};
  border: 1px solid ${props => props.$type === 'success' ? '#bbf7d0' : '#fecaca'};
  color: ${props => props.$type === 'success' ? '#16a34a' : '#dc2626'};
`;

const MessageIcon = styled.span`
  font-size: 16px;
`;

const ProfileCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
`;

const ProfileHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
`;

const Avatar = styled.div`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 700;
  color: white;
`;

const ProfileInfo = styled.div`
  flex: 1;
`;

const DisplayName = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 4px 0;
`;

const UserRole = styled.p`
  font-size: 14px;
  color: #6c757d;
  margin: 0;
`;

const EditButton = styled.button`
  background: #667eea;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #5a67d8;
    transform: translateY(-1px);
  }
`;

const ProfileForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const FormRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;

  @media (max-width: 640px) {
    grid-template-columns: 1fr;
  }
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
`;

const Label = styled.label`
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
`;

const Input = styled.input`
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
    background-color: #f8f9fa;
    cursor: not-allowed;
  }
`;

const FormActions = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 10px;
`;

const CancelButton = styled.button`
  background: #6c757d;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background: #5a6268;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const SaveButton = styled.button`
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background: #5a67d8;
    transform: translateY(-1px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const ProfileDetails = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const DetailRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f1f3f4;

  &:last-child {
    border-bottom: none;
  }
`;

const DetailLabel = styled.span`
  font-weight: 600;
  color: #2c3e50;
`;

const DetailValue = styled.span`
  color: #6c757d;
`;

const StatusBadge = styled.span<{ $active: boolean }>`
  background: ${props => props.$active ? '#d4edda' : '#f8d7da'};
  color: ${props => props.$active ? '#155724' : '#721c24'};
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
`;

const AccountInfo = styled.div`
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
`;

const InfoTitle = styled.h3`
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 20px 0;
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
`;

const InfoCard = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
`;

const InfoIcon = styled.div`
  font-size: 24px;
`;

const InfoContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const InfoLabel = styled.span`
  font-size: 12px;
  font-weight: 600;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const InfoText = styled.span`
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
`;

export default Profile;
