-- Migration: Add Generation Stages Tracking
-- This migration adds support for tracking AI agent stages during playbook generation

-- Create generation stages table
CREATE TABLE IF NOT EXISTS generation_stages (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES user_sessions(id) ON DELETE CASCADE,
    stage_name VARCHAR NOT NULL,
    stage_display_name VARCHAR NOT NULL,
    stage_order INTEGER NOT NULL,
    status VARCHAR DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'failed'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    stage_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_generation_stages_session_id ON generation_stages(session_id);
CREATE INDEX IF NOT EXISTS idx_generation_stages_status ON generation_stages(status);
CREATE INDEX IF NOT EXISTS idx_generation_stages_stage_order ON generation_stages(stage_order);

-- Add RLS policies
ALTER TABLE generation_stages ENABLE ROW LEVEL SECURITY;

-- Policy for users to view their own generation stages
CREATE POLICY "Users can view own generation stages" ON generation_stages
    FOR SELECT USING (
        session_id IN (
            SELECT id FROM user_sessions WHERE user_id = auth.uid()::text
        )
    );

-- Policy for service role to manage generation stages
CREATE POLICY "Service role can manage generation stages" ON generation_stages
    FOR ALL USING (auth.role() = 'service_role');

-- Function to initialize generation stages for a session
CREATE OR REPLACE FUNCTION initialize_generation_stages(p_session_id UUID)
RETURNS VOID AS $$
BEGIN
    -- Delete existing stages for this session (in case of restart)
    DELETE FROM generation_stages WHERE session_id = p_session_id;
    
    -- Insert all stages in order
    INSERT INTO generation_stages (session_id, stage_name, stage_display_name, stage_order, status) VALUES
    (p_session_id, 'business_discovery', 'Business Discovery', 1, 'pending'),
    (p_session_id, 'competitor_research', 'Competitor Research', 2, 'pending'),
    (p_session_id, 'positioning_analysis', 'Positioning Analysis', 3, 'pending'),
    (p_session_id, 'trust_building', 'Trust Building', 4, 'pending'),
    (p_session_id, 'emotional_intelligence', 'Emotional Intelligence', 5, 'pending'),
    (p_session_id, 'social_proof_generator', 'Social Proof Generation', 6, 'pending'),
    (p_session_id, 'messaging_generator', 'Messaging Framework', 7, 'pending'),
    (p_session_id, 'content_creator', 'Content Creation', 8, 'pending'),
    (p_session_id, 'quality_reviewer', 'Quality Review', 9, 'pending'),
    (p_session_id, 'reflection_orchestrator', 'Reflection & Refinement', 10, 'pending'),
    (p_session_id, 'final_assembly', 'Final Assembly', 11, 'pending');
END;
$$ LANGUAGE plpgsql;

-- Function to update stage status
CREATE OR REPLACE FUNCTION update_stage_status(
    p_session_id UUID,
    p_stage_name VARCHAR,
    p_status VARCHAR,
    p_stage_data JSONB DEFAULT NULL,
    p_error_message TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    UPDATE generation_stages 
    SET 
        status = p_status,
        stage_data = COALESCE(p_stage_data, stage_data),
        error_message = p_error_message,
        started_at = CASE 
            WHEN p_status = 'in_progress' AND started_at IS NULL THEN NOW()
            ELSE started_at
        END,
        completed_at = CASE 
            WHEN p_status IN ('completed', 'failed') THEN NOW()
            ELSE completed_at
        END,
        updated_at = NOW()
    WHERE session_id = p_session_id AND stage_name = p_stage_name;
END;
$$ LANGUAGE plpgsql;

-- Function to get generation progress
CREATE OR REPLACE FUNCTION get_generation_progress(p_session_id UUID)
RETURNS TABLE(
    stage_name VARCHAR,
    stage_display_name VARCHAR,
    stage_order INTEGER,
    status VARCHAR,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    stage_data JSONB,
    error_message TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        gs.stage_name,
        gs.stage_display_name,
        gs.stage_order,
        gs.status,
        gs.started_at,
        gs.completed_at,
        gs.stage_data,
        gs.error_message
    FROM generation_stages gs
    WHERE gs.session_id = p_session_id
    ORDER BY gs.stage_order;
END;
$$ LANGUAGE plpgsql;

-- Add trigger for updating updated_at
CREATE TRIGGER update_generation_stages_updated_at 
    BEFORE UPDATE ON generation_stages
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();