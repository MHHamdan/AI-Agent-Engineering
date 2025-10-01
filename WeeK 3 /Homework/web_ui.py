"""
🚀 E-commerce Multi-Agent System - Modern Web UI
================================================
Beautiful, interactive web interface for the multi-agent e-commerce system.

Features:
- 🎨 Modern, professional design
- 💬 Real-time chat interface with agents
- 📊 Interactive data visualizations
- 🤖 Multi-agent workflow automation
- 📈 Live analytics dashboard
- 🎯 Quick action buttons
- 🔄 Workflow progress tracking

Launch: python web_ui.py
"""

import gradio as gr
import asyncio
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from typing import List, Tuple

# Import our multi-agent system
from multi_agent_demo import (
    InventoryAgent,
    CustomerServiceAgent,
    AnalyticsAgent,
    MCPToolExecutor
)

# Initialize agents globally
inventory_agent = InventoryAgent()
cs_agent = CustomerServiceAgent()
analytics_agent = AnalyticsAgent()

# Chat history storage
chat_history = []

# Custom CSS for modern look
custom_css = """
.gradio-container {
    font-family: 'Inter', sans-serif;
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    text-align: center;
}

.agent-card {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin: 1rem 0;
}

.metric-card {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem;
}

.status-success {
    color: #10b981;
    font-weight: 600;
}

.status-warning {
    color: #f59e0b;
    font-weight: 600;
}

.status-error {
    color: #ef4444;
    font-weight: 600;
}
"""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_timestamp():
    """Get formatted timestamp."""
    return datetime.now().strftime("%H:%M:%S")


def create_inventory_chart():
    """Create inventory status visualization."""
    products = {
        "Laptop Pro 15": 45,
        "Wireless Mouse": 150,
        "USB-C Cable": 8,
        "Ergonomic Keyboard": 0,
        "Monitor 27\"": 22
    }

    colors = []
    for qty in products.values():
        if qty == 0:
            colors.append('#ef4444')  # Red
        elif qty < 10:
            colors.append('#f59e0b')  # Orange
        else:
            colors.append('#10b981')  # Green

    fig = go.Figure(data=[
        go.Bar(
            x=list(products.keys()),
            y=list(products.values()),
            marker_color=colors,
            text=list(products.values()),
            textposition='auto',
        )
    ])

    fig.update_layout(
        title="📦 Current Inventory Status",
        xaxis_title="Product",
        yaxis_title="Stock Quantity",
        template="plotly_white",
        height=400,
        showlegend=False
    )

    return fig


def create_sales_chart():
    """Create sales performance visualization."""
    data = {
        'Date': ['Sep 15', 'Sep 20', 'Sep 28', 'Sep 29'],
        'Revenue': [1329.98, 349.99, 12.99, 42.98],
        'Orders': [1, 1, 1, 1]
    }

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data['Date'],
        y=data['Revenue'],
        mode='lines+markers',
        name='Revenue',
        line=dict(color='#667eea', width=3),
        marker=dict(size=10)
    ))

    fig.update_layout(
        title="📈 Sales Performance",
        xaxis_title="Date",
        yaxis_title="Revenue ($)",
        template="plotly_white",
        height=400
    )

    return fig


def create_customer_segment_chart():
    """Create customer segmentation pie chart."""
    segments = {
        'VIP': 1,
        'Gold': 1,
        'Regular': 1
    }

    colors = ['#667eea', '#764ba2', '#9b87f5']

    fig = go.Figure(data=[go.Pie(
        labels=list(segments.keys()),
        values=list(segments.values()),
        marker=dict(colors=colors),
        hole=0.4
    )])

    fig.update_layout(
        title="👥 Customer Segmentation",
        template="plotly_white",
        height=400
    )

    return fig


# =============================================================================
# AGENT INTERACTION FUNCTIONS
# =============================================================================

