#!/usr/bin/env python3
"""
PayPal Manager - OpenClaw Skill
Manage PayPal payments: create orders, check status, capture, list transactions.
Usage:
  python3 paypal.py create --amount 49.99 --currency USD --description "ProspectX Plan"
  python3 paypal.py status ORDER_ID
  python3 paypal.py capture ORDER_ID
  python3 paypal.py transactions --days 30
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error
import base64
from datetime import datetime, timedelta, timezone

# Config
CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID", "AaKtH5cYT_4hxGQJYWDfTQauHe8Xm_T2K-M-ww5gWmUv2j7FxAqbJ_rx4KP-2hSgc0QFIwRESWqgnQpo")
SECRET = os.environ.get("PAYPAL_SECRET", "EE8rPmoJlVvSSV_TnrW0Nam8cPOGqudkUCiVPBQ2hmF2S0Th8wrRztuKBD9WKuhLJza4_KurcxwkP-EK")
MODE = os.environ.get("PAYPAL_MODE", "live")

BASE_URL = "https://api-m.paypal.com" if MODE == "live" else "https://api-m.sandbox.paypal.com"


def get_access_token():
    url = f"{BASE_URL}/v1/oauth2/token"
    credentials = base64.b64encode(f"{CLIENT_ID}:{SECRET}".encode()).decode()
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]


def api_request(method, path, payload=None, token=None):
    if token is None:
        token = get_access_token()
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[ERROR] HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def create_order(amount, currency, description, return_url=None, cancel_url=None):
    token = get_access_token()
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": currency,
                "value": str(amount)
            },
            "description": description
        }],
        "application_context": {
            "return_url": return_url or "https://prospectx.aiflowhub.online/payment/success",
            "cancel_url": cancel_url or "https://prospectx.aiflowhub.online/payment/cancel",
            "brand_name": "ProspectX",
            "user_action": "PAY_NOW"
        }
    }
    result = api_request("POST", "/v2/checkout/orders", payload, token)
    order_id = result.get("id")
    approve_link = next((l["href"] for l in result.get("links", []) if l["rel"] == "approve"), None)
    print(f"✅ Order created!")
    print(f"   Order ID : {order_id}")
    print(f"   Status   : {result.get('status')}")
    print(f"   Pay URL  : {approve_link}")
    return result


def get_order_status(order_id):
    token = get_access_token()
    result = api_request("GET", f"/v2/checkout/orders/{order_id}", token=token)
    print(f"📦 Order: {order_id}")
    print(f"   Status : {result.get('status')}")
    units = result.get("purchase_units", [])
    for u in units:
        amt = u.get("amount", {})
        print(f"   Amount : {amt.get('value')} {amt.get('currency_code')}")
        print(f"   Desc   : {u.get('description', '-')}")
    return result


def capture_order(order_id):
    token = get_access_token()
    result = api_request("POST", f"/v2/checkout/orders/{order_id}/capture", {}, token)
    status = result.get("status")
    print(f"💰 Capture result: {status}")
    for unit in result.get("purchase_units", []):
        for cap in unit.get("payments", {}).get("captures", []):
            print(f"   Capture ID : {cap.get('id')}")
            print(f"   Amount     : {cap.get('amount', {}).get('value')} {cap.get('amount', {}).get('currency_code')}")
            print(f"   Status     : {cap.get('status')}")
    return result


def list_transactions(days=30):
    token = get_access_token()
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    params = urllib.parse.urlencode({
        "start_date": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_date": end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fields": "all",
        "page_size": 100,
        "page": 1
    })
    result = api_request("GET", f"/v1/reporting/transactions?{params}", token=token)
    txns = result.get("transaction_details", [])
    print(f"📋 Transactions (last {days} days): {len(txns)} found")
    for t in txns:
        info = t.get("transaction_info", {})
        amt = info.get("transaction_amount", {})
        print(f"   [{info.get('transaction_initiation_date', '')[:10]}] "
              f"{info.get('transaction_id')} | "
              f"{info.get('transaction_status')} | "
              f"{amt.get('value')} {amt.get('currency_code')} | "
              f"{info.get('transaction_subject', '-')}")
    return result


def main():
    parser = argparse.ArgumentParser(description="PayPal Manager CLI")
    subparsers = parser.add_subparsers(dest="command")

    # create
    p_create = subparsers.add_parser("create", help="Create a payment order")
    p_create.add_argument("--amount", required=True, type=float)
    p_create.add_argument("--currency", default="USD")
    p_create.add_argument("--description", default="Payment")
    p_create.add_argument("--return-url")
    p_create.add_argument("--cancel-url")

    # status
    p_status = subparsers.add_parser("status", help="Check order status")
    p_status.add_argument("order_id")

    # capture
    p_capture = subparsers.add_parser("capture", help="Capture an approved order")
    p_capture.add_argument("order_id")

    # transactions
    p_txns = subparsers.add_parser("transactions", help="List recent transactions")
    p_txns.add_argument("--days", type=int, default=30)

    args = parser.parse_args()

    if args.command == "create":
        create_order(args.amount, args.currency, args.description, args.return_url, args.cancel_url)
    elif args.command == "status":
        get_order_status(args.order_id)
    elif args.command == "capture":
        capture_order(args.order_id)
    elif args.command == "transactions":
        list_transactions(args.days)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
