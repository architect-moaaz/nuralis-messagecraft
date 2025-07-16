-- Add OAuth columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR;
ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR DEFAULT 'local';
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

-- Make password_hash optional for OAuth users
ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;

-- Add indexes for OAuth
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
CREATE INDEX IF NOT EXISTS idx_users_auth_provider ON users(auth_provider);

-- Add unique constraint for google_id
ALTER TABLE users ADD CONSTRAINT unique_google_id UNIQUE(google_id);