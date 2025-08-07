# Cost Control Setup - $5/Month Budget Protection

## 🛡️ Quick Setup for Cisco Live Amsterdam

This guide helps you set up cost protection before your Cisco Live presentation to prevent unexpected charges from high traffic.

## Step 1: Set Up Google Cloud Budget Alert

### Option A: Using the Script (Recommended)
```bash
# Make the script executable
chmod +x setup-budget.sh

# Run the budget setup
./setup-budget.sh
```

### Option B: Manual Setup via Console
1. Go to [Google Cloud Billing Budgets](https://console.cloud.google.com/billing/budgets)
2. Click "Create Budget"
3. Set these values:
   - **Name**: "Cisco Chatbot Budget - $5 Limit"
   - **Budget Amount**: $5.00
   - **Time Range**: Monthly
   - **Alert Thresholds**: 50%, 90%, 100%
4. Add your email for notifications
5. Click "Finish"

## Step 2: Deploy Rate Limiting

The rate limiting code has been added to `streamlit_app.py`. Deploy it:

```bash
# Commit the rate limiting changes
git add streamlit_app.py
git commit -m "Add rate limiting: 10 requests/minute for cost control"
git push

# Deploy to Google Cloud Run
gcloud run deploy cisco-automation-certification-station \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

## What You Get

### Budget Protection
- **Email alerts** at $2.50 (50%), $4.50 (90%), and $5.00 (100%)
- **Early warning** system to monitor costs
- **Manual control** - you decide when to stop the service

### Rate Limiting
- **10 requests per minute** per user (IP-based)
- **Prevents abuse** and runaway costs
- **User-friendly messages** explaining the limit
- **Usage indicators** when approaching limit

## Expected Costs

| Traffic Level | Daily Queries | Monthly Cost |
|---------------|---------------|--------------|
| **Current** | 50-100 | $0.05-0.50 |
| **Cisco Live Spike** | 500-1000 | $2-5 |
| **High Sustained** | 2000+ | $5-15 |

## Monitoring Your Usage

### Check Current Costs
```bash
# View current billing
gcloud billing accounts list
gcloud billing projects describe YOUR_PROJECT_ID
```

### View Budget Status
- **Console**: https://console.cloud.google.com/billing/budgets
- **Alerts**: Check your email for threshold notifications

### Monitor Service Usage
- **Cloud Run Metrics**: https://console.cloud.google.com/run
- **Request counts**, **error rates**, **response times**

## Emergency Stop

If costs spike unexpectedly:

```bash
# Stop the service immediately
gcloud run services update cisco-automation-certification-station \
    --region us-central1 \
    --min-instances 0 \
    --max-instances 0

# Or delete the service entirely
gcloud run services delete cisco-automation-certification-station \
    --region us-central1
```

## Testing Rate Limiting

Test locally before your presentation:

```bash
# Run locally
streamlit run streamlit_app.py

# Test rate limiting by sending 11+ requests quickly
# You should see the rate limit message after 10 requests
```

## ✅ Pre-Presentation Checklist

- [ ] Budget alert set up with $5 limit
- [ ] Email notifications configured
- [ ] Rate limiting deployed and tested
- [ ] Emergency stop commands ready
- [ ] Monitoring dashboard bookmarked

## Support

If you hit the budget limit during Cisco Live:
1. **Don't panic** - the system will keep working
2. **Check your email** for budget alert details
3. **Monitor usage** in Google Cloud Console
4. **Scale down** if needed using emergency stop commands

Your presentation will be great! 🚀
