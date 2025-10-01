#!/bin/bash

# Demo Launch Script with Public URL Sharing
# This creates a shareable link for presentations

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                                                                    ║"
echo "║     🌐 E-commerce Multi-Agent System - DEMO MODE                  ║"
echo "║          Creating Shareable Public URL...                         ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Starting demo server with public URL sharing..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 What's happening:"
echo "  • Launching web UI with Gradio"
echo "  • Creating secure tunnel for public access"
echo "  • Generating shareable URL"
echo ""
echo "⏱️  This takes about 10-15 seconds..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Change to project directory
cd "$(dirname "$0")"

# Launch with sharing enabled
uv run python web_ui.py

echo ""
echo "👋 Demo server stopped. Goodbye!"