# Enterprise LLM Evaluation Lab

A practical, ready-to-run platform for enterprise AI teams to evaluate two LLM versions (for example GPT-5.4 vs GPT-5.5) using the same production-like task set, consistent runtime settings, and evidence-based scoring.

## Why this goes beyond documentation comparisons
Model cards and release notes are useful, but they do not reliably predict behavior on your workflows. This lab runs real prompts across quality, reliability, cost, latency, schema conformance, and failure handling so decisions are based on observed outcomes rather than feature claims.

## What this project does
- Runs identical prompts against **Model A** and **Model B**.
- Captures output quality and operational metrics: latency, token usage, cost, retries, errors, JSON/schema compliance, refusal behavior.
- Scores responses using:
  - Rule-based checks
  - Golden answer overlap
  - LLM-as-judge (1-5 dimension scoring)
  - Blind pairwise judging (A vs B)
- Stores results in SQLite and CSV.
- Generates markdown and CSV reports with routing recommendations.
- Provides a Streamlit dashboard for side-by-side analysis.

## Repository structure
```text
enterprise-llm-eval-lab/
├── README.md
├── requirements.txt
├── .env.example
├── config/
├── data/
├── src/
├── outputs/
└── tests/
```

## Quick start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment:
   ```bash
   cp .env.example .env
   # add OPENAI_API_KEY and/or LITELLM_API_KEY
   ```
3. Configure models in `config/models.yaml`.
4. Run evaluation:
   ```bash
   python src/main.py run-eval --config config/eval_config.yaml
   ```
5. Generate report:
   ```bash
   python src/main.py generate-report --config config/eval_config.yaml --run-id <run_id>
   ```
6. Launch dashboard:
   ```bash
   streamlit run src/dashboard/streamlit_app.py
   ```

## Defining decision goals
Set goals before running:
- Default model for broad enterprise workload
- Premium model for high-complexity tasks
- Agentic/tool workflow model
- Budget-sensitive routing model

Then map goals to scoring weights in `config/scoring_weights.yaml`.

## Prompt datasets
Sample prompts are in `data/prompts_sample.csv` with fields for:
- prompt metadata
- expected format
- golden answer
- flags for JSON, long-context, multi-turn, tool simulation, hallucination traps

Add your own rows with the same schema.

## Model configuration
`config/models.yaml` supports per-model settings:
- provider (`openai` or `litellm`)
- model name
- temperature, max tokens, timeout, retries
- input/output token costs for cost estimation

No API keys are hardcoded.

## Scoring design
1. **Rule-based**: JSON validity, required fields, format hints, forbidden phrases, length.
2. **Golden answer**: exact match + token overlap baseline.
3. **LLM judge**: accuracy, relevance, completeness, reasoning, instruction following, clarity, hallucination risk, enterprise readiness, client-safe tone, format compliance.
4. **Blind pairwise**: winner A/B/Tie + rationale and confidence.

## Specialized tests
- Long-context reasoning
- Multi-turn consistency (10 turns)
- Recovery from broken inputs (JSON/code/incomplete specs)
- Ambiguity handling (clarifying questions)
- Hallucination red-team traps (fake URLs, future events, missing references)
- Agent workflow benchmark simulations

## How to interpret outputs
- `outputs/results/latest_eval_results.csv`: prompt-level and model-level metrics.
- `outputs/results/latest_pairwise_results.csv`: blind pairwise decisions.
- `outputs/reports/report_<run_id>.md`: executive summary, winners, risks, migration guidance.

## Routing recommendations
The recommender supports practical decision patterns:
- **Case A**: Slight quality edge but much higher cost → default A, route complex tasks to B.
- **Case B**: Strong tool-use edge for B → route agentic workflows to B.
- **Case C**: B wins quality + reliability + cost-performance → full migration.
- **Case D**: Similar performance on simple tasks → route by task type.

## CLI commands
```bash
python src/main.py run-eval --config config/eval_config.yaml
python src/main.py run-multiturn --config config/eval_config.yaml
python src/main.py run-agent-benchmark --config config/eval_config.yaml
python src/main.py generate-report --config config/eval_config.yaml --run-id <run_id>
streamlit run src/dashboard/streamlit_app.py
```

## Limitations and next steps
- Sample dataset is intentionally small; scale with internal prompts.
- Golden scoring currently uses overlap heuristics; semantic scoring can be added.
- Add human adjudication for high-stakes deployment decisions.
