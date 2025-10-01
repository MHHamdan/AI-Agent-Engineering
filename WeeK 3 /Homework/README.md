# E-commerce MCP Server - Week 3 Homework

## Overview

This is a comprehensive Model Context Protocol (MCP) server implementation for e-commerce operations. The server provides 5 enterprise-level tools that can be consumed by AI agents through MCP clients like Claude Desktop, Cursor, or custom implementations.

## MCP Tools Implemented

### 1. check_inventory_status
- **Purpose**: Real-time inventory tracking and stock management
- **Parameters**: `sku` (Product SKU identifier)
- **Returns**: Comprehensive inventory information including stock levels, pricing, warehouse location, and availability status
- **Use Case**: Order fulfillment systems, inventory audits, stock alerts

### 2. process_order
- **Purpose**: Complete order lifecycle management
- **Parameters**:
  - `order_id` (Order identifier)
  - `action` (retrieve, ship, cancel, or complete)
- **Returns**: Order details and action confirmation
- **Use Case**: Order management systems, fulfillment workflows, customer service

### 3. get_customer_analytics
- **Purpose**: Customer insights and segmentation
- **Parameters**: `customer_id` (Customer identifier)
- **Returns**: Detailed customer analytics including lifetime value, purchase history, and segment classification
- **Use Case**: CRM systems, marketing campaigns, customer retention strategies

### 4. generate_product_recommendations
- **Purpose**: AI-powered product recommendations
- **Parameters**:
  - `customer_id` (Customer identifier)
  - `category` (Optional category filter)
- **Returns**: Personalized product recommendations with relevance scores
- **Use Case**: Upselling, cross-selling, personalized shopping experiences

### 5. generate_sales_report
- **Purpose**: Business intelligence and sales analytics
- **Parameters**: `period` (day, week, month, or year)
- **Returns**: Comprehensive sales report with key metrics, trends, and insights
- **Use Case**: Executive dashboards, forecasting, strategic planning

## Installation

### Prerequisites
- Python 3.13+ (or Python 3.10+)
- uv package manager

### Setup

```bash
# Install dependencies
uv sync

# Run the MCP server
uv run python main.py
```

## Configuration for MCP Clients

### Claude Desktop Configuration

Add this to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ecommerce-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/mohammed/Documents/AI-Agent-Engineering/WeeK 3 /Homework",
        "run",
        "python",
        "main.py"
      ]
    }
  }
}
```

### Cursor Configuration

In Cursor, add to your `.cursorrules` or workspace settings:

```json
{
  "mcp": {
    "servers": {
      "ecommerce-mcp-server": {
        "command": "uv",
        "args": ["--directory", "/path/to/Homework", "run", "python", "main.py"],
        "env": {}
      }
    }
  }
}
```

## Usage Examples

### Example 1: Check Inventory
```
Agent Query: "Check the inventory status for product PROD001"

Response:
{
  "product_name": "Laptop Pro 15",
  "sku": "PROD001",
  "stock_quantity": 45,
  "price": "$1299.99",
  "category": "Electronics",
  "warehouse_location": "WH-001",
  "status": "✅ In Stock"
}
```

### Example 2: Process Order
```
Agent Query: "Retrieve order ORD002 details"

Response:
{
  "order_id": "ORD002",
  "customer_id": "CUST002",
  "items": ["PROD003"],
  "item_count": 1,
  "total_amount": "$12.99",
  "status": "pending",
  "order_date": "2025-09-28"
}
```

### Example 3: Customer Analytics
```
Agent Query: "Get analytics for customer CUST001"

Response:
{
  "customer_id": "CUST001",
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "total_orders": 15,
  "lifetime_value": "$4500.50",
  "customer_segment": "VIP",
  "engagement_level": "High",
  "recommendation": "Offer exclusive early access to new products and premium customer support"
}
```

### Example 4: Product Recommendations
```
Agent Query: "Generate product recommendations for CUST001 in Electronics"

Response:
{
  "customer": "Alice Johnson",
  "customer_id": "CUST001",
  "recommendations": [
    {
      "product_name": "Laptop Pro 15",
      "sku": "PROD001",
      "price": "$1299.99",
      "relevance_score": "95%",
      "reason": "Based on your VIP status and purchase history"
    }
  ],
  "total_recommendations": 1
}
```

### Example 5: Sales Report
```
Agent Query: "Generate a weekly sales report"

Response:
{
  "report_period": "Week",
  "generated_at": "2025-09-29 22:45:00",
  "sales_metrics": {
    "total_revenue": "$1735.94",
    "total_orders": 4,
    "average_order_value": "$433.99"
  },
  "order_status_breakdown": {
    "shipped": 1,
    "pending": 1,
    "delivered": 1,
    "processing": 1
  },
  "top_selling_product": {
    "name": "Wireless Mouse",
    "units_sold": 2
  },
  "inventory_alerts": {
    "low_stock_items": ["USB-C Cable"],
    "out_of_stock_items": ["Ergonomic Keyboard"]
  },
  "insights": [
    "Revenue growth trending positive",
    "1 items need restocking soon",
    "Order fulfillment rate: 25.0%"
  ]
}
```

## Testing

### Manual Testing with MCP Inspector

```bash
# Install MCP Inspector
npx @modelcontextprotocol/inspector uv --directory . run python main.py
```

### Testing with Python Client

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_tools():
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "main.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print("Available tools:", [tool.name for tool in tools.tools])

            # Test check_inventory_status
            result = await session.call_tool("check_inventory_status", {"sku": "PROD001"})
            print("Inventory check result:", result)

asyncio.run(test_mcp_tools())
```

## Architecture Highlights

### Mock Database Layer
- In-memory data stores simulating production databases
- Easy to replace with real database connections (PostgreSQL, MongoDB, etc.)
- Includes realistic business data with proper relationships

### Error Handling
- Comprehensive try-catch blocks in all tools
- Validation of input parameters
- User-friendly error messages
- Graceful degradation

### Tool Design Principles
- Single Responsibility: Each tool has one clear purpose
- Comprehensive Documentation: Detailed docstrings with examples
- Type Safety: Full type hints for parameters and returns
- JSON Responses: Structured data for easy parsing by AI agents

## Enterprise Applications

This MCP server demonstrates real-world enterprise use cases:

1. **Inventory Management**: Real-time stock tracking prevents overselling
2. **Order Fulfillment**: Automated workflows reduce manual processing
3. **Customer Intelligence**: Data-driven insights improve retention
4. **Personalization**: AI-powered recommendations increase conversions
5. **Business Analytics**: Executive-level reporting enables strategic decisions

## Project Structure

```
Homework/
├── main.py                 # MCP server implementation
├── pyproject.toml         # Project dependencies (uv)
├── README.md             # This file
├── TESTING_EVIDENCE.md   # Test results and screenshots
└── week_03_hw_template.py # Original homework template
```

## Author

Mohammed - AI Agent Engineering Week 3 Homework

## License

Educational project for AI Agent Engineering course.