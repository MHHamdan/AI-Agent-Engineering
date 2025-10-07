#!/bin/bash

# Launch script for E-commerce Multi-Agent Web UI

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                                                                    ║"
echo "║       🚀 E-commerce Multi-Agent System - Web UI Launcher          ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🔧 Initializing system..."
echo ""

# Change to project directory
cd "$(dirname "$0")"

# Check if dependencies are installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed"
    echo "📦 Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ Dependencies found"
echo "🚀 Starting web server..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Dashboard Features:"
echo "  • Real-time business metrics"
echo "  • Interactive data visualizations"
echo "  • Inventory status monitoring"
echo "  • Sales performance tracking"
echo ""
echo "💬 Agent Chat:"
echo "  • Talk to Inventory Agent"
echo "  • Talk to Customer Service Agent"
echo "  • Talk to Analytics Agent"
echo ""
echo "⚡ Quick Actions:"
echo "  • Check inventory"
echo "  • Look up orders"
echo "  • Analyze customers"
echo "  • Generate reports"
echo ""
echo "🔄 Automated Workflows:"
echo "  • VIP Customer Upsell"
echo "  • Inventory Audit"
echo "  • Daily Business Review"
echo "  • Order Fulfillment"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 The web interface will open automatically in your browser"
echo "📍 URL: http://localhost:7860"
echo ""
echo "⏹️  Press Ctrl+C to stop the server"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Launch the web UI
uv run python web_ui.py

echo ""
echo "👋 Server stopped. Goodbye!"