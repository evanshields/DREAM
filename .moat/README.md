# Drawbridge Task Runner - Dream AI

## Overview

The Drawbridge Task Runner is a systematic approach to managing UI fixes and design consistency for the Dream AI application. It uses structured task files to track and implement incremental improvements.

## File Structure

```
.moat/
├── tasks.md                    # Human-readable task list with statuses
├── task_details.json           # Structured task data for automation
├── DRAWBRIDGE_AGENT_RULE.md    # Cursor agent rules (add to Cursor settings)
├── CURSOR_INTEGRATION.md       # Integration guide for Cursor
└── README.md                    # This file
```

## Usage

### Adding Tasks

**Option 1: Manual Entry**

Edit `tasks.md` and add a new task section:

```markdown
### Task Title
- **ID**: DREAM-XXX
- **Status**: [ ]
- **Component**: `path/to/component.tsx`
- **Description**: What needs to be changed
- **Details**: Specific instructions
- **Notes**: --
```

Then add corresponding JSON entry to `task_details.json`:

```json
{
  "id": "DREAM-XXX",
  "status": "open",
  "priority": "low|medium|high",
  "component": "path/to/component.tsx",
  "description": "What needs to be changed",
  "change_type": "style|structure|accessibility|bug",
  "design_token": "applicable-token-name",
  "created": "YYYY-MM-DD"
}
```

**Option 2: AI-Assisted**

Simply describe the issue to the Dream AI agent with "Drawbridge task" or "Add to .moat" and it will:
1. Create the task in both `tasks.md` and `task_details.json`
2. Assign appropriate ID, priority, and metadata
3. Link to relevant design tokens from `design-language-dream.md`

### Processing Tasks

**Activate the Drawbridge Task Runner agent** (now integrated as a Cursor agent):

```
Process Drawbridge tasks
```

Or use any of these phrases:
- "Run Drawbridge"
- "Work on .moat tasks"
- "Fix the open Drawbridge tasks"

The agent will:
1. Read all open tasks from `.moat/tasks.md`
2. Reference design tokens from `design-language-dream.md`
3. Locate affected components
4. Apply minimal, focused changes
5. Update task statuses
6. Add commit-style notes to `tasks.md`

**Note**: See `.moat/CURSOR_INTEGRATION.md` for instructions on adding the Drawbridge agent to your Cursor rules.

### Task Statuses

- `[ ]` **Open**: Ready to be worked on
- `[-]` **In Progress**: Currently being implemented
- `[x]` **Done**: Completed with notes
- `[~]` **Skipped**: Not applicable with reasoning

## Task Types

### Style Changes
- Color corrections (align to design tokens)
- Spacing adjustments (use design scale)
- Typography fixes (font families, sizes, weights)
- Border and shadow updates

### Structure Changes
- Component refactoring (minimal, requested only)
- Prop API adjustments
- Layout improvements

### Accessibility
- ARIA label additions
- Focus state improvements
- Contrast fixes
- Keyboard navigation

### Bug Fixes
- Visual glitches
- Responsive issues
- State management bugs (UI-related only)

## Design Language Integration

All tasks must reference and follow `design-language-dream.md`:

- **Colors**: Use design tokens, not hardcoded values
- **Spacing**: Use Tailwind scale (4, 6, 8, etc.)
- **Typography**: Use `font-heading` (Playfair Display) or `font-sans` (Libre Franklin)
- **Components**: Follow component token specifications

## Best Practices

### Keep Changes Minimal
- One logical change per task
- Smallest possible diff
- No scope creep

### Reference Design Language
- Always link to design tokens
- Cite specific sections (e.g., "Colors > Primary Colors")
- Maintain consistency with design system

### Document Changes
- Add commit-style notes to tasks
- Include before/after context
- Link to related tasks if applicable

### Test After Changes
- Verify visual appearance
- Check responsive behavior
- Test accessibility (keyboard, screen reader)

## Example Workflow

1. **User reports**: "The primary button on the Dashboard page doesn't match the design language"

2. **AI creates task**:
   ```markdown
   ### Fix Dashboard Primary Button Color
   - **ID**: DREAM-042
   - **Status**: [ ]
   - **Component**: `src/pages/Dashboard.tsx`
   - **Description**: Update primary button to use YinMn Blue (#2E5090)
   - **Details**: Replace current blue with design token yinmn-blue
   - **Notes**: --
   ```

3. **AI processes task**:
   - Locates button in `Dashboard.tsx`
   - Applies color change: `bg-[#2E5090] hover:bg-[#1E3A6B]`
   - Updates task status to `[x]`
   - Adds note: "Applied YinMn Blue per design-language-dream.md line 40"

4. **Task is completed and moved to Completed section**

## Constraints

### What Drawbridge Does
- ✅ Incremental, focused UI fixes
- ✅ Design language enforcement
- ✅ Accessibility improvements
- ✅ Visual consistency updates

### What Drawbridge Doesn't Do
- ❌ Large architectural changes
- ❌ New feature development
- ❌ Backend modifications
- ❌ Database schema changes
- ❌ Major refactors

## Integration with Other Agents

Drawbridge Task Runner works alongside other Dream AI agents:

- **Design System Enforcer**: Finds issues → Creates Drawbridge tasks
- **UX Engineer**: Identifies improvements → Creates Drawbridge tasks
- **UI Implementer**: Requests fixes → Creates Drawbridge tasks

## Metrics

Track task completion in `task_details.json` metadata:

```json
"metadata": {
  "last_updated": "2025-12-20",
  "total_tasks": 50,
  "open_tasks": 12,
  "in_progress": 3,
  "completed": 33,
  "skipped": 2
}
```

## Cursor Agent Integration

The Drawbridge Task Runner is now available as a **Cursor agent** that activates automatically. 

**Quick Setup**:
1. Open `.moat/DRAWBRIDGE_AGENT_RULE.md`
2. Copy the agent rules
3. Add to your Cursor rules (Settings → Rules for AI)
4. Start using: "Process Drawbridge tasks"

See `.moat/CURSOR_INTEGRATION.md` for detailed integration instructions.

## Version History

- **v1.1** (December 2025): Added Cursor agent integration with automatic activation
- **v1.0** (December 2025): Initial Drawbridge Task Runner setup for Dream AI


