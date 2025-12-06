# Swalook CRM Backend Overview

## Project Description
Swalook CRM is a comprehensive backend API built with Django and Django REST Framework for managing salon/beauty business operations. The system provides a complete CRM solution for salons including customer management, billing, appointments, staff management, inventory tracking, and business analytics.

## Technology Stack
- **Framework**: Django 4.1.3
- **API Framework**: Django REST Framework
- **Database**: MySQL
- **Authentication**: Token-based authentication
- **Deployment**: AWS (based on project name)
- **Additional Libraries**:
  - django-cors-headers (CORS support)
  - django-silk (profiling)
  - Pillow (image processing)
  - boto3/awscli (AWS integration)
  - xhtml2pdf (PDF generation)
  - openpyxl (Excel export)

## Core Features

### 1. User Management
- Vendor/Salon registration and authentication
- Staff login system
- Admin access
- Profile management with GST, PAN, and business details
- Multi-branch support

### 2. Service Management
- Service categories and individual services
- Pricing and duration management
- Gender-specific services (men/women)
- Combo services

### 3. Customer Management
- Customer profiles with contact details
- Loyalty points system
- Customer history and preferences
- Birthday and anniversary tracking

### 4. Billing & Invoicing
- Invoice generation with tax calculations
- Service and product billing
- PDF invoice generation
- Payment mode tracking
- Loyalty points redemption

### 5. Appointment System
- Appointment booking and management
- Staff assignment
- Daily/weekly appointment views
- Appointment analytics

### 6. Staff Management
- Staff profiles and roles
- Salary management with slabs and commissions
- Attendance tracking with geolocation
- Performance analytics
- Payslip generation

### 7. Inventory Management
- Product categories and inventory tracking
- Stock management
- Expiry date monitoring
- Product utilization tracking
- Inventory invoices

### 8. Expense Management
- Expense categories and tracking
- Purchase management
- Vendor expense tracking
- Financial analytics

### 9. Loyalty Program
- Points-based loyalty system
- Membership types
- Coupons and discounts
- Customer loyalty ledger

### 10. Business Analytics
- Sales analysis (daily, weekly, monthly, yearly)
- Customer analytics
- Staff performance metrics
- Product/service analysis
- Revenue summaries

### 11. Social Media Integration
- Instagram/Facebook integration
- Image upload and sharing
- Token management

## Database Models

### Core Entities
- **SwalookUserProfile**: Salon/vendor profiles
- **SalonBranch**: Multi-branch support
- **VendorCustomers**: Customer database
- **VendorService**: Service catalog
- **VendorInvoice**: Billing records
- **VendorAppointment**: Appointment scheduling
- **VendorStaff**: Staff management
- **VendorInventoryProduct**: Product inventory
- **VendorExpense**: Expense tracking

### Supporting Models
- Loyalty points, coupons, categories
- Staff attendance and salary
- Business analysis data
- Social media integrations

## API Endpoints

The API provides RESTful endpoints for all features:

### Authentication
- `/api/swalook/create_account/` - Vendor registration
- `/api/swalook/centralized/login/` - Unified login
- `/api/swalook/login/` - Vendor login
- `/api/swalook/staff/login/` - Staff login
- `/api/swalook/admin/login/` - Admin login

### Core Operations
- Services: CRUD operations for services and categories
- Customers: Customer management and loyalty
- Billing: Invoice creation, PDF generation, analytics
- Appointments: Booking, editing, analytics
- Staff: Management, attendance, salary
- Inventory: Product management, utilization
- Expenses: Tracking and categorization
- Analytics: Various business intelligence endpoints

## Security & Configuration
- Token-based authentication
- CORS enabled for frontend integration
- File-based caching
- Email notifications
- Error logging and admin alerts
- SSL/TLS support (configurable)

## Deployment
- Hosted on AWS
- MySQL RDS database
- Static/media file serving
- Gunicorn WSGI server
- Environment-based configuration

## Development Notes
- Uses Django's built-in admin interface
- Silk profiling for performance monitoring
- Comprehensive error handling
- Transactional operations for data integrity
- Image processing capabilities
- Excel export functionality

This backend serves as the core engine for the Swalook CRM mobile and web applications, providing a robust API for salon business management.

---

# Inventory Analytics - Deployment & Frontend Integration

## Part 1: Deployment Steps

### 1. Pull & Apply Migrations
```bash
cd /path/to/aws_swalook
git pull origin main

# Create and apply migrations
python manage.py makemigrations _api_
python manage.py migrate

# Restart server
sudo supervisorctl restart swalook  # or: sudo systemctl restart gunicorn
```

### 2. Verify Deployment
```bash
curl -H "Authorization: Token <TOKEN>" \
  "https://api.swalook.com/api/swalook/analytics/inventory/summary/?branch_name=<BRANCH_ID>"
```

---

## Part 2: Frontend Integration

### API Endpoints & Contracts

