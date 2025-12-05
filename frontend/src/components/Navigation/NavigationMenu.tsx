/**
 * NavigationMenu Component
 * 
<<<<<<< HEAD
 * Handles nested navigation with expandable/collapsible submenus
 * Supports multi-level hierarchies with proper indentation
 */
import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import styled from 'styled-components';
=======
 * Handles nested navigation with expandable/collapsible accordion submenus
 * Supports multi-level hierarchies with proper indentation and smooth animations
 */
import React, { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import styled, { css } from 'styled-components';
>>>>>>> origin/development
import { NavigationItem } from '../../config/navigation';
import { useTheme } from '../../contexts/ThemeContext';
import { Theme } from '../../config/theme';

interface NavigationMenuProps {
  items: NavigationItem[];
  isExpanded: boolean;
  level?: number;
}

<<<<<<< HEAD
const NavigationMenu: React.FC<NavigationMenuProps> = ({ items, isExpanded: sidebarExpanded, level = 0 }) => {
  const { theme } = useTheme();
  const location = useLocation();
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  const toggleExpand = (label: string) => {
=======
// Chevron SVG icon component for accordion expand/collapse
const ChevronIcon: React.FC<{ isExpanded: boolean }> = ({ isExpanded }) => (
  <svg 
    width="12" 
    height="12" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2.5" 
    strokeLinecap="round" 
    strokeLinejoin="round"
    style={{
      transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)',
      transition: 'transform 0.2s ease',
      flexShrink: 0
    }}
  >
    <polyline points="9 18 15 12 9 6" />
  </svg>
);

const NavigationMenu: React.FC<NavigationMenuProps> = ({ items, isExpanded: sidebarExpanded, level = 0 }) => {
  const { theme, themeName } = useTheme();
  const location = useLocation();
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const isDarkMode = themeName === 'dark';

  // Auto-expand parent items when a child is active
  useEffect(() => {
    const findActiveParents = (navItems: NavigationItem[], parents: string[] = []): string[] => {
      for (const item of navItems) {
        if (item.path === location.pathname) {
          return parents;
        }
        if (item.children) {
          const found = findActiveParents(item.children, [...parents, item.label]);
          if (found.length > 0) {
            return found;
          }
        }
      }
      return [];
    };
    
    const activeParents = findActiveParents(items);
    if (activeParents.length > 0) {
      setExpandedItems(prev => {
        const newSet = new Set(prev);
        activeParents.forEach(parent => newSet.add(parent));
        return newSet;
      });
    }
  }, [location.pathname, items]);

  const toggleExpand = (label: string, e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
>>>>>>> origin/development
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

<<<<<<< HEAD
=======
  const isExactActive = (item: NavigationItem): boolean => {
    return item.path === location.pathname;
  };

  // Render a simple navigation link (no children)
  const renderNavLink = (item: NavigationItem, exactActive: boolean, active: boolean) => (
    <StyledNavLink
      to={item.path!}
      $theme={theme}
      $level={level}
      $active={exactActive}
      $hasActiveChild={active && !exactActive}
      $isDarkMode={isDarkMode}
    >
      <NavIcon $color={item.color}>{item.icon}</NavIcon>
      {sidebarExpanded && <NavLabel>{item.label}</NavLabel>}
    </StyledNavLink>
  );

  // Render accordion header content (icon and label)
  const renderAccordionContent = (item: NavigationItem) => {
    if (item.path) {
      return (
        <AccordionNavLink to={item.path} $level={level}>
          <NavIcon $color={item.color}>{item.icon}</NavIcon>
          {sidebarExpanded && <NavLabel>{item.label}</NavLabel>}
        </AccordionNavLink>
      );
    }
    return (
      <>
        <NavIcon $color={item.color}>{item.icon}</NavIcon>
        {sidebarExpanded && <NavLabel>{item.label}</NavLabel>}
      </>
    );
  };

  // Render accordion header with expand/collapse button
  const renderAccordionHeader = (item: NavigationItem, isItemExpanded: boolean, active: boolean) => (
    <AccordionHeader
      onClick={(e) => {
        if (!item.path) {
          toggleExpand(item.label, e);
        }
      }}
      $theme={theme}
      $level={level}
      $active={active}
      $isExpanded={isItemExpanded}
      $isDarkMode={isDarkMode}
    >
      {renderAccordionContent(item)}
      {sidebarExpanded && (
        <ExpandButton 
          onClick={(e) => toggleExpand(item.label, e)}
          $isExpanded={isItemExpanded}
          $isDarkMode={isDarkMode}
          aria-label={isItemExpanded ? 'Collapse' : 'Expand'}
        >
          <ChevronIcon isExpanded={isItemExpanded} />
        </ExpandButton>
      )}
    </AccordionHeader>
  );

  // Render menu button (fallback for items without path or children)
  const renderMenuButton = (item: NavigationItem, active: boolean) => (
    <MenuButton
      onClick={() => toggleExpand(item.label)}
      $theme={theme}
      $level={level}
      $active={active}
      $isDarkMode={isDarkMode}
    >
      <NavIcon $color={item.color}>{item.icon}</NavIcon>
      {sidebarExpanded && <NavLabel>{item.label}</NavLabel>}
    </MenuButton>
  );

>>>>>>> origin/development
  return (
    <MenuContainer>
      {items.map((item) => {
        const hasChildren = item.children && item.children.length > 0;
<<<<<<< HEAD
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
                {sidebarExpanded && <NavLabel>{item.label}</NavLabel>}
                {hasChildren && sidebarExpanded && (
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
                {sidebarExpanded && <NavLabel>{item.label}</NavLabel>}
                {hasChildren && sidebarExpanded && (
                  <ExpandIcon $isExpanded={isExpanded}>
                    {isExpanded ? '▼' : '▶'}
                  </ExpandIcon>
                )}
              </MenuButton>
            )}

            {hasChildren && isExpanded && (
              <SubMenu $isExpanded={isExpanded}>
=======
        const isItemExpanded = expandedItems.has(item.label);
        const active = isActive(item);
        const exactActive = isExactActive(item);

        // Determine which component to render
        let menuItemContent;
        if (item.path && !hasChildren) {
          menuItemContent = renderNavLink(item, exactActive, active);
        } else if (hasChildren) {
          menuItemContent = renderAccordionHeader(item, isItemExpanded, active);
        } else {
          menuItemContent = renderMenuButton(item, active);
        }

        return (
          <MenuItem key={item.label} $level={level}>
            {menuItemContent}
            {hasChildren && (
              <AccordionContent $isExpanded={isItemExpanded && sidebarExpanded} $isDarkMode={isDarkMode}>
>>>>>>> origin/development
                <NavigationMenu
                  items={item.children!}
                  isExpanded={sidebarExpanded}
                  level={level + 1}
                />
<<<<<<< HEAD
              </SubMenu>
=======
              </AccordionContent>
>>>>>>> origin/development
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
<<<<<<< HEAD
=======
  gap: 2px;
>>>>>>> origin/development
`;

const MenuItem = styled.div<{ $level: number }>`
  position: relative;
<<<<<<< HEAD
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
=======
`;

const baseItemStyles = css<{ $level: number; $active: boolean; $isDarkMode: boolean }>`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  padding-left: ${(props) => 12 + props.$level * 16}px;
  color: ${(props) => props.$isDarkMode 
    ? `rgba(255, 255, 255, ${props.$active ? 1 : 0.7})` 
    : `rgba(30, 41, 59, ${props.$active ? 1 : 0.7})`};
  text-decoration: none;
  transition: all 0.15s ease;
  font-size: ${(props) => props.$level === 0 ? 14 : 13}px;
  border-radius: 8px;
  margin: 0 8px;
  min-height: 40px;
  
  &:hover {
    background-color: ${(props) => props.$isDarkMode 
      ? 'rgba(255, 255, 255, 0.08)' 
      : 'rgba(0, 0, 0, 0.04)'};
    color: ${(props) => props.$isDarkMode ? 'white' : '#1e293b'};
  }
`;

const activeStyles = css<{ $isDarkMode: boolean }>`
  background-color: ${(props) => props.$isDarkMode 
    ? 'rgba(124, 58, 237, 0.15)' 
    : 'rgba(124, 58, 237, 0.1)'};
  color: ${(props) => props.$isDarkMode ? 'white' : '#1e293b'};
  
  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 24px;
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
    border-radius: 0 3px 3px 0;
  }

  &:hover {
    background-color: ${(props) => props.$isDarkMode 
      ? 'rgba(124, 58, 237, 0.2)' 
      : 'rgba(124, 58, 237, 0.15)'};
  }
`;

const StyledNavLink = styled(NavLink)<{ $theme: Theme; $level: number; $active: boolean; $hasActiveChild?: boolean; $isDarkMode: boolean }>`
  ${baseItemStyles}
  position: relative;
  
  ${(props) => props.$active && activeStyles}
  
  ${(props) => props.$hasActiveChild && css<{ $isDarkMode: boolean }>`
    color: ${props.$isDarkMode ? 'rgba(255, 255, 255, 0.95)' : 'rgba(30, 41, 59, 0.95)'};
  `}

  &.active {
    ${activeStyles}
  }
`;

const AccordionHeader = styled.div<{ $theme: Theme; $level: number; $active: boolean; $isExpanded: boolean; $isDarkMode: boolean }>`
  ${baseItemStyles}
  position: relative;
  cursor: pointer;
  
  ${(props) => props.$active && !props.$isExpanded && css<{ $isDarkMode: boolean }>`
    color: ${props.$isDarkMode ? 'rgba(255, 255, 255, 0.95)' : 'rgba(30, 41, 59, 0.95)'};
  `}
`;

const AccordionNavLink = styled(NavLink)<{ $level: number }>`
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  color: inherit;
  text-decoration: none;
  min-height: inherit;
`;

const MenuButton = styled.button<{ $theme: Theme; $level: number; $active: boolean; $isDarkMode: boolean }>`
  ${baseItemStyles}
  width: calc(100% - 16px);
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  
  ${(props) => props.$active && activeStyles}
`;

const ExpandButton = styled.button<{ $isExpanded: boolean; $isDarkMode: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: ${(props) => props.$isDarkMode 
    ? 'rgba(255, 255, 255, 0.5)' 
    : 'rgba(0, 0, 0, 0.4)'};
  transition: all 0.15s ease;
  margin-left: auto;
  flex-shrink: 0;
  
  &:hover {
    background: ${(props) => props.$isDarkMode 
      ? 'rgba(255, 255, 255, 0.1)' 
      : 'rgba(0, 0, 0, 0.05)'};
    color: ${(props) => props.$isDarkMode ? 'white' : '#1e293b'};
>>>>>>> origin/development
  }
`;

const NavIcon = styled.span<{ $color?: string }>`
  font-size: 18px;
<<<<<<< HEAD
  min-width: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${(props) => props.$color || 'white'};
  filter: ${(props) => (props.$color ? 'none' : 'none')};
=======
  min-width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${(props) => props.$color || 'inherit'};
  flex-shrink: 0;
>>>>>>> origin/development
`;

const NavLabel = styled.span`
  flex: 1;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
<<<<<<< HEAD
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
=======
  letter-spacing: 0.01em;
`;

const AccordionContent = styled.div<{ $isExpanded: boolean; $isDarkMode: boolean }>`
  overflow: hidden;
  /* 
   * max-height is set to a large value to enable CSS transitions.
   * CSS cannot animate to 'auto' height, so we use a value large enough
   * to accommodate deeply nested navigation (supports ~25 items at 40px each).
   */
  max-height: ${(props) => (props.$isExpanded ? '2000px' : '0')};
  opacity: ${(props) => (props.$isExpanded ? 1 : 0)};
  transition: max-height 0.25s ease-out, opacity 0.2s ease;
  background: ${(props) => props.$isDarkMode 
    ? 'rgba(0, 0, 0, 0.15)' 
    : 'rgba(0, 0, 0, 0.02)'};
  margin: ${(props) => props.$isExpanded ? '2px 0' : '0'};
  border-radius: 4px;
  margin-left: 8px;
  margin-right: 8px;
>>>>>>> origin/development
`;

export default NavigationMenu;
