import asyncio
from llm_bench.adapters.base import CLIAdapter, CLIOutput


def test_cli_output_dataclass():
    output = CLIOutput(
        stdout="hello",
        stderr="",
        exit_code=0,
        wall_time_s=1.5,
        tokens=100,
        tool_calls=2,
        cost_usd=0.01,
    )
    assert output.exit_code == 0
    assert output.wall_time_s == 1.5


def test_adapter_is_abstract():
    try:
        adapter = CLIAdapter(model="test")
        asyncio.run(adapter.run("prompt", "/tmp"))
        assert False, "Should have raised NotImplementedError"
    except NotImplementedError:
        pass
