#!/usr/bin/env python3
"""
QA Agent Test Generator
Generates tests from testing guides.

Usage:
    python generator.py --guide=TESTING_GUIDE_TASKS_1.0_TO_1.22.md
    python generator.py --guide=path/guide.md --type=unit
    python generator.py --task=1.10
"""

import re
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import argparse
import yaml


@dataclass
class TestTask:
    """Test task extracted from testing guide."""
    task_number: str
    name: str
    description: str
    test_steps: List[str]
    expected_result: str
    file_path: Optional[str] = None
    status: str = "unknown"  # ✅ | ❌ | ⏳


class TestingGuideParser:
    """Parse testing guides to extract test scenarios."""

    def parse_guide(self, guide_path: Path) -> List[TestTask]:
        """Parse testing guide and extract test tasks."""
        with open(guide_path, "r") as f:
            content = f.read()

        tasks = []

        # Match ### Task X.Y: Name pattern
        task_pattern = r"###\s+Task\s+([\d.]+):\s+(.+?)$\n(.*?)(?=###\s+Task|##[^#]|\Z)"

        for match in re.finditer(task_pattern, content, re.MULTILINE | re.DOTALL):
            task_num = match.group(1)
            task_name = match.group(2).strip()
            task_content = match.group(3)

            # Extract test steps
            test_steps = self._extract_test_steps(task_content)

            # Extract expected results
            expected_result = self._extract_expected_result(task_content)

            # Determine status
            status = self._determine_status(task_content)

            # Determine file path if mentioned
            file_path = self._extract_file_path(task_content)

            task = TestTask(
                task_number=task_num,
                name=task_name,
                description=task_content[:200],  # First 200 chars
                test_steps=test_steps,
                expected_result=expected_result,
                file_path=file_path,
                status=status,
            )
            tasks.append(task)

        return tasks

    def _extract_test_steps(self, content: str) -> List[str]:
        """Extract test steps from task content."""
        steps = []

        # Look for "#### Test Steps:" section
        match = re.search(
            r"####\s+Test Steps:(.*?)(?=####|\Z)",
            content,
            re.DOTALL
        )

        if match:
            steps_section = match.group(1)

            # Extract numbered or bulleted items
            for line in steps_section.split("\n"):
                line = line.strip()
                # Match numbered lists, checkboxes, or bullets
                if re.match(r"^\d+\.|^\-\s+\[|\-\s+", line):
                    # Clean up the line
                    clean = re.sub(r"^\d+\.\s*|\-\s*\[.*?\]\s*|\-\s+", "", line)
                    if clean:
                        steps.append(clean)

        return steps[:10]  # Limit to 10 steps

    def _extract_expected_result(self, content: str) -> str:
        """Extract expected result from task content."""
        match = re.search(
            r"\*\*Expected Result:\*\*\s+(.+?)(?=\n\n|###|\Z)",
            content,
            re.DOTALL
        )

        if match:
            result = match.group(1).strip()
            # Clean up markdown
            result = re.sub(r"\n\s+", " ", result)
            return result[:200]  # Limit to 200 chars

        return "Tests pass without errors"

    def _determine_status(self, content: str) -> str:
        """Determine if task is complete based on status indicator."""
        if "✅" in content or "Complete" in content:
            return "✅"
        elif "❌" in content or "Incomplete" in content:
            return "❌"
        else:
            return "⏳"

    def _extract_file_path(self, content: str) -> Optional[str]:
        """Extract file path if mentioned in task."""
        match = re.search(r"\*\*File(s)?:\*\s+`?([^`\n]+)`?", content)
        if match:
            return match.group(2).strip()
        return None


