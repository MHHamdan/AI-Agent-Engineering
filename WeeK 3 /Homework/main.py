"""
E-commerce MCP Server
=====================
A comprehensive Model Context Protocol server for e-commerce operations.

This MCP server provides enterprise-level tools for:
- Inventory management and stock tracking
- Order processing and fulfillment
- Customer analytics and segmentation
- Product recommendations
- Sales reporting and analytics

Author: Mohammed (AI Agent Engineering - Week 3 Homework)
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

# Initialize MCP server
mcp = FastMCP("ecommerce-mcp-server")

# Mock database - In production, these would connect to real databases
INVENTORY_DB = {
    "PROD001": {"name": "Laptop Pro 15", "sku": "PROD001", "stock": 45, "price": 1299.99, "category": "Electronics", "warehouse": "WH-001"},
    "PROD002": {"name": "Wireless Mouse", "sku": "PROD002", "stock": 150, "price": 29.99, "category": "Electronics", "warehouse": "WH-001"},
    "PROD003": {"name": "USB-C Cable", "sku": "PROD003", "stock": 8, "price": 12.99, "category": "Accessories", "warehouse": "WH-002"},
    "PROD004": {"name": "Ergonomic Keyboard", "sku": "PROD004", "stock": 0, "price": 89.99, "category": "Electronics", "warehouse": "WH-001"},
    "PROD005": {"name": "Monitor 27 inch", "sku": "PROD005", "stock": 22, "price": 349.99, "category": "Electronics", "warehouse": "WH-001"},
}

ORDERS_DB = {
    "ORD001": {"order_id": "ORD001", "customer_id": "CUST001", "items": ["PROD001", "PROD002"], "total": 1329.98, "status": "shipped", "date": "2025-09-15"},
    "ORD002": {"order_id": "ORD002", "customer_id": "CUST002", "items": ["PROD003"], "total": 12.99, "status": "pending", "date": "2025-09-28"},
    "ORD003": {"order_id": "ORD003", "customer_id": "CUST001", "items": ["PROD005"], "total": 349.99, "status": "delivered", "date": "2025-09-20"},
    "ORD004": {"order_id": "ORD004", "customer_id": "CUST003", "items": ["PROD002", "PROD003"], "total": 42.98, "status": "processing", "date": "2025-09-29"},
}

CUSTOMERS_DB = {
    "CUST001": {"customer_id": "CUST001", "name": "Alice Johnson", "email": "alice@example.com", "total_orders": 15, "lifetime_value": 4500.50, "segment": "VIP"},
    "CUST002": {"customer_id": "CUST002", "name": "Bob Smith", "email": "bob@example.com", "total_orders": 3, "lifetime_value": 450.00, "segment": "Regular"},
    "CUST003": {"customer_id": "CUST003", "name": "Carol White", "email": "carol@example.com", "total_orders": 8, "lifetime_value": 1200.00, "segment": "Gold"},
}


@mcp.tool()
async def check_inventory_status(sku: str) -> str:
    """
    Check the current inventory status for a product.

    This tool provides real-time inventory information including stock levels,
    pricing, warehouse location, and stock status (in-stock/low-stock/out-of-stock).
    Essential for order fulfillment and inventory management systems.

    Args:
        sku: Product SKU identifier (e.g., 'PROD001')

    Returns:
        Comprehensive inventory information including stock level, price, and availability status

    Example:
        >>> await check_inventory_status("PROD001")
        "Product: Laptop Pro 15 | SKU: PROD001 | Stock: 45 units | Price: $1299.99 | Status: In Stock | Warehouse: WH-001"
    """
    try:
        if not sku:
            return "❌ Error: SKU parameter is required"

        product = INVENTORY_DB.get(sku.upper())

        if not product:
            return f"❌ Product with SKU '{sku}' not found in inventory database"

        # Determine stock status
        stock_level = product["stock"]
        if stock_level == 0:
            status = "⛔ Out of Stock"
        elif stock_level < 10:
            status = "⚠️  Low Stock"
        else:
            status = "✅ In Stock"

        result = {
            "product_name": product["name"],
            "sku": product["sku"],
            "stock_quantity": stock_level,
            "price": f"${product['price']:.2f}",
            "category": product["category"],
            "warehouse_location": product["warehouse"],
            "status": status
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"❌ Error checking inventory: {str(e)}"


@mcp.tool()
async def process_order(order_id: str, action: str) -> str:
    """
    Process and manage e-commerce orders with various actions.

    This tool handles order lifecycle management including status updates,
    order retrieval, and fulfillment tracking. Supports actions like 'retrieve',
    'ship', 'cancel', and 'complete' to manage the full order workflow.

    Args:
        order_id: Unique order identifier (e.g., 'ORD001')
        action: Action to perform - 'retrieve', 'ship', 'cancel', or 'complete'

    Returns:
        Order details and confirmation of the action performed

    Example:
        >>> await process_order("ORD001", "retrieve")
        "Order ORD001 | Customer: CUST001 | Items: 2 | Total: $1329.98 | Status: shipped"

        >>> await process_order("ORD002", "ship")
        "✅ Order ORD002 has been shipped successfully"
    """
    try:
        if not order_id or not action:
            return "❌ Error: Both order_id and action parameters are required"

        order = ORDERS_DB.get(order_id.upper())

        if not order:
            return f"❌ Order '{order_id}' not found in the system"

        action = action.lower()

        if action == "retrieve":
            result = {
                "order_id": order["order_id"],
                "customer_id": order["customer_id"],
                "items": order["items"],
                "item_count": len(order["items"]),
                "total_amount": f"${order['total']:.2f}",
                "status": order["status"],
                "order_date": order["date"]
            }
            return json.dumps(result, indent=2)

        elif action == "ship":
            if order["status"] in ["shipped", "delivered"]:
                return f"⚠️  Order {order_id} has already been {order['status']}"
            order["status"] = "shipped"
            return f"✅ Order {order_id} has been shipped successfully. Customer {order['customer_id']} will be notified."

        elif action == "cancel":
            if order["status"] in ["shipped", "delivered"]:
                return f"❌ Cannot cancel order {order_id}. Order has already been {order['status']}"
            order["status"] = "cancelled"
            return f"✅ Order {order_id} has been cancelled. Refund will be processed within 3-5 business days."

        elif action == "complete":
            if order["status"] != "shipped":
                return f"⚠️  Order {order_id} must be shipped before it can be completed. Current status: {order['status']}"
            order["status"] = "delivered"
            return f"✅ Order {order_id} marked as delivered. Thank you for your business!"

        else:
            return f"❌ Invalid action '{action}'. Valid actions: retrieve, ship, cancel, complete"

    except Exception as e:
        return f"❌ Error processing order: {str(e)}"


@mcp.tool()
async def get_customer_analytics(customer_id: str) -> str:
    """
    Retrieve comprehensive customer analytics and segmentation data.

    This tool provides detailed customer insights including purchase history,
    lifetime value, customer segment classification, and personalized recommendations.
    Critical for CRM, marketing campaigns, and customer retention strategies.

    Args:
        customer_id: Unique customer identifier (e.g., 'CUST001')

    Returns:
        Detailed customer analytics including orders, lifetime value, and segment classification

    Example:
        >>> await get_customer_analytics("CUST001")
        "Customer: Alice Johnson | Total Orders: 15 | Lifetime Value: $4500.50 | Segment: VIP | Recommendation: Offer exclusive early access to new products"
    """
    try:
        if not customer_id:
            return "❌ Error: customer_id parameter is required"

        customer = CUSTOMERS_DB.get(customer_id.upper())

        if not customer:
            return f"❌ Customer '{customer_id}' not found in database"

        # Generate recommendations based on segment
        segment = customer["segment"]
        if segment == "VIP":
            recommendation = "Offer exclusive early access to new products and premium customer support"
        elif segment == "Gold":
            recommendation = "Send personalized discount codes and loyalty rewards"
        else:
            recommendation = "Engage with targeted email campaigns and special promotions"

        # Calculate engagement level
        ltv = customer["lifetime_value"]
        if ltv > 3000:
            engagement = "High"
        elif ltv > 1000:
            engagement = "Medium"
        else:
            engagement = "Low"

        result = {
            "customer_id": customer["customer_id"],
            "name": customer["name"],
            "email": customer["email"],
            "total_orders": customer["total_orders"],
            "lifetime_value": f"${customer['lifetime_value']:.2f}",
            "customer_segment": segment,
            "engagement_level": engagement,
            "recommendation": recommendation
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"❌ Error retrieving customer analytics: {str(e)}"


@mcp.tool()
async def generate_product_recommendations(customer_id: str, category: Optional[str] = None) -> str:
    """
    Generate AI-powered product recommendations for customers.

    This tool analyzes customer purchase history and preferences to suggest
    relevant products. Can be filtered by category for more targeted recommendations.
    Powers upselling, cross-selling, and personalized shopping experiences.

    Args:
        customer_id: Unique customer identifier (e.g., 'CUST001')
        category: Optional product category filter (e.g., 'Electronics', 'Accessories')

    Returns:
        List of recommended products with relevance scores and reasoning

    Example:
        >>> await generate_product_recommendations("CUST001", "Electronics")
        "Recommendations for Alice Johnson: [Laptop Pro 15 (95% match), Monitor 27 inch (87% match)]"
    """
    try:
        if not customer_id:
            return "❌ Error: customer_id parameter is required"

        customer = CUSTOMERS_DB.get(customer_id.upper())

        if not customer:
            return f"❌ Customer '{customer_id}' not found in database"

        # Filter products by category if specified
        products = list(INVENTORY_DB.values())
        if category:
            products = [p for p in products if p["category"].lower() == category.lower()]
            if not products:
                return f"❌ No products found in category '{category}'"

        # Generate recommendations (in real system, this would use ML/collaborative filtering)
        recommendations = []
        for product in products[:3]:  # Top 3 recommendations
            if product["stock"] > 0:  # Only recommend in-stock items
                # Simulate relevance score based on customer segment
                if customer["segment"] == "VIP":
                    relevance = 95 if product["price"] > 100 else 85
                elif customer["segment"] == "Gold":
                    relevance = 88 if product["price"] > 50 else 92
                else:
                    relevance = 80 if product["price"] < 50 else 75

                recommendations.append({
                    "product_name": product["name"],
                    "sku": product["sku"],
                    "price": f"${product['price']:.2f}",
                    "relevance_score": f"{relevance}%",
                    "reason": f"Based on your {customer['segment']} status and purchase history"
                })

        if not recommendations:
            return f"⚠️  No products currently available for recommendation"

        result = {
            "customer": customer["name"],
            "customer_id": customer_id,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"❌ Error generating recommendations: {str(e)}"


@mcp.tool()
async def generate_sales_report(period: str = "week") -> str:
    """
    Generate comprehensive sales analytics and reports.

    This tool creates detailed sales reports for specified time periods including
    revenue metrics, top products, order statistics, and trend analysis. Essential
    for business intelligence, forecasting, and strategic decision-making.

    Args:
        period: Time period for report - 'day', 'week', 'month', or 'year' (default: 'week')

    Returns:
        Comprehensive sales report with key metrics and insights

    Example:
        >>> await generate_sales_report("week")
        "Sales Report (Week) | Total Revenue: $1,735.94 | Orders: 4 | Avg Order: $433.99 | Top Product: Laptop Pro 15"
    """
    try:
        period = period.lower()
        valid_periods = ["day", "week", "month", "year"]

        if period not in valid_periods:
            return f"❌ Invalid period '{period}'. Valid options: {', '.join(valid_periods)}"

        # Calculate metrics from orders
        total_revenue = sum(order["total"] for order in ORDERS_DB.values())
        total_orders = len(ORDERS_DB)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        # Calculate order status breakdown
        status_counts = {}
        for order in ORDERS_DB.values():
            status = order["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        # Find top selling products
        product_sales = {}
        for order in ORDERS_DB.values():
            for item_sku in order["items"]:
                product_sales[item_sku] = product_sales.get(item_sku, 0) + 1

        top_product_sku = max(product_sales, key=product_sales.get) if product_sales else None
        top_product = INVENTORY_DB.get(top_product_sku, {}).get("name", "N/A") if top_product_sku else "N/A"

        # Calculate inventory health
        low_stock_items = [p["name"] for p in INVENTORY_DB.values() if 0 < p["stock"] < 10]
        out_of_stock_items = [p["name"] for p in INVENTORY_DB.values() if p["stock"] == 0]

        result = {
            "report_period": period.capitalize(),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sales_metrics": {
                "total_revenue": f"${total_revenue:.2f}",
                "total_orders": total_orders,
                "average_order_value": f"${avg_order_value:.2f}"
            },
            "order_status_breakdown": status_counts,
            "top_selling_product": {
                "name": top_product,
                "units_sold": product_sales.get(top_product_sku, 0)
            },
            "inventory_alerts": {
                "low_stock_items": low_stock_items,
                "out_of_stock_items": out_of_stock_items
            },
            "insights": [
                f"Revenue growth trending {'positive' if total_revenue > 1500 else 'stable'}",
                f"{len(low_stock_items)} items need restocking soon",
                f"Order fulfillment rate: {(status_counts.get('delivered', 0) / total_orders * 100):.1f}%"
            ]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"❌ Error generating sales report: {str(e)}"


# Run the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')
