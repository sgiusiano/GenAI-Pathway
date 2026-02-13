from langchain_core.tools import tool


@tool
def search_knowledge_base(query: str) -> str:
    """Search the support knowledge base for solutions and articles.

    Args:
        query: Search query describing the issue or question

    Returns:
        Relevant help articles and troubleshooting steps
    """
    kb_articles = {
        "reset password": """Article KB-101: Password Reset
1. Go to login page and click "Forgot Password"
2. Enter your email address
3. Check email for reset link (valid 1 hour)
4. Create new password (min 8 chars, 1 number, 1 special char)
5. Log in with new credentials""",

        "shipping delay": """Article KB-203: Shipping Delays
Common causes:
- Weather events affecting carrier operations
- Address validation issues
- Customs processing (international orders)
Solution: Check order status tool for real-time updates. Orders delayed >5 days qualify for shipping refund.""",

        "product not working": """Article KB-305: Product Troubleshooting
First steps:
1. Check power source and connections
2. Restart device completely
3. Update firmware/software to latest version
4. Check compatibility with your system
5. Review user manual troubleshooting section
If issue persists: Contact support for warranty claim""",

        "return policy": """Article KB-107: Return & Refund Policy
- 30-day return window from delivery date
- Product must be unused in original packaging
- Refund processed within 5-7 business days
- Return shipping: FREE for defective items, $10 fee for buyer's remorse
- Exchanges processed faster than refunds""",

        "account locked": """Article KB-112: Account Security Lockout
Accounts lock after 5 failed login attempts (security measure).
Unlock methods:
1. Wait 30 minutes for auto-unlock
2. Use "Forgot Password" to reset immediately
3. Contact support with ID verification for instant unlock""",
    }

    query_lower = query.lower()
    for keyword, article in kb_articles.items():
        if keyword in query_lower or any(word in query_lower for word in keyword.split()):
            return f"Found relevant article:\n\n{article}"

    return "No exact match found. Recommended: Contact support for personalized assistance."


@tool
def check_order_status(order_id: str) -> str:
    """Check the current status and tracking information for an order.

    Args:
        order_id: Order ID number (e.g., "ORD-12345")

    Returns:
        Order status, tracking number, and estimated delivery
    """
    orders = {
        "ORD-12345": {
            "status": "In Transit",
            "tracking": "1Z999AA10123456784",
            "carrier": "UPS",
            "shipped": "2025-09-28",
            "estimated_delivery": "2025-10-04",
            "items": "Premium Business Laptop (LPT-001)",
        },
        "ORD-12346": {
            "status": "Delivered",
            "tracking": "1Z999AA10123456785",
            "carrier": "UPS",
            "shipped": "2025-09-25",
            "estimated_delivery": "2025-09-30",
            "items": "Wireless Headphones (HPH-205)",
        },
        "ORD-12347": {
            "status": "Processing",
            "tracking": "Not yet assigned",
            "carrier": "TBD",
            "shipped": "Not shipped",
            "estimated_delivery": "2025-10-06",
            "items": "4K Monitor (MON-227)",
        },
        "ORD-12348": {
            "status": "Delayed",
            "tracking": "1Z999AA10123456786",
            "carrier": "FedEx",
            "shipped": "2025-09-26",
            "estimated_delivery": "2025-10-05 (Originally 2025-10-02)",
            "items": "Mechanical Keyboard (KBD-310)",
        },
    }

    order_upper = order_id.upper()
    if order_upper not in orders:
        return f"Order {order_id} not found. Please verify order number."

    order = orders[order_upper]
    return f"""Order Status: {order['status']}
Order ID: {order_upper}
Items: {order['items']}
Carrier: {order['carrier']}
Tracking: {order['tracking']}
Shipped: {order['shipped']}
Estimated Delivery: {order['estimated_delivery']}"""


@tool
def process_refund(order_id: str, reason: str, amount: float) -> str:
    """Process a refund request (requires human approval).

    Args:
        order_id: Order ID to refund
        reason: Reason for refund (defective, wrong item, buyer's remorse, etc.)
        amount: Refund amount in dollars

    Returns:
        Refund processing status
    """
    return f"""REFUND REQUEST (Pending Approval):
Order ID: {order_id}
Reason: {reason}
Amount: ${amount:.2f}
Status: Awaiting manager approval
Action: Human approval required before processing
Processing time: 5-7 business days after approval"""


@tool
def escalate_ticket(ticket_id: str, customer_id: str, issue_summary: str, priority: str = "normal") -> str:
    """Escalate a support ticket to a human agent.

    Args:
        ticket_id: Support ticket ID
        customer_id: Customer account ID
        issue_summary: Brief description of the issue
        priority: Priority level (low, normal, high, urgent)

    Returns:
        Escalation confirmation
    """
    priority_eta = {
        "low": "24-48 hours",
        "normal": "12-24 hours",
        "high": "4-8 hours",
        "urgent": "1-2 hours",
    }

    eta = priority_eta.get(priority.lower(), "12-24 hours")

    return f"""Ticket Escalated Successfully:
Ticket ID: {ticket_id}
Customer: {customer_id}
Issue: {issue_summary}
Priority: {priority.upper()}
Assigned to: Human Support Team
Expected Response: {eta}
Status: Agent will contact you via email"""


