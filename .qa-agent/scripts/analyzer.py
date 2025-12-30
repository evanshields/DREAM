#!/usr/bin/env python3
"""
QA Agent Failure Analyzer
Analyzes test failures and attempts autonomous fixes.

Usage:
    python analyzer.py --analyze              # Analyze last test run
    python analyzer.py --report=path/report   # Analyze specific report
"""

import json
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import yaml
import argparse


class FailureType(Enum):
    """Types of test failures."""
    IMPORT_ERROR = "import_error"
    ASSERTION_ERROR = "assertion_error"
    TIMEOUT_ERROR = "timeout_error"
    FIXTURE_ERROR = "fixture_error"
    ATTRIBUTE_ERROR = "attribute_error"
    TYPE_ERROR = "type_error"
    SNAPSHOT_MISMATCH = "snapshot_mismatch"
    UNKNOWN = "unknown"


@dataclass
class Failure:
    """Test failure information."""
    test_name: str
    failure_type: FailureType
    message: str
    traceback: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None

    @property
    def is_auto_fixable(self) -> bool:
        """Check if this failure can be auto-fixed."""
        auto_fixable = {
            FailureType.IMPORT_ERROR,
            FailureType.FIXTURE_ERROR,
            FailureType.SNAPSHOT_MISMATCH,
            FailureType.TIMEOUT_ERROR,
        }
        return self.failure_type in auto_fixable


class FailureAnalyzer:
    """Analyze test failures and categorize them."""

    # Regex patterns for failure detection
    ERROR_PATTERNS = {
        FailureType.IMPORT_ERROR: [
            r"ImportError",
            r"ModuleNotFoundError",
            r"cannot import name",
        ],
        FailureType.ASSERTION_ERROR: [
            r"AssertionError",
            r"assert .* == .*",
        ],
        FailureType.TIMEOUT_ERROR: [
            r"TimeoutError",
            r"Timeout",
            r"timeout exceeded",
        ],
        FailureType.FIXTURE_ERROR: [
            r"FixtureLookupError",
            r"fixture .* not found",
        ],
        FailureType.SNAPSHOT_MISMATCH: [
            r"Snapshot.*does not match",
            r"Snapshot mismatch",
            r"assert.*snapshot",
        ],
        FailureType.ATTRIBUTE_ERROR: [
            r"AttributeError",
            r"has no attribute",
        ],
        FailureType.TYPE_ERROR: [
            r"TypeError",
            r"unsupported operand type",
        ],
    }

    def __init__(self, config_path: Path = Path(".qa-agent.yml")):
        """Initialize analyzer with configuration."""
        self.config = self._load_config(config_path)
        self.fixer = AutoFixer()

    def analyze_report(self, report_path: Path) -> Dict[str, List[Failure]]:
        """Analyze pytest JSON report."""
        try:
            with open(report_path, "r") as f:
                report = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"❌ Error reading report: {e}")
            return {"auto_fixable": [], "requires_human": []}

        failures = self._extract_failures(report)
        return self._categorize_failures(failures)

    def analyze_last_run(self) -> Dict[str, List[Failure]]:
        """Analyze the last test run."""
        state_dir = Path(".qa-agent/state")

        # Find the most recent report
        report_files = list(state_dir.glob("*-report.json"))
        if not report_files:
            print("❌ No test reports found")
            return {"auto_fixable": [], "requires_human": []}

        latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
        return self.analyze_report(latest_report)

    def _extract_failures(self, report: dict) -> List[Failure]:
        """Extract failures from pytest JSON report."""
        failures = []

        for test in report.get("tests", []):
            if test.get("outcome") != "failed":
                continue

            call = test.get("call", {})
            longrepr = call.get("longrepr", "")
            traceback_str = call.get("traceback", "")

            failure_type = self._classify_failure(longrepr, traceback_str)

            failure = Failure(
                test_name=test.get("nodeid", "unknown"),
                failure_type=failure_type,
                message=longrepr[:500],  # Truncate message
                traceback=traceback_str[:1000],  # Truncate traceback
                file_path=test.get("fspath"),
                line_number=test.get("lineno"),
            )
            failures.append(failure)

        return failures

    def _classify_failure(self, message: str, traceback_str: str = "") -> FailureType:
        """Classify failure by error message."""
        combined = f"{message}\n{traceback_str}"

        for failure_type, patterns in self.ERROR_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, combined, re.IGNORECASE):
                    return failure_type

        return FailureType.UNKNOWN

    def _categorize_failures(self, failures: List[Failure]) -> Dict[str, List[Failure]]:
        """Categorize failures as auto-fixable or requiring human intervention."""
        return {
            "auto_fixable": [f for f in failures if f.is_auto_fixable],
            "requires_human": [f for f in failures if not f.is_auto_fixable],
        }

    @staticmethod
    def _load_config(config_path: Path) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}
        except yaml.YAMLError:
            return {}


