from __future__ import annotations

import json
import yaml
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class TokenUsage:
    input: int = 0
    output: int = 0
    thinking: int = 0
    cache_read: int = 0

    @property
    def total(self) -> int:
        return self.input + self.output + self.thinking


@dataclass
class EfficiencyMetrics:
    tokens: TokenUsage = field(default_factory=TokenUsage)
    tool_calls: int = 0
    wall_time_s: float = 0.0
    cost_usd: float = 0.0


@dataclass
class Scores:
    correctness: Optional[float] = None
    completion: Optional[float] = None
    efficiency: Optional[EfficiencyMetrics] = None
    quality: Optional[float] = None
    instruction_following: Optional[float] = None


@dataclass
class TaskConfig:
    id: str
    name: str
    tier: int
    prompt: str
    timeout: int
    skill: Optional[str]
    tags: list[str]
    scoring_automated: list[str]
    scoring_flagged: list[str]
    task_dir: Path = field(repr=False)

    @classmethod
    def from_dir(cls, task_dir: Path) -> TaskConfig:
        yaml_path = task_dir / "task.yaml"
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        return cls(
            id=data["id"],
            name=data["name"],
            tier=data["tier"],
            prompt=data["prompt"],
            timeout=data["timeout"],
            skill=data.get("skill"),
            tags=data.get("tags", []),
            scoring_automated=data.get("scoring", {}).get("automated", []),
            scoring_flagged=data.get("scoring", {}).get("flagged", []),
            task_dir=task_dir,
        )


@dataclass
class RunResult:
    task_id: str
    model: str
    cli: str
    skill: Optional[str]
    scores: Scores
    timestamp: str
    prompt: str = ""
    raw_output: str = ""
    tier: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