@tool
def update_account_settings(customer_id: str, setting: str, new_value: str) -> str:
    """Update customer account settings or preferences.

    Args:
        customer_id: Customer account ID
        setting: Setting to update (email, phone, address, newsletter, notifications)
        new_value: New value for the setting

    Returns:
        Update confirmation
    """
    valid_settings = ["email", "phone", "address", "newsletter", "notifications"]

    if setting.lower() not in valid_settings:
        return f"Invalid setting: {setting}. Valid options: {', '.join(valid_settings)}"

    return f"""Account Setting Updated:
Customer ID: {customer_id}
Setting: {setting}
New Value: {new_value}
Status: Updated successfully
Note: Changes take effect immediately"""


@tool
def check_warranty(product_sku: str, purchase_date: str) -> str:
    """Verify warranty coverage for a product.

    Args:
        product_sku: Product SKU code
        purchase_date: Purchase date (YYYY-MM-DD format)

    Returns:
        Warranty status and coverage details
    """
    from datetime import datetime, timedelta

    warranties = {
        "LPT-001": {"period": 36, "type": "Comprehensive"},
        "HPH-205": {"period": 24, "type": "Limited Hardware"},
        "MSE-104": {"period": 12, "type": "Limited Hardware"},
        "KBD-310": {"period": 24, "type": "Limited Hardware"},
        "MON-227": {"period": 36, "type": "Comprehensive"},
    }

    sku_upper = product_sku.upper()
    if sku_upper not in warranties:
        return f"Product {product_sku} not found in warranty database."

    warranty = warranties[sku_upper]
    try:
        purchase = datetime.strptime(purchase_date, "%Y-%m-%d")
        expiration = purchase + timedelta(days=warranty["period"] * 30)
        today = datetime.now()

        remaining_days = (expiration - today).days

        if remaining_days > 0:
            status = "✓ ACTIVE"
            remaining_months = remaining_days // 30
            return f"""Warranty Status: {status}
Product: {sku_upper}
Type: {warranty['type']}
Period: {warranty['period']} months
Purchase Date: {purchase_date}
Expiration: {expiration.strftime('%Y-%m-%d')}
Remaining: {remaining_months} months ({remaining_days} days)"""
        else:
            status = "✗ EXPIRED"
            expired_days = abs(remaining_days)
            return f"""Warranty Status: {status}
Product: {sku_upper}
Expired: {expired_days} days ago
Options: Extended warranty available for purchase"""

    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD (e.g., 2025-01-15)"


@tool
def get_troubleshooting_steps(product_category: str, issue: str) -> str:
    """Retrieve detailed troubleshooting procedures for common issues.

    Args:
        product_category: Product category (laptop, headphones, monitor, etc.)
        issue: Specific issue description

    Returns:
        Step-by-step troubleshooting guide
    """
    troubleshooting = {
        ("laptop", "won't turn on"): """Laptop Won't Power On - Troubleshooting:
1. Connect power adapter and verify LED indicator lights up
2. Remove battery and hold power button 30 seconds (power drain)
3. Reinsert battery and try powering on
4. Try power adapter in different outlet
5. Check for physical damage to power port
6. If still not working: Contact support for hardware diagnosis""",

        ("headphones", "no sound"): """Headphones No Audio - Troubleshooting:
1. Ensure headphones are fully charged (check LED status)
2. Verify Bluetooth connection (disconnect and re-pair)
3. Check volume on both device and headphones
4. Test with different audio source (different phone/computer)
5. Reset headphones: Hold power + volume down for 10 seconds
6. Update device Bluetooth drivers
7. If issue persists: May be hardware failure, contact support""",

        ("monitor", "no display"): """Monitor No Display - Troubleshooting:
1. Check power cable connection and power indicator LED
2. Verify video cable (HDMI/DP) is securely connected both ends
3. Try different video cable if available
4. Test different video input port on monitor
5. Check computer is outputting signal (test with different monitor)
6. Press monitor input/source button to cycle inputs
7. Reset monitor: Unplug power for 60 seconds, reconnect""",
    }

    category_lower = product_category.lower()
    issue_lower = issue.lower()

    for (cat, prob), steps in troubleshooting.items():
        if cat in category_lower and prob in issue_lower:
            return steps

    return f"""General troubleshooting for {product_category}:
1. Restart the device completely
2. Check all cable connections
3. Update firmware/drivers to latest version
4. Review product manual for specific guidance
5. Contact support if issue continues

For detailed help, search knowledge base or escalate to support agent."""


# Export all tools
POST_SALES_TOOLS = [
    search_knowledge_base,
    check_order_status,
    process_refund,  # Side-effect tool
    escalate_ticket,
    update_account_settings,
    check_warranty,
    get_troubleshooting_steps,
]
