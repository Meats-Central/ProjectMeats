/**
 * Main App Component
 *
 * ProjectMeats3 React Application
 * Full Business Management System with AI Assistant
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { NavigationProvider } from './contexts/NavigationContext';
import { ThemeProvider } from './contexts/ThemeContext';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard';
import Suppliers from './pages/Suppliers';
import Customers from './pages/Customers';
import PurchaseOrders from './pages/PurchaseOrders';
import AccountsReceivables from './pages/AccountsReceivables';
import Contacts from './pages/Contacts';
import Plants from './pages/Plants';
import Carriers from './pages/Carriers';
import AIAssistant from './pages/AIAssistant';
import Login from './pages/Login';
import SignUp from './pages/SignUp';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import ApiTestComponent from './components/ApiTestComponent';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <ThemeProvider>
        <Router
          future={{
            v7_startTransition: true,
            v7_relativeSplatPath: true,
          }}
        >
          <NavigationProvider>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<SignUp />} />
              <Route path="/" element={<Layout />}>
                <Route index element={<Dashboard />} />
                <Route path="suppliers" element={<Suppliers />} />
                <Route path="customers" element={<Customers />} />
                <Route path="purchase-orders" element={<PurchaseOrders />} />
                <Route path="accounts-receivables" element={<AccountsReceivables />} />
                <Route path="contacts" element={<Contacts />} />
                <Route path="plants" element={<Plants />} />
                <Route path="carriers" element={<Carriers />} />
                <Route path="ai-assistant" element={<AIAssistant />} />
                <Route path="profile" element={<Profile />} />
                <Route path="settings" element={<Settings />} />
                <Route path="api-test" element={<ApiTestComponent />} />
              </Route>
            </Routes>
          </NavigationProvider>
        </Router>
      </ThemeProvider>
    </AuthProvider>
  );
};

export default App;
