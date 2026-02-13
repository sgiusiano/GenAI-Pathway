from langchain_core.tools import tool


@tool
def search_product_catalog(query: str) -> str:
    """Search the product catalog for items matching the query.

    Args:
        query: Search terms for products (e.g., "laptop", "wireless headphones")

    Returns:
        Product information including names, features, and SKUs
    """
    # Mock product database
    products = {
        "laptop": "Premium Business Laptop - 16GB RAM, 512GB SSD, 14-inch display. SKU: LPT-001. Price: $1,299",
        "headphones": "Wireless Noise-Canceling Headphones - 30hr battery, Premium sound. SKU: HPH-205. Price: $299",
        "mouse": "Ergonomic Wireless Mouse - Rechargeable, 6 buttons. SKU: MSE-104. Price: $79",
        "keyboard": "Mechanical Keyboard - RGB lighting, Cherry MX switches. SKU: KBD-310. Price: $159",
        "monitor": "4K Ultra HD Monitor - 27-inch, HDR support. SKU: MON-227. Price: $549",
    }

    query_lower = query.lower()
    results = []
    for key, product in products.items():
        if key in query_lower or query_lower in key:
            results.append(product)

    if results:
        return "\n".join(results)
    return "No products found matching your query. Try different search terms."


@tool
def get_pricing(sku: str) -> str:
    """Get detailed pricing information for a specific product SKU.

    Args:
        sku: Product SKU code (e.g., "LPT-001")

    Returns:
        Pricing details including MSRP, current price, and any active promotions
    """
    pricing_db = {
        "LPT-001": "Premium Business Laptop | MSRP: $1,499 | Current: $1,299 | Promotion: 13% off until end of month",
        "HPH-205": "Wireless Headphones | MSRP: $349 | Current: $299 | Promotion: Holiday sale 14% off",
        "MSE-104": "Ergonomic Mouse | MSRP: $89 | Current: $79 | Promotion: 11% off",
        "KBD-310": "Mechanical Keyboard | MSRP: $179 | Current: $159 | Promotion: 11% off",
        "MON-227": "4K Monitor | MSRP: $549 | Current: $549 | No active promotions",
    }

    return pricing_db.get(sku.upper(), f"SKU {sku} not found in pricing database.")


@tool
def check_inventory(sku: str, quantity: int = 1) -> str:
    """Check stock availability for a product.

    Args:
        sku: Product SKU code
        quantity: Desired quantity (default: 1)

    Returns:
        Availability status and estimated ship date
    """
    # Mock inventory
    inventory = {
        "LPT-001": {"stock": 45, "warehouse": "East Coast"},
        "HPH-205": {"stock": 120, "warehouse": "West Coast"},
        "MSE-104": {"stock": 8, "warehouse": "Central"},
        "KBD-310": {"stock": 0, "warehouse": "East Coast"},
        "MON-227": {"stock": 33, "warehouse": "West Coast"},
    }

    sku_upper = sku.upper()
    if sku_upper not in inventory:
        return f"SKU {sku} not found."

    item = inventory[sku_upper]
    if item["stock"] >= quantity:
        return f"✓ IN STOCK: {item['stock']} units available at {item['warehouse']} warehouse. Ships within 2 business days."
    elif item["stock"] > 0:
        return f"LIMITED STOCK: Only {item['stock']} units available (you requested {quantity}). Ships within 2 business days."
    else:
        return f"OUT OF STOCK: Currently unavailable. Expected restock in 2-3 weeks."


@tool
def calculate_discount(sku: str, quantity: int, customer_type: str = "regular") -> str:
    """Calculate volume discounts and special customer pricing.

    Args:
        sku: Product SKU code
        quantity: Number of units
        customer_type: Customer category (regular, premium, enterprise)

    Returns:
        Discount breakdown and final price
    """
    base_prices = {
        "LPT-001": 1299,
        "HPH-205": 299,
        "MSE-104": 79,
        "KBD-310": 159,
        "MON-227": 549,
    }

    sku_upper = sku.upper()
    if sku_upper not in base_prices:
        return f"SKU {sku} not found."

    base_price = base_prices[sku_upper]
    subtotal = base_price * quantity

    # Volume discount
    volume_discount = 0
    if quantity >= 10:
        volume_discount = 0.15
    elif quantity >= 5:
        volume_discount = 0.10

    # Customer type discount
    customer_discount = {"regular": 0, "premium": 0.05, "enterprise": 0.12}.get(customer_type.lower(), 0)

    total_discount = min(volume_discount + customer_discount, 0.25)  # Max 25% discount
    discount_amount = subtotal * total_discount
    final_price = subtotal - discount_amount

    return f"""Discount Calculation for {sku_upper}:
Base price: ${base_price} × {quantity} = ${subtotal:,.2f}
Volume discount ({quantity} units): {volume_discount*100:.0f}%
Customer tier ({customer_type}): {customer_discount*100:.0f}%
Total discount: {total_discount*100:.0f}% (${discount_amount:,.2f})
FINAL PRICE: ${final_price:,.2f}"""


