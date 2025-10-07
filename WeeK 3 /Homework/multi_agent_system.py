"""
Multi-Agent E-commerce System
==============================
This system demonstrates multiple AI agents working together using the MCP server.

Agents:
1. Inventory Agent - Manages stock and inventory
2. Customer Service Agent - Handles orders and customer queries
3. Analytics Agent - Generates reports and insights
4. Coordinator Agent - Orchestrates the workflow

Each agent uses OpenAI GPT-3.5-turbo and communicates with the MCP server
to perform e-commerce tasks.
"""

import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI

# Import our MCP tools directly for this demo
from main import (
    check_inventory_status,
    process_order,
    get_customer_analytics,
    generate_product_recommendations,
    generate_sales_report
)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("MODEL_NAME", "gpt-3.5-turbo")


class MCPToolExecutor:
    """Wrapper to execute MCP tools and format results for AI agents."""

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


class BaseAgent:
    """Base class for all AI agents."""

    def __init__(self, name: str, role: str, system_prompt: str):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.conversation_history: List[Dict[str, str]] = []

    def call_llm(self, user_message: str) -> str:
        """Call OpenAI API with the agent's system prompt."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"❌ Error calling LLM: {str(e)}"

    def log(self, message: str):
        """Log agent activity."""
        print(f"\n🤖 [{self.name}] {message}")


class InventoryAgent(BaseAgent):
    """Agent specialized in inventory management."""

    def __init__(self):
        super().__init__(
            name="Inventory Agent",
            role="Inventory Manager",
            system_prompt="""You are an Inventory Management Agent for an e-commerce company.
Your responsibilities:
- Check stock levels for products
- Identify low stock and out-of-stock items
- Recommend restocking priorities
- Provide inventory status reports

Be concise and data-driven in your responses."""
        )

    async def check_stock(self, sku: str) -> Dict[str, Any]:
        """Check inventory for a specific product."""
        self.log(f"Checking inventory for SKU: {sku}")

        result = await MCPToolExecutor.execute_tool(
            "check_inventory_status",
            {"sku": sku}
        )

        # Parse and analyze
        analysis = self.call_llm(
            f"Analyze this inventory data and provide a brief assessment:\n{result}"
        )

        return {
            "sku": sku,
            "data": result,
            "analysis": analysis
        }

    async def audit_inventory(self, skus: List[str]) -> str:
        """Perform inventory audit across multiple products."""
        self.log(f"Performing inventory audit for {len(skus)} products")

        results = []
        for sku in skus:
            result = await MCPToolExecutor.execute_tool(
                "check_inventory_status",
                {"sku": sku}
            )
            results.append(f"SKU {sku}: {result}")

        # Get LLM analysis
        combined_data = "\n\n".join(results)
        analysis = self.call_llm(
            f"Review this inventory audit and identify critical issues:\n{combined_data}"
        )

        return analysis


class CustomerServiceAgent(BaseAgent):
    """Agent specialized in customer service and order management."""

    def __init__(self):
        super().__init__(
            name="Customer Service Agent",
            role="Customer Service Representative",
            system_prompt="""You are a Customer Service Agent for an e-commerce company.
Your responsibilities:
- Handle customer inquiries about orders
- Process order updates (ship, cancel, complete)
- Provide personalized product recommendations
- Analyze customer profiles for better service

