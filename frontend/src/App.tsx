/**
 * Main App Component
 * 
 * ProjectMeats3 React Application
 * Full Business Management System with AI Assistant
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
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
import ApiTestComponent from './components/ApiTestComponent';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
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
          <Route path="api-test" element={<ApiTestComponent />} />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;