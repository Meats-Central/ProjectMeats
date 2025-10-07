import React, { useState, useEffect } from 'react';
import { apiService, Supplier } from '../services/apiService';

const ApiTestComponent: React.FC = () => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const testCreateSupplier = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const newSupplier = {
        name: `Test Supplier ${new Date().getTime()}`,
        contact_person: 'Test Person',
        email: 'test@example.com',
        phone: '555-0123',
        address: '123 Test St',
        city: 'Test City',
        state: 'TS',
        zip_code: '12345',
      };

      const result = await apiService.createSupplier(newSupplier);

      setSuccess(`✅ Successfully created supplier: ${result.name} (ID: ${result.id})`);
      fetchSuppliers(); // Refresh the list
    } catch (err) {
      console.error('Error creating supplier:', err);
      setError(`❌ Error creating supplier: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchSuppliers = async () => {
    try {
      const supplierData = await apiService.getSuppliers();
      setSuppliers(supplierData);
    } catch (err) {
      console.error('Error fetching suppliers:', err);
      setError(`❌ Error fetching suppliers: ${err}`);
    }
  };

  useEffect(() => {
    fetchSuppliers();
  }, []);

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h2>🧪 API Test Component</h2>
      <div style={{ marginBottom: '20px' }}>
        <button
          onClick={testCreateSupplier}
          disabled={loading}
          style={{
            backgroundColor: '#007bff',
            color: 'white',
            padding: '10px 20px',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1,
          }}
        >
          {loading ? '⏳ Creating...' : '✨ Test Create Supplier'}
        </button>
      </div>

      {error && (
        <div
          style={{
            backgroundColor: '#f8d7da',
            color: '#721c24',
            padding: '10px',
            borderRadius: '4px',
            marginBottom: '10px',
          }}
        >
          {error}
        </div>
      )}

      {success && (
        <div
          style={{
            backgroundColor: '#d1edff',
            color: '#155724',
            padding: '10px',
            borderRadius: '4px',
            marginBottom: '10px',
          }}
        >
          {success}
        </div>
      )}

      <h3>📋 Current Suppliers ({suppliers.length})</h3>
      <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
        {suppliers.map((supplier) => (
          <div
            key={supplier.id}
            style={{
              border: '1px solid #dee2e6',
              padding: '10px',
              marginBottom: '5px',
              borderRadius: '4px',
              backgroundColor: '#f8f9fa',
            }}
          >
            <strong>
              #{supplier.id} - {supplier.name}
            </strong>
            <br />
            Contact: {supplier.contact_person}
            <br />
            Email: {supplier.email}
            <br />
            Phone: {supplier.phone}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ApiTestComponent;
