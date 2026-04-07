"""Validator for tier3-service-generator task."""
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
total_tests = 8


def run_gen(*args):
    result = subprocess.run(
        [sys.executable, str(gen_py)] + list(args),
        capture_output=True, text=True, timeout=10,
        cwd=str(workspace),
    )
    return result


def parse_unit(path: Path) -> configparser.ConfigParser:
    """Parse a systemd unit file (INI-like format)."""
    config = configparser.ConfigParser(interpolation=None)
    config.read(path)
    return config


try:
    # Test 1: Basic generation with required args only
    run_gen("--name", "testapp", "--exec", "/usr/bin/testapp", "--output", "test1.service")
    svc = workspace / "test1.service"
    if svc.exists():
        config = parse_unit(svc)
        if "Unit" in config and "Service" in config and "Install" in config:
            tests_passed += 1

    # Test 2: Description field
    run_gen("--name", "myapp", "--exec", "/usr/bin/myapp", "--description", "My Application", "--output", "test2.service")
    svc = workspace / "test2.service"
    if svc.exists():
        content = svc.read_text()
        if "My Application" in content:
            tests_passed += 1

    # Test 3: User field
    run_gen("--name", "webserver", "--exec", "/usr/bin/web", "--user", "www-data", "--output", "test3.service")
    svc = workspace / "test3.service"
    if svc.exists():
        content = svc.read_text()
        if "www-data" in content:
            tests_passed += 1

    # Test 4: Restart policy
    run_gen("--name", "daemon", "--exec", "/usr/bin/daemon", "--restart", "always", "--restart-sec", "10", "--output", "test4.service")
    svc = workspace / "test4.service"
    if svc.exists():
        content = svc.read_text()
        if "always" in content and "10" in content:
            tests_passed += 1

    # Test 5: After directive
    run_gen("--name", "dbapp", "--exec", "/usr/bin/dbapp", "--after", "network.target", "--after", "postgresql.service", "--output", "test5.service")
    svc = workspace / "test5.service"
    if svc.exists():
        content = svc.read_text()
        if "network.target" in content and "postgresql.service" in content:
            tests_passed += 1

    # Test 6: Environment variables
    run_gen("--name", "envapp", "--exec", "/usr/bin/envapp", "--env", "PORT=8080", "--env", "DEBUG=false", "--output", "test6.service")
    svc = workspace / "test6.service"
    if svc.exists():
        content = svc.read_text()
        if "PORT=8080" in content and "DEBUG=false" in content:
            tests_passed += 1

    # Test 7: Working directory
    run_gen("--name", "dirapp", "--exec", "/usr/bin/dirapp", "--working-dir", "/opt/myapp", "--output", "test7.service")
    svc = workspace / "test7.service"
    if svc.exists():
        content = svc.read_text()
        if "/opt/myapp" in content:
            tests_passed += 1

    # Test 8: WantedBy in Install section
    run_gen("--name", "installapp", "--exec", "/usr/bin/installapp", "--wanted-by", "graphical.target", "--output", "test8.service")
    svc = workspace / "test8.service"
    if svc.exists():
        content = svc.read_text()
        if "graphical.target" in content and "[Install]" in content:
            tests_passed += 1

except Exception:
    pass

# Clean up generated files
for f in workspace.glob("test*.service"):
    f.unlink(missing_ok=True)

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.8 else 1)