async def chat_with_agent(message: str, agent_type: str, history: List) -> Tuple[List, str]:
    """Chat interface with selected agent."""

    if not message.strip():
        return history, ""

    # Add user message
    history.append({"role": "user", "content": message})

    # Process based on agent type
    response = ""

    try:
        if agent_type == "Inventory Agent":
            # Extract SKU if mentioned
            if "PROD" in message.upper():
                sku = message.upper().split("PROD")[1][:3]
                sku = f"PROD{sku}"
                result = await inventory_agent.check_stock(sku)
                response = f"**Inventory Check for {sku}**\n\n{result['analysis']}\n\n```json\n{result['data']}\n```"
            else:
                response = "Please specify a product SKU (e.g., PROD001) to check inventory."

        elif agent_type == "Customer Service Agent":
            # Check if it's an order inquiry
            if "ORD" in message.upper():
                order_id = message.upper().split("ORD")[1][:3]
                order_id = f"ORD{order_id}"
                response = await cs_agent.handle_order_inquiry(order_id)
            elif "recommend" in message.lower() or "suggest" in message.lower():
                # Extract customer ID
                if "CUST" in message.upper():
                    cust_id = message.upper().split("CUST")[1][:3]
                    cust_id = f"CUST{cust_id}"
                    response = await cs_agent.recommend_products(cust_id)
                else:
                    response = "Please specify a customer ID (e.g., CUST001) for recommendations."
            else:
                response = "I can help with:\n- Order inquiries (mention order ID like ORD001)\n- Product recommendations (mention customer ID like CUST001)"

        elif agent_type == "Analytics Agent":
            if "report" in message.lower():
                period = "week"
                if "day" in message.lower():
                    period = "day"
                elif "month" in message.lower():
                    period = "month"
                response = await analytics_agent.generate_business_report(period)
            elif "CUST" in message.upper():
                cust_id = message.upper().split("CUST")[1][:3]
                cust_id = f"CUST{cust_id}"
                response = await analytics_agent.analyze_customer_segment(cust_id)
            else:
                response = "I can help with:\n- Sales reports (mention 'report' and period: day/week/month)\n- Customer analysis (mention customer ID like CUST001)"

        else:
            response = "Please select an agent type first."

    except Exception as e:
        response = f"❌ Error: {str(e)}"

    # Add agent response
    history.append({"role": "assistant", "content": response})

    return history, ""


async def quick_inventory_check(sku: str) -> str:
    """Quick inventory check function."""
    if not sku:
        return "⚠️ Please enter a product SKU (e.g., PROD001)"

    try:
        result = await inventory_agent.check_stock(sku.upper())
        output = f"## Inventory Status for {sku.upper()}\n\n"
        output += f"**Analysis:** {result['analysis']}\n\n"
        output += f"**Details:**\n```json\n{result['data']}\n```"
        return output
    except Exception as e:
        return f"❌ Error: {str(e)}"


async def quick_order_lookup(order_id: str) -> str:
    """Quick order lookup function."""
    if not order_id:
        return "⚠️ Please enter an order ID (e.g., ORD001)"

    try:
        result = await cs_agent.handle_order_inquiry(order_id.upper())
        return result
    except Exception as e:
        return f"❌ Error: {str(e)}"


async def quick_customer_analysis(customer_id: str) -> str:
    """Quick customer analysis function."""
    if not customer_id:
        return "⚠️ Please enter a customer ID (e.g., CUST001)"

    try:
        result = await analytics_agent.analyze_customer_segment(customer_id.upper())
        return result
    except Exception as e:
        return f"❌ Error: {str(e)}"


async def generate_report(period: str) -> str:
    """Generate sales report."""
    try:
        result = await analytics_agent.generate_business_report(period.lower())
        return result
    except Exception as e:
        return f"❌ Error: {str(e)}"


