"""
Multi-Agent E-commerce System - Demo Version
=============================================
This demonstrates multi-agent workflow WITHOUT requiring OpenAI API calls.
Uses simulated AI responses to show how agents collaborate.

This is perfect for testing the MCP server integration and multi-agent patterns
without API costs.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional

# Import our MCP tools directly
from main import (
    check_inventory_status,
    process_order,
    get_customer_analytics,
    generate_product_recommendations,
    generate_sales_report
)


class MCPToolExecutor:
    """Wrapper to execute MCP tools and format results."""

    @staticmethod
    async def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> str:
        """Execute an MCP tool and return the result."""
        try:
            if tool_name == "check_inventory_status":
                return await check_inventory_status(parameters.get("sku", ""))

            elif tool_name == "process_order":
                return await process_order(
                    parameters.get("order_id", ""),
                    parameters.get("action", "")
                )

            elif tool_name == "get_customer_analytics":
                return await get_customer_analytics(parameters.get("customer_id", ""))

            elif tool_name == "generate_product_recommendations":
                return await generate_product_recommendations(
                    parameters.get("customer_id", ""),
                    parameters.get("category")
                )

            elif tool_name == "generate_sales_report":
                return await generate_sales_report(parameters.get("period", "week"))

            else:
                return f"❌ Unknown tool: {tool_name}"

        except Exception as e:
            return f"❌ Error executing {tool_name}: {str(e)}"


class SimulatedAgent:
    """Base agent with simulated intelligence (no API calls)."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def log(self, message: str):
        """Log agent activity."""
        print(f"\n🤖 [{self.name}] {message}")

    def analyze(self, context: str, data: str) -> str:
        """Simulated analysis based on data patterns."""
        # Simple rule-based responses
        if "Out of Stock" in data:
            return f"⚠️  ALERT: Item is out of stock. Immediate restocking required."
        elif "Low Stock" in data:
            return f"⚠️  WARNING: Stock levels are low. Recommend restocking within 48 hours."
        elif "VIP" in data:
            return f"💎 VIP Customer: Prioritize service and offer premium recommendations."
        elif "lifetime_value" in data and "4500" in data:
            return f"📈 High-value customer ($4500+ LTV). Excellent retention candidate."
        elif "total_revenue" in data:
            return f"📊 Strong sales performance. Revenue trending positive."
        else:
            return f"✅ Status nominal. Continue monitoring."


class InventoryAgent(SimulatedAgent):
    """Agent specialized in inventory management."""

    def __init__(self):
        super().__init__("Inventory Agent", "Inventory Manager")

    async def check_stock(self, sku: str) -> Dict[str, Any]:
        """Check inventory for a specific product."""
        self.log(f"Checking inventory for SKU: {sku}")

        result = await MCPToolExecutor.execute_tool(
            "check_inventory_status",
            {"sku": sku}
        )

        analysis = self.analyze("inventory", result)

        return {
            "sku": sku,
            "data": result,
            "analysis": analysis
        }

    async def audit_inventory(self, skus: List[str]) -> str:
        """Perform inventory audit across multiple products."""
        self.log(f"Performing inventory audit for {len(skus)} products")

        results = []
        critical_items = []
        low_stock_items = []

        for sku in skus:
            result = await MCPToolExecutor.execute_tool(
                "check_inventory_status",
                {"sku": sku}
            )

            if "Out of Stock" in result:
                critical_items.append(sku)
            elif "Low Stock" in result:
                low_stock_items.append(sku)

            results.append(f"\n{sku}: {result}")

        # Generate audit report
        report = "📋 INVENTORY AUDIT REPORT\n" + "="*60
        report += "\n".join(results)
        report += "\n\n" + "="*60
        report += "\n\n📊 SUMMARY:"
        report += f"\n• Total products audited: {len(skus)}"
        report += f"\n• Critical (Out of Stock): {len(critical_items)}"
        report += f"\n• Warning (Low Stock): {len(low_stock_items)}"

        if critical_items:
            report += f"\n\n⚠️  CRITICAL: {', '.join(critical_items)} - Immediate action required"
        if low_stock_items:
            report += f"\n⚠️  WARNING: {', '.join(low_stock_items)} - Restock soon"

        return report


