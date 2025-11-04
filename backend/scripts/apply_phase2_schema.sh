#!/bin/bash

set -e

echo "📊 Applying Phase 2 database schema..."

# Wait for postgres to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n sopm --timeout=60s

# Apply schema
echo "📝 Creating user function tables..."
kubectl exec -it deployment/postgres -n sopm -- psql -U postgres -d sopm <<EOF
-- User-uploaded functions
CREATE TABLE IF NOT EXISTS user_functions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    runtime VARCHAR(20) NOT NULL,
    code_reference VARCHAR(255),
    dependencies TEXT,
    memory_limit_mb INT DEFAULT 128,
    cpu_limit_millicores INT DEFAULT 500,
    timeout_seconds INT DEFAULT 30,
    status VARCHAR(20) DEFAULT 'pending',
    image_url VARCHAR(255),
    build_logs TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, name)
);

CREATE INDEX IF NOT EXISTS idx_user_functions_user ON user_functions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_functions_status ON user_functions(status);

-- Function versions
CREATE TABLE IF NOT EXISTS function_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    function_id UUID REFERENCES user_functions(id) ON DELETE CASCADE,
    version_number INT NOT NULL,
    code_reference VARCHAR(255),
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(function_id, version_number)
);

-- Function executions
CREATE TABLE IF NOT EXISTS function_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    function_id UUID REFERENCES user_functions(id) ON DELETE CASCADE,
    job_id INT REFERENCES jobs(id),
    status VARCHAR(20),
    input_data JSONB,
    output_data TEXT,
    error_message TEXT,
    execution_time_ms FLOAT,
    memory_used_mb INT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_executions_function ON function_executions(function_id);
CREATE INDEX IF NOT EXISTS idx_executions_status ON function_executions(status);
EOF

echo "✅ Phase 2 schema applied successfully!"
