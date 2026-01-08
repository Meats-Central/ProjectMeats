import React from 'react';
import styled from 'styled-components';

const Plants: React.FC = () => {
  return (
    <Container>
      <Header>
        <Title>Plants</Title>
        <Subtitle>Manage your processing facilities and locations</Subtitle>
      </Header>

      <ComingSoon>
        <Icon>🏢</Icon>
        <Text>Plant Management</Text>
        <SubText>Coming Soon - Facility and location management</SubText>
        <Features>
          <FeatureItem>• Plant location and details management</FeatureItem>
          <FeatureItem>• Processing capacity tracking</FeatureItem>
          <FeatureItem>• Equipment and resource management</FeatureItem>
          <FeatureItem>• Production scheduling and planning</FeatureItem>
        </Features>
      </ComingSoon>
    </Container>
  );
};

const Container = styled.div`
  max-width: 1200px;
`;

const Header = styled.div`
  margin-bottom: 40px;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: rgb(var(--color-text-primary));
  margin: 0 0 8px 0;
`;

const Subtitle = styled.p`
  font-size: 16px;
  color: #6c757d;
  margin: 0;
`;

const ComingSoon = styled.div`
  background: rgb(var(--color-surface));
  color: rgb(var(--color-surface-foreground));
  border-radius: 12px;
  padding: 60px 40px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
`;

const Icon = styled.div`
  font-size: 64px;
  margin-bottom: 20px;
`;

const Text = styled.h2`
  font-size: 24px;
  color: rgb(var(--color-text-primary));
  margin-bottom: 10px;
`;

const SubText = styled.p`
  color: #6c757d;
  margin-bottom: 30px;
  font-size: 16px;
`;

const Features = styled.div`
  max-width: 400px;
  margin: 0 auto;
  text-align: left;
`;

const FeatureItem = styled.div`
  color: rgb(var(--color-text-primary));
  margin-bottom: 8px;
  font-size: 14px;
`;

export default Plants;
