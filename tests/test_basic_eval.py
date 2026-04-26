from src.metrics.cost import estimate_cost
from src.metrics.schema_validation import is_valid_json
from src.scoring.golden_answer_scorer import score_golden
from src.scoring.rule_based_scorer import score_rule_based


def test_cost_estimation():
    assert estimate_cost(100, 50, 0.001, 0.002) == 0.2


def test_json_validation():
    assert is_valid_json('{"x": 1}')
    assert not is_valid_json('{"x": 1')


def test_golden_scorer_overlap():
    score = score_golden("hello world", "hello")
    assert score["golden_score"] > 0


def test_rule_based_json():
    out = '{"next_action_plan": ["step1", "step2"]}'
    score = score_rule_based(out, "json", True, "next_action_plan")
    assert score["checks"]["json_valid"] is True