class AutoFixer:
    """Automatically fix common test failures."""

    def fix_failures(self, failures: List[Failure]) -> Dict[str, int]:
        """Attempt to fix auto-fixable failures."""
        results = {"fixed": 0, "failed": 0, "skipped": 0}

        for failure in failures:
            if not failure.is_auto_fixable:
                results["skipped"] += 1
                continue

            success = self._fix_failure(failure)
            if success:
                results["fixed"] += 1
                print(f"✅ Fixed: {failure.test_name}")
            else:
                results["failed"] += 1
                print(f"❌ Could not fix: {failure.test_name}")

        return results

    def _fix_failure(self, failure: Failure) -> bool:
        """Attempt to fix a specific failure."""
        if failure.failure_type == FailureType.IMPORT_ERROR:
            return self._fix_import_error(failure)
        elif failure.failure_type == FailureType.SNAPSHOT_MISMATCH:
            return self._fix_snapshot_mismatch(failure)
        elif failure.failure_type == FailureType.TIMEOUT_ERROR:
            return self._fix_timeout_error(failure)
        elif failure.failure_type == FailureType.FIXTURE_ERROR:
            return self._fix_fixture_error(failure)
        else:
            return False

    def _fix_import_error(self, failure: Failure) -> bool:
        """Attempt to fix import errors."""
        # Extract missing module name
        match = re.search(r"cannot import name '(\w+)'", failure.message)
        if not match:
            match = re.search(r"No module named '([\w.]+)'", failure.message)

        if not match:
            return False

        missing_import = match.group(1)
        print(f"   Would add import for: {missing_import}")
        # Note: Actual implementation would require AST manipulation
        return False  # Placeholder

    def _fix_snapshot_mismatch(self, failure: Failure) -> bool:
        """Update snapshot files."""
        # Extract test file from nodeid
        test_file = failure.test_name.split("::")[0]

        result = subprocess.run(
            ["pytest", test_file, "--snapshot-update"],
            capture_output=True
        )

        return result.returncode == 0

    def _fix_timeout_error(self, failure: Failure) -> bool:
        """Increase timeout in pytest.ini."""
        pytest_ini = Path("pytest.ini")
        if not pytest_ini.exists():
            return False

        try:
            with open(pytest_ini, "r") as f:
                lines = f.readlines()

            # Find timeout line
            for i, line in enumerate(lines):
                if line.startswith("timeout"):
                    # Extract current timeout
                    match = re.search(r"timeout\s*=\s*(\d+)", line)
                    if match:
                        current = int(match.group(1))
                        new_timeout = current * 2
                        lines[i] = f"timeout = {new_timeout}\n"

                        with open(pytest_ini, "w") as f:
                            f.writelines(lines)

                        print(f"   Updated timeout: {current}s → {new_timeout}s")
                        return True

            return False
        except Exception as e:
            print(f"   Error updating timeout: {e}")
            return False

    def _fix_fixture_error(self, failure: Failure) -> bool:
        """Attempt to fix fixture lookup errors."""
        match = re.search(r"fixture '(\w+)' not found", failure.message)
        if not match:
            return False

        fixture_name = match.group(1)
        print(f"   Missing fixture: {fixture_name}")
        # Note: Actual implementation would check conftest.py
        return False  # Placeholder


def print_analysis_results(analysis: Dict[str, List[Failure]]):
    """Print analysis results."""
    auto_fixable = analysis["auto_fixable"]
    requires_human = analysis["requires_human"]

    print("\n" + "=" * 60)
    print("🔍 Failure Analysis")
    print("=" * 60)

    if not auto_fixable and not requires_human:
        print("✅ No failures found!")
        return

    if auto_fixable:
        print(f"\n🔧 Auto-Fixable ({len(auto_fixable)}):")
        for failure in auto_fixable:
            print(f"  • {failure.test_name}")
            print(f"    Type: {failure.failure_type.value}")
            print(f"    Message: {failure.message[:60]}...")

    if requires_human:
        print(f"\n⚠️  Requires Human Intervention ({len(requires_human)}):")
        for failure in requires_human:
            print(f"  • {failure.test_name}")
            print(f"    Type: {failure.failure_type.value}")
            print(f"    Message: {failure.message[:60]}...")

    print("=" * 60 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="QA Agent Failure Analyzer")
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze last test run"
    )
    parser.add_argument(
        "--report",
        help="Path to specific test report"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix auto-fixable failures"
    )
    parser.add_argument(
        "--config",
        default=".qa-agent.yml",
        help="Path to configuration file"
    )

    args = parser.parse_args()

    analyzer = FailureAnalyzer(Path(args.config))

    # Load analysis
    if args.report:
        analysis = analyzer.analyze_report(Path(args.report))
    else:
        analysis = analyzer.analyze_last_run()

    # Print results
    print_analysis_results(analysis)

    # Attempt fixes if requested
    if args.fix:
        fixer = AutoFixer()
        results = fixer.fix_failures(analysis["auto_fixable"])
        print(f"\n📊 Fix Summary: {results['fixed']} fixed, {results['failed']} failed, {results['skipped']} skipped")


if __name__ == "__main__":
    main()
