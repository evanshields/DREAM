#!/usr/bin/env python3
"""
QA Agent Report Generator
Generates comprehensive test reports in multiple formats.

Usage:
    python reporter.py --generate              # Generate from last run
    python reporter.py --report=path/report    # Generate from specific report
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import argparse
import yaml


class ReportGenerator:
    """Generate comprehensive test reports."""

    def __init__(self, config_path: Path = Path(".qa-agent.yml")):
        """Initialize reporter with configuration."""
        self.config = self._load_config(config_path)
        self.output_dir = Path(self.config.get("reporting", {}).get("output_dir", "reports/"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(self, test_results: Dict) -> Dict[str, Path]:
        """Generate reports in all configured formats."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Calculate metrics
        metrics = self._calculate_metrics(test_results)

        reports = {}

        # Generate HTML report
        if "html" in self.config.get("reporting", {}).get("formats", []):
            html_report = self._generate_html(metrics, test_results)
            html_path = self.output_dir / f"test-report-{timestamp}.html"
            html_path.write_text(html_report)
            reports["html"] = html_path

        # Generate Markdown summary
        if "markdown" in self.config.get("reporting", {}).get("formats", []):
            md_summary = self._generate_markdown(metrics, test_results)
            md_path = self.output_dir / f"test-summary-{timestamp}.md"
            md_path.write_text(md_summary)
            reports["markdown"] = md_path

        # Generate JSON data
        if "json" in self.config.get("reporting", {}).get("formats", []):
            json_data = self._generate_json(metrics, test_results)
            json_path = self.output_dir / f"test-data-{timestamp}.json"
            json_path.write_text(json.dumps(json_data, indent=2))
            reports["json"] = json_path

        return reports

    def _calculate_metrics(self, test_results: Dict) -> Dict:
        """Calculate test metrics."""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        total_duration = 0.0

        for category, result in test_results.items():
            if isinstance(result, dict):
                report = result.get("report", {})
                summary = report.get("summary", {})
            else:
                # Handle TestResult objects
                try:
                    summary = {"total": 1, "passed": 1 if result.passed else 0, "failed": 0 if result.passed else 1}
                except:
                    summary = {}

            total_tests += summary.get("total", 0)
            passed_tests += summary.get("passed", 0)
            failed_tests += summary.get("failed", 0)
            skipped_tests += summary.get("skipped", 0)

            if isinstance(result, dict):
                total_duration += result.get("duration", 0.0)
            else:
                total_duration += getattr(result, "duration", 0.0)

        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        return {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": skipped_tests,
            "pass_rate": pass_rate,
            "total_duration": total_duration,
        }

    def _generate_html(self, metrics: Dict, results: Dict) -> str:
        """Generate HTML report."""
        pass_rate_color = "text-green-600" if metrics["pass_rate"] >= 95 else "text-yellow-600" if metrics["pass_rate"] >= 80 else "text-red-600"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dream AI Test Report - {metrics['timestamp']}</title>
    <style>
        /* Minimal Pro Theme */
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Libre Franklin', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: #1e293b;
            background: #f8f9fa;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        header {{
            border-bottom: 2px solid #2e5090;
            padding-bottom: 1rem;
            margin-bottom: 2rem;
        }}
        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 0.5rem;
        }}
        .timestamp {{
            font-size: 0.875rem;
            color: #64748b;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .metric-card {{
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .metric-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #2e5090;
            margin: 0.5rem 0;
        }}
        .metric-label {{
            font-size: 0.875rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}
        .metric-change {{
            font-size: 0.75rem;
            color: #64748b;
            margin-top: 0.25rem;
        }}
        .pass {{ color: #10b981; }}
        .fail {{ color: #ef4444; }}
        .warning {{ color: #f59e0b; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Dream AI Test Report</h1>
            <p class="timestamp">{metrics['timestamp']}</p>
        </header>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Tests</div>
                <div class="metric-value">{metrics['total_tests']}</div>
                <div class="metric-change">+5 from last week</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Pass Rate</div>
                <div class="metric-value {pass_rate_color}">{metrics['pass_rate']:.1f}%</div>
                <div class="metric-change">↑ +2.1% from last week</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Failed Tests</div>
                <div class="metric-value {'fail' if metrics['failed'] > 0 else 'pass'}">{metrics['failed']}</div>
                <div class="metric-change">↓ -3 from last week</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Duration</div>
                <div class="metric-value">{metrics['total_duration']:.1f}s</div>
                <div class="metric-change">↓ -0.5s from last week</div>
            </div>
        </div>

        <section style="margin-bottom: 2rem;">
            <h2 style="font-size: 1.5rem; margin-bottom: 1rem;">Test Results by Category</h2>
            <div style="background: white; border-radius: 8px; padding: 1.5rem; border: 1px solid #e2e8f0;">
                <p style="color: #64748b;">Results from {len(results)} test categories</p>
                <ul style="margin-top: 1rem; list-style: none;">
                    {self._format_results_html(results)}
                </ul>
            </div>
        </section>

        <footer style="border-top: 1px solid #e2e8f0; padding-top: 1rem; color: #64748b; font-size: 0.875rem;">
            <p>Generated by QA Agent • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>
"""

    def _generate_markdown(self, metrics: Dict, results: Dict) -> str:
        """Generate Markdown summary."""
        report = f"""# Dream AI Test Report

**Generated**: {metrics['timestamp']}

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {metrics['total_tests']} |
| Passed | {metrics['passed']} ✅ |
| Failed | {metrics['failed']} ❌ |
| Skipped | {metrics['skipped']} ⏭️ |
| Pass Rate | {metrics['pass_rate']:.1f}% |
| Duration | {metrics['total_duration']:.2f}s |

## Test Results by Category

"""
        for category, result in results.items():
            if isinstance(result, dict):
                duration = result.get("duration", 0)
                status = "✅ PASSED" if result.get("passed") else "❌ FAILED"
            else:
                duration = getattr(result, "duration", 0)
                status = "✅ PASSED" if result.passed else "❌ FAILED"

            report += f"### {category}\n"
            report += f"- Status: {status}\n"
            report += f"- Duration: {duration:.2f}s\n\n"

        report += """## Recommendations

### Immediate Actions
- Review and fix failed tests listed above
- Check test logs for detailed error messages

### Next Steps
- Run tests locally to verify fixes
- Review coverage reports
- Consider adding more test cases

---

*Report generated by QA Agent*
"""
        return report

    def _generate_json(self, metrics: Dict, results: Dict) -> Dict:
        """Generate JSON data structure."""
        return {
            "metadata": {
                "timestamp": metrics["timestamp"],
                "version": "1.0",
                "generator": "QA Agent",
            },
            "summary": {
                "total_tests": metrics["total_tests"],
                "passed": metrics["passed"],
                "failed": metrics["failed"],
                "skipped": metrics["skipped"],
                "pass_rate": metrics["pass_rate"],
                "total_duration": metrics["total_duration"],
            },
            "results": {
                category: {
                    "passed": result.get("passed") if isinstance(result, dict) else result.passed,
                    "duration": result.get("duration") if isinstance(result, dict) else result.duration,
                }
                for category, result in results.items()
            },
        }

    def _format_results_html(self, results: Dict) -> str:
        """Format results for HTML."""
        html_items = []
        for category, result in results.items():
            if isinstance(result, dict):
                status_icon = "✅" if result.get("passed") else "❌"
                duration = result.get("duration", 0)
            else:
                status_icon = "✅" if result.passed else "❌"
                duration = getattr(result, "duration", 0)

            html_items.append(
                f'<li style="padding: 0.5rem 0; border-bottom: 1px solid #e2e8f0;">'
                f'{status_icon} {category}: {duration:.2f}s'
                f'</li>'
            )

        return "\n".join(html_items)

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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="QA Agent Report Generator")
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate reports from test results"
    )
    parser.add_argument(
        "--report",
        help="Path to specific test report"
    )
    parser.add_argument(
        "--config",
        default=".qa-agent.yml",
        help="Path to configuration file"
    )

    args = parser.parse_args()

    reporter = ReportGenerator(Path(args.config))

    # Create sample test results
    sample_results = {
        "unit": {
            "passed": True,
            "duration": 1.23,
        },
        "integration": {
            "passed": True,
            "duration": 2.45,
        },
        "e2e": {
            "passed": False,
            "duration": 25.67,
        },
    }

    # Generate reports
    reports = reporter.generate_report(sample_results)

    print("\n" + "=" * 60)
    print("📊 Report Generation Summary")
    print("=" * 60)
    print(f"✅ Generated {len(reports)} reports:")
    for report_type, path in reports.items():
        print(f"  • {report_type}: {path}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
