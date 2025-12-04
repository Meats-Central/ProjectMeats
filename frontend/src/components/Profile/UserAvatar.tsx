/**
 * UserAvatar Component
 * 
 * Displays user avatar with optional upload functionality in edit mode.
 * Features:
 * - Circular avatar display
 * - Edit mode with upload icon overlay
 * - File input for image selection
 * - Theme-aware styling
 * - ARIA accessible
 * - Tenant-isolated storage ready
 */
import React, { useState } from 'react';
import styled from 'styled-components';
import { useTheme } from '../../contexts/ThemeContext';
import { Theme } from '../../config/theme';

interface UserAvatarProps {
  isEditMode: boolean;
  imageUrl?: string | null;
  initials: string;
  onUpload: (file: File) => void | Promise<void>;
  size?: number;
}

const UserAvatar: React.FC<UserAvatarProps> = ({
  isEditMode,
  imageUrl,
  initials,
  onUpload,
  size = 100,
}) => {
  const { theme } = useTheme();
  const [uploading, setUploading] = useState(false);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      alert('Please upload a valid image file (JPEG, PNG, GIF, or WebP)');
      return;
    }

    // Validate file size (5MB max)
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
      alert('File size must be less than 5MB');
      return;
    }

    try {
      setUploading(true);
      await onUpload(file);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload image. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <AvatarContainer $size={size}>
      <AvatarCircle $size={size} $theme={theme} $hasImage={!!imageUrl}>
        {imageUrl ? (
          <AvatarImage src={imageUrl} alt="User profile" />
        ) : (
          <AvatarInitials $size={size}>{initials}</AvatarInitials>
        )}
      </AvatarCircle>

      {isEditMode && (
        <UploadOverlay $size={size} $theme={theme}>
          <UploadLabel htmlFor="avatar-upload" $uploading={uploading}>
            <UploadIcon $uploading={uploading}>
              {uploading ? '⏳' : '📷'}
            </UploadIcon>
            <UploadText>Upload</UploadText>
            <HiddenFileInput
              id="avatar-upload"
              type="file"
              accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
              onChange={handleFileChange}
              disabled={uploading}
              aria-label="Upload profile picture"
            />
          </UploadLabel>
        </UploadOverlay>
      )}
    </AvatarContainer>
  );
};

const AvatarContainer = styled.div<{ $size: number }>`
  position: relative;
  width: ${(props) => props.$size}px;
  height: ${(props) => props.$size}px;
`;

const AvatarCircle = styled.div<{ $size: number; $theme: Theme; $hasImage: boolean }>`
  width: ${(props) => props.$size}px;
  height: ${(props) => props.$size}px;
  border-radius: 50%;
  background: ${(props) =>
    props.$hasImage
      ? 'transparent'
      : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }
`;

const AvatarImage = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
`;

const AvatarInitials = styled.div<{ $size: number }>`
  font-size: ${(props) => props.$size * 0.4}px;
  font-weight: 700;
  color: white;
  user-select: none;
`;

const UploadOverlay = styled.div<{ $size: number; $theme: Theme }>`
  position: absolute;
  bottom: 0;
  right: 0;
  width: ${(props) => props.$size * 0.35}px;
  height: ${(props) => props.$size * 0.35}px;
  border-radius: 50%;
  background: ${(props) =>
    props.$theme.name === 'dark'
      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  }

  &:active {
    transform: scale(0.95);
  }
`;

const UploadLabel = styled.label<{ $uploading: boolean }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  cursor: ${(props) => (props.$uploading ? 'not-allowed' : 'pointer')};
  opacity: ${(props) => (props.$uploading ? 0.6 : 1)};
`;

const UploadIcon = styled.div<{ $uploading: boolean }>`
  font-size: 18px;
  animation: ${(props) => (props.$uploading ? 'spin 1s linear infinite' : 'none')};

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
`;

const UploadText = styled.span`
  font-size: 8px;
  font-weight: 600;
  color: white;
  margin-top: 2px;
  text-transform: uppercase;
`;

const HiddenFileInput = styled.input`
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
`;

export default UserAvatar;
