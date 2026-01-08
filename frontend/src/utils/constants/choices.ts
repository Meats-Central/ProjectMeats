/**
 * Backend Choices Constants
 * 
 * These constants MUST match the TextChoices classes in backend/apps/core/models.py
 * Any changes to backend choices require updates here.
 * 
 * Phase 4: Frontend Integration & UX Alignment
 */

import { MultiSelectOption } from '../../components/Shared';

// Supplier Department Choices
// Backend: CarrierDepartmentChoices (also used for Supplier)
export const DEPARTMENT_CHOICES: MultiSelectOption[] = [
  { value: 'Sales', label: 'Sales' },
  { value: 'Purchasing', label: 'Purchasing' },
  { value: 'Logistics', label: 'Logistics' },
  { value: "Doc's BOL", label: "Doc's BOL" },
  { value: "Doc's COA", label: "Doc's COA" },
];

// Customer Industry Choices
// Backend: IndustryChoices
export const INDUSTRY_CHOICES: MultiSelectOption[] = [
  { value: 'Restaurant', label: 'Restaurant' },
  { value: 'Food Service', label: 'Food Service' },
  { value: 'Retail', label: 'Retail' },
  { value: 'Wholesale', label: 'Wholesale' },
  { value: 'Export', label: 'Export' },
  { value: 'Processing', label: 'Processing' },
  { value: 'Distribution', label: 'Distribution' },
];

// Protein Type Choices
// Backend: ProteinTypeChoices (expanded to 9 options in invoices/models.py)
export const PROTEIN_TYPE_CHOICES: MultiSelectOption[] = [
  { value: 'Beef', label: 'Beef' },
  { value: 'Pork', label: 'Pork' },
  { value: 'Chicken', label: 'Chicken' },
  { value: 'Turkey', label: 'Turkey' },
  { value: 'Lamb', label: 'Lamb' },
  { value: 'Fish', label: 'Fish' },
  { value: 'Seafood', label: 'Seafood' },
  { value: 'Veal', label: 'Veal' },
  { value: 'Bison', label: 'Bison' },
];

// Carrier Release Format Choices
// Backend: CarrierReleaseFormatChoices
export const CARRIER_RELEASE_FORMAT_CHOICES: MultiSelectOption[] = [
  { value: 'Email', label: 'Email' },
  { value: 'Fax', label: 'Fax' },
  { value: 'Phone', label: 'Phone' },
  { value: 'Portal', label: 'Portal' },
];

// Certificate Type Choices (for reference)
// Backend: CertificateTypeChoices
export const CERTIFICATE_TYPE_CHOICES: MultiSelectOption[] = [
  { value: 'USDA', label: 'USDA' },
  { value: 'FDA', label: 'FDA' },
  { value: 'Organic', label: 'Organic' },
  { value: 'Halal', label: 'Halal' },
  { value: 'Kosher', label: 'Kosher' },
  { value: 'Non-GMO', label: 'Non-GMO' },
  { value: 'Gluten-Free', label: 'Gluten-Free' },
  { value: 'Grass-Fed', label: 'Grass-Fed' },
];

// Shipping Offered Choices (for reference)
// Backend: ShippingOfferedChoices
export const SHIPPING_OFFERED_CHOICES: MultiSelectOption[] = [
  { value: 'Ground', label: 'Ground' },
  { value: 'Air', label: 'Air' },
  { value: 'Ocean', label: 'Ocean' },
  { value: 'Rail', label: 'Rail' },
  { value: 'Refrigerated', label: 'Refrigerated' },
  { value: 'Frozen', label: 'Frozen' },
  { value: 'Express', label: 'Express' },
];

// Payment Terms Choices (for reference)
// Backend: AccountingPaymentTermsChoices
export const PAYMENT_TERMS_CHOICES: MultiSelectOption[] = [
  { value: 'Net 30', label: 'Net 30' },
  { value: 'Net 60', label: 'Net 60' },
  { value: 'Net 90', label: 'Net 90' },
  { value: 'Due on Receipt', label: 'Due on Receipt' },
  { value: 'COD', label: 'COD (Cash on Delivery)' },
  { value: '2/10 Net 30', label: '2/10 Net 30 (2% discount if paid within 10 days)' },
];