class CustomerServiceAgent(SimulatedAgent):
    """Agent specialized in customer service."""

    def __init__(self):
        super().__init__("Customer Service Agent", "Customer Service Rep")

    async def handle_order_inquiry(self, order_id: str) -> str:
        """Handle customer inquiry about an order."""
        self.log(f"Handling inquiry for order: {order_id}")

        order_data = await MCPToolExecutor.execute_tool(
            "process_order",
            {"order_id": order_id, "action": "retrieve"}
        )

        # Parse the data
        try:
            data = json.loads(order_data)
            response = f"""
📧 CUSTOMER EMAIL RESPONSE
==========================

Dear Valued Customer,

Thank you for contacting us regarding your order {data.get('order_id')}.

Order Details:
• Order ID: {data.get('order_id')}
• Status: {data.get('status').upper()}
• Total: {data.get('total_amount')}
• Items: {data.get('item_count')} item(s)
• Order Date: {data.get('order_date')}

Your order is currently {data.get('status')}.
{self._get_status_message(data.get('status'))}

If you have any questions, please don't hesitate to contact us.

Best regards,
Customer Service Team
"""
        except:
            response = f"Order data: {order_data}"

        return response

    def _get_status_message(self, status: str) -> str:
        """Get appropriate message based on order status."""
        messages = {
            "shipped": "You should receive tracking information shortly.",
            "delivered": "Your order has been successfully delivered!",
            "pending": "We're preparing your order for shipment.",
            "processing": "Your order is being processed by our warehouse team."
        }
        return messages.get(status, "We're working on your order.")

    async def recommend_products(self, customer_id: str, category: Optional[str] = None) -> str:
        """Generate personalized product recommendations."""
        self.log(f"Generating recommendations for customer: {customer_id}")

        # Get customer analytics
        customer_data = await MCPToolExecutor.execute_tool(
            "get_customer_analytics",
            {"customer_id": customer_id}
        )

        # Get recommendations
        recommendations = await MCPToolExecutor.execute_tool(
            "generate_product_recommendations",
            {"customer_id": customer_id, "category": category}
        )

        try:
            cust = json.loads(customer_data)
            recs = json.loads(recommendations)

            email = f"""
📧 PERSONALIZED PRODUCT RECOMMENDATIONS
========================================

Dear {cust.get('name')},

As one of our valued {cust.get('customer_segment')} customers, we've handpicked
some exclusive recommendations just for you:

"""
            for idx, rec in enumerate(recs.get('recommendations', []), 1):
                email += f"""
{idx}. {rec.get('product_name')}
   Price: {rec.get('price')}
   Match Score: {rec.get('relevance_score')}
   Why: {rec.get('reason')}
"""

            email += f"""
These selections are based on your purchase history and preferences.
Shop now and enjoy your {cust.get('customer_segment')} benefits!

Best regards,
Your Personal Shopping Team
"""
        except:
            email = f"Customer: {customer_data}\n\nRecommendations: {recommendations}"

        return email

    async def ship_order(self, order_id: str) -> str:
        """Process order shipment."""
        self.log(f"Processing shipment for order: {order_id}")

        result = await MCPToolExecutor.execute_tool(
            "process_order",
            {"order_id": order_id, "action": "ship"}
        )

        notification = f"""
📧 SHIPMENT NOTIFICATION
========================

Your order {order_id} has been shipped! 🚚

{result}

Track your package: https://tracking.example.com/{order_id}

Estimated delivery: 3-5 business days

Thank you for shopping with us!
"""
        return notification


class AnalyticsAgent(SimulatedAgent):
    """Agent specialized in business analytics."""

    def __init__(self):
        super().__init__("Analytics Agent", "Business Analyst")

    async def generate_business_report(self, period: str = "week") -> str:
        """Generate comprehensive business report."""
        self.log(f"Generating {period} business report")

        report_data = await MCPToolExecutor.execute_tool(
            "generate_sales_report",
            {"period": period}
        )

        try:
            data = json.loads(report_data)
            metrics = data.get('sales_metrics', {})

            summary = f"""
📊 EXECUTIVE BUSINESS SUMMARY
==============================
Report Period: {data.get('report_period')}
Generated: {data.get('generated_at')}

KEY METRICS:
• Total Revenue: {metrics.get('total_revenue')}
• Total Orders: {metrics.get('total_orders')}
• Average Order Value: {metrics.get('average_order_value')}

TOP PERFORMER:
• {data.get('top_selling_product', {}).get('name')} ({data.get('top_selling_product', {}).get('units_sold')} units)

OPERATIONAL INSIGHTS:
"""
            for insight in data.get('insights', []):
                summary += f"• {insight}\n"

            alerts = data.get('inventory_alerts', {})
            if alerts.get('out_of_stock_items'):
                summary += f"\n⚠️  URGENT: {len(alerts['out_of_stock_items'])} items out of stock"
            if alerts.get('low_stock_items'):
                summary += f"\n⚠️  Warning: {len(alerts['low_stock_items'])} items low on stock"

            summary += "\n\n✅ RECOMMENDATIONS:\n"
            summary += "• Continue current sales strategies\n"
            summary += "• Address inventory shortages immediately\n"
            summary += "• Focus on top-performing product categories\n"

        except:
            summary = f"Report data: {report_data}"

        return summary

    async def analyze_customer_segment(self, customer_id: str) -> str:
        """Analyze customer segment."""
        self.log(f"Analyzing customer segment for: {customer_id}")

        analytics = await MCPToolExecutor.execute_tool(
            "get_customer_analytics",
            {"customer_id": customer_id}
        )

        try:
            data = json.loads(analytics)

            insights = f"""
📊 CUSTOMER SEGMENT ANALYSIS
=============================

Customer: {data.get('name')} ({data.get('customer_id')})
Segment: {data.get('customer_segment')}
Engagement: {data.get('engagement_level')}

METRICS:
• Lifetime Value: {data.get('lifetime_value')}
• Total Orders: {data.get('total_orders')}

STRATEGIC RECOMMENDATION:
{data.get('recommendation')}

ACTION ITEMS:
"""
            if data.get('customer_segment') == 'VIP':
                insights += "• Assign dedicated account manager\n"
                insights += "• Offer exclusive early access to new products\n"
                insights += "• Provide white-glove customer service\n"
            elif data.get('customer_segment') == 'Gold':
                insights += "• Send quarterly appreciation gifts\n"
                insights += "• Offer loyalty program benefits\n"
                insights += "• Personalized email campaigns\n"
            else:
                insights += "• Engage with targeted promotions\n"
                insights += "• Encourage repeat purchases\n"
                insights += "• Build brand loyalty\n"

        except:
            insights = f"Analytics: {analytics}"

        return insights


