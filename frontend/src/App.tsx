/**
 * Main App Component
 *
 * ProjectMeats3 React Application
 * Full Business Management System with AI Assistant
 */
import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { NavigationProvider } from './contexts/NavigationContext';
import { ThemeProvider } from './contexts/ThemeContext';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard';
import Suppliers from './pages/Suppliers';
import Customers from './pages/Customers';
import PurchaseOrders from './pages/PurchaseOrders';
import SalesOrders from './pages/SalesOrders';
import AccountsReceivables from './pages/AccountsReceivables';
import Payables from './pages/Payables';
import ColdStorage from './pages/ColdStorage';
import Contacts from './pages/Contacts';
import Plants from './pages/Plants';
import Carriers from './pages/Carriers';
import AIAssistant from './pages/AIAssistant';
import Cockpit from './pages/Cockpit';
import CallLog from './pages/Cockpit/CallLog';
import Claims from './pages/Accounting/Claims';
import PayablePOs from './pages/Accounting/PayablePOs';
import ReceivableSOs from './pages/Accounting/ReceivableSOs';
import Invoices from './pages/Accounting/Invoices';
import Processes from './pages/Processes';
import Reports from './pages/Reports';
import Login from './pages/Login';
import SignUp from './pages/SignUp';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import { ComingSoon } from './pages/ComingSoon';
import ApiTestComponent from './components/ApiTestComponent';

const App: React.FC = () => {
  // Dynamic favicon and title based on environment
  useEffect(() => {
    const updateFaviconAndTitle = () => {
      // Get environment from runtime config (set by deployment pipeline)
      // Falls back to build-time env or 'development' for local dev
      const environment = 
        window.ENV?.ENVIRONMENT || 
        (typeof import.meta !== 'undefined' ? import.meta.env?.MODE : undefined) ||
        (typeof process !== 'undefined' ? process.env?.NODE_ENV : undefined) ||
        'development';

      // Normalize environment string
      const env = environment.toLowerCase();

      // Select favicon and title prefix based on environment
      let faviconPath = '/favicon-prod.svg'; // Production (red MC)
      let titlePrefix = '';

      if (env === 'development' || env === 'dev') {
        faviconPath = '/favicon-dev.svg'; // Green DEV (SVG)
        titlePrefix = '[DEV] ';
      } else if (env === 'uat' || env === 'staging') {
        faviconPath = '/favicon-uat.svg'; // Yellow UAT (SVG)
        titlePrefix = '[UAT] ';
      }

      // Update favicon
      let faviconLink = document.querySelector<HTMLLinkElement>("link[rel*='icon']");
      if (!faviconLink) {
        // Create favicon link if it doesn't exist
        faviconLink = document.createElement('link');
        faviconLink.rel = 'icon';
        document.head.appendChild(faviconLink);
      }
      faviconLink.href = faviconPath;

      // Update page title with environment prefix
      const baseTitle = 'Meats Central';
      if (!document.title.startsWith('[')) {
        document.title = titlePrefix + baseTitle;
      }

      // Log for debugging (only in development)
      if (env === 'development' || env === 'dev') {
        console.log(`[Environment] ${env} - Favicon: ${faviconPath}`);
      }
    };

    updateFaviconAndTitle();
  }, []); // Run once on mount

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
                
                {/* Suppliers & Related */}
                <Route path="suppliers" element={<Suppliers />} />
                <Route path="suppliers/contacts" element={<Contacts />} />
                <Route path="plants" element={<Plants />} />
                
                {/* Customers & Related */}
                <Route path="customers" element={<Customers />} />
                <Route path="customers/contacts" element={<Contacts />} />
                
                {/* Orders */}
                <Route path="purchase-orders" element={<PurchaseOrders />} />
                <Route path="purchase-orders/attachments" element={<ComingSoon title="Purchase Order Attachments" description="View and manage attachments for purchase orders." />} />
                <Route path="sales-orders" element={<SalesOrders />} />
                <Route path="sales-orders/attachments" element={<ComingSoon title="Sales Order Attachments" description="View and manage attachments for sales orders." />} />
                
                {/* Accounting */}
                <Route path="accounts-receivables" element={<AccountsReceivables />} />
                <Route path="accounting/claims" element={<Claims />} />
                <Route path="accounting/receivables/claims" element={<Claims />} />
                <Route path="accounting/payables/claims" element={<Claims />} />
                <Route path="accounting/receivables/sos" element={<ReceivableSOs />} />
                <Route path="accounting/receivables/invoices" element={<Invoices />} />
                <Route path="accounting/payables" element={<Payables />} />
                <Route path="accounting/payables/pos" element={<PayablePOs />} />
                
                {/* Other Pages */}
                <Route path="cold-storage" element={<ColdStorage />} />
                <Route path="carriers" element={<Carriers />} />
                <Route path="contacts" element={<Contacts />} />
                <Route path="ai-assistant" element={<AIAssistant />} />
                <Route path="cockpit" element={<Cockpit />} />
                <Route path="cockpit/call-log" element={<CallLog />} />
                <Route path="processes" element={<Processes />} />
                <Route path="reports" element={<Reports />} />
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
