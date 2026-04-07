"""Validator for tier4-service-generator-context-heavy — checks org conventions."""
import json
import subprocess
import sys
import configparser
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
gen_py = workspace / "generate_service.py"

if not gen_py.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0
tests_passed = 0
total_tests = 10


def run_gen(*args):
    result = subprocess.run(
        [sys.executable, str(gen_py)] + list(args),
        capture_output=True, text=True, timeout=10,
        cwd=str(workspace),
    )
    return result


try:
    # Generate a service with minimal args
    run_gen("--name", "myapp", "--exec", "/usr/bin/myapp", "--output", "test_ctx.service")
    svc = workspace / "test_ctx.service"
    if not svc.exists():
        raise FileNotFoundError("Service file not generated")

    content = svc.read_text()

    # Test 1: Has all three sections
    if "[Unit]" in content and "[Service]" in content and "[Install]" in content:
        tests_passed += 1

    # Test 2: User is svc-{name}, NOT root
    if "svc-myapp" in content and "User=root" not in content:
        tests_passed += 1

    # Test 3: consul-agent.service dependency
    if "consul-agent.service" in content:
        tests_passed += 1

    # Test 4: vault-agent.service dependency
    if "vault-agent.service" in content:
        tests_passed += 1

    # Test 5: LimitNOFILE=65535
    if "LimitNOFILE=65535" in content:
        tests_passed += 1

    # Test 6: LimitNPROC=4096
    if "LimitNPROC=4096" in content:
        tests_passed += 1

    # Test 7: EnvironmentFile from /etc/platform/{name}/env
    if "/etc/platform/myapp/env" in content:
        tests_passed += 1

    # Test 8: WorkingDirectory defaults to /opt/platform/{name}/
    if "/opt/platform/myapp" in content:
        tests_passed += 1

    # Test 9: Health check ExecStartPre
    if "healthcheck" in content and "myapp" in content:
        tests_passed += 1

    # Test 10: RestartSec=10 (not 5)
    if "RestartSec=10" in content:
        tests_passed += 1

except Exception:
    pass

# Clean up
for f in workspace.glob("test_ctx*.service"):
    f.unlink(missing_ok=True)

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.8 else 1)
