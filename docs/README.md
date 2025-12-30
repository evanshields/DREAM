# DREAM AI Documentation

> Comprehensive documentation for analysts, investors, and engineers

---

## Quick Links

| Document | Purpose | Audience |
|----------|---------|----------|
| **[Root README](../README.md)** | Product overview, architecture, quick start | All |
| **[User Flows](flows.md)** | Detailed walkthroughs of core user journeys | Product, UX, Analysts |
| **[CRE Underwriting Concepts](cre-underwriting-concepts.md)** | Metrics explained for analysts | Analysts, Investors, Principals |
| **[Demo Script](demo-script.md)** | Live demo walkthrough with sample deal | Sales, Product |
| **[Shieldstone Integration Guide](SHIELDSTONE_INTEGRATION_GUIDE.md)** | Technical methodology implementation | Engineers |
| **[Shieldstone Manual Index](SHIELDSTONE_MANUAL_INDEX.md)** | Complete manual section reference | Engineers, Analysts |
| **[Shieldstone Standards Reference](SHIELDSTONE_STANDARDS_REFERENCE.md)** | Coding standards for methodology | Engineers |

---

## Documentation Overview

### For Analysts & Investors

**Start Here:**
1. **[Root README](../README.md)** - Understand what DREAM AI does and why it exists
2. **[CRE Underwriting Concepts](cre-underwriting-concepts.md)** - Learn the metrics and methodology
3. **[User Flows](flows.md)** - See how to use DREAM AI step-by-step

**When You Need:**
- **To understand a specific metric:** See [CRE Underwriting Concepts](cre-underwriting-concepts.md)
- **To learn a workflow:** See [User Flows](flows.md)
- **To prepare a demo:** See [Demo Script](demo-script.md)

### For Engineers

**Start Here:**
1. **[Root README](../README.md)** - Understand the architecture and tech stack
2. **[Shieldstone Integration Guide](SHIELDSTONE_INTEGRATION_GUIDE.md)** - Learn the methodology implementation
3. **[Shieldstone Manual Index](SHIELDSTONE_MANUAL_INDEX.md)** - Navigate the 7,800+ line manual

**When You Need:**
- **To implement a calculation:** See [Shieldstone Integration Guide](SHIELDSTONE_INTEGRATION_GUIDE.md)
- **To understand methodology:** See [Shieldstone Manual Index](SHIELDSTONE_MANUAL_INDEX.md)
- **To follow coding standards:** See [Shieldstone Standards Reference](SHIELDSTONE_STANDARDS_REFERENCE.md)

### For Product & Sales

**Start Here:**
1. **[Root README](../README.md)** - Product positioning and competitive advantages
2. **[Demo Script](demo-script.md)** - Prepare for live demonstrations
3. **[User Flows](flows.md)** - Understand detailed user journeys

**When You Need:**
- **To demo to investors:** See [Demo Script](demo-script.md)
- **To explain a feature:** See [User Flows](flows.md)
- **To position vs. competitors:** See [Root README](../README.md)

---

## Document Summaries

### [User Flows](flows.md)

Comprehensive documentation of 8 core user journeys:

1. **New User Onboarding** - Signup to first analysis in <10 minutes
2. **Quick Deal Screening (BOE)** - 2-minute pass/fail decision
3. **Full Deal Underwriting** - Complete IC-ready analysis in 7 minutes
4. **Investment Committee Presentation** - Present with live pro forma
5. **Pipeline Management** - Track deals across stages
6. **Pro Forma Sensitivity Analysis** - Test downside scenarios
7. **Team Collaboration** - Real-time multi-user workflows
8. **Custom Investment Criteria** - Configure screening preferences

**Best For:** Product managers, UX designers, analysts learning the platform

### [CRE Underwriting Concepts](cre-underwriting-concepts.md)

A practical guide to multifamily investment metrics:

- **Property Fundamentals:** Classification, unit mix, occupancy
- **Financial Metrics:** Revenue, expenses, NOI
- **Return Calculations:** IRR, equity multiple, cap rates, CoC, DSCR
- **Risk Assessment:** Risk-adjusted hurdles, red flags, sensitivity
- **Market Analysis:** Market tiers, key metrics, regulatory environment
- **Valuation Methods:** Income approach, comps, cost approach
- **Financing Structures:** Agency, bridge, refinancing (90/90 rule)
- **Value-Add Strategies:** Revenue enhancement, expense reduction
- **Exit Strategies:** Exit cap triangulation (3-method)
- **Due Diligence:** Financial, physical, environmental, legal
- **Common Pitfalls:** 10+ mistakes and how to avoid them

**Best For:** Analysts, investors, principals wanting to understand metrics and methodology

### [Demo Script](demo-script.md)

A guided 15-minute walkthrough for demonstrating DREAM AI:

