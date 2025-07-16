-- Migration: Add Credits System for Production Mode
-- This migration adds support for credit-based kit generation

-- Add credits and generation tracking to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS credits INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS free_kits_used INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_kits_generated INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS google_id VARCHAR UNIQUE,
ADD COLUMN IF NOT EXISTS auth_provider VARCHAR DEFAULT 'local',
ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

-- Create credits transactions table
CREATE TABLE IF NOT EXISTS credit_transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    transaction_type VARCHAR NOT NULL, -- 'purchase', 'usage', 'refund', 'bonus'
    credits_amount INTEGER NOT NULL, -- positive for additions, negative for usage
    balance_after INTEGER NOT NULL,
    description TEXT,
    stripe_payment_intent_id VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create kit generations table for detailed tracking
CREATE TABLE IF NOT EXISTS kit_generations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES user_sessions(id),
    business_description TEXT NOT NULL,
    company_name VARCHAR,
    industry VARCHAR,
    credits_used INTEGER DEFAULT 1,
    generation_type VARCHAR DEFAULT 'paid', -- 'free', 'paid'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Update payments table to support credit purchases
ALTER TABLE payments
ADD COLUMN IF NOT EXISTS payment_type VARCHAR DEFAULT 'subscription', -- 'subscription', 'credits'
ADD COLUMN IF NOT EXISTS credits_purchased INTEGER,
ADD COLUMN IF NOT EXISTS stripe_payment_intent_id VARCHAR UNIQUE;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_created_at ON credit_transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_kit_generations_user_id ON kit_generations(user_id);
CREATE INDEX IF NOT EXISTS idx_kit_generations_created_at ON kit_generations(created_at);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
CREATE INDEX IF NOT EXISTS idx_payments_stripe_payment_intent_id ON payments(stripe_payment_intent_id);

-- Add RLS policies for new tables
ALTER TABLE credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE kit_generations ENABLE ROW LEVEL SECURITY;

-- Policies for credit_transactions
CREATE POLICY "Users can view own credit transactions" ON credit_transactions
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Service role can manage credit transactions" ON credit_transactions
    FOR ALL USING (auth.role() = 'service_role');

-- Policies for kit_generations
CREATE POLICY "Users can view own kit generations" ON kit_generations
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert own kit generations" ON kit_generations
    FOR INSERT WITH CHECK (user_id = auth.uid());

-- Function to check if user can generate kit
CREATE OR REPLACE FUNCTION can_user_generate_kit(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    v_credits INTEGER;
    v_free_kits_used INTEGER;
    v_is_production BOOLEAN;
BEGIN
    -- Get user's current credits and free kits used
    SELECT credits, free_kits_used 
    INTO v_credits, v_free_kits_used
    FROM users 
    WHERE id = p_user_id;
    
    -- Check if production mode (you'll need to pass this from application)
    v_is_production := current_setting('app.is_production', true)::BOOLEAN;
    
    IF NOT v_is_production THEN
        -- In development mode, always allow
        RETURN TRUE;
    END IF;
    
    -- In production mode, check if user has credits or hasn't used free kit
    IF v_credits > 0 THEN
        RETURN TRUE;
    ELSIF v_free_kits_used < 1 THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to use credits or free kit
CREATE OR REPLACE FUNCTION use_kit_generation(p_user_id UUID)
RETURNS TABLE(success BOOLEAN, message TEXT, credits_remaining INTEGER) AS $$
DECLARE
    v_credits INTEGER;
    v_free_kits_used INTEGER;
BEGIN
    -- Lock the user row to prevent race conditions
    SELECT credits, free_kits_used 
    INTO v_credits, v_free_kits_used
    FROM users 
    WHERE id = p_user_id
    FOR UPDATE;
    
    -- Check if user has credits
    IF v_credits > 0 THEN
        -- Use credit
        UPDATE users 
        SET credits = credits - 1,
            total_kits_generated = total_kits_generated + 1
        WHERE id = p_user_id;
        
        -- Record transaction
        INSERT INTO credit_transactions (
            user_id, transaction_type, credits_amount, 
            balance_after, description
        ) VALUES (
            p_user_id, 'usage', -1, 
            v_credits - 1, 'Kit generation'
        );
        
        RETURN QUERY SELECT TRUE, 'Credit used successfully', v_credits - 1;
    ELSIF v_free_kits_used < 1 THEN
        -- Use free kit
        UPDATE users 
        SET free_kits_used = free_kits_used + 1,
            total_kits_generated = total_kits_generated + 1
        WHERE id = p_user_id;
        
        RETURN QUERY SELECT TRUE, 'Free kit used', 0;
    ELSE
        -- No credits or free kits available
        RETURN QUERY SELECT FALSE, 'No credits available. Please purchase credits to continue.', 0;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to add credits after purchase
CREATE OR REPLACE FUNCTION add_user_credits(
    p_user_id UUID, 
    p_credits INTEGER, 
    p_stripe_payment_intent_id VARCHAR,
    p_description TEXT DEFAULT 'Credit purchase'
)
RETURNS INTEGER AS $$
DECLARE
    v_new_balance INTEGER;
BEGIN
    -- Update user credits
    UPDATE users 
    SET credits = credits + p_credits
    WHERE id = p_user_id
    RETURNING credits INTO v_new_balance;
    
    -- Record transaction
    INSERT INTO credit_transactions (
        user_id, transaction_type, credits_amount, 
        balance_after, description, stripe_payment_intent_id
    ) VALUES (
        p_user_id, 'purchase', p_credits, 
        v_new_balance, p_description, p_stripe_payment_intent_id
    );
    
    RETURN v_new_balance;
END;
$$ LANGUAGE plpgsql;