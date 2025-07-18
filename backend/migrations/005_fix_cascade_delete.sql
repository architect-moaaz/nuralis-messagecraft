-- Fix foreign key constraints to enable proper cascade deletion
-- This ensures that when a user_sessions record is deleted, all related records are automatically deleted

-- Drop the existing foreign key constraint on kit_generations
ALTER TABLE kit_generations 
DROP CONSTRAINT IF EXISTS kit_generations_session_id_fkey;

-- Recreate the foreign key with CASCADE delete
ALTER TABLE kit_generations 
ADD CONSTRAINT kit_generations_session_id_fkey 
FOREIGN KEY (session_id) REFERENCES user_sessions(id) ON DELETE CASCADE;

-- Verify the constraint exists for generation_stages (should already have CASCADE)
-- This is just for documentation - the constraint should already be correct
-- ALTER TABLE generation_stages 
-- DROP CONSTRAINT IF EXISTS generation_stages_session_id_fkey;
-- ALTER TABLE generation_stages 
-- ADD CONSTRAINT generation_stages_session_id_fkey 
-- FOREIGN KEY (session_id) REFERENCES user_sessions(id) ON DELETE CASCADE;