- **Pre-Demo Setup:** Environment preparation checklist
- **Demo Flow:** Step-by-step script with timings
  - Introduction & value prop (2 min)
  - Document upload & extraction (2 min)
  - BOE analysis review (3 min)
  - Full underwriting & pro forma (4 min)
  - Investment committee memo (2 min)
  - Additional features & wrap-up (2 min)
- **Q&A:** Common questions and answers
- **Audience Variations:** Technical, financial, operations
- **Post-Demo Follow-Up:** Email templates and timing

**Best For:** Sales teams, product demos, investor presentations

### [Shieldstone Integration Guide](SHIELDSTONE_INTEGRATION_GUIDE.md)

Technical documentation for implementing the Shieldstone methodology:

- Methodology overview
- Python library structure
- Key calculations and formulas
- Integration patterns
- Testing requirements
- Code examples

**Best For:** Engineers implementing calculations

### [Shieldstone Manual Index](SHIELDSTONE_MANUAL_INDEX.md)

Complete index of the 7,800+ line Shieldstone Technical Manual V2.0:

- All 14 sections with subsections
- Line number references
- Key concepts and formulas
- Cross-references between sections

**Best For:** Engineers navigating the manual

### [Shieldstone Standards Reference](SHIELDSTONE_STANDARDS_REFERENCE.md)

Coding standards for methodology implementation:

- Code style guidelines
- Documentation requirements
- Testing standards
- Version control practices

**Best For:** Engineers contributing to Shieldstone library

---

## Contributing to Documentation

### Documentation Standards

**All documentation should be:**
1. **Clear:** Written for the intended audience
2. **Accurate:** Reflects current product state
3. **Complete:** Covers edge cases and alternatives
4. **Up-to-Date:** Version and date tracked
5. **Searchable:** Good headings, table of contents

### Updating Docs

When you update DREAM AI features:

1. **Update relevant doc files:**
   - Product changes → Update `flows.md`
   - New metrics → Update `cre-underwriting-concepts.md`
   - Demo changes → Update `demo-script.md`
   - Architecture changes → Update root `README.md`

2. **Update version and date:**
   - Add entry to changelog at bottom of doc
   - Update "Last Updated" date at top

3. **Cross-reference:**
   - Link to related sections in other docs
   - Keep navigation consistent

4. **Test:**
   - Follow your own instructions
   - Verify all links work
   - Ensure code examples run

### Doc Review Checklist

Before committing doc changes:

- [ ] Spelling and grammar checked
- [ ] All links tested
- [ ] Code examples verified
- [ ] Screenshots current (if any)
- [ ] Version and date updated
- [ ] Table of contents updated
- [ ] Cross-references accurate

---

## API Documentation

### OpenAPI/Swagger

Interactive API documentation available at:
- **Development:** `http://localhost:8000/docs`
- **Production:** `https://api.dream.ai/docs`

### API Guides

Detailed guides for common API workflows:
- Authentication
- Deal creation and analysis
- Document upload and extraction
- Pro forma calculations
- Report generation
- Webhook integration

**Status:** Coming soon (Phase 8+)

---

## Video Tutorials

### Planned Video Content

1. **Getting Started** (5 min)
   - Account setup
   - First deal upload
   - Understanding results

2. **Pro Forma Deep Dive** (10 min)
   - Editing assumptions
   - Understanding AI rationale
   - Sensitivity analysis

3. **Investment Criteria** (8 min)
   - Configuring criteria
   - Understanding scoring
   - Testing against historical deals

4. **Pipeline Management** (7 min)
   - Kanban workflow
   - Task assignment
   - Team collaboration

5. **Excel Export & Mapping** (12 min)
   - Basic export
   - House model
   - Custom template mapping

**Status:** Coming in Q1 2026

---

## Support Resources

### Getting Help

**Documentation Issues:**
- Open GitHub issue with `documentation` label
- Email: docs@dream.ai

**Product Questions:**
- Check [CRE Underwriting Concepts](cre-underwriting-concepts.md) first
- Slack community: [Join here](https://dream-ai-community.slack.com)
- Email: support@dream.ai

**Technical Support:**
- API docs: `https://api.dream.ai/docs`
- GitHub issues: Technical bugs and feature requests
- Email: engineering@dream.ai

### Office Hours

**For Customers:**
- Weekly Q&A: Wednesdays 2-3pm ET
- Monthly product updates: First Thursday of month
- Join Slack for announcements

---

## Feedback

We continuously improve our documentation based on user feedback.

**What's working well?**
**What's confusing?**
**What's missing?**

Please let us know:
- Email: docs@dream.ai
- Slack: #documentation channel
- GitHub: Open issue with `documentation` label

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 20, 2025 | Initial documentation suite |
| | | - Root README.md |
| | | - docs/flows.md |
| | | - docs/cre-underwriting-concepts.md |
| | | - docs/demo-script.md |
| | | - docs/README.md (this file) |

---

**Maintained By:** DREAM AI Documentation Team  
**Last Updated:** December 20, 2025

For questions or suggestions: docs@dream.ai
