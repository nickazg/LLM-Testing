from llm_bench.adapters.base import CLIAdapter, CLIOutput
from llm_bench.adapters.claude_code import ClaudeCodeAdapter
from llm_bench.adapters.open_code import OpenCodeAdapter
from llm_bench.adapters.kilo import KiloAdapter

ADAPTERS: dict[str, type[CLIAdapter]] = {
    "claude-code": ClaudeCodeAdapter,
    "open-code": OpenCodeAdapter,
    "kilo": KiloAdapter,
}


def get_adapter(cli_name: str, model: str, **kwargs) -> CLIAdapter:
    cls = ADAPTERS.get(cli_name)
    if cls is None:
        raise ValueError(f"Unknown CLI: {cli_name}. Available: {list(ADAPTERS.keys())}")
    return cls(model=model, **kwargs)


__all__ = ["CLIAdapter", "CLIOutput", "get_adapter"]
