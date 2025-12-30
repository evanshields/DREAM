# Vision-based UI Reviewer - Quick Reference Card

---

## 🚀 Quick Start

```
"Conduct a Vision-based UI review of Dream"
```

---

## 🎯 What It Does

✅ Navigates to your running app in browser  
✅ Captures screenshots & accessibility snapshots  
✅ Analyzes against `design-language-dream.md`  
✅ Identifies spacing, color, typography, component issues  
✅ Assesses CRE usability (numeric legibility, table scannability)  
✅ Creates detailed review report with code fixes  
✅ Implements fixes when you approve  

---

## 🔍 Activation Phrases

| Say This | Agent Does |
|----------|------------|
| "Conduct a Vision-based UI review" | Full review of all key pages |
| "Review the dashboard page only" | Single page review |
| "Inspect UI in browser" | Visual inspection |
| "Review dark mode" | Dark mode compliance check |
| "Check design compliance" | Design language audit |

---

## 📋 What It Audits

### ✅ Design Language Compliance
- **Colors**: All from design palette, no hardcoded values
- **Typography**: Correct fonts, sizes, **tabular-nums** on numbers
- **Spacing**: Standard tokens (p-4, p-6, gap-4, mb-8)
- **Components**: Buttons, cards, inputs, tables, badges

### ✅ CRE Usability
- **Numeric Legibility**: tabular-nums, serif fonts, alignment
- **Table Scannability**: Hover states, row striping, sticky headers
- **Metric Hierarchy**: Visual prominence of key metrics
- **Action Clarity**: Primary/secondary button differentiation

---

## 📊 Output: Review Report

**Location**: `docs/ui-review-[date].md`

**Contains**:
- ✅ Executive summary with compliance score
- ✅ Issue-by-issue breakdown (Critical → High → Medium → Low)
- ✅ File paths & line numbers for each issue
- ✅ Proposed code fixes (copy-paste ready)
- ✅ CRE usability analysis with scores
- ✅ Screenshots with annotations
- ✅ Prioritized recommendations

---

## 🔧 Common Issues & Fixes

### ❌ Missing `tabular-nums` (CRITICAL - Most Common)
```typescript
- <div className="text-3xl font-heading">18.5%</div>
+ <div className="text-3xl font-heading tabular-nums">18.5%</div>
```

### ❌ Inconsistent Card Padding (HIGH)
```typescript
- <div className="p-3">
+ <div className="p-6">
```

### ❌ Missing Table Hover States (MEDIUM)
```typescript
- <tr className="border-b border-border">
+ <tr className="border-b border-border hover:bg-background-tertiary transition-colors">
```

### ❌ Hardcoded Colors (HIGH)
```typescript
- <span className="text-[#10B981]">
+ <span className="text-brand-success">
```

---

## 📈 Severity Levels

| Level | Priority | Fix Timing |
|-------|----------|------------|
| **Critical** 🔴 | P0 | Before next deployment |
| **High** 🟠 | P1 | End of week |
| **Medium** 🟡 | P2 | Current sprint |
| **Low** 🟢 | P3 | When convenient |

---

## 🔄 Typical Workflow

```
1. You: "Run Vision-based UI review of dashboard"

2. Agent:
   - Navigates to http://localhost:3000
   - Captures screenshots
   - Analyzes design compliance
   - Creates docs/ui-review-2025-12-20.md
   - Reports: "Found 12 issues (2 critical, 4 high)"

3. You: "Implement critical and high fixes"

4. Agent:
   - Applies tabular-nums
   - Fixes padding
   - Replaces hardcoded colors
   - Re-inspects visually
   - Updates report: "Resolved, compliance now 92%"
```

---

## 📚 Documentation

| Document | What It Contains |
|----------|------------------|
| `docs/UI_VISION_REVIEWER_GUIDE.md` | Complete guide (process, checklists, FAQ) |
| `docs/ui-review-example.md` | Example review report with all sections |
| `docs/VISION_REVIEWER_SETUP.md` | Setup summary & best practices |
| `design-language-dream.md` | Design standards reference |

---

## 🎓 Best Practices

1. **Review early and often**: After features, before releases
2. **Fix critical issues first**: Illegible data > visual polish
3. **Track compliance over time**: Compare reports, monitor scores
4. **Re-inspect after fixes**: Verify improvements, catch regressions
5. **Integrate into PR process**: Add design review checklist

---

## 🔑 Key Inspection Points Checklist

**Before releasing, verify:**

- [ ] All numeric displays have `tabular-nums`
- [ ] All colors from design-language-dream.md
- [ ] Card padding uses p-4 or p-6
- [ ] Tables have hover states
- [ ] Buttons follow component tokens
- [ ] Key metrics visually prominent
- [ ] Focus states visible
- [ ] Spacing uses design tokens (no magic numbers)

---

## 🤝 Integration with Other Agents

| Agent | Focus | Use After |
|-------|-------|-----------|
| **UX Engineer** | HTML structure | To create prototypes |
| **UI Engineer** | Styling | To apply design language |
| **Framework Converter** | Next.js conversion | To build production app |
| **👁️ Vision Reviewer** | Visual inspection | To verify implementation |
| **Design System Enforcer** | Code refactoring | To fix token violations |

---

## ⏱️ Time Estimates

| Task | Estimated Time |
|------|----------------|
| Full review (3-5 pages) | 10-20 minutes |
| Single page review | 3-5 minutes |
| Implementing critical fixes | 15-30 minutes |
| Implementing all fixes | 1-2 hours |
| Re-inspection | 5-10 minutes |

---

## 🎯 Compliance Score Targets

| Score | Status | Action |
|-------|--------|--------|
| 90%+ | ✅ Excellent | Maintain quality |
| 75-89% | 🟡 Good | Address medium issues |
| 60-74% | 🟠 Needs Work | Fix high-priority issues |
| <60% | 🔴 Critical | Immediate attention required |

---

## 💡 Pro Tips

1. **Start small**: Review one page first to get familiar
2. **Fix in batches**: Group similar issues (all tabular-nums together)
3. **Use code search**: Find all instances of an issue before fixing
4. **Document decisions**: If you deviate from recommendations, note why
5. **Celebrate progress**: Track compliance improvements over time

---

## 🆘 Troubleshooting

**App not running?**
→ Start dev server: `npm run dev`

**Wrong URL?**
→ Specify: "Review Dream at http://localhost:5173"

**Too many issues?**
→ Say: "Focus on critical and high-severity issues only"

**Want specific focus?**
→ Say: "Review tables only" or "Check typography compliance"

**Need to skip a page?**
→ Say: "Review dashboard and underwriting, skip deal list"

---

## 📞 Quick Commands

| Command | Result |
|---------|--------|
| `"Full UI review"` | All pages, complete audit |
| `"Review dashboard only"` | Single page |
| `"Check typography"` | Typography compliance only |
| `"Inspect tables"` | Table usability focus |
| `"Review dark mode"` | Dark mode compliance |
| `"Verify fixes"` | Re-inspect after changes |
| `"Compliance score"` | Quick scoring without full report |

---

## 🎉 Ready to Use!

**Try it now:**
```
"Conduct a Vision-based UI review of Dream"
```

---

**For detailed documentation, see**: `docs/UI_VISION_REVIEWER_GUIDE.md`

