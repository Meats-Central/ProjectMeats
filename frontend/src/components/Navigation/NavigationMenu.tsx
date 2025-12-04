/**
 * NavigationMenu Component
 * 
 * Handles nested navigation with expandable/collapsible submenus
 * Supports multi-level hierarchies with proper indentation
 */
import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { NavigationItem } from '../../config/navigation';
import { useTheme } from '../../contexts/ThemeContext';
import { Theme } from '../../config/theme';

interface NavigationMenuProps {
  items: NavigationItem[];
  isExpanded: boolean;
  level?: number;
}

const NavigationMenu: React.FC<NavigationMenuProps> = ({ items, isExpanded, level = 0 }) => {
  const { theme } = useTheme();
  const location = useLocation();
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  const toggleExpand = (label: string) => {
    setExpandedItems((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(label)) {
        newSet.delete(label);
      } else {
        newSet.add(label);
      }
      return newSet;
    });
  };

  const isActive = (item: NavigationItem): boolean => {
    if (item.path && location.pathname === item.path) return true;
    if (item.children) {
      return item.children.some((child) => isActive(child));
    }
    return false;
  };

  return (
    <MenuContainer>
      {items.map((item) => {
        const hasChildren = item.children && item.children.length > 0;
        const isExpanded = expandedItems.has(item.label);
        const active = isActive(item);

        return (
          <MenuItem key={item.label} $level={level}>
            {item.path ? (
              <StyledNavLink
                to={item.path}
                $theme={theme}
                $level={level}
                $active={active}
                onClick={() => hasChildren && toggleExpand(item.label)}
              >
                <NavIcon $color={item.color}>{item.icon}</NavIcon>
                {isExpanded && <NavLabel>{item.label}</NavLabel>}
                {hasChildren && isExpanded && (
                  <ExpandIcon $isExpanded={isExpanded}>
                    {isExpanded ? '▼' : '▶'}
                  </ExpandIcon>
                )}
              </StyledNavLink>
            ) : (
              <MenuButton
                onClick={() => toggleExpand(item.label)}
                $theme={theme}
                $level={level}
                $active={active}
              >
                <NavIcon $color={item.color}>{item.icon}</NavIcon>
                {isExpanded && <NavLabel>{item.label}</NavLabel>}
                {hasChildren && isExpanded && (
                  <ExpandIcon $isExpanded={isExpanded}>
                    {isExpanded ? '▼' : '▶'}
                  </ExpandIcon>
                )}
              </MenuButton>
            )}

            {hasChildren && isExpanded && (
              <SubMenu $isExpanded={isExpanded}>
                <NavigationMenu
                  items={item.children!}
                  isExpanded={isExpanded}
                  level={level + 1}
                />
              </SubMenu>
            )}
          </MenuItem>
        );
      })}
    </MenuContainer>
  );
};

const MenuContainer = styled.div`
  display: flex;
  flex-direction: column;
`;

const MenuItem = styled.div<{ $level: number }>`
  position: relative;
  margin-bottom: 2px;
`;

const StyledNavLink = styled(NavLink)<{ $theme: Theme; $level: number; $active: boolean }>`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 15px;
  padding-left: ${(props) => 15 + props.$level * 20}px;
  color: white;
  text-decoration: none;
  transition: all 0.2s ease;
  font-size: ${(props) => Math.max(14 - props.$level, 12)}px;
  background: ${(props) => (props.$active ? 'rgba(255, 255, 255, 0.15)' : 'transparent')};
  border-left: ${(props) => (props.$active ? '3px solid #667eea' : '3px solid transparent')};

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
  }

  &.active {
    background-color: rgba(255, 255, 255, 0.15);
    border-left: 3px solid #667eea;
  }
`;

const MenuButton = styled.button<{ $theme: Theme; $level: number; $active: boolean }>`
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 15px;
  padding-left: ${(props) => 15 + props.$level * 20}px;
  color: white;
  background: ${(props) => (props.$active ? 'rgba(255, 255, 255, 0.15)' : 'transparent')};
  border: none;
  border-left: ${(props) => (props.$active ? '3px solid #667eea' : '3px solid transparent')};
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: ${(props) => Math.max(14 - props.$level, 12)}px;
  text-align: left;

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
  }
`;

const NavIcon = styled.span<{ $color?: string }>`
  font-size: 18px;
  min-width: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${(props) => props.$color || 'white'};
  filter: ${(props) => (props.$color ? 'none' : 'none')};
`;

const NavLabel = styled.span`
  flex: 1;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const ExpandIcon = styled.span<{ $isExpanded: boolean }>`
  font-size: 10px;
  transition: transform 0.2s ease;
  transform: ${(props) => (props.$isExpanded ? 'rotate(0deg)' : 'rotate(-90deg)')};
  margin-left: auto;
`;

const SubMenu = styled.div<{ $isExpanded: boolean }>`
  overflow: hidden;
  max-height: ${(props) => (props.$isExpanded ? '1000px' : '0')};
  transition: max-height 0.3s ease;
  background: rgba(0, 0, 0, 0.2);
`;

export default NavigationMenu;
