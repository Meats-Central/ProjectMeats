import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  Alert,
  RefreshControl
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { ApiService } from '../services/ApiService';
import { RootStackParamList, User, UserTenant, Tenant } from '../types';

type TenantsScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Tenants'>;

interface Props {
  navigation: TenantsScreenNavigationProp;
  user: User;
  onTenantSelect: (tenant: Tenant) => void;
  onLogout: () => void;
}

interface TenantItemProps {
  tenant: UserTenant;
  onPress: () => void;
}

const TenantItem: React.FC<TenantItemProps> = ({ tenant, onPress }) => (
  <TouchableOpacity style={styles.tenantItem} onPress={onPress}>
    <View style={styles.tenantHeader}>
      <Text style={styles.tenantName}>{tenant.tenant_name}</Text>
      <View style={[styles.badge, tenant.is_trial ? styles.trialBadge : styles.paidBadge]}>
        <Text style={styles.badgeText}>
          {tenant.is_trial ? 'TRIAL' : 'PAID'}
        </Text>
      </View>
    </View>
    <Text style={styles.tenantRole}>Role: {tenant.role.toUpperCase()}</Text>
    <Text style={styles.tenantSlug}>@{tenant.tenant_slug}</Text>
  </TouchableOpacity>
);

export default function TenantsScreen({ navigation, user, onTenantSelect, onLogout }: Props) {
  const [tenants, setTenants] = useState<UserTenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadTenants();
  }, []);

  const loadTenants = async () => {
    try {
      const userTenants = await ApiService.getMyTenants();
      setTenants(userTenants);
    } catch (error: any) {
      console.error('Error loading tenants:', error);
      Alert.alert('Error', 'Failed to load tenants');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleTenantPress = async (userTenant: UserTenant) => {
    try {
      // Get full tenant details
      const tenant = await ApiService.getTenant(userTenant.tenant_id);
      onTenantSelect(tenant);
    } catch (error: any) {
      console.error('Error loading tenant details:', error);
      Alert.alert('Error', 'Failed to load tenant details');
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    loadTenants();
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Logout', style: 'destructive', onPress: onLogout },
      ]
    );
  };

  const renderTenant = ({ item }: { item: UserTenant }) => (
    <TenantItem 
      tenant={item} 
      onPress={() => handleTenantPress(item)} 
    />
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading tenants...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Select Organization</Text>
        <Text style={styles.welcomeText}>
          Welcome, {user.first_name || user.username}
        </Text>
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>
      </View>

      {tenants.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>No organizations found</Text>
          <Text style={styles.emptySubtext}>
            Contact your administrator to get access to an organization.
          </Text>
        </View>
      ) : (
        <FlatList
          data={tenants}
          keyExtractor={(item) => item.tenant_id}
          renderItem={renderTenant}
          contentContainerStyle={styles.list}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={handleRefresh}
            />
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    backgroundColor: '#fff',
    padding: 20,
    paddingTop: 50,
    borderBottomWidth: 1,
    borderBottomColor: '#e1e5e9',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 5,
  },
  welcomeText: {
    fontSize: 16,
    color: '#7f8c8d',
    marginBottom: 15,
  },
  logoutButton: {
    alignSelf: 'flex-end',
    backgroundColor: '#e74c3c',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 5,
  },
  logoutText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  list: {
    padding: 15,
  },
  tenantItem: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#e1e5e9',
  },
  tenantHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  tenantName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    flex: 1,
  },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10,
  },
  trialBadge: {
    backgroundColor: '#f39c12',
  },
  paidBadge: {
    backgroundColor: '#27ae60',
  },
  badgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  tenantRole: {
    fontSize: 14,
    color: '#3498db',
    marginBottom: 3,
  },
  tenantSlug: {
    fontSize: 12,
    color: '#95a5a6',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  emptyText: {
    fontSize: 18,
    color: '#7f8c8d',
    marginBottom: 10,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#95a5a6',
    textAlign: 'center',
  },
});