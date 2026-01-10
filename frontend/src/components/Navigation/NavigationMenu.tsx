/**
 * NavigationMenu Component
 * 
 * Handles nested navigation with expandable/collapsible accordion submenus
 * Supports multi-level hierarchies with proper indentation and smooth animations
 */
import React, { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import styled, { css } from 'styled-components';
import { NavigationItem } from '../../config/navigation';
import { useTheme } from '../../contexts/ThemeContext';
import { Theme } from '../../config/theme';

interface NavigationMenuProps {
  items: NavigationItem[];
  isExpanded: boolean;
  level?: number;
}

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
  // Changed from Set to string | null for exclusive accordion (only one open at a time)
  const [expandedItem, setExpandedItem] = useState<string | null>(null);
  const isDarkMode = themeName === 'dark';

  // Auto-expand parent items when a child is active
  useEffect(() => {
    const findActiveParent = (navItems: NavigationItem[]): string | null => {
      for (const item of navItems) {
        if (item.path === location.pathname && item.children) {
          return item.label;
        }
        if (item.children) {
          const found = findActiveParent(item.children);
          if (found) {
            return item.label; // Return top-level parent only
          }
        }
      }
      return null;
    };
    
    const activeParent = findActiveParent(items);
    if (activeParent) {
      setExpandedItem(activeParent);
    }
  }, [location.pathname, items]);

  const toggleExpand = (label: string, e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    // Exclusive accordion: if clicking the same item, collapse it; otherwise expand the new one
    setExpandedItem((prev) => (prev === label ? null : label));
  };

  const isActive = (item: NavigationItem): boolean => {
    if (item.path && location.pathname === item.path) return true;
    if (item.children) {
      return item.children.some((child) => isActive(child));
    }
    return false;
  };

  const isExactActive = (item: NavigationItem): boolean => {
    return item.path === location.pathname;
  };

  const hasExactActiveChild = (item: NavigationItem): boolean => {
    if (!item.children) return false;
    return item.children.some((child) => {
      if (child.path === location.pathname) return true;
      if (child.children) return hasExactActiveChild(child);
      return false;
    });
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
  const renderAccordionHeader = (item: NavigationItem, isItemExpanded: boolean, active: boolean, hasActiveChild: boolean) => (
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
      $hasExactActiveChild={hasActiveChild}
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

  return (
    <MenuContainer>
      {items.map((item) => {
        const hasChildren = item.children && item.children.length > 0;
        const isItemExpanded = expandedItem === item.label; // Changed from Set.has() to direct comparison
        const active = isActive(item);
        const exactActive = isExactActive(item);
        const hasActiveChild = hasExactActiveChild(item);

        // Determine which component to render
        let menuItemContent;
        if (item.path && !hasChildren) {
          menuItemContent = renderNavLink(item, exactActive, active);
        } else if (hasChildren) {
          menuItemContent = renderAccordionHeader(item, isItemExpanded, active, hasActiveChild);
        } else {
          menuItemContent = renderMenuButton(item, active);
        }

        return (
          <MenuItem key={item.label} $level={level}>
            {menuItemContent}
            {hasChildren && (
              <AccordionContent $isExpanded={isItemExpanded && sidebarExpanded} $isDarkMode={isDarkMode}>
                <NavigationMenu
                  items={item.children!}
                  isExpanded={sidebarExpanded}
                  level={level + 1}
                />
              </AccordionContent>
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
  gap: 0;
`;

const MenuItem = styled.div<{ $level: number }>`
  position: relative;
  /* Removed margin-bottom to ensure consistent spacing handled by baseItemStyles */
`;

const baseItemStyles = css<{ $level: number; $active: boolean; $isDarkMode: boolean }>`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 12px;
  padding-left: ${(props) => 12 + props.$level * 16}px;
  color: ${(props) => props.$isDarkMode 
    ? `rgba(255, 255, 255, ${props.$active ? 1 : 0.7})` 
    : `rgba(30, 41, 59, ${props.$active ? 1 : 0.7})`};
  text-decoration: none;
  transition: all 0.15s ease;
  font-size: ${(props) => props.$level === 0 ? 14 : 13}px;
  border-radius: 8px;
  margin: 0 8px 4px 8px;
  height: 60px;
  box-sizing: border-box;
  
  &:hover {
    background-color: ${(props) => props.$isDarkMode 
      ? 'rgba(255, 255, 255, 0.08)' 
      : 'rgba(0, 0, 0, 0.04)'};
    color: ${(props) => props.$isDarkMode ? 'white' : 'rgb(var(--color-text-primary))'};
  }
`;

const activeStyles = css<{ $isDarkMode: boolean }>`
  background-color: ${(props) => props.$isDarkMode 
    ? 'rgba(var(--color-primary), 0.15)' 
    : 'rgba(var(--color-primary), 0.1)'};
  color: ${(props) => props.$isDarkMode ? 'white' : 'rgb(var(--color-text-primary))'};
  
  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 24px;
    background: rgb(var(--color-primary));
    border-radius: 0 3px 3px 0;
  }

  &:hover {
    background-color: ${(props) => props.$isDarkMode 
      ? 'rgba(var(--color-primary), 0.2)' 
      : 'rgba(var(--color-primary), 0.15)'};
  }
`;

const StyledNavLink = styled(NavLink)<{ $theme: Theme; $level: number; $active: boolean; $hasActiveChild?: boolean; $isDarkMode: boolean }>`
  ${baseItemStyles}
  position: relative;
  
  ${(props) => props.$active && activeStyles}
  
  ${(props) => props.$hasActiveChild && css<{ $isDarkMode: boolean }>`
    color: ${props.$isDarkMode ? 'rgba(255, 255, 255, 0.95)' : 'rgb(var(--color-text-primary))'};
  `}

  &.active {
    ${activeStyles}
  }
`;

const AccordionHeader = styled.div<{ $theme: Theme; $level: number; $active: boolean; $isExpanded: boolean; $isDarkMode: boolean; $hasExactActiveChild?: boolean }>`
  ${baseItemStyles}
  position: relative;
  cursor: pointer;
  
  ${(props) => props.$active && !props.$hasExactActiveChild && css<{ $isDarkMode: boolean }>`
    background-color: ${props.$isDarkMode 
      ? 'rgba(var(--color-primary), 0.15)' 
      : 'rgba(var(--color-primary), 0.1)'};
    color: ${props.$isDarkMode ? 'white' : 'rgb(var(--color-text-primary))'};
    
    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 50%;
      transform: translateY(-50%);
      width: 3px;
      height: 32px;
      background: rgb(var(--color-primary));
      border-radius: 0 3px 3px 0;
    }

    &:hover {
      background-color: ${props.$isDarkMode 
        ? 'rgba(var(--color-primary), 0.2)' 
        : 'rgba(var(--color-primary), 0.15)'};
    }
  `}
  
  ${(props) => props.$active && props.$hasExactActiveChild && css<{ $isDarkMode: boolean }>`
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
    color: ${(props) => props.$isDarkMode ? 'white' : 'rgb(var(--color-text-primary))'};
  }
`;

const NavIcon = styled.span<{ $color?: string }>`
  font-size: 18px;
  min-width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: inherit;
  flex-shrink: 0;
  opacity: 0.9;
`;

const NavLabel = styled.span`
  flex: 1;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
`;

export default NavigationMenu;
