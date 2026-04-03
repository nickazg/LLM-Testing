from __future__ import annotations

import json
import re
from pathlib import Path

from llm_bench.adapters.claude_code import ClaudeCodeAdapter

RUBRICS = {
    "quality": """Rate the code quality on a scale of 1-5:
1 = Broken, unreadable, or fundamentally wrong approach
2 = Works but poor style, unnecessary complexity, or non-idiomatic
3 = Acceptable — functional, readable, minor issues
4 = Good — clean, idiomatic, well-structured
5 = Excellent — elegant, efficient, production-ready

Focus on: readability, idiomatic patterns, appropriate complexity, naming, structure.""",

    "instruction_following": """Rate how well the code follows the original instructions on a scale of 1-5:
1 = Completely ignored instructions or did something else entirely
2 = Partially followed — missed major requirements
3 = Mostly followed — minor deviations or extras
4 = Followed well — all requirements met, minimal extras
5 = Perfectly followed — exactly what was asked, nothing more, nothing less

Focus on: completeness, accuracy, no unrequested features, no missing requirements.""",
}


def build_judge_prompt(task_prompt: str, code: str, dimension: str) -> str:
    rubric = RUBRICS.get(dimension, f"Rate the {dimension} on a scale of 1-5.")
    return f"""You are a blind code reviewer. You do not know which model or tool produced this code.

## Original Task
{task_prompt}

## Code Produced
```
{code}
```

## Scoring Dimension: {dimension.replace("_", " ").title()}
{rubric}

Respond with ONLY a JSON object:
{{"score": <1-5>, "reasoning": "<brief explanation>"}}"""


def parse_judge_response(response: str) -> dict:
    try:
        data = json.loads(response.strip())
        if "score" in data:
            return data
    except json.JSONDecodeError:
        pass

    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            if "score" in data:
                return data
        except json.JSONDecodeError:
            pass

    match = re.search(r'\{[^{}]*"score"\s*:\s*\d[^{}]*\}', response)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return {"score": None, "reasoning": f"Could not parse judge response: {response[:200]}"}


async def judge_code(
    task_prompt: str,
    code: str,
    dimension: str,
    env_file: str | None = None,
) -> dict:
    prompt = build_judge_prompt(task_prompt, code, dimension)

    adapter = ClaudeCodeAdapter(model="opus", env_file=env_file)
    output = await adapter.run(prompt=prompt, cwd="/tmp", timeout=120)

    return parse_judge_response(output.stdout)