class TestGenerator:
    """Generate test code from testing guide scenarios."""

    def __init__(self, templates_dir: Path = Path(".qa-agent/templates")):
        """Initialize generator with templates."""
        self.templates_dir = templates_dir

    def generate_test(
        self,
        task: TestTask,
        test_type: str = "unit"
    ) -> str:
        """Generate test code for a task."""
        template = self._load_template(test_type)

        if not template:
            return f"# Could not load template for {test_type}"

        # Create test name
        test_name = self._make_test_name(task.name)

        # Format test steps as comments
        steps_comment = self._format_test_steps(task.test_steps)

        # Fill template
        test_code = template.format(
            task_number=task.task_number,
            test_name=test_name,
            test_description=task.name,
            test_steps=steps_comment,
            expected_result=task.expected_result,
        )

        return test_code

    def generate_tests_for_guide(
        self,
        guide_path: Path,
        test_type: str = "unit"
    ) -> Dict[str, str]:
        """Generate tests for all tasks in a guide."""
        parser = TestingGuideParser()
        tasks = parser.parse_guide(guide_path)

        generated = {}
        for task in tasks:
            if task.status == "✅":  # Skip completed tasks
                continue

            test_code = self.generate_test(task, test_type)
            generated[task.task_number] = test_code

        return generated

    def _load_template(self, test_type: str) -> Optional[str]:
        """Load test template."""
        template_file = self.templates_dir / f"{test_type}-test.template.py"

        try:
            with open(template_file, "r") as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️  Template not found: {template_file}")
            return None

    def _make_test_name(self, task_name: str) -> str:
        """Convert task name to test function name."""
        # "Manual Entry Form" → "test_manual_entry_form"
        name = task_name.lower()
        name = re.sub(r"[^\w\s]", "", name)
        name = re.sub(r"\s+", "_", name)
        return f"test_{name}"

    def _format_test_steps(self, steps: List[str]) -> str:
        """Format test steps as code comments."""
        if not steps:
            return "    # Test implementation goes here"

        formatted = []
        for i, step in enumerate(steps, 1):
            # Clean up the step
            clean_step = re.sub(r"^\d+\.\s*|\-\s*\[\s*\]\s*", "", step)
            formatted.append(f"        # {i}. {clean_step}")

        return "\n".join(formatted)


def save_generated_tests(
    generated: Dict[str, str],
    output_dir: Path = Path("tests/unit")
) -> int:
    """Save generated test code to files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_count = 0

    for task_num, test_code in generated.items():
        # Create filename from task number
        filename = f"test_task_{task_num.replace('.', '_')}.py"
        filepath = output_dir / filename

        # Check if file already exists
        if filepath.exists():
            print(f"⏭️  Skipping {filename} (already exists)")
            continue

        try:
            with open(filepath, "w") as f:
                f.write(test_code)
            print(f"✅ Created: {filepath}")
            saved_count += 1
        except Exception as e:
            print(f"❌ Error saving {filepath}: {e}")

    return saved_count


def print_generation_summary(
    tasks: List[TestTask],
    generated: Dict[str, str]
):
    """Print generation summary."""
    print("\n" + "=" * 60)
    print("📝 Test Generation Summary")
    print("=" * 60)
    print(f"Total tasks: {len(tasks)}")
    print(f"Completed (✅): {sum(1 for t in tasks if t.status == '✅')}")
    print(f"To generate: {len(generated)}")
    print("=" * 60 + "\n")

    if generated:
        print("Generated tests:")
        for task_num in sorted(generated.keys()):
            print(f"  • Task {task_num}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="QA Agent Test Generator")
    parser.add_argument(
        "--guide",
        required=True,
        help="Path to testing guide"
    )
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "e2e"],
        default="unit",
        help="Type of tests to generate"
    )
    parser.add_argument(
        "--task",
        help="Specific task to generate (e.g., 1.10)"
    )
    parser.add_argument(
        "--output",
        help="Output directory for generated tests"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show generated code without saving"
    )

    args = parser.parse_args()

    guide_path = Path(args.guide)
    if not guide_path.exists():
        print(f"❌ Guide file not found: {guide_path}")
        return

    # Parse guide
    parser_obj = TestingGuideParser()
    tasks = parser_obj.parse_guide(guide_path)

    print(f"📖 Parsed {len(tasks)} tasks from guide")

    # Generate tests
    generator = TestGenerator()

    if args.task:
        # Generate specific task
        task = next((t for t in tasks if t.task_number == args.task), None)
        if not task:
            print(f"❌ Task {args.task} not found")
            return

        test_code = generator.generate_test(task, args.type)

        if args.dry_run:
            print("\n📄 Generated Test Code:\n")
            print(test_code)
        else:
            print(f"✅ Generated test for task {args.task}")
    else:
        # Generate all incomplete tasks
        generated = generator.generate_tests_for_guide(guide_path, args.type)

        # Print summary
        print_generation_summary(tasks, generated)

        # Save if not dry-run
        if not args.dry_run and generated:
            output_dir = Path(args.output or f"tests/{args.type}")
            saved = save_generated_tests(generated, output_dir)
            print(f"\n✅ Generated {saved} test files")
        elif args.dry_run:
            print("📄 Generated code (dry-run mode):")
            for task_num, code in generated.items():
                print(f"\n--- Task {task_num} ---")
                print(code[:300] + "...")


if __name__ == "__main__":
    main()
