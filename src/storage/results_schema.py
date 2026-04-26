EVAL_RESULTS_DDL = """
CREATE TABLE IF NOT EXISTS eval_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT,
    prompt_id TEXT,
    category TEXT,
    task_type TEXT,
    model_key TEXT,
    model_label TEXT,
    response_text TEXT,
    latency_seconds REAL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    estimated_cost REAL,
    retries INTEGER,
    error TEXT,
    requires_json INTEGER,
    json_valid INTEGER,
    schema_compliant INTEGER,
    refusal_detected INTEGER,
    rule_score REAL,
    golden_score REAL,
    judge_score REAL,
    overall_score REAL,
    created_at TEXT
);
"""

PAIRWISE_DDL = """
CREATE TABLE IF NOT EXISTS pairwise_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT,
    prompt_id TEXT,
    winner TEXT,
    reason TEXT,
    confidence TEXT,
    raw_json TEXT,
    created_at TEXT
);
"""

AGENT_DDL = """
CREATE TABLE IF NOT EXISTS agent_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT,
    workflow_name TEXT,
    model_key TEXT,
    completion_rate REAL,
    tool_misuse_rate REAL,
    human_corrections INTEGER,
    avg_runtime REAL,
    business_quality REAL,
    schema_compliance REAL,
    output_usability REAL,
    created_at TEXT
);
"""
