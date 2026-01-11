# Drawbridge Agent - Cursor Integration Guide

## Overview

The Drawbridge Task Runner is now configured as a Cursor agent that activates automatically when you mention specific keywords. This document explains how to integrate it into your Cursor workspace.

## Integration Steps

### Option 1: Add to Cursor Rules (Recommended)

1. **Open Cursor Settings**:
   - Go to `File` → `Preferences` → `Settings`
   - Search for "Rules for AI"
   - Or use `Ctrl+,` (Windows) / `Cmd+,` (Mac) and search "rules"

2. **Add Drawbridge Agent Rule**:
   - Open the rules editor
   - Copy the entire contents of `.moat/DRAWBRIDGE_AGENT_RULE.md`
   - Paste it into your Cursor rules file
   - Save the file

3. **Verify Integration**:
   - The agent will now activate when you use keywords like:
     - "Drawbridge"
     - "Process Drawbridge tasks"
     - "Run Drawbridge"
     - ".moat tasks"

### Option 2: Reference File (Alternative)

If you prefer to keep rules in a separate file:

1. **Add Reference in Cursor Rules**:
   ```markdown
   # Drawbridge Task Runner Agent
   
   See `.moat/DRAWBRIDGE_AGENT_RULE.md` for complete agent rules.
   
   When user mentions "Drawbridge" or "Process Drawbridge tasks", 
   activate the Drawbridge Task Runner agent as defined in that file.
   ```

2. **The agent will read the full rules from the file**

## Testing the Integration

### Test Activation

Try these prompts to verify the agent activates:

1. **Basic Activation**:
   ```
   Process Drawbridge tasks
   ```

2. **Alternative Phrasing**:
   ```
   Run Drawbridge on open tasks
   ```

3. **Direct Reference**:
   ```
   Work on the tasks in .moat/tasks.md
   ```

### Expected Behavior

When activated, the Drawbridge agent will:

1. ✅ Read `.moat/tasks.md` for open tasks
2. ✅ Read `.moat/task_details.json` for structured data
3. ✅ Reference `design-language-dream.md` for design tokens
4. ✅ Process tasks one by one (high → medium → low priority)
5. ✅ Make minimal, focused changes
6. ✅ Update task statuses with commit-style notes
7. ✅ Provide completion summary

## Agent Capabilities

### What Drawbridge Can Do

- ✅ Apply design language fixes (colors, spacing, typography)
- ✅ Fix accessibility issues (ARIA labels, focus states)
- ✅ Update component styling to match design tokens
- ✅ Fix visual bugs and inconsistencies
- ✅ Make minimal refactoring (when explicitly requested)

### What Drawbridge Won't Do

- ❌ Large architectural changes
- ❌ New feature development
- ❌ Backend modifications
- ❌ Major refactors
- ❌ Scope creep beyond task description

## Workflow Examples

### Example 1: Adding a Task

**You**: "The button on Dashboard doesn't match the design language - add this to Drawbridge"

**Drawbridge Agent**: 
- Creates task DREAM-XXX in `.moat/tasks.md`
- Adds structured entry to `.moat/task_details.json`
- Links to relevant design tokens

### Example 2: Processing Tasks

**You**: "Process Drawbridge tasks"

**Drawbridge Agent**:
- Reads all open tasks
- Processes them systematically
- Updates components
- Marks tasks as done
- Provides summary

### Example 3: Single Task Fix

**You**: "Fix the spacing issue on MetricCard - it's in Drawbridge as DREAM-042"

**Drawbridge Agent**:
- Locates DREAM-042 in tasks
- Reads MetricCard component
- Applies spacing fix using design scale
- Updates task status
- Documents change

## Integration with Other Agents

Drawbridge works seamlessly with your other Dream AI agents:

### Design System Enforcer → Drawbridge
- Design System Enforcer finds issues
- Creates Drawbridge tasks automatically
- Drawbridge processes the fixes

### Vision-based UI Reviewer → Drawbridge
- UI Reviewer identifies visual issues
- Creates Drawbridge tasks with screenshots
- Drawbridge implements the fixes

### UI Engineer → Drawbridge
- UI Engineer notices inconsistencies
- Creates Drawbridge tasks for follow-up
- Drawbridge applies the corrections

## Troubleshooting

### Agent Not Activating

**Issue**: Drawbridge agent doesn't activate when expected

**Solutions**:
1. Check that rules are saved in Cursor settings
2. Try explicit keywords: "Drawbridge agent", "Process Drawbridge"
3. Verify `.moat/DRAWBRIDGE_AGENT_RULE.md` exists
4. Restart Cursor if needed

### Tasks Not Processing

**Issue**: Agent activates but doesn't process tasks

**Solutions**:
1. Verify `.moat/tasks.md` has tasks with `[ ]` status
2. Check `.moat/task_details.json` has valid JSON
3. Ensure `design-language-dream.md` is accessible
4. Check file paths in tasks are correct

### Design Token Not Found

**Issue**: Agent can't find design token reference

**Solutions**:
1. Verify `design-language-dream.md` exists in project root
2. Check task has correct design token name
3. Agent will skip task with reasoning if token not found

## Best Practices

### Task Creation

1. **Be Specific**: Clear descriptions help agent understand the change
2. **Reference Design Language**: Mention specific sections when possible
3. **One Change Per Task**: Keep tasks focused and minimal
4. **Include File Paths**: Exact component paths speed up processing

### Task Processing

1. **Review Before Processing**: Check tasks make sense
2. **Process in Batches**: Handle related tasks together
3. **Verify Changes**: Review diffs after processing
4. **Test After Changes**: Ensure functionality preserved

### Maintenance

1. **Clean Up Completed Tasks**: Archive old completed tasks periodically
2. **Update Metadata**: Keep task counts accurate
3. **Review Skipped Tasks**: Understand why tasks were skipped
4. **Document Patterns**: Note common fixes for future reference

## File Structure

```
.moat/
├── tasks.md                    # Human-readable task list
├── task_details.json           # Structured task data
├── DRAWBRIDGE_AGENT_RULE.md    # Agent rules (for Cursor)
├── CURSOR_INTEGRATION.md        # This file
└── README.md                    # General documentation
```

## Next Steps

1. ✅ Add Drawbridge agent rules to Cursor settings
2. ✅ Test agent activation with sample prompts
3. ✅ Add your first real task to `.moat/tasks.md`
4. ✅ Process tasks and verify changes
5. ✅ Integrate with other Dream AI agents

## Support

If you encounter issues:

1. Check `.moat/README.md` for general documentation
2. Review `.moat/DRAWBRIDGE_AGENT_RULE.md` for agent behavior
3. Verify task format matches examples
4. Ensure design language file is accessible

---

**Version**: 1.0  
**Last Updated**: December 2025  
**Status**: Ready for integration