@tool
def schedule_demo(product_sku: str, customer_email: str, preferred_date: str) -> str:
    """Schedule a product demonstration (requires human approval).

    Args:
        product_sku: SKU of product to demo
        customer_email: Customer email address
        preferred_date: Preferred demo date (e.g., "2025-10-15")

    Returns:
        Demo scheduling confirmation
    """
    return f"""DEMO SCHEDULE REQUEST (Pending Approval):
Product: {product_sku}
Customer: {customer_email}
Requested Date: {preferred_date}
Status: Awaiting manager approval
Action: Human approval required before confirmation"""


@tool
def get_competitor_comparison(product_category: str) -> str:
    """Compare our products with competitor offerings.

    Args:
        product_category: Category to compare (laptop, headphones, etc.)

    Returns:
        Competitive analysis and differentiation points
    """
    comparisons = {
        "laptop": """Premium Business Laptop vs Competitors:
Our Product: $1,299 | 16GB RAM, 512GB SSD, 3yr warranty
Competitor A: $1,399 | 16GB RAM, 256GB SSD, 1yr warranty
Competitor B: $1,249 | 8GB RAM, 512GB SSD, 2yr warranty
ADVANTAGE: Best value with superior warranty coverage""",

        "headphones": """Wireless Headphones vs Competitors:
Our Product: $299 | 30hr battery, ANC, Premium drivers
Competitor A: $329 | 25hr battery, ANC, Standard drivers
Competitor B: $279 | 30hr battery, No ANC, Premium drivers
ADVANTAGE: Best balance of battery life, ANC, and audio quality""",

        "monitor": """4K Monitor vs Competitors:
Our Product: $549 | 27-inch, HDR, 5ms response
Competitor A: $599 | 27-inch, HDR, 4ms response
Competitor B: $499 | 27-inch, No HDR, 5ms response
ADVANTAGE: Competitive pricing with HDR support"""
    }

    return comparisons.get(product_category.lower(), f"No comparison data available for {product_category}")


@tool
def check_customer_eligibility(customer_id: str, program: str = "enterprise") -> str:
    """Verify customer eligibility for special programs or discounts.

    Args:
        customer_id: Customer account ID
        program: Program to check (enterprise, education, nonprofit)

    Returns:
        Eligibility status and program benefits
    """
    # Mock eligibility database
    customers = {
        "CUST-1001": {"type": "enterprise", "discount": 12, "support": "priority"},
        "CUST-1002": {"type": "education", "discount": 15, "support": "standard"},
        "CUST-1003": {"type": "regular", "discount": 0, "support": "standard"},
        "CUST-1004": {"type": "nonprofit", "discount": 20, "support": "priority"},
    }

    customer = customers.get(customer_id.upper())
    if not customer:
        return f"Customer ID {customer_id} not found. May be new customer - standard pricing applies."

    if customer["type"] == program.lower():
        return f"""✓ ELIGIBLE for {program.upper()} Program:
Customer: {customer_id}
Discount: {customer['discount']}%
Support Level: {customer['support'].upper()}
Additional Benefits: Extended payment terms, dedicated account manager"""
    else:
        return f"""Customer {customer_id} is registered as {customer['type'].upper()}, not eligible for {program.upper()} program.
Current discount: {customer['discount']}%"""


# Export all tools
SALES_TOOLS = [
    search_product_catalog,
    get_pricing,
    check_inventory,
    calculate_discount,
    schedule_demo,  # Side-effect tool
    get_competitor_comparison,
    check_customer_eligibility,
]
