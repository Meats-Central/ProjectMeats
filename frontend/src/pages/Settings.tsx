import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import styled from 'styled-components';

interface Settings {
  notifications: {
    email: boolean;
    push: boolean;
    orderUpdates: boolean;
    systemUpdates: boolean;
  };
  preferences: {
    language: string;
    timezone: string;
    dateFormat: string;
    currency: string;
  };
  privacy: {
    profileVisible: boolean;
    shareData: boolean;
  };
}

const Settings: React.FC = () => {
  const { user } = useAuth();
  const [settings, setSettings] = useState<Settings>({
    notifications: {
      email: true,
      push: true,
      orderUpdates: true,
      systemUpdates: false
    },
    preferences: {
      language: 'en',
      timezone: 'UTC',
      dateFormat: 'MM/DD/YYYY',
      currency: 'USD'
    },
    privacy: {
      profileVisible: true,
      shareData: false
    }
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    // Load settings from localStorage (in a real app, this would come from an API)
    const savedSettings = localStorage.getItem('userSettings');
    if (savedSettings) {
      try {
        setSettings(JSON.parse(savedSettings));
      } catch (error) {
        console.error('Failed to parse saved settings:', error);
      }
    }
  }, []);

  const handleSave = async () => {
    setLoading(true);
    setMessage(null);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Save to localStorage (in a real app, this would be an API call)
      localStorage.setItem('userSettings', JSON.stringify(settings));
      
      setMessage({ type: 'success', text: 'Settings saved successfully!' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save settings. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const handleNotificationChange = (key: keyof Settings['notifications']) => {
    setSettings(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [key]: !prev.notifications[key]
      }
    }));
    if (message) setMessage(null);
  };

  const handlePreferenceChange = (key: keyof Settings['preferences'], value: string) => {
    setSettings(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [key]: value
      }
    }));
    if (message) setMessage(null);
  };

  const handlePrivacyChange = (key: keyof Settings['privacy']) => {
    setSettings(prev => ({
      ...prev,
      privacy: {
        ...prev.privacy,
        [key]: !prev.privacy[key]
      }
    }));
    if (message) setMessage(null);
  };

  const resetToDefaults = () => {
    setSettings({
      notifications: {
        email: true,
        push: true,
        orderUpdates: true,
        systemUpdates: false
      },
      preferences: {
        language: 'en',
        timezone: 'UTC',
        dateFormat: 'MM/DD/YYYY',
        currency: 'USD'
      },
      privacy: {
        profileVisible: true,
        shareData: false
      }
    });
    setMessage({ type: 'success', text: 'Settings reset to defaults!' });
  };

  if (!user) {
    return (
      <Container>
        <LoadingMessage>Loading settings...</LoadingMessage>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <Title>Settings</Title>
        <Subtitle>Customize your ProjectMeats experience</Subtitle>
      </Header>

      {message && (
        <Message $type={message.type}>
          <MessageIcon>{message.type === 'success' ? '✅' : '❌'}</MessageIcon>
          {message.text}
        </Message>
      )}

      <SettingsContent>
        {/* Notification Settings */}
        <SettingsSection>
          <SectionHeader>
            <SectionIcon>🔔</SectionIcon>
            <div>
              <SectionTitle>Notifications</SectionTitle>
              <SectionDescription>Manage how you receive updates and alerts</SectionDescription>
            </div>
          </SectionHeader>

          <SettingGroup>
            <SettingItem>
              <SettingInfo>
                <SettingLabel>Email Notifications</SettingLabel>
                <SettingDescription>Receive notifications via email</SettingDescription>
              </SettingInfo>
              <Toggle
                $active={settings.notifications.email}
                onClick={() => handleNotificationChange('email')}
              >
                <ToggleSlider $active={settings.notifications.email} />
              </Toggle>
            </SettingItem>

            <SettingItem>
              <SettingInfo>
                <SettingLabel>Push Notifications</SettingLabel>
                <SettingDescription>Receive browser push notifications</SettingDescription>
              </SettingInfo>
              <Toggle
                $active={settings.notifications.push}
                onClick={() => handleNotificationChange('push')}
              >
                <ToggleSlider $active={settings.notifications.push} />
              </Toggle>
            </SettingItem>

            <SettingItem>
              <SettingInfo>
                <SettingLabel>Order Updates</SettingLabel>
                <SettingDescription>Get notified about order status changes</SettingDescription>
              </SettingInfo>
              <Toggle
                $active={settings.notifications.orderUpdates}
                onClick={() => handleNotificationChange('orderUpdates')}
              >
                <ToggleSlider $active={settings.notifications.orderUpdates} />
              </Toggle>
            </SettingItem>

            <SettingItem>
              <SettingInfo>
                <SettingLabel>System Updates</SettingLabel>
                <SettingDescription>Receive notifications about system maintenance and updates</SettingDescription>
              </SettingInfo>
              <Toggle
                $active={settings.notifications.systemUpdates}
                onClick={() => handleNotificationChange('systemUpdates')}
              >
                <ToggleSlider $active={settings.notifications.systemUpdates} />
              </Toggle>
            </SettingItem>
          </SettingGroup>
        </SettingsSection>

        {/* Preferences */}
        <SettingsSection>
          <SectionHeader>
            <SectionIcon>⚙️</SectionIcon>
            <div>
              <SectionTitle>Preferences</SectionTitle>
              <SectionDescription>Customize your interface and regional settings</SectionDescription>
            </div>
          </SectionHeader>

          <SettingGroup>
            <SettingItem>
              <SettingInfo>
                <SettingLabel>Language</SettingLabel>
                <SettingDescription>Choose your preferred language</SettingDescription>
              </SettingInfo>
              <Select
                value={settings.preferences.language}
                onChange={(e) => handlePreferenceChange('language', e.target.value)}
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
              </Select>
            </SettingItem>

            <SettingItem>
              <SettingInfo>
                <SettingLabel>Timezone</SettingLabel>
                <SettingDescription>Set your local timezone</SettingDescription>
              </SettingInfo>
              <Select
                value={settings.preferences.timezone}
                onChange={(e) => handlePreferenceChange('timezone', e.target.value)}
              >
                <option value="UTC">UTC</option>
                <option value="EST">EST (Eastern)</option>
                <option value="CST">CST (Central)</option>
                <option value="MST">MST (Mountain)</option>
                <option value="PST">PST (Pacific)</option>
              </Select>
            </SettingItem>

            <SettingItem>
              <SettingInfo>
                <SettingLabel>Date Format</SettingLabel>
                <SettingDescription>Choose how dates are displayed</SettingDescription>
              </SettingInfo>
              <Select
                value={settings.preferences.dateFormat}
                onChange={(e) => handlePreferenceChange('dateFormat', e.target.value)}
              >
                <option value="MM/DD/YYYY">MM/DD/YYYY (US)</option>
                <option value="DD/MM/YYYY">DD/MM/YYYY (EU)</option>
                <option value="YYYY-MM-DD">YYYY-MM-DD (ISO)</option>
              </Select>
            </SettingItem>

            <SettingItem>
              <SettingInfo>
                <SettingLabel>Currency</SettingLabel>
                <SettingDescription>Default currency for pricing</SettingDescription>
              </SettingInfo>
              <Select
                value={settings.preferences.currency}
                onChange={(e) => handlePreferenceChange('currency', e.target.value)}
              >
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
                <option value="GBP">GBP (£)</option>
                <option value="CAD">CAD (C$)</option>
              </Select>
            </SettingItem>
          </SettingGroup>
        </SettingsSection>

        {/* Privacy Settings */}
        <SettingsSection>
          <SectionHeader>
            <SectionIcon>🔒</SectionIcon>
            <div>
              <SectionTitle>Privacy</SectionTitle>
              <SectionDescription>Control your privacy and data sharing preferences</SectionDescription>
            </div>
          </SectionHeader>

          <SettingGroup>
            <SettingItem>
              <SettingInfo>
                <SettingLabel>Profile Visibility</SettingLabel>
                <SettingDescription>Allow other users to see your profile information</SettingDescription>
              </SettingInfo>
              <Toggle
                $active={settings.privacy.profileVisible}
                onClick={() => handlePrivacyChange('profileVisible')}
              >
                <ToggleSlider $active={settings.privacy.profileVisible} />
              </Toggle>
            </SettingItem>

            <SettingItem>
              <SettingInfo>
                <SettingLabel>Data Sharing</SettingLabel>
                <SettingDescription>Allow anonymous usage data to be shared for improvements</SettingDescription>
              </SettingInfo>
              <Toggle
                $active={settings.privacy.shareData}
                onClick={() => handlePrivacyChange('shareData')}
              >
                <ToggleSlider $active={settings.privacy.shareData} />
              </Toggle>
            </SettingItem>
          </SettingGroup>
        </SettingsSection>
      </SettingsContent>

      <Actions>
        <ResetButton onClick={resetToDefaults} disabled={loading}>
          Reset to Defaults
        </ResetButton>
        <SaveButton onClick={handleSave} disabled={loading}>
          {loading ? 'Saving...' : 'Save Changes'}
        </SaveButton>
      </Actions>
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

const SettingsContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 30px;
  margin-bottom: 30px;
`;

const SettingsSection = styled.div`
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
`;

const SectionHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
`;

const SectionIcon = styled.div`
  font-size: 24px;
`;

const SectionTitle = styled.h3`
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
`;

const SectionDescription = styled.p`
  font-size: 14px;
  color: #6c757d;
  margin: 4px 0 0 0;
`;

const SettingGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const SettingItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #f1f3f4;

  &:last-child {
    border-bottom: none;
  }
`;

const SettingInfo = styled.div`
  flex: 1;
`;

const SettingLabel = styled.div`
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
`;

const SettingDescription = styled.div`
  font-size: 14px;
  color: #6c757d;
`;

const Toggle = styled.button<{ $active: boolean }>`
  width: 48px;
  height: 24px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
  background: ${props => props.$active ? '#667eea' : '#e9ecef'};
  position: relative;
`;

const ToggleSlider = styled.div<{ $active: boolean }>`
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  position: absolute;
  top: 2px;
  left: ${props => props.$active ? '26px' : '2px'};
  transition: left 0.2s ease;
`;

const Select = styled.select`
  padding: 8px 12px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 14px;
  color: #2c3e50;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const Actions = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
`;

const ResetButton = styled.button`
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

export default Settings;
