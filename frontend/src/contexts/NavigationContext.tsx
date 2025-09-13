import React, { createContext, useContext, useState, useCallback } from 'react';
import { useLocation } from 'react-router-dom';

interface NavigationContextType {
  currentModule: string;
  moduleData: { [key: string]: any };
  setModuleData: (module: string, data: any) => void;
  clearModuleData: (module: string) => void;
  breadcrumbPath: string[];
  setBreadcrumbPath: (path: string[]) => void;
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

const NavigationContext = createContext<NavigationContextType | undefined>(undefined);

export const useNavigation = () => {
  const context = useContext(NavigationContext);
  if (!context) {
    throw new Error('useNavigation must be used within a NavigationProvider');
  }
  return context;
};

interface NavigationProviderProps {
  children: React.ReactNode;
}

export const NavigationProvider: React.FC<NavigationProviderProps> = ({ children }) => {
  const location = useLocation();
  const [moduleData, setModuleDataState] = useState<{ [key: string]: any }>({});
  const [breadcrumbPath, setBreadcrumbPath] = useState<string[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Get current module from location
  const currentModule = location.pathname.split('/')[1] || 'dashboard';

  const setModuleData = useCallback((module: string, data: any) => {
    setModuleDataState(prev => ({
      ...prev,
      [module]: { ...prev[module], ...data }
    }));
  }, []);

  const clearModuleData = useCallback((module: string) => {
    setModuleDataState(prev => {
      const newData = { ...prev };
      delete newData[module];
      return newData;
    });
  }, []);

  const value: NavigationContextType = {
    currentModule,
    moduleData,
    setModuleData,
    clearModuleData,
    breadcrumbPath,
    setBreadcrumbPath,
    sidebarOpen,
    setSidebarOpen,
  };

  return (
    <NavigationContext.Provider value={value}>
      {children}
    </NavigationContext.Provider>
  );
};