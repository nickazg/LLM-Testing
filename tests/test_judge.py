from llm_bench.judge import build_judge_prompt, parse_judge_response


def test_build_judge_prompt():
    prompt = build_judge_prompt(
        task_prompt="Write hello world in Python",
        code="print('Hello, World!')",
        dimension="quality",
    )
    assert "Write hello world" in prompt
    assert "print('Hello, World!')" in prompt
    assert "quality" in prompt.lower() or "Quality" in prompt


def test_parse_judge_response_valid():
    response = '{"score": 4, "reasoning": "Clean and simple implementation."}'
    result = parse_judge_response(response)
    assert result["score"] == 4
    assert "Clean" in result["reasoning"]


def test_parse_judge_response_extracts_json():
    response = 'Here is my assessment:\n\n```json\n{"score": 3, "reasoning": "Acceptable."}\n```'
    result = parse_judge_response(response)
    assert result["score"] == 3


def test_parse_judge_response_invalid():
    response = "I think the code is pretty good, maybe 4 out of 5."
    result = parse_judge_response(response)
    assert result["score"] is None
    assert "parse" in result["reasoning"].lower() or result["reasoning"]