async def run_workflow(workflow_name: str) -> str:
    """Run a complete multi-agent workflow."""
    output = f"# 🚀 Running Workflow: {workflow_name}\n\n"
    output += f"**Started at:** {format_timestamp()}\n\n"
    output += "---\n\n"

    try:
        if workflow_name == "VIP Customer Upsell":
            output += "## Step 1: Check Order Status\n\n"
            order = await cs_agent.handle_order_inquiry("ORD001")
            output += order + "\n\n---\n\n"

            output += "## Step 2: Analyze Customer Profile\n\n"
            analysis = await analytics_agent.analyze_customer_segment("CUST001")
            output += analysis + "\n\n---\n\n"

            output += "## Step 3: Generate Recommendations\n\n"
            recs = await cs_agent.recommend_products("CUST001", "Electronics")
            output += recs + "\n\n"

        elif workflow_name == "Inventory Audit":
            output += "## Performing Complete Inventory Audit\n\n"
            skus = ["PROD001", "PROD002", "PROD003", "PROD004", "PROD005"]
            audit = await inventory_agent.audit_inventory(skus)
            output += audit + "\n\n"

        elif workflow_name == "Daily Business Review":
            output += "## Step 1: Sales Performance\n\n"
            sales = await analytics_agent.generate_business_report("week")
            output += sales + "\n\n---\n\n"

            output += "## Step 2: Critical Inventory Check\n\n"
            inv = await inventory_agent.check_stock("PROD004")
            output += f"**Analysis:** {inv['analysis']}\n\n"
            output += f"**Data:** {inv['data']}\n\n"

        elif workflow_name == "Order Fulfillment":
            output += "## Step 1: Order Details\n\n"
            order_data = await MCPToolExecutor.execute_tool(
                "process_order",
                {"order_id": "ORD002", "action": "retrieve"}
            )
            output += f"```json\n{order_data}\n```\n\n---\n\n"

            output += "## Step 2: Inventory Verification\n\n"
            inv = await inventory_agent.check_stock("PROD003")
            output += f"{inv['analysis']}\n\n---\n\n"

            output += "## Step 3: Process Shipment\n\n"
            ship = await cs_agent.ship_order("ORD002")
            output += ship + "\n\n"

        output += f"\n\n**✅ Workflow completed at:** {format_timestamp()}"

    except Exception as e:
        output += f"\n\n❌ **Error:** {str(e)}"

    return output


# =============================================================================
# CREATE GRADIO INTERFACE
# =============================================================================

