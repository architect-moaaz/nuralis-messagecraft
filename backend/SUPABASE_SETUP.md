# Supabase Setup Guide

This guide will help you configure MessageCraft to use your Supabase database.

## ⚠️ IMPORTANT: API Keys Required

The example API keys in your `.env` file need to be replaced with your real Supabase keys.

### Get Your Real API Keys:

1. Go to: https://app.supabase.com
2. Select your project: `cuslsfwlfpcbonvaferb`
3. Go to Settings → API
4. Copy the **anon public** key and **service_role secret** key
5. Update your `.env` file with these real keys

## Configuration Status

Your Supabase configuration template is set up:

- **Supabase URL**: `https://cuslsfwlfpcbonvaferb.supabase.co` ✅
- **Database Password**: Configured ✅  
- **API Keys**: ❌ Need real keys from dashboard
- **Environment**: Template ready in `.env` file

## Next Steps

### 1. Install Dependencies

Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Initialize Database Schema (Optional)

If your Supabase database doesn't have the required tables, run:

```bash
python init_database.py
```

This will create the following tables:
- `user_sessions` - Stores messaging playbooks
- `usage_tracking` - Tracks feature usage for billing
- `users` - User account information
- `payments` - Payment and subscription data

### 3. Test the Connection (Optional)

Verify everything is working:

```bash
python test_simple_supabase.py
```

This will test:
- ✅ Database connection
- ✅ Basic table operations
- ✅ Insert/Select/Delete functionality

### 4. Start the API Server

Start the enhanced API server that uses Supabase:

```bash
python enhanced_api.py
```

Or with uvicorn:

```bash
uvicorn enhanced_api:app --host 127.0.0.1 --port 8002 --reload
```

## Environment Variables

The following environment variables are now configured in your `.env` file:

```env
# Supabase Configuration
SUPABASE_URL=https://cuslsfwlfpcbonvaferb.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# PostgreSQL Direct Connection
DATABASE_URL=postgresql://postgres:Qaz%233wsx@db.cuslsfwlfpcbonvaferb.supabase.co:5432/postgres
```

## API Endpoints

With Supabase configured, you can use these endpoints:

- `POST /api/v1/generate-playbook` - Generate messaging playbooks
- `GET /api/v1/user/playbooks` - Get user's playbooks
- `GET /api/v1/playbook/{id}` - Get specific playbook
- `DELETE /api/v1/playbook/{id}` - Delete playbook
- `GET /api/v1/playbook-status/{id}` - Check generation status

## Troubleshooting

### Connection Issues

If you get connection errors:

1. Verify your Supabase project is active
2. Check that Row Level Security (RLS) policies allow your operations
3. Ensure the database password is correct
4. Run `python test_supabase.py` for detailed error messages

### Missing Tables

If tables are missing:

1. Run `python init_database.py` to create them
2. Check your Supabase dashboard for table creation
3. Verify the schema.sql file is correct

### Authentication Issues

If you get authentication errors:

1. Check your SUPABASE_KEY in the .env file
2. Verify the service role key for admin operations
3. Check RLS policies in your Supabase dashboard

## Database Schema

The database includes these main tables:

### user_sessions
- Stores messaging playbooks and generation results
- Includes business input, status, and generated content

### usage_tracking  
- Tracks feature usage for billing and analytics
- Records user actions and plan types

### users
- User account information and plan details
- Authentication and subscription management

### payments
- Payment history and subscription status
- Integration with Stripe for billing

## Security Features

- **Row Level Security (RLS)** - Users can only access their own data
- **Service Role Key** - Admin operations use elevated permissions
- **Environment Variables** - Sensitive data stored securely
- **SQL Injection Protection** - Parameterized queries via Supabase client

Your MessageCraft application is now configured to use Supabase! 🚀