# Claude Skills Catalog

**Total Available Skills: 52**

This document catalogs all Claude Code skills available in this project. Skills extend Claude's capabilities with specialized knowledge, workflows, and tool integrations.

---

## How to Use Skills

Skills are automatically triggered when relevant to your request, or you can explicitly invoke them by:
- Mentioning the skill name in your message
- Using the format: `/skill-name` (e.g., `/test-driven-development`)
- Asking Claude to use a specific skill: "Use the systematic-debugging skill to help me find this bug"

---

## Table of Contents

1. [MCP & Content Extraction Tools](#mcp--content-extraction-tools)
2. [Creative & Design Skills](#creative--design-skills)
3. [Document & Content Creation](#document--content-creation)
4. [Web & Application Development](#web--application-development)
5. [Meta Skills](#meta-skills)
6. [Collaboration Skills](#collaboration-skills)
7. [Debugging Skills](#debugging-skills)
8. [Problem-Solving Skills](#problem-solving-skills)
9. [Testing Skills](#testing-skills)
10. [Research Skills](#research-skills)
11. [Architecture Skills](#architecture-skills)

---

## MCP & Content Extraction Tools

### article-extractor
**Description:** Extract clean article content from URLs (blog posts, articles, tutorials) and save as readable text. Use when you want to download, extract, or save an article/blog post from a URL without ads, navigation, or clutter.

**How to invoke:**
- "Extract the article from [URL]"
- "Download this blog post as clean text"
- `/article-extractor [URL]`

**Location:** `.claude/skills/article-extractor/`

---

### ship-learn-next
**Description:** Transform learning content (like YouTube transcripts, articles, tutorials) into actionable implementation plans using the Ship-Learn-Next framework. Use when you want to turn advice, lessons, or educational content into concrete action steps, reps, or a learning quest.

**How to invoke:**
- "Turn this tutorial into an action plan"
- "Make this learning content actionable"
- `/ship-learn-next [content]`

**Location:** `.claude/skills/ship-learn-next/`

---

### tapestry
**Description:** Unified content extraction and action planning. Automatically detects content type (YouTube video, article, PDF) and processes accordingly to extract content and create an action plan.

**How to invoke:**
- "tapestry [URL]"
- "weave [URL]"
- "help me plan [URL]"
- "extract and plan [URL]"
- "make this actionable [URL]"

**Location:** `.claude/skills/tapestry/`

---

### youtube-transcript
**Description:** Download YouTube video transcripts. Use when you need to get captions, subtitles, or transcribe a YouTube video.

**How to invoke:**
- "Get the transcript from [YouTube URL]"
- "Download YouTube captions from [URL]"
- `/youtube-transcript [URL]`

**Location:** `.claude/skills/youtube-transcript/`

---

## Creative & Design Skills

### algorithmic-art
**Description:** Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. Use for generative art, algorithmic art, flow fields, or particle systems.

**How to invoke:**
- "Create generative art that..."
- "Make algorithmic art using flow fields"
- "Build a p5.js particle system"

**Location:** `.claude/skills/algorithmic-art/`

---

### brand-guidelines
**Description:** Applies Anthropic's official brand colors and typography to any artifact. Use when brand colors, style guidelines, visual formatting, or company design standards apply.

**How to invoke:**
- "Apply Anthropic brand guidelines to this"
- "Use Anthropic's brand colors"
- "Style this with company design standards"

**Location:** `.claude/skills/brand-guidelines/`

---

### canvas-design
**Description:** Create beautiful visual art in .png and .pdf documents using design philosophy. Use when creating posters, pieces of art, designs, or other static pieces.

**How to invoke:**
- "Design a poster for..."
- "Create visual art that..."
- "Make a static design for..."

**Location:** `.claude/skills/canvas-design/`

---

### frontend-design
**Description:** Create distinctive, production-grade frontend interfaces with high design quality. Use when building web components, pages, dashboards, React components, HTML/CSS layouts, or styling web UI.

**How to invoke:**
- "Build a landing page for..."
- "Create a React dashboard with..."
- "Design a web component that..."

**Location:** `.claude/skills/frontend-design/`

---

### slack-gif-creator
**Description:** Knowledge and utilities for creating animated GIFs optimized for Slack. Provides constraints, validation tools, and animation concepts.

**How to invoke:**
- "Make me a GIF for Slack of..."
- "Create an animated Slack GIF showing..."

**Location:** `.claude/skills/slack-gif-creator/`

---

### theme-factory
**Description:** Toolkit for styling artifacts with themes. Apply 10 pre-set themes with colors/fonts to slides, docs, reports, HTML landing pages, or generate new themes on-the-fly.

**How to invoke:**
- "Apply a theme to this presentation"
- "Style this document with..."
- "Generate a new theme for..."

**Location:** `.claude/skills/theme-factory/`

---

## Document & Content Creation

### doc-coauthoring
**Description:** Guide users through a structured workflow for co-authoring documentation, proposals, technical specs, decision docs, or similar structured content.

**How to invoke:**
- "Help me write documentation for..."
- "Let's co-author a proposal for..."
- "Draft a technical spec for..."

**Location:** `.claude/skills/doc-coauthoring/`

---

### docx
**Description:** Comprehensive Word document creation, editing, and analysis with support for tracked changes, comments, and formatting preservation.

**How to invoke:**
- "Create a Word document with..."
- "Edit this .docx file to..."
- "Add tracked changes to..."

**Location:** `.claude/skills/docx/`

---

### pdf
**Description:** Comprehensive PDF manipulation toolkit for extracting text/tables, creating PDFs, merging/splitting documents, and handling forms.

**How to invoke:**
- "Extract text from this PDF"
- "Fill in this PDF form"
- "Merge these PDF documents"

**Location:** `.claude/skills/pdf/`

---

### pptx
**Description:** PowerPoint presentation creation, editing, and analysis. Create new presentations, modify content, work with layouts, and add speaker notes.

**How to invoke:**
- "Create a presentation about..."
- "Edit this PowerPoint to..."
- "Add slides for..."

**Location:** `.claude/skills/pptx/`

---

### xlsx
**Description:** Comprehensive Excel spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis, and visualization.

**How to invoke:**
- "Create a spreadsheet with..."
- "Analyze this Excel data"
- "Add formulas to calculate..."

**Location:** `.claude/skills/xlsx/`

---

### internal-comms
**Description:** Resources for writing internal communications using company formats. Use for status reports, leadership updates, newsletters, FAQs, incident reports, project updates, etc.

**How to invoke:**
- "Write a status report for..."
- "Create a project update about..."
- "Draft an incident report for..."

**Location:** `.claude/skills/internal-comms/`

---

## Web & Application Development

### mcp-builder
**Description:** Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools.

**How to invoke:**
- "Help me build an MCP server for..."
- "Create an MCP integration with..."
- `/mcp-builder`

**Location:** `.claude/skills/mcp-builder/`

---

### webapp-testing
**Description:** Toolkit for interacting with and testing local web applications using Playwright. Verify frontend functionality, debug UI behavior, capture screenshots, and view browser logs.

**How to invoke:**
- "Test this web app for..."
- "Debug this UI behavior"
- "Capture a screenshot of..."

**Location:** `.claude/skills/webapp-testing/`

---

### web-artifacts-builder
**Description:** Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using React, Tailwind CSS, and shadcn/ui. Use for complex artifacts requiring state management or routing.

**How to invoke:**
- "Build a complex React artifact with..."
- "Create a multi-component web app using shadcn/ui"

**Location:** `.claude/skills/web-artifacts-builder/`

---

## Meta Skills

### skill-creator
**Description:** Guide for creating effective skills. Use when you want to create a new skill or update an existing skill that extends Claude's capabilities.

**How to invoke:**
- "Help me create a new skill for..."
- "I want to write a skill that..."
- `/skill-creator`

**Location:** `.claude/skills/skill-creator/`

---

### using-skills
**Description:** Getting Started with Skills - Skills wiki intro with mandatory workflows, search tool, and brainstorming triggers.

**How to invoke:**
- "How do I use skills?"
- "Show me available skills"
- `/using-skills`

**Location:** `.claude/skills/using-skills/`

---

### sharing-skills
**Description:** Contribute skills back to upstream via branch and PR.

**How to invoke:**
- "Help me share this skill upstream"
- "Create a PR for this skill"

**Location:** `.claude/skills/meta/sharing-skills/`

---

### pulling-updates-from-skills-repository
**Description:** Sync local skills repository with upstream changes from obra/superpowers-skills.

**How to invoke:**
- "Update my skills from upstream"
- "Pull latest skills updates"

**Location:** `.claude/skills/meta/pulling-updates-from-skills-repository/`

---

### gardening-skills-wiki
**Description:** Maintain skills wiki health - check links, naming, cross-references, and coverage.

**How to invoke:**
- "Check the skills wiki health"
- "Validate skills documentation"

**Location:** `.claude/skills/meta/gardening-skills-wiki/`

---

### testing-skills-with-subagents
**Description:** RED-GREEN-REFACTOR for process documentation - baseline without skill, write addressing failures, iterate closing loopholes.

**How to invoke:**
- "Test this skill with subagents"
- "Validate this skill works correctly"

**Location:** `.claude/skills/meta/testing-skills-with-subagents/`

---

### writing-skills
**Description:** TDD for process documentation - test with subagents before writing, iterate until bulletproof.

**How to invoke:**
- "Help me write a new skill"
- "Create a skill for..."

**Location:** `.claude/skills/meta/writing-skills/` and `.claude/skills/writing-skills/`

---

## Collaboration Skills

### brainstorming
**Description:** **MANDATORY before any creative work** - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation.

**How to invoke:**
- Automatically triggered before creative work
- "Let's brainstorm this feature"
- `/brainstorming`

**Location:** `.claude/skills/brainstorming/` and `.claude/skills/collaboration/brainstorming/`

---

### dispatching-parallel-agents
**Description:** Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies.

**How to invoke:**
- "Run these tasks in parallel"
- "Dispatch agents for these independent tasks"
- `/dispatching-parallel-agents`

**Location:** `.claude/skills/dispatching-parallel-agents/` and `.claude/skills/collaboration/dispatching-parallel-agents/`

---

### executing-plans
**Description:** Use when you have a written implementation plan to execute in a separate session with review checkpoints.

**How to invoke:**
- "Execute this implementation plan"
- "Follow this plan with review checkpoints"
- `/executing-plans`

**Location:** `.claude/skills/executing-plans/` and `.claude/skills/collaboration/executing-plans/`

---

### finishing-a-development-branch
**Description:** Use when implementation is complete and all tests pass. Guides completion by presenting structured options for merge, PR, or cleanup.

**How to invoke:**
- "I'm done with this feature, what's next?"
- "How should I integrate this work?"
- `/finishing-a-development-branch`

**Location:** `.claude/skills/finishing-a-development-branch/` and `.claude/skills/collaboration/finishing-a-development-branch/`

---

### receiving-code-review
**Description:** Use when receiving code review feedback, before implementing suggestions. Requires technical rigor and verification, not performative agreement or blind implementation.

**How to invoke:**
- "I received code review feedback"
- "Help me process this review"
- `/receiving-code-review`

**Location:** `.claude/skills/receiving-code-review/` and `.claude/skills/collaboration/receiving-code-review/`

---

### requesting-code-review
**Description:** Use when completing tasks, implementing major features, or before merging to verify work meets requirements.

**How to invoke:**
- "Review my code"
- "Check if this meets requirements"
- `/requesting-code-review`

**Location:** `.claude/skills/requesting-code-review/` and `.claude/skills/collaboration/requesting-code-review/`

---

### subagent-driven-development
**Description:** Use when executing implementation plans with independent tasks in the current session.

**How to invoke:**
- "Execute this plan with subagents"
- "Use subagent-driven development"
- `/subagent-driven-development`

**Location:** `.claude/skills/subagent-driven-development/` and `.claude/skills/collaboration/subagent-driven-development/`

---

### using-git-worktrees
**Description:** Use when starting feature work that needs isolation from current workspace. Creates isolated git worktrees with smart directory selection and safety verification.

**How to invoke:**
- "Create a worktree for this feature"
- "Set up isolated workspace"
- `/using-git-worktrees`

**Location:** `.claude/skills/using-git-worktrees/` and `.claude/skills/collaboration/using-git-worktrees/`

---

### using-superpowers
**Description:** Use when starting any conversation - establishes how to find and use skills, requiring Skill tool invocation before ANY response including clarifying questions.

**How to invoke:**
- Automatically triggered at conversation start
- "Show me superpowers"
- `/using-superpowers`

**Location:** `.claude/skills/using-superpowers/`

---

### remembering-conversations
**Description:** Search previous Claude Code conversations for facts, patterns, decisions, and context using semantic or text search.

**How to invoke:**
- "Search my previous conversations for..."
- "What did we decide about...?"
- "Find when we discussed..."

**Location:** `.claude/skills/collaboration/remembering-conversations/`

---

### writing-plans
**Description:** Use when you have a spec or requirements for a multi-step task, before touching code. Creates detailed implementation plans with bite-sized tasks.

**How to invoke:**
- "Help me write a plan for..."
- "Create an implementation plan"
- `/writing-plans`

**Location:** `.claude/skills/writing-plans/` and `.claude/skills/collaboration/writing-plans/`

---

## Debugging Skills

### systematic-debugging
**Description:** **Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes.** Four-phase debugging framework that ensures root cause investigation before attempting fixes.

**How to invoke:**
- Automatically triggered when bugs are detected
- "Debug this issue systematically"
- `/systematic-debugging`

**Location:** `.claude/skills/systematic-debugging/` and `.claude/skills/debugging/systematic-debugging/`

---

### verification-before-completion
**Description:** **Use when about to claim work is complete, fixed, or passing.** Requires running verification commands and confirming output before making success claims.

**How to invoke:**
- Automatically triggered before completion claims
- "Verify this is complete"
- `/verification-before-completion`

**Location:** `.claude/skills/verification-before-completion/` and `.claude/skills/debugging/verification-before-completion/`

---

### defense-in-depth
**Description:** Validate at every layer data passes through to make bugs impossible.

**How to invoke:**
- "Add defense-in-depth validation"
- "Validate at every layer"

**Location:** `.claude/skills/debugging/defense-in-depth/`

---

### root-cause-tracing
**Description:** Systematically trace bugs backward through call stack to find original trigger.

**How to invoke:**
- "Trace the root cause of this bug"
- "Find where this error originates"

**Location:** `.claude/skills/debugging/root-cause-tracing/`

---

## Testing Skills

### test-driven-development
**Description:** **Use when implementing any feature or bugfix, before writing implementation code.** Write the test first, watch it fail, write minimal code to pass.

**How to invoke:**
- Automatically triggered for feature/bugfix work
- "Use TDD for this feature"
- `/test-driven-development`

**Location:** `.claude/skills/test-driven-development/` and `.claude/skills/testing/test-driven-development/`

---

### condition-based-waiting
**Description:** Replace arbitrary timeouts with condition polling for reliable async tests.

**How to invoke:**
- "Use condition-based waiting in tests"
- "Replace timeouts with polling"

**Location:** `.claude/skills/testing/condition-based-waiting/`

---

### testing-anti-patterns
**Description:** Never test mock behavior. Never add test-only methods to production classes. Understand dependencies before mocking.

**How to invoke:**
- "Review my tests for anti-patterns"
- "Check if I'm testing mocks"

**Location:** `.claude/skills/testing/testing-anti-patterns/`

---

## Problem-Solving Skills

### when-stuck
**Description:** Dispatch to the right problem-solving technique based on how you're stuck.

**How to invoke:**
- "I'm stuck on this problem"
- "Help me figure out what to do next"
- `/when-stuck`

**Location:** `.claude/skills/problem-solving/when-stuck/`

---

### simplification-cascades
**Description:** Find one insight that eliminates multiple components - "if this is true, we don't need X, Y, or Z"

**How to invoke:**
- "Help me simplify this design"
- "What can we eliminate here?"
- `/simplification-cascades`

**Location:** `.claude/skills/problem-solving/simplification-cascades/`

---

### collision-zone-thinking
**Description:** Force unrelated concepts together to discover emergent properties - "What if we treated X like Y?"

**How to invoke:**
- "Help me think creatively about this"
- "Combine these unrelated concepts"
- `/collision-zone-thinking`

**Location:** `.claude/skills/problem-solving/collision-zone-thinking/`

---

### scale-game
**Description:** Test at extremes (1000x bigger/smaller, instant/year-long) to expose fundamental truths hidden at normal scales.

**How to invoke:**
- "Test this at extreme scales"
- "What if this was 1000x bigger?"
- `/scale-game`

**Location:** `.claude/skills/problem-solving/scale-game/`

---

### meta-pattern-recognition
**Description:** Spot patterns appearing in 3+ domains to find universal principles.

**How to invoke:**
- "Find patterns across domains"
- "What universal principles apply here?"
- `/meta-pattern-recognition`

**Location:** `.claude/skills/problem-solving/meta-pattern-recognition/`

---

### inversion-exercise
**Description:** Flip core assumptions to reveal hidden constraints and alternative approaches - "what if the opposite were true?"

**How to invoke:**
- "What if we inverted this assumption?"
- "Challenge the core premise"
- `/inversion-exercise`

**Location:** `.claude/skills/problem-solving/inversion-exercise/`

---

## Research Skills

### tracing-knowledge-lineages
**Description:** Understand how ideas evolved over time to find old solutions for new problems and avoid repeating past failures.

**How to invoke:**
- "Trace the history of this idea"
- "How did this concept evolve?"
- `/tracing-knowledge-lineages`

**Location:** `.claude/skills/research/tracing-knowledge-lineages/`

---

## Architecture Skills

### preserving-productive-tensions
**Description:** Recognize when disagreements reveal valuable context. Preserve multiple valid approaches instead of forcing premature resolution.

**How to invoke:**
- "Preserve these different approaches"
- "Don't force a resolution yet"
- `/preserving-productive-tensions`

**Location:** `.claude/skills/architecture/preserving-productive-tensions/`

---

## Quick Reference

### Most Commonly Used Skills

1. **test-driven-development** - Use for ANY feature or bugfix
2. **systematic-debugging** - Use for ANY bug or unexpected behavior
3. **brainstorming** - MANDATORY before creative work
4. **verification-before-completion** - Required before claiming completion
5. **writing-plans** - Use before multi-step implementation
6. **requesting-code-review** - Use before merging or completion

### Skills by Use Case

**When starting new work:**
- brainstorming
- writing-plans
- using-git-worktrees

**When implementing:**
- test-driven-development
- subagent-driven-development
- executing-plans

**When debugging:**
- systematic-debugging
- root-cause-tracing
- defense-in-depth

**When finishing:**
- verification-before-completion
- requesting-code-review
- finishing-a-development-branch

**When stuck:**
- when-stuck
- collision-zone-thinking
- inversion-exercise
- simplification-cascades

---

## Notes

- Many skills have duplicates in both root level and organized subdirectories for easier access
- Skills marked as **MANDATORY** or **AUTOMATIC** will be triggered by Claude Code based on context
- You can explicitly invoke any skill using `/skill-name` format
- Skills can be combined - for example, using TDD while executing a plan with systematic debugging

---

*Last updated: 2026-01-11*
*Total Skills: 52*
