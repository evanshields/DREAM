#!/usr/bin/env python3
"""
QA Agent Test Runner
Orchestrates test execution with smart test selection and fast-fail strategy.

Usage:
    python runner.py --mode=auto          # Auto-detect and run affected tests
    python runner.py --mode=all           # Run all tests
    python runner.py --mode=unit          # Run only unit tests
    python runner.py --files=file1 file2  # Run tests for specific files
"""

import subprocess
import json
import time
import sys
import re
from pathlib import Path
from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from enum import Enum
import yaml
import argparse


class TestCategory(Enum):
    """Test categories in execution order."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"


@dataclass
class TestResult:
    """Result of a test execution."""
    category: TestCategory
    returncode: int
    duration: float
    stdout: str
    stderr: str
    report_file: Optional[Path] = None

    @property
    def passed(self) -> bool:
        """Check if tests passed."""
        return self.returncode == 0

    @property
    def failed(self) -> bool:
        """Check if tests failed."""
        return self.returncode != 0


class TestSelector:
    """Select which tests to run based on file changes."""

    def __init__(self, config_path: Path = Path(".qa-agent.yml")):
        """Initialize selector with configuration."""
        self.config = self._load_config(config_path)
        self.impact_map = self.config.get("impact_map", {})

    def select_for_changes(self, changed_files: Set[str]) -> List[TestCategory]:
        """Determine which tests to run based on changed files."""
        categories = set()

        for file_pattern, test_cats in self.impact_map.items():
            for changed_file in changed_files:
                if self._matches_pattern(changed_file, file_pattern):
                    for cat_str in test_cats:
                        if cat_str != "affected-test":  # Skip metadata marker
                            try:
                                categories.add(TestCategory(cat_str))
                            except ValueError:
                                pass

        # Return in order: unit -> integration -> e2e
        ordered = []
        for cat in TestCategory:
            if cat in categories:
                ordered.append(cat)

        return ordered or [TestCategory.UNIT]  # Default to unit tests

    def select_all(self) -> List[TestCategory]:
        """Return all test categories in order."""
        return [cat for cat in TestCategory]

    def _matches_pattern(self, filepath: str, pattern: str) -> bool:
        """Check if filepath matches glob pattern."""
        # Convert glob pattern to regex
        regex_pattern = pattern.replace("*", ".*").replace("?", ".")
        regex_pattern = f"^{regex_pattern}$"
        return bool(re.match(regex_pattern, filepath))

    @staticmethod
    def _load_config(config_path: Path) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"⚠️  Config file not found: {config_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"❌ Error parsing config: {e}")
            return {}


class TestRunner:
    """Execute tests with intelligent selection and fast-fail strategy."""

    def __init__(self, config_path: Path = Path(".qa-agent.yml")):
        """Initialize runner with configuration."""
        self.config = self._load_config(config_path)
        self.selector = TestSelector(config_path)
        self.fast_fail = self.config.get("test_execution", {}).get("fast_fail", True)
        self.timeout = self.config.get("test_execution", {}).get("timeout_seconds", 300)
        self.state_dir = Path(".qa-agent/state")
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def run_for_changes(self, changed_files: Set[str]) -> Dict[TestCategory, TestResult]:
        """Run tests for changed files."""
        categories = self.selector.select_for_changes(changed_files)

        print(f"📝 Changed files: {len(changed_files)}")
        print(f"🎯 Running tests: {', '.join(c.value for c in categories)}")

        return self.run_categories(categories)

    def run_categories(self, categories: List[TestCategory]) -> Dict[TestCategory, TestResult]:
        """Run specified test categories in order."""
        results = {}

        for category in categories:
            print(f"\n▶️  Running {category.value} tests...")

            result = self._run_category(category)
            results[category] = result

            # Print result
            status = "✅" if result.passed else "❌"
            print(f"{status} {category.value} tests: {'PASSED' if result.passed else 'FAILED'} ({result.duration:.2f}s)")

            # Stop on failure if fast_fail enabled
            if result.failed and self.fast_fail:
                print(f"\n🛑 Stopping (fast-fail enabled, {category.value} tests failed)")
                break

        return results

    def run_all(self) -> Dict[TestCategory, TestResult]:
        """Run all tests."""
        categories = self.selector.select_all()
        return self.run_categories(categories)

    def _run_category(self, category: TestCategory) -> TestResult:
        """Run tests for a specific category."""
        cmd = self._build_pytest_command(category)

        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self.timeout
        )
        duration = time.time() - start_time

        # Save JSON report
        report_file = self.state_dir / f"{category.value}-report.json"
        if report_file.exists():
            report_file_obj = report_file
        else:
            report_file_obj = None

        return TestResult(
            category=category,
            returncode=result.returncode,
            duration=duration,
            stdout=result.stdout,
            stderr=result.stderr,
            report_file=report_file_obj
        )

    def _build_pytest_command(self, category: TestCategory) -> List[str]:
        """Build pytest command for category."""
        test_dir = f"tests/{category.value}/"
        report_file = self.state_dir / f"{category.value}-report.json"

        cmd = [
            "pytest",
            test_dir,
            "-v",
            "--tb=short",
            "--json-report",
            f"--json-report-file={report_file}",
        ]

        if self.fast_fail:
            cmd.append("-x")  # Stop on first failure

        return cmd

    @staticmethod
    def _load_config(config_path: Path) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"⚠️  Config file not found: {config_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"❌ Error parsing config: {e}")
            return {}


def get_changed_files() -> Set[str]:
    """Get list of changed files using git diff."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("⚠️  Could not get changed files from git")
        return set()

    files = set(line.strip() for line in result.stdout.strip().split("\n") if line.strip())
    return files


def print_summary(results: Dict[TestCategory, TestResult]):
    """Print test execution summary."""
    total_duration = sum(r.duration for r in results.values())
    total_passed = sum(1 for r in results.values() if r.passed)
    total_failed = sum(1 for r in results.values() if r.failed)

    print("\n" + "=" * 60)
    print("📊 Test Execution Summary")
    print("=" * 60)
    print(f"Total Duration: {total_duration:.2f}s")
    print(f"Passed: {total_passed}/{len(results)}")
    print(f"Failed: {total_failed}/{len(results)}")

    if total_failed == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed. See details above.")

    print("=" * 60 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="QA Agent Test Runner")
    parser.add_argument(
        "--mode",
        choices=["auto", "all", "unit", "integration", "e2e"],
        default="auto",
        help="Test execution mode"
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="Specific files to test"
    )
    parser.add_argument(
        "--config",
        default=".qa-agent.yml",
        help="Path to configuration file"
    )

    args = parser.parse_args()

    runner = TestRunner(Path(args.config))

    # Determine what to run
    if args.mode == "auto":
        changed_files = get_changed_files()
        if not changed_files:
            print("ℹ️  No changed files detected")
            return
        results = runner.run_for_changes(changed_files)
    elif args.mode == "all":
        results = runner.run_all()
    elif args.files:
        changed_files = set(args.files)
        results = runner.run_for_changes(changed_files)
    else:
        # Single category
        category = TestCategory(args.mode)
        results = runner.run_categories([category])

    # Print summary
    print_summary(results)

    # Exit with failure code if any tests failed
    if any(r.failed for r in results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