#### 1. Summary Widget
**GET** `/api/swalook/analytics/inventory/summary/?branch_name={branchId}`
```typescript
interface InventorySummary {
  status: boolean;
  data: {
    total_skus: number;
    inventory_value: number;
    low_stock_count: number;
    out_of_stock_count: number;
    inventory_turnover: number;
  }
}
```

#### 2. Stock Health Card
**GET** `/api/swalook/analytics/inventory/stock-health/?branch_name={branchId}&days=30`
```typescript
interface StockHealth {
  status: boolean;
  data: {
    summary: {
      healthy_count: number;
      healthy_percent: number;
      low_count: number;
      low_percent: number;
      out_count: number;
      out_percent: number;
      avg_days_of_stock: number;
    };
    low_stock_items: Array<{
      id: string;
      product_id: string;
      product_name: string;
      stocks_in_hand: number;
      days_of_stock: number | "Out" | "-";
      reorder_threshold: number;
      category: string | null;
    }>;
  }
}
```

#### 3. Inventory Value (ABC Segmentation)
**GET** `/api/swalook/analytics/inventory/value/?branch_name={branchId}`
```typescript
interface InventoryValue {
  status: boolean;
  data: {
    total_value: number;
    avg_cost_per_sku: number;
    abc_segmentation: {
      A: { percent: number; value: number; sku_count: number };
      B: { percent: number; value: number; sku_count: number };
      C: { percent: number; value: number; sku_count: number };
    };
    top_value_skus: Array<{
      id: string;
      product_name: string;
      value: number;
      stocks_in_hand: number;
    }>;
  }
}
```

#### 4. Inventory Items Table
**GET** `/api/swalook/inventory/items/?branch_name={branchId}&page=1&page_size=20`

| Param | Type | Example |
|-------|------|---------|
| search | string | "Shampoo" |
| category | uuid | category ID |
| stock_status | enum | "healthy", "low", "out" |
| sort_by | string | "-stocks_in_hand", "product_name" |
| page | int | 1 |
| page_size | int | 20 |

```typescript
interface InventoryItems {
  status: boolean;
  data: {
    count: number;
    page: number;
    page_size: number;
    next: string | null;
    previous: string | null;
    results: Array<{
      id: string;
      product_id: string;
      product_name: string;
      category_details: { id: string; product_category: string } | null;
      stocks_in_hand: number;
      cost_price: number | null;
      product_price: number;
      value: number;
      days_of_stock: number | "Out" | "-";
      reorder_threshold: number;
      unit: string;
      supplier: string;
      last_purchase_date: string | null;
      expiry_date: string;
    }>;
  }
}
```

#### 5. Item History (Drawer)
**GET** `/api/swalook/inventory/items/{id}/history/?branch_name={branchId}`
```typescript
interface ItemHistory {
  status: boolean;
  data: {
    product: { id: string; product_id: string; product_name: string; stocks_in_hand: number };
    purchases: Array<{ id: string; supplier: string; quantity: number; cost: number; date: string }>;
    utilizations: Array<{ id: string; staff: string; product_quantity: number; created_at: string }>;
    adjustments: Array<{ id: string; adjustment_quantity: number; adjustment_type: string; notes: string | null; date: string }>;
  }
}
```

#### 6. Shrinkage Log Widget
**GET** `/api/swalook/inventory/adjustments/?branch_name={branchId}&limit=10`
```typescript
interface Adjustments {
  status: boolean;
  data: Array<{
    id: string;
    product: string;
    product_name: string;
    product_id_code: string;
    adjustment_quantity: number;  // negative = reduction
    adjustment_type: "Damaged" | "Expired" | "Lost" | "Correction" | "Other";
    notes: string | null;
    date: string;
    created_at: string;
  }>;
}
```

**POST** `/api/swalook/inventory/adjustments/?branch_name={branchId}`
```json
{
  "product": "uuid-of-product",
  "adjustment_quantity": -2,
  "adjustment_type": "Damaged",
  "notes": "Dropped during handling",
  "date": "2025-12-05"
}
```

#### 7. Top Suppliers Widget
**GET** `/api/swalook/analytics/inventory/suppliers/?branch_name={branchId}&limit=5`
```typescript
interface TopSuppliers {
  status: boolean;
  data: Array<{ name: string; total_value: number }>;
}
```

---

## Frontend Implementation Checklist

- [ ] Create API service functions for each endpoint
- [ ] Implement Summary Widget (4 KPI cards)
- [ ] Implement Stock Health donut chart + low-stock list
- [ ] Implement ABC segmentation chart + top SKUs
- [ ] Implement Inventory Table with filters/sort/pagination
- [ ] Implement Item Detail Drawer with history tabs
- [ ] Implement Shrinkage Log list
- [ ] Implement Stock Adjustment modal (POST)
- [ ] Implement Top Suppliers widget
- [ ] Add "Reorder" button that links to Purchase Order creation