def create_interface():
    """Create the main Gradio interface."""

    with gr.Blocks(css=custom_css, title="E-commerce Multi-Agent System", theme=gr.themes.Soft()) as app:

        # Header
        gr.HTML("""
            <div class="header">
                <h1>🤖 E-commerce Multi-Agent System</h1>
                <p style="font-size: 1.2rem; margin-top: 1rem;">
                    Powered by MCP Server & AI Agents
                </p>
            </div>
        """)

        # Main tabs
        with gr.Tabs() as tabs:

            # ==================== DASHBOARD TAB ====================
            with gr.Tab("📊 Dashboard"):
                gr.Markdown("## Real-Time Business Metrics")

                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML("""
                            <div class="metric-card">
                                <h3>💰 Total Revenue</h3>
                                <h2 style="color: #667eea;">$1,735.94</h2>
                                <p>+12% vs last period</p>
                            </div>
                        """)

                    with gr.Column(scale=1):
                        gr.HTML("""
                            <div class="metric-card">
                                <h3>📦 Total Orders</h3>
                                <h2 style="color: #10b981;">4</h2>
                                <p>This week</p>
                            </div>
                        """)

                    with gr.Column(scale=1):
                        gr.HTML("""
                            <div class="metric-card">
                                <h3>👥 Active Customers</h3>
                                <h2 style="color: #764ba2;">3</h2>
                                <p>1 VIP, 1 Gold, 1 Regular</p>
                            </div>
                        """)

                    with gr.Column(scale=1):
                        gr.HTML("""
                            <div class="metric-card">
                                <h3>⚠️ Stock Alerts</h3>
                                <h2 style="color: #ef4444;">2</h2>
                                <p>1 critical, 1 warning</p>
                            </div>
                        """)

                with gr.Row():
                    with gr.Column():
                        inventory_plot = gr.Plot(value=create_inventory_chart())
                    with gr.Column():
                        sales_plot = gr.Plot(value=create_sales_chart())

                with gr.Row():
                    with gr.Column():
                        segment_plot = gr.Plot(value=create_customer_segment_chart())
                    with gr.Column():
                        gr.Markdown("""
                        ### 📋 Quick Insights

                        **Top Performing Products:**
                        1. 🖱️ Wireless Mouse - 2 units sold
                        2. 💻 Laptop Pro 15 - 1 unit sold

                        **Inventory Alerts:**
                        - ⛔ Ergonomic Keyboard - OUT OF STOCK
                        - ⚠️ USB-C Cable - LOW STOCK (8 units)

                        **Customer Highlights:**
                        - 💎 VIP Customer: Alice Johnson ($4,500 LTV)
                        - 📈 Average Order Value: $433.99

                        **Recommendations:**
                        - Restock PROD004 immediately
                        - Consider upselling to VIP customers
                        - Monitor PROD003 stock levels
                        """)

            # ==================== AGENT CHAT TAB ====================
            with gr.Tab("💬 Chat with Agents"):
                gr.Markdown("## Talk to Specialized AI Agents")

                with gr.Row():
                    agent_selector = gr.Dropdown(
                        choices=["Inventory Agent", "Customer Service Agent", "Analytics Agent"],
                        value="Inventory Agent",
                        label="Select Agent",
                        info="Choose which agent you want to chat with"
                    )

                chatbot = gr.Chatbot(
                    label="Agent Conversation",
                    height=500,
                    type="messages"
                )

                with gr.Row():
                    msg = gr.Textbox(
                        label="Your Message",
                        placeholder="Type your message here... (e.g., 'Check inventory for PROD001')",
                        scale=4
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)

                gr.Markdown("""
                ### 💡 Example Queries:

                **Inventory Agent:**
                - "Check inventory for PROD001"
                - "What's the stock level for PROD003?"

                **Customer Service Agent:**
                - "Show me order ORD001"
                - "Recommend products for CUST001"

                **Analytics Agent:**
                - "Generate a weekly sales report"
                - "Analyze customer CUST001"
                """)

                # Chat functionality
                send_btn.click(
                    fn=chat_with_agent,
                    inputs=[msg, agent_selector, chatbot],
                    outputs=[chatbot, msg]
                )
                msg.submit(
                    fn=chat_with_agent,
                    inputs=[msg, agent_selector, chatbot],
                    outputs=[chatbot, msg]
                )

            # ==================== QUICK ACTIONS TAB ====================
            with gr.Tab("⚡ Quick Actions"):
                gr.Markdown("## Fast Access to Common Tasks")

                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 📦 Inventory Check")
                        inv_sku = gr.Textbox(
                            label="Product SKU",
                            placeholder="PROD001",
                            value="PROD001"
                        )
                        inv_btn = gr.Button("Check Inventory", variant="primary")
                        inv_output = gr.Markdown()

                        inv_btn.click(
                            fn=quick_inventory_check,
                            inputs=[inv_sku],
                            outputs=[inv_output]
                        )

                    with gr.Column():
                        gr.Markdown("### 📋 Order Lookup")
                        order_id = gr.Textbox(
                            label="Order ID",
                            placeholder="ORD001",
                            value="ORD001"
                        )
                        order_btn = gr.Button("Look Up Order", variant="primary")
                        order_output = gr.Markdown()

                        order_btn.click(
                            fn=quick_order_lookup,
                            inputs=[order_id],
                            outputs=[order_output]
                        )

                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 👤 Customer Analysis")
                        cust_id = gr.Textbox(
                            label="Customer ID",
                            placeholder="CUST001",
                            value="CUST001"
                        )
                        cust_btn = gr.Button("Analyze Customer", variant="primary")
                        cust_output = gr.Markdown()

                        cust_btn.click(
                            fn=quick_customer_analysis,
                            inputs=[cust_id],
                            outputs=[cust_output]
                        )

                    with gr.Column():
                        gr.Markdown("### 📊 Sales Report")
                        report_period = gr.Radio(
                            choices=["Day", "Week", "Month", "Year"],
                            value="Week",
                            label="Report Period"
                        )
                        report_btn = gr.Button("Generate Report", variant="primary")
                        report_output = gr.Markdown()

                        report_btn.click(
                            fn=generate_report,
                            inputs=[report_period],
                            outputs=[report_output]
                        )

            # ==================== WORKFLOWS TAB ====================
            with gr.Tab("🔄 Automated Workflows"):
                gr.Markdown("## Multi-Agent Workflow Automation")

                workflow_choice = gr.Radio(
                    choices=[
                        "VIP Customer Upsell",
                        "Inventory Audit",
                        "Daily Business Review",
                        "Order Fulfillment"
                    ],
                    value="VIP Customer Upsell",
                    label="Select Workflow"
                )

                gr.Markdown("""
                ### 📖 Workflow Descriptions:

                **VIP Customer Upsell:** Check order status → Analyze customer profile → Generate personalized recommendations

                **Inventory Audit:** Check all products → Identify critical issues → Generate restocking priorities

                **Daily Business Review:** Generate sales report → Check critical inventory → Provide strategic insights

                **Order Fulfillment:** Retrieve order → Verify inventory → Process shipment → Send notification
                """)

                workflow_btn = gr.Button("🚀 Run Workflow", variant="primary", size="lg")
                workflow_output = gr.Markdown()

                workflow_btn.click(
                    fn=run_workflow,
                    inputs=[workflow_choice],
                    outputs=[workflow_output]
                )

            # ==================== ABOUT TAB ====================
            with gr.Tab("ℹ️ About"):
                gr.Markdown("""
                # 🤖 E-commerce Multi-Agent System

                ## Overview

                This is a cutting-edge multi-agent system built for e-commerce operations.
                It demonstrates how multiple specialized AI agents can collaborate to automate
                complex business workflows.

                ## 🏗️ Architecture

                ### MCP Server (Backend)
                - **5 Enterprise Tools:** Inventory management, order processing, customer analytics,
                  product recommendations, and sales reporting
                - **Protocol:** Model Context Protocol (MCP)
                - **Transport:** stdio

                ### AI Agents (Intelligence Layer)
                1. **Inventory Agent** - Stock management and restocking
                2. **Customer Service Agent** - Order handling and customer engagement
                3. **Analytics Agent** - Business intelligence and reporting

                ### Web UI (Frontend)
                - **Framework:** Gradio
                - **Visualizations:** Plotly
                - **Features:** Real-time dashboards, chat interface, workflow automation

                ## 🎯 Features

                ✅ Real-time business metrics dashboard
                ✅ Interactive chat with specialized agents
                ✅ Quick actions for common tasks
                ✅ Automated multi-agent workflows
                ✅ Data visualizations and analytics
                ✅ Professional, modern UI

                ## 🚀 Technology Stack

                - **Backend:** Python, FastMCP
                - **Agents:** Custom multi-agent architecture
                - **Frontend:** Gradio, Plotly, Pandas
                - **AI:** Simulated intelligence (no API costs)

                ## 📝 Created By

                **Mohammed**
                AI Agent Engineering - Week 3 Project
                E-commerce Multi-Agent System with MCP Integration

                ## 📄 License

                Educational project for AI Agent Engineering course.

                ---

                ### 🔗 Quick Links

                - View source code in project directory
                - Read full documentation in README.md
                - Check testing evidence in TESTING_EVIDENCE.md

                **Version:** 1.0.0
                **Last Updated:** September 30, 2025
                """)

        # Footer
        gr.HTML("""
            <div style="text-align: center; margin-top: 2rem; padding: 1rem; color: #666;">
                <p>🤖 Powered by MCP Server & Multi-Agent AI | Built with Gradio</p>
            </div>
        """)

    return app


# =============================================================================
# LAUNCH APPLICATION
# =============================================================================

if __name__ == "__main__":
    print("🚀 Launching E-commerce Multi-Agent System Web UI...")
    print("📡 Initializing agents...")
    print("🎨 Building interface...")
    print()

    app = create_interface()

    print("✅ System ready!")
    print("🌐 Opening web browser...")
    print()

    # Launch with share=True to get a public URL for demos
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,  # Enable public URL sharing
        show_error=True,
        quiet=False
    )