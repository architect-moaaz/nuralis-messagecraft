# MessageCraft Production Setup Guide

This guide will help you set up MessageCraft in production mode with Google OAuth, Stripe payments, and credit-based kit generation.

## Features in Production Mode

- **Google OAuth Authentication**: Users can sign in with Google
- **Credit System**: Users get 1 free kit, then must purchase credits
- **Stripe Integration**: Accept payments for credit packages
- **Kit Generation Limits**: Enforced limits based on credits
- **Secure Authentication**: JWT tokens with bcrypt password hashing

## Prerequisites

1. **Supabase Account**: For database and authentication
2. **Google Cloud Console**: For OAuth 2.0 credentials
3. **Stripe Account**: For payment processing
4. **Anthropic API Key**: For AI generation

## Step 1: Database Setup

1. Run the migrations in your Supabase SQL editor:
   ```sql
   -- First run schema.sql
   -- Then run migrations/002_add_credits_system.sql
   ```

2. Enable Row Level Security (RLS) on all tables

## Step 2: Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: 
     - `http://localhost:8000/api/v1/auth/google/callback` (development)
     - `https://yourdomain.com/api/v1/auth/google/callback` (production)
5. Copy the Client ID and Client Secret

## Step 3: Stripe Setup

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Create products and prices for:
   
   **Credit Packages:**
   - 10 Credits - $99
   - 50 Credits - $399
   - 100 Credits - $699
   
   **Subscription Plans (optional):**
   - Basic - $79/month
   - Professional - $149/month
   - Agency - $299/month

3. Copy the Price IDs for each product
4. Set up webhook endpoint:
   - URL: `https://yourdomain.com/api/v1/stripe-webhook`
   - Events: `checkout.session.completed`, `payment_intent.succeeded`
5. Copy the webhook signing secret

## Step 4: Environment Configuration

1. Copy the production environment template:
   ```bash
   cp backend/.env.production.example backend/.env.production
   ```

2. Fill in all required values:
   ```env
   # Set to production
   ENVIRONMENT=production
   
   # Generate a secure secret key (32+ characters)
   SECRET_KEY=your-very-secure-secret-key-here
   
   # Add your API keys
   ANTHROPIC_API_KEY=sk-ant-...
   
   # Supabase configuration
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_KEY=eyJ...
   SUPABASE_SERVICE_ROLE_KEY=eyJ...
   DATABASE_URL=postgresql://...
   
   # Google OAuth
   GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-...
   GOOGLE_REDIRECT_URI=https://yourdomain.com/api/v1/auth/google/callback
   
   # Stripe
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   
   # Add all Stripe Price IDs
   STRIPE_PRICE_CREDITS_10=price_xxx
   STRIPE_PRICE_CREDITS_50=price_xxx
   STRIPE_PRICE_CREDITS_100=price_xxx
   
   # Frontend URL
   FRONTEND_URL=https://yourdomain.com
   ```

## Step 5: Deploy Backend

### Using Docker:

1. Build the production image:
   ```bash
   docker build -f backend/Dockerfile.production -t messagecraft-backend:production ./backend
   ```

2. Run with production environment:
   ```bash
   docker run --env-file backend/.env.production -p 8000:8000 messagecraft-backend:production
   ```

### Using Docker Compose:

1. Update `docker-compose.yml` to use production settings
2. Run:
   ```bash
   docker-compose --env-file backend/.env.production up -d
   ```

## Step 6: Frontend Configuration

Update your frontend to:

1. Add Google Sign-In button
2. Show credit balance
3. Add credit purchase flow
4. Handle generation limits

Example frontend integration:
```javascript
// Check if user can generate
const response = await fetch('/api/v1/check-generation-eligibility', {
  headers: { 'Authorization': `Bearer ${token}` }
});

if (!response.ok) {
  // Show credit purchase options
  showCreditPurchaseModal();
}
```

## Step 7: Testing Production Features

1. **Test Free Kit Generation**:
   - Register new user
   - Generate one kit (should work)
   - Try to generate second kit (should require credits)

2. **Test Credit Purchase**:
   - Click purchase credits
   - Complete Stripe checkout
   - Verify credits added to account

3. **Test Google OAuth**:
   - Click "Sign in with Google"
   - Complete OAuth flow
   - Verify account created/linked

## Security Checklist

- [ ] Strong SECRET_KEY configured
- [ ] HTTPS enabled on production domain
- [ ] Database RLS policies active
- [ ] API keys stored securely
- [ ] CORS configured for your domain only
- [ ] Rate limiting implemented
- [ ] Error logging configured

## Monitoring

1. Set up Stripe webhook monitoring
2. Monitor Supabase database usage
3. Track API errors and performance
4. Monitor credit usage patterns

## Support

For issues or questions:
- Check logs: `docker logs messagecraft-backend`
- Verify environment variables are loaded
- Test database connectivity
- Verify Stripe webhook delivery