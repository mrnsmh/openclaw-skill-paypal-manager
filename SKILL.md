---
name: paypal-manager
description: Manage PayPal payments — create payment links, check order status, capture payments, and list recent transactions via PayPal REST API.
license: MIT
metadata:
  version: 1.0.0
  author: Jack2
  tags: paypal, payments, ecommerce, finance
---

# PayPal Manager Skill

Manage PayPal payments directly from OpenClaw using the PayPal REST API. No SDK required — pure Python with urllib.

## Capabilities

1. **Create payment orders** — Generate a PayPal checkout URL to send to customers
2. **Check order status** — Verify if a payment has been approved or completed
3. **Capture payments** — Finalize an approved order and receive the funds
4. **List transactions** — View recent PayPal transactions for reporting

## Setup

Set environment variables (or they fall back to hardcoded defaults for Marouane's live account):

```bash
export PAYPAL_CLIENT_ID="your_client_id"
export PAYPAL_SECRET="your_secret"
export PAYPAL_MODE="live"  # or "sandbox"
```

## Usage

### Create a Payment Link
```bash
python3 scripts/paypal.py create --amount 49.99 --currency USD --description "ProspectX Plan"
```
Output: Order ID + PayPal checkout URL to share with the customer.

### Check Order Status
```bash
python3 scripts/paypal.py status ORDER_ID
```

### Capture an Approved Payment
```bash
python3 scripts/paypal.py capture ORDER_ID
```
Use after the customer approves the payment on PayPal.

### List Recent Transactions
```bash
python3 scripts/paypal.py transactions --days 30
```
Lists all transactions from the last N days.

## How to Use from OpenClaw

Ask the agent:
- "Create a PayPal payment link for €99 for ProspectX Pro"
- "Check PayPal order status for ORDER_ID"
- "Capture the PayPal payment ORDER_ID"
- "List my PayPal transactions from the last 7 days"

The agent will run `scripts/paypal.py` with the appropriate arguments.

## Files

| File | Description |
|------|-------------|
| `scripts/paypal.py` | Main CLI script |
| `references/paypal-api.md` | PayPal REST API quick reference |
