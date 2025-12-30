# QA Agent User Guide

**Version**: 1.0
**Last Updated**: December 2025
**Status**: Ready to Use

---

## Overview

The QA Agent is an autonomous testing & quality assurance system for Dream Vision that:

- ✅ **Auto-invokes** when code changes are detected
- ✅ **Runs tests intelligently** (unit → integration → E2E)
- ✅ **Debugs failures** and attempts autonomous fixes
- ✅ **Generates tests** from testing guides
- ✅ **Produces comprehensive reports** (HTML, Markdown, JSON)

---

## Quick Start

### Installation

1. **Install dependencies**:
   ```bash
   pip install -r .qa-agent/requirements.txt
   ```

2. **Verify setup**:
   ```bash
   python .qa-agent/scripts/runner.py --mode=unit
   ```

### Basic Usage

#### Run Tests for Changed Files
```bash
npm run qa:run
```
Detects which files changed and runs only affected tests (smart selection).

#### Debug Test Failures
```bash
npm run qa:debug
```
Analyzes test failures and attempts to fix common issues automatically.

#### Generate Tests from Guide
```bash
npm run qa:generate
```
Parses the testing guide and generates missing tests.

#### Generate Reports
```bash
npm run qa:report
```
Creates comprehensive test reports in HTML, Markdown, and JSON formats.

---

## Operating Modes

### 1. QA Runner (Auto-Invoked)

**Trigger**: File save in `src/`, `backend/`, or `tests/`

**What it does**:
1. Detects changed files using `git diff`
2. Maps files to affected test categories
3. Runs tests: unit (fastest) → integration → E2E
4. Stops on first failure (fast-fail strategy)
5. Attempts autonomous fixes
6. Reports results

**Example Output**:
```
📝 Changed files: 3
🎯 Running tests: unit, integration

▶️  Running unit tests...
✅ unit tests: PASSED (1.2s)

▶️  Running integration tests...
✅ integration tests: PASSED (0.9s)

📊 Test Execution Summary
==================================================
Total Duration: 2.1s
Passed: 45/45
Failed: 0/45
✅ All tests passed!
==================================================
```

### 2. QA Debugger

**Trigger**: User mentions "debug test failures"

**What it does**:
1. Reads test output and JSON reports
2. Categorizes failures (auto-fixable vs. manual)
3. Attempts autonomous fixes:
   - ImportError: Add missing imports
   - SnapshotMismatch: Update snapshot files
   - TimeoutError: Increase pytest.ini timeout
   - FixtureLookupError: Update test signatures
4. Reports what was fixed and what needs attention

**Example Output**:
```
🔍 Failure Analysis
==================================================

🔧 Auto-Fixable (2):
  • test_import_module - ImportError
    Type: import_error
    Message: cannot import name 'IRRCalculator'

  • test_snapshot_ui - Snapshot mismatch
    Type: snapshot_mismatch
    Message: Snapshot does not match

⚠️  Requires Human Intervention (1):
  • test_roi_calculation - AssertionError
    Type: assertion_error
    Message: Expected 14.5%, got 12.3%

==================================================
```

### 3. QA Generator

**Trigger**: User mentions "generate tests"

**What it does**:
1. Parses testing guide (TESTING_GUIDE_TASKS_1.0_TO_1.22.md)
2. Extracts task descriptions and test steps
3. Generates test code from templates
4. Creates files in appropriate test directories
5. Runs generated tests to verify

**Example Output**:
```
📖 Parsed 25 tasks from guide

📝 Test Generation Summary
==================================================
Total tasks: 25
Completed (✅): 15
To generate: 10
==================================================

Generated tests:
  • Task 1.14 - OM Extraction Service
  • Task 1.15 - T-12 Extraction Service
  • Task 1.16 - Rent Roll Extraction Service

✅ Generated 3 test files
```

### 4. QA Reporter

**Trigger**: User mentions "test report"

**What it does**:
1. Collects test results from pytest JSON reports
2. Calculates metrics (pass rate, coverage, duration)
3. Generates reports in multiple formats:
   - **HTML**: Interactive dashboard with Minimal Pro theme
   - **Markdown**: Summary for PR comments
   - **JSON**: Structured data for analysis
4. Includes trend analysis and recommendations

**Report Location**: `reports/test-report-{timestamp}.html`

---

## Configuration

The QA Agent is configured via `.qa-agent.yml`. Key settings:

```yaml
auto_invoke:
  enabled: true
  debounce_ms: 500          # Wait 500ms after last change

test_execution:
  fast_fail: true           # Stop on first failure
  order: [unit, integration, e2e]
  timeout_seconds: 300

auto_fix:
  enabled: true
  fixable_errors:           # These will be auto-fixed
    - import_error
    - fixture_error
    - snapshot_mismatch
    - timeout_error

test_generation:
  auto_run_generated: true  # Verify generated tests pass

reporting:
  formats: [html, markdown, json]
  metrics: [pass_rate, coverage_percent, performance_ms]
```

---

## Smart File-to-Test Mapping

The QA Agent intelligently selects which tests to run based on what changed:

| Changed File Pattern | Tests to Run |
|---|---|
| `src/lib/shieldstone/*.py` | unit + integration |
| `src/components/**/*.tsx` | integration + E2E |
| `src/pages/**/*.tsx` | E2E |
| `backend/services/**/*.py` | unit + integration |
| `backend/api/**/*.py` | integration + E2E |
| `tests/**/*.py` | re-run changed test |

---

## Auto-Fix Capabilities

The QA Agent can automatically fix these common issues:

### 1. ImportError
```python
# Before
from wrong.module import NotFound

# After (auto-fixed)
from correct.module import Found
```

### 2. SnapshotMismatch
- Automatically runs `pytest --snapshot-update`
- Updates snapshot files with new values

