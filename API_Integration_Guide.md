# Swalook API Integration Guide: Service-Based Inventory Consumption

## Overview

This guide provides the necessary API details to integrate the service-based inventory consumption feature.

---

## 1. Create Consumption Rules

**Endpoint**: `POST /api/swalook/inventory/service-usage/`
**Query Param**: `?branch_name={{branch_id}}`
**Description**: Link a service to a product for partial consumption.

**Headers**:

- `Authorization`: `Token {{auth_token}}`
- `Content-Type`: `application/json`

**Payload**:

```json
{
  "service": "SERVICE_UUID", // UUID of the service
  "product": "PRODUCT_UUID", // UUID of the inventory product
  "usage_amount": 25, // Amount consumed per service
  "product_total_capacity": 100 // Total capacity of the product unit
}
```

---

## 2. Create Invoice (Trigger Consumption)

**Endpoint**: `POST /api/swalook/billing/`
**Query Param**: `?branch_name={{branch_id}}`
**Description**: Create an invoice. **Critically**, this acts as the trigger for inventory consumption.

**Headers**:

- `Authorization`: `Token {{auth_token}}`
- `Content-Type`: `application/json`

### ⚠️ Critical Requirement

The `json_data` array **MUST** contain the `id` of the service. This ID is used to look up the consumption rules created in Step 1.

**Payload**:

```json
{
  "customer_name": "Jane Doe",
  "mobile_no": "9988776655",
  "services": "Hair Spa",

  // CRITICAL: json_data must include Service UUIDs
  "json_data": [
    {
      "id": "SERVICE_UUID_HERE", // <--- REQUIRED: Actual Service UUID
      "Description": "Hair Spa",
      "quantity": "1",
      "Rate": "800",
      "Amount": "800"
    }
  ],

  "hair_length": "medium",
  "total_prise": "800",
  "grand_total": "800",
  "mode_of_payment": "Cash",
  "new_mode": [{ "mode": "Cash", "amount": "800" }],
  "date": "2026-02-05",
  "slno": "INV-TEST-001"
}
```

---

## 3. Verification

To verify the integration is working:

1. Create consumption rules for a service (e.g., Hair Spa -> Spa Cream).
2. Create an invoice using that service with the payload structure above.
3. Check the backend logs or `_api_productconsumptiontracker` table.

**Success Logs**:

- `[CONSUMPTION] Found service in json_data: Hair Spa (ID: ...)`
- `[TRACKER] Processing: Spa Cream`