# Workflow Scenarios
async def workflow_vip_customer_order():
    """Scenario: Handle VIP customer order and upsell."""
    print("\n" + "="*70)
    print("SCENARIO 1: VIP Customer Order Processing & Upsell")
    print("="*70)

    cs_agent = CustomerServiceAgent()
    analytics_agent = AnalyticsAgent()

    print("\n📦 Step 1: Check Order Status")
    order_status = await cs_agent.handle_order_inquiry("ORD001")
    print(order_status)

    print("\n📊 Step 2: Analyze Customer Profile")
    customer_insights = await analytics_agent.analyze_customer_segment("CUST001")
    print(customer_insights)

    print("\n💡 Step 3: Generate Product Recommendations")
    recommendations = await cs_agent.recommend_products("CUST001", "Electronics")
    print(recommendations)


async def workflow_inventory_alert():
    """Scenario: Inventory alert and restocking."""
    print("\n" + "="*70)
    print("SCENARIO 2: Inventory Alert & Restocking Analysis")
    print("="*70)

    inv_agent = InventoryAgent()

    print("\n📦 Performing Inventory Audit")
    skus = ["PROD001", "PROD002", "PROD003", "PROD004", "PROD005"]
    audit_report = await inv_agent.audit_inventory(skus)
    print(audit_report)


async def workflow_daily_business_review():
    """Scenario: Daily business review."""
    print("\n" + "="*70)
    print("SCENARIO 3: Daily Business Review")
    print("="*70)

    analytics_agent = AnalyticsAgent()
    inv_agent = InventoryAgent()

    print("\n📈 Step 1: Sales Performance")
    sales_report = await analytics_agent.generate_business_report("week")
    print(sales_report)

    print("\n📦 Step 2: Critical Inventory Check")
    critical_check = await inv_agent.check_stock("PROD004")
    print(f"\nData: {critical_check['data']}")
    print(f"\n{critical_check['analysis']}")


async def workflow_order_fulfillment():
    """Scenario: Complete order fulfillment."""
    print("\n" + "="*70)
    print("SCENARIO 4: Order Fulfillment Workflow")
    print("="*70)

    cs_agent = CustomerServiceAgent()
    inv_agent = InventoryAgent()

    order_id = "ORD002"

    print(f"\n📦 Step 1: Review Order {order_id}")
    order_data = await MCPToolExecutor.execute_tool(
        "process_order",
        {"order_id": order_id, "action": "retrieve"}
    )
    print(order_data)

    print("\n📦 Step 2: Verify Inventory")
    inv_check = await inv_agent.check_stock("PROD003")
    print(f"\n{inv_check['analysis']}")

    print("\n🚚 Step 3: Process Shipment")
    shipment = await cs_agent.ship_order(order_id)
    print(shipment)


async def main_menu():
    """Interactive menu."""
    print("\n" + "="*70)
    print("🤖 MULTI-AGENT E-COMMERCE SYSTEM (Demo Mode)")
    print("="*70)
    print("\nAvailable Scenarios:")
    print("1. VIP Customer Order Processing & Upsell")
    print("2. Inventory Alert & Restocking Analysis")
    print("3. Daily Business Review")
    print("4. Order Fulfillment Workflow")
    print("5. Run All Scenarios")
    print("0. Exit")

    choice = input("\nSelect scenario (0-5): ").strip()

    if choice == "1":
        await workflow_vip_customer_order()
    elif choice == "2":
        await workflow_inventory_alert()
    elif choice == "3":
        await workflow_daily_business_review()
    elif choice == "4":
        await workflow_order_fulfillment()
    elif choice == "5":
        print("\n🚀 Running all scenarios...\n")
        await workflow_vip_customer_order()
        await workflow_inventory_alert()
        await workflow_daily_business_review()
        await workflow_order_fulfillment()
    elif choice == "0":
        print("\n👋 Goodbye!")
        return
    else:
        print("\n❌ Invalid choice")
        await main_menu()

    again = input("\n\nRun another scenario? (y/n): ").strip().lower()
    if again == 'y':
        await main_menu()
    else:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    print("\n🔧 Initializing Multi-Agent System (Demo Mode)")
    print("📝 Note: Using simulated AI responses (no API calls required)")
    print("🎯 Focus: Demonstrating multi-agent workflow with MCP server\n")

    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")