Be helpful, empathetic, and efficient."""
        )

    async def handle_order_inquiry(self, order_id: str) -> str:
        """Handle customer inquiry about an order."""
        self.log(f"Handling inquiry for order: {order_id}")

        # Get order details
        order_data = await MCPToolExecutor.execute_tool(
            "process_order",
            {"order_id": order_id, "action": "retrieve"}
        )

        # Generate customer-friendly response
        response = self.call_llm(
            f"A customer is asking about their order. Here's the data:\n{order_data}\n\n"
            f"Provide a friendly response explaining the order status."
        )

        return response

    async def recommend_products(self, customer_id: str, category: Optional[str] = None) -> str:
        """Generate personalized product recommendations."""
        self.log(f"Generating recommendations for customer: {customer_id}")

        # Get customer analytics first
        customer_data = await MCPToolExecutor.execute_tool(
            "get_customer_analytics",
            {"customer_id": customer_id}
        )

        # Get recommendations
        recommendations = await MCPToolExecutor.execute_tool(
            "generate_product_recommendations",
            {"customer_id": customer_id, "category": category}
        )

        # Generate personalized message
        response = self.call_llm(
            f"Customer profile:\n{customer_data}\n\n"
            f"Recommendations:\n{recommendations}\n\n"
            f"Write a personalized email suggesting these products to the customer."
        )

        return response

    async def ship_order(self, order_id: str) -> str:
        """Process order shipment."""
        self.log(f"Processing shipment for order: {order_id}")

        result = await MCPToolExecutor.execute_tool(
            "process_order",
            {"order_id": order_id, "action": "ship"}
        )

        # Generate confirmation message
        response = self.call_llm(
            f"Order shipment result:\n{result}\n\n"
            f"Generate a customer notification email about the shipment."
        )

        return response


class AnalyticsAgent(BaseAgent):
    """Agent specialized in business analytics and reporting."""

    def __init__(self):
        super().__init__(
            name="Analytics Agent",
            role="Business Analyst",
            system_prompt="""You are a Business Analytics Agent for an e-commerce company.
Your responsibilities:
- Generate sales reports and insights
- Identify trends and patterns
- Provide actionable recommendations
- Support strategic decision-making

Be analytical, insightful, and focused on actionable insights."""
        )

    async def generate_business_report(self, period: str = "week") -> str:
        """Generate comprehensive business report."""
        self.log(f"Generating {period} business report")

        # Get sales report
        report_data = await MCPToolExecutor.execute_tool(
            "generate_sales_report",
            {"period": period}
        )

        # Generate executive summary
        summary = self.call_llm(
            f"Analyze this sales report and provide an executive summary with key insights and recommendations:\n{report_data}"
        )

        return summary

    async def analyze_customer_segment(self, customer_id: str) -> str:
        """Analyze customer segment and provide insights."""
        self.log(f"Analyzing customer segment for: {customer_id}")

        analytics = await MCPToolExecutor.execute_tool(
            "get_customer_analytics",
            {"customer_id": customer_id}
        )

        insights = self.call_llm(
            f"Analyze this customer data and provide strategic insights:\n{analytics}\n\n"
            f"Focus on: retention strategies, upsell opportunities, and engagement tactics."
        )

        return insights


class CoordinatorAgent(BaseAgent):
    """Coordinator agent that orchestrates multi-agent workflows."""

    def __init__(self):
        super().__init__(
            name="Coordinator Agent",
            role="Workflow Coordinator",
            system_prompt="""You are a Coordinator Agent that orchestrates multi-agent workflows.
Your responsibilities:
- Understand complex user requests
- Break down tasks for specialized agents
- Coordinate agent activities
- Synthesize results into coherent responses

