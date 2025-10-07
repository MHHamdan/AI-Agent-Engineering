# Quick Start Guide - E-commerce MCP Server

## 30-Second Setup

```bash
# 1. Navigate to project
cd "/home/mohammed/Documents/AI-Agent-Engineering/WeeK 3 /Homework"

# 2. Install dependencies (if not already done)
uv sync

# 3. Test the server
uv run python test_server.py

# 4. Run the MCP server
uv run python main.py
```

## 🎯 What You Get

**5 Enterprise-Ready MCP Tools:**

1. `check_inventory_status` - Real-time stock tracking
2. `process_order` - Order lifecycle management
3. `get_customer_analytics` - Customer insights & segmentation
4. `generate_product_recommendations` - AI-powered personalization
5. `generate_sales_report` - Business intelligence & analytics

## 🔧 Configure Your MCP Client

### Claude Desktop

Edit config file:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

Add this configuration:

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

### Cursor IDE

Add to workspace settings or `.cursorrules`:

```json
{
  "mcp": {
    "servers": {
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
}
```

##  Example Queries for AI Agents

Once configured, try these queries:

```
"Check the inventory status for product PROD001"

"Get analytics for customer CUST001"

"Generate product recommendations for CUST001 in the Electronics category"

"Show me the order details for ORD001"

"Generate a weekly sales report"

"Which products are low on stock?"

"Ship order ORD002"
```

## Quick Test

```bash
# Verify all tools work
uv run python test_server.py

# Expected output: All tests pass ✅
```

##  More Information

- **Full Documentation:** See `README.md`
- **Testing Evidence:** See `TESTING_EVIDENCE.md`
- **Reflection:** See `week_03_hw_template.py` (lines 204-234)
- **Submission Details:** See `SUBMISSION_SUMMARY.md`

##  Troubleshooting

**Problem:** `uv: command not found`
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Problem:** Module import errors
```bash
# Reinstall dependencies
uv sync --reinstall
```

**Problem:** Server not responding
```bash
# Check server starts
uv run python main.py
# Should wait for stdin (this is normal for MCP servers)
# Press Ctrl+C to exit
```

## ✅ Verification Checklist

- [ ] Dependencies installed (`uv sync`)
- [ ] Test script passes (`uv run python test_server.py`)
- [ ] MCP client configured (Claude Desktop/Cursor)
- [ ] Server responds to agent queries

##  What This Demonstrates

✅ Complete MCP server implementation
✅ 5 production-ready tools
✅ Comprehensive error handling
✅ Enterprise-level architecture
✅ Full documentation & testing
✅ Real-world business applications

---

**Ready to use!** Configure your MCP client and start querying the tools through AI agents.