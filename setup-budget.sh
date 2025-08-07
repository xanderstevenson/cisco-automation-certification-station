#!/bin/bash

# Google Cloud Budget Setup - $5/Month with Recommended Alerts
# Run this script to set up cost protection for your Cisco Live presentation

echo "🛡️  Setting up $5/month budget protection..."

# Get your billing account ID
BILLING_ACCOUNT=$(gcloud billing accounts list --format="value(name)" --limit=1)

if [ -z "$BILLING_ACCOUNT" ]; then
    echo "❌ No billing account found. Please set up billing first:"
    echo "   https://console.cloud.google.com/billing"
    exit 1
fi

echo "📊 Using billing account: $BILLING_ACCOUNT"

# Create budget with recommended thresholds
gcloud billing budgets create \
    --billing-account="$BILLING_ACCOUNT" \
    --display-name="Cisco Chatbot Budget - $5 Limit" \
    --budget-amount=5.00 \
    --threshold-rule=percent=50,basis=CURRENT_SPEND \
    --threshold-rule=percent=90,basis=CURRENT_SPEND \
    --threshold-rule=percent=100,basis=CURRENT_SPEND \
    --format="table(name,displayName,budgetFilter.projects,amount)"

echo ""
echo "✅ Budget alerts configured:"
echo "   • 50% threshold ($2.50) - Early warning"
echo "   • 90% threshold ($4.50) - Urgent warning" 
echo "   • 100% threshold ($5.00) - Budget exceeded"
echo ""
echo "📧 You'll receive email alerts at each threshold"
echo "🌐 View budget: https://console.cloud.google.com/billing/budgets"
echo ""
echo "⚠️  IMPORTANT: Budget alerts are notifications only."
echo "   Your service will continue running unless you manually stop it."
echo "   Consider implementing rate limiting for additional protection."