Be organized, efficient, and ensure all aspects of the request are addressed."""
        )

        self.inventory_agent = InventoryAgent()
        self.customer_service_agent = CustomerServiceAgent()
        self.analytics_agent = AnalyticsAgent()

    async def handle_complex_request(self, user_request: str) -> str:
        """Handle complex multi-step requests."""
        self.log(f"Processing request: {user_request}")

        # Analyze request and plan workflow
        plan = self.call_llm(
            f"User request: {user_request}\n\n"
            f"Available agents:\n"
            f"- Inventory Agent (check stock, audit inventory)\n"
            f"- Customer Service Agent (orders, recommendations)\n"
            f"- Analytics Agent (reports, insights)\n\n"
            f"Identify which agents should be involved and what tasks they should perform. "
            f"Be specific and concise."
        )

        print(f"\n📋 Workflow Plan:\n{plan}\n")

        return plan


# Predefined Workflow Scenarios
async def workflow_vip_customer_order():
    """Scenario: Handle VIP customer order and upsell opportunity."""
    print("\n" + "="*70)
    print("SCENARIO 1: VIP Customer Order Processing & Upsell")
    print("="*70)

    coordinator = CoordinatorAgent()
    cs_agent = coordinator.customer_service_agent
    analytics_agent = coordinator.analytics_agent

    # Step 1: Check order status
    print("\n📦 Step 1: Check Order Status")
    order_status = await cs_agent.handle_order_inquiry("ORD001")
    print(order_status)

    # Step 2: Analyze customer for upsell
    print("\n📊 Step 2: Analyze Customer Profile")
    customer_insights = await analytics_agent.analyze_customer_segment("CUST001")
    print(customer_insights)

    # Step 3: Generate recommendations
    print("\n💡 Step 3: Generate Product Recommendations")
    recommendations = await cs_agent.recommend_products("CUST001", "Electronics")
    print(recommendations)


async def workflow_inventory_alert():
    """Scenario: Inventory alert and restocking workflow."""
    print("\n" + "="*70)
    print("SCENARIO 2: Inventory Alert & Restocking Analysis")
    print("="*70)

    coordinator = CoordinatorAgent()
    inv_agent = coordinator.inventory_agent

    # Audit all products
    print("\n📦 Performing Inventory Audit")
    skus = ["PROD001", "PROD002", "PROD003", "PROD004", "PROD005"]
    audit_report = await inv_agent.audit_inventory(skus)
    print(audit_report)


async def workflow_daily_business_review():
    """Scenario: Daily business review with multiple agents."""
    print("\n" + "="*70)
    print("SCENARIO 3: Daily Business Review")
    print("="*70)

    coordinator = CoordinatorAgent()
    analytics_agent = coordinator.analytics_agent
    inv_agent = coordinator.inventory_agent

    # Step 1: Generate sales report
    print("\n📈 Step 1: Sales Performance")
    sales_report = await analytics_agent.generate_business_report("week")
    print(sales_report)

    # Step 2: Check critical inventory
    print("\n📦 Step 2: Critical Inventory Check")
    critical_check = await inv_agent.check_stock("PROD004")  # Out of stock item
    print(f"\nData: {critical_check['data']}")
    print(f"\nAnalysis: {critical_check['analysis']}")


async def workflow_order_fulfillment():
    """Scenario: Complete order fulfillment workflow."""
    print("\n" + "="*70)
    print("SCENARIO 4: Order Fulfillment Workflow")
    print("="*70)

    coordinator = CoordinatorAgent()
    cs_agent = coordinator.customer_service_agent
    inv_agent = coordinator.inventory_agent

    order_id = "ORD002"

    # Step 1: Check order details
    print(f"\n📦 Step 1: Review Order {order_id}")
    order_data = await MCPToolExecutor.execute_tool(
        "process_order",
        {"order_id": order_id, "action": "retrieve"}
    )
    print(order_data)

    # Step 2: Verify inventory for items (PROD003)
    print("\n📦 Step 2: Verify Inventory")
    inv_check = await inv_agent.check_stock("PROD003")
    print(f"\nAnalysis: {inv_check['analysis']}")

    # Step 3: Ship the order
    print("\n🚚 Step 3: Process Shipment")
    shipment = await cs_agent.ship_order(order_id)
    print(shipment)


async def main_menu():
    """Interactive menu for running different scenarios."""
    print("\n" + "="*70)
    print("🤖 MULTI-AGENT E-COMMERCE SYSTEM")
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

    # Ask if user wants to continue
    again = input("\n\nRun another scenario? (y/n): ").strip().lower()
    if again == 'y':
        await main_menu()
    else:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    print("\n🔧 Initializing Multi-Agent System...")
    print(f"📡 Using OpenAI Model: {MODEL}")
    print(f"🔑 API Key: {os.getenv('OPENAI_API_KEY')[:20]}...")

    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")