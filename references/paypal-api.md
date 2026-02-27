# PayPal REST API Reference

## Authentication
- **Endpoint**: `POST /v1/oauth2/token`
- **Method**: Basic Auth (Client ID : Secret → base64)
- **Body**: `grant_type=client_credentials`
- **Response**: `{ "access_token": "...", "expires_in": 32400 }`

## Base URLs
| Mode    | URL                            |
|---------|-------------------------------|
| Live    | https://api-m.paypal.com       |
| Sandbox | https://api-m.sandbox.paypal.com |

## Orders API (v2)

### Create Order
```
POST /v2/checkout/orders
Authorization: Bearer {token}
Content-Type: application/json

{
  "intent": "CAPTURE",
  "purchase_units": [{ "amount": { "currency_code": "USD", "value": "49.99" } }],
  "application_context": { "return_url": "...", "cancel_url": "..." }
}
```
Returns: `{ "id": "ORDER_ID", "status": "CREATED", "links": [{ "rel": "approve", "href": "https://www.paypal.com/checkoutnow?token=..." }] }`

### Get Order
```
GET /v2/checkout/orders/{order_id}
Authorization: Bearer {token}
```

### Capture Order
```
POST /v2/checkout/orders/{order_id}/capture
Authorization: Bearer {token}
Content-Type: application/json
Body: {}
```

## Transactions Reporting API (v1)

### List Transactions
```
GET /v1/reporting/transactions?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z&fields=all&page_size=100
Authorization: Bearer {token}
```

## Order Statuses
- `CREATED` — Order created, not yet approved
- `SAVED` — Order saved
- `APPROVED` — Buyer approved (ready to capture)
- `VOIDED` — Order voided
- `COMPLETED` — Payment captured successfully

## Environment Variables
| Variable          | Description             |
|-------------------|------------------------|
| PAYPAL_CLIENT_ID  | Your PayPal App Client ID |
| PAYPAL_SECRET     | Your PayPal App Secret  |
| PAYPAL_MODE       | `live` or `sandbox`     |