### 3. TimeoutError
- Increases timeout in `pytest.ini`
- Doubles the current timeout value

### 4. FixtureLookupError
- Updates test function signatures
- Adds missing fixture parameters

---

## Test Generation from Guides

Generate tests automatically from `TESTING_GUIDE_TASKS_1.0_TO_1.22.md`:

```bash
npm run qa:generate
```

The generator will:
1. Parse task descriptions and test steps
2. Create test code using templates
3. Follow existing test patterns
4. Place tests in correct directories
5. Verify tests pass

**Generated Test Structure**:
```python
class TestTaskName:
    """Test for Task X.Y: Description"""

    def test_basic_functionality(self):
        """Test basic behavior with expected steps"""
        # Test steps formatted as comments
        # Placeholder assertions to implement
        pass
```

---

## Report Formats

### HTML Reports

Interactive HTML dashboard with:
- 📊 Metrics summary (pass rate, duration, coverage)
- 📈 Charts and trend analysis
- 📋 Detailed results by category
- 🎨 Minimal Pro styling

Location: `reports/test-report-{timestamp}.html`

### Markdown Reports

Summary for PR comments:
```markdown
# Dream AI Test Report

## Summary
| Metric | Value |
|--------|-------|
| Total Tests | 67 |
| Passed | 66 ✅ |
| Failed | 1 ❌ |
| Pass Rate | 98.5% |
| Duration | 2.3s |

## Results by Category
### unit
- Status: ✅ PASSED
- Duration: 1.2s
```

### JSON Reports

Structured data for programmatic access:
```json
{
  "metadata": {
    "timestamp": "2025-12-25T10:30:00Z",
    "version": "1.0"
  },
  "summary": {
    "total_tests": 67,
    "passed": 66,
    "failed": 1,
    "pass_rate": 98.5
  }
}
```

---

## Troubleshooting

### QA Agent Not Running

**Problem**: Tests not running when files change

**Solution**:
1. Check that `.qa-agent.yml` exists and is configured
2. Verify pytest is installed: `pip install pytest`
3. Try running manually: `npm run qa:run`

### Import Errors in Generated Tests

**Problem**: Generated tests have ImportError

**Solution**:
1. Run the debugger: `npm run qa:debug --fix`
2. Or manually add missing imports to generated test file

### Snapshot Mismatches

**Problem**: Snapshot tests failing after UI changes

**Solution**:
1. Review the changes carefully
2. Update snapshots: `npm run qa:debug --fix`
3. Or manually: `pytest --snapshot-update`

### Configuration Issues

**Problem**: Settings from `.qa-agent.yml` not applying

**Solution**:
1. Verify YAML syntax is correct
2. Check file paths are relative to project root
3. Restart any running processes

---

## Best Practices

### 1. Keep Tests Fast
- Unit tests should complete in <1ms
- Integration tests in <10ms
- E2E tests in <30s each

### 2. Use Meaningful Test Names
```python
# Good
def test_noi_calculation_with_vacancy_adjustment():
    pass

# Bad
def test_calc():
    pass
```

### 3. Test Behavioral Changes
- When fixing bugs, add tests to prevent regressions
- When adding features, generate tests from guide first

### 4. Review Auto-Fixed Tests
- QA Agent fixes are safe, but review them
- Verify the fixes maintain test intent
- Commit the fixes to git

### 5. Generate Tests from Guides
- Keep testing guide synchronized with code
- Generate missing tests regularly
- Delete obsolete tests when features removed

---

## Integration with Cursor

The QA Agent integrates with Cursor's rules system:

1. **Auto-activation**: File saves trigger test runs automatically
2. **npm commands**: Use `npm run qa:*` for quick access
3. **Reports**: Review HTML reports in browser
4. **Debugging**: Use `/qa-debug` or `npm run qa:debug`

---

## Performance Metrics

### Expected Execution Times
- **Unit tests**: ~1.2s (27 tests at 1ms each)
- **Integration tests**: ~0.9s (18 tests at 10ms each)
- **E2E tests**: ~25s (22 tests at 5-30s each)
- **Total suite**: ~2.3s fast path, ~30s full suite

### Coverage Targets
- **Overall**: >95%
- **Financial calculations**: 100%
- **Scenario management**: >98%
- **User workflows**: >90%

---

## Getting Help

### View QA Agent Status
```bash
python .qa-agent/scripts/runner.py --mode=all
```

### Test Specific File
```bash
python .qa-agent/scripts/runner.py --files=src/lib/shieldstone/returns.py
```

### Generate Report Only
```bash
python .qa-agent/scripts/reporter.py --generate
```

### View Configuration
```bash
cat .qa-agent.yml
```

---

## Advanced Usage

### Run Only Unit Tests
```bash
npm run test:unit
```

### Run with Coverage Report
```bash
npm run test:coverage
```

### Run Tests in Watch Mode
```bash
npm run test:watch
```

### Generate Tests for Specific Task
```bash
python .qa-agent/scripts/generator.py --guide=TESTING_GUIDE_TASKS_1.0_TO_1.22.md --task=1.14
```

---

## Next Steps

1. ✅ **Understand the basics** (read above)
2. ✅ **Try the commands** (`npm run qa:*`)
3. ✅ **Review generated reports** (check `reports/` folder)
4. ✅ **Make code changes** (QA Agent runs automatically)
5. ✅ **Generate tests** (from testing guide)
6. ✅ **Improve coverage** (track in reports)

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review `.qa-agent.yml` configuration
3. Check test output for detailed errors
4. Review plan file: `C:\Users\evana\.claude\plans\snug-greeting-deer.md`

---

**Happy Testing! 🚀**

The QA Agent is here to automate your testing workflow and give you fast feedback on code changes.
