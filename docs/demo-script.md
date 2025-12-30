# DREAM AI Live Demo Script

> A guided walkthrough for demonstrating DREAM AI to analysts, investors, and principals

**Duration:** 15 minutes  
**Demo Deal:** Oakwood Apartments, Nashville, TN  
**Last Updated:** December 20, 2025

---

## Pre-Demo Setup (5 minutes before)

### 1. Prepare Demo Environment

- [ ] Open DREAM AI in Chrome (clean browser profile, no distractions)
- [ ] Load sample deal: Oakwood Apartments (Nashville)
- [ ] Have documents ready in folder:
  - `Oakwood_OM.pdf`
  - `T12_Operating_Statement.xlsx`
  - `Rent_Roll_Current.xlsx`
  - `Property_Photos/` folder
- [ ] Test internet connection and screen sharing
- [ ] Close unnecessary tabs and applications
- [ ] Set browser zoom to 100% or 110% (readable on shared screen)
- [ ] Mute notifications

### 2. Know Your Audience

**For Investment Firms / Principals:**
- Emphasize time savings (4-8 hours → 7 minutes)
- Focus on institutional methodology (Shieldstone)
- Highlight defensible outputs for IC presentations

**For Emerging Sponsors:**
- Emphasize cost savings vs. Argus ($15K-50K/year)
- Show how to scale without hiring more analysts
- Demo Excel export for existing workflows

**For Family Offices:**
- Focus on transparency and auditability
- Emphasize conservative assumptions
- Show sensitivity analysis for risk management

**For Brokers:**
- Speed (respond to deals in 2 minutes)
- Consistent screening criteria
- Professional BOE memos to send buyers

---

## Demo Script

### [0:00-2:00] Introduction & Value Proposition (2 minutes)

**Script:**

> "Thanks for joining today. I'm going to show you DREAM AI—an AI-powered acquisitions intelligence platform that reduces deal analysis from 4-8 hours to under 7 minutes while maintaining institutional-quality output.
> 
> DREAM AI is built on the Shieldstone Technical Underwriting Manual—a comprehensive institutional methodology for multifamily underwriting. This ensures every analysis is:
> - **Transparent**: Every assumption documented with rationale
> - **Defensible**: All inputs supported by market data
> - **Conservative**: Assumptions err on the side of caution
>
> Today, I'll walk through a real deal—Oakwood Apartments in Nashville—from document upload to final investment committee memo. Let's dive in."

**[Screen: Dashboard]**

Point out key elements:
- Pipeline overview (deals by stage)
- Recent activity
- Quick action: "New Deal" button

---

### [2:00-4:00] Document Upload & Extraction (2 minutes)

**Script:**

> "Let's start by uploading a new deal. I've received an OM from a broker on Oakwood Apartments, a 168-unit Class B property in Nashville."

**Action: Click "New Deal"**

```
┌─────────────────────────────────────────────────────────────────┐
│  New Deal                                                        │
│                                                                  │
│  Deal Name: [Oakwood Apartments]                                │
└─────────────────────────────────────────────────────────────────┘
```

**Script:**

> "I'll give it a name and upload the documents we received. DREAM AI can process PDFs, Excel files, and images."

**Action: Drag and drop three files:**
- `Oakwood_OM.pdf`
- `T12_Operating_Statement.xlsx`
- `Rent_Roll_Current.xlsx`

**Script:**

> "For a quick first look, I'll run a Back of Envelope analysis. This takes about 90 seconds and costs less than 15 cents in AI API fees."

**Action: Select "BOE Analysis" and click "Analyze Deal"**

**[Processing Screen - 90 seconds]**

**Script while processing:**

> "Behind the scenes, DREAM AI is:
> 1. Extracting property details—address, unit count, vintage, financials
> 2. Pulling market research—MSA classification, submarket data, employment trends
> 3. Running screening—checking against our investment criteria with risk-adjusted hurdles
> 4. Building a basic pro forma—10-year DCF with AI-suggested assumptions
> 5. Generating a 1-2 page Back of Envelope memo
>
> All financial calculations are done in Python—not by the AI—which means they're deterministic, instant, and zero-hallucination risk. The AI's job is to extract data and generate narratives, not do math."

**[BOE Results appear]**

---

### [4:00-7:00] BOE Analysis Review (3 minutes)

**[Screen: BOE Results]**

**Script:**

> "Alright, analysis is complete. Let me walk through what DREAM AI found."

**Section 1: Investment Score & Recommendation**

```
┌──────────────────────────────────────────────────────────┐
│  RECOMMENDATION: PROCEED                                  │
│  Score: 78/100 (BUY)                                      │
│  Confidence: High                                          │
└──────────────────────────────────────────────────────────┘
```

**Script:**

> "DREAM AI scored this deal 78 out of 100, which falls into our 'BUY' range. The recommendation is PROCEED. Let's see why."

**Section 2: Key Metrics**

```
QUICK METRICS
├─ Purchase Price:   $29.4M ($175K/unit)
├─ Going-In Cap:     5.8%
├─ Stabilized Cap:   6.2%
├─ IRR:              19.2% ✓ (exceeds 18.0% target)
├─ Equity Multiple:  1.89x ✓ (exceeds 1.80x target)
└─ CoC (Stab):       8.4%
```

**Script:**

> "The returns look strong—19.2% IRR and 1.89x equity multiple over a 5-year hold. Both exceed our target hurdles of 18% and 1.80x. Price per unit is $175K, which is in line with Nashville Class B comps."

**Section 3: Investment Thesis**

**Script:**

> "Here's the AI-generated executive summary:"

**[Read aloud, highlighting key points]:**

> "Oakwood presents a strong value-add opportunity in a growing Nashville submarket. Recent exterior renovations are complete, and below-market rents offer $175/unit upside through light interior renovations. Returns exceed target hurdles with moderate execution risk."

**Section 4: Strengths & Concerns**

**Script:**

> "DREAM AI identified 5 strengths and 3 concerns. Let me highlight the top ones:
>
> **Strengths:**
> 1. Below-market rents: $175/unit upside (this is huge—every $100/unit is ~$300K in annual NOI)
> 2. Strong market: Nashville has 3.2% job growth, well above national average
> 3. Recent $8M exterior renovation complete—we don't have to do that
>
> **Concerns:**
> 1. Property age: 39 years old, so we need to budget ongoing CapEx carefully
> 2. Supply risk: 2,500 units under construction—but DREAM AI notes these are mostly Class A, different renter profile
> 3. Property tax reassessment likely after purchase—DREAM AI modeled this at 70% of sale price, which is conservative for Tennessee
>
> Every one of these concerns is manageable. None are deal-killers."

**Section 5: Next Steps**

**Script:**

> "DREAM AI even suggests next steps:
> - Request updated T-12 and rent roll
> - Tour property and competitive set
> - Validate renovation budget with contractor
> - Confirm property tax reassessment with county
>
> This is exactly what we'd do manually, but now it's laid out automatically."

**Action: Click "Download PDF"**

**Script:**

> "I can download this as a professional PDF memo to send to my team or respond to the broker. This whole process—upload to BOE memo—took 2 minutes."

---

### [7:00-11:00] Full Underwriting & Pro Forma (4 minutes)

**Script:**

> "The BOE analysis tells us this deal is worth pursuing. Now let's run a full underwriting for our investment committee presentation."

**Action: Click "Full Underwriting"**

**[Processing Screen - 5 minutes in background]**

**Script:**

> "Full underwriting takes about 5-7 minutes because DREAM AI is:
> - Extracting every unit from the rent roll (168 units)
> - Breaking down all 12 T-12 expense line items
> - Pulling deep market research with comps
> - Building a complete 10-year pro forma with monthly detail
> - Running sensitivity analysis
> - Generating an 8-10 page investment committee memo
>
> While that's processing, let me show you the pro forma editor."

**Action: Navigate to Pro Forma tab**

**[Screen: Pro Forma Assumptions]**

**Script:**

> "DREAM AI generates initial assumptions using AI, but you can edit anything. Let me show you the revenue section."

**Section 1: Revenue Assumptions**

```
Unit Mix                               In-Place  Market
├─ 1BR (48 units, 750 SF)             $1,150    $1,325
├─ 2BR (96 units, 1,100 SF)           $1,475    $1,650
└─ 3BR (24 units, 1,350 SF)           $1,850    $2,025

Pro Forma Rents (Post-Renovation)
├─ 1BR: [$1,325] (market rate)
├─ 2BR: [$1,650] (market rate)
└─ 3BR: [$2,025] (market rate)

💡 AI Rationale: Recent comps show $1,300-1,350 for renovated
   1BRs. We're using $1,325 as conservative midpoint.
```

**Script:**

> "Notice how DREAM AI explains *why* it chose these assumptions. It's not a black box—every number has a rationale tied to market data.
>
> If I want to change an assumption, I just click and edit. Watch this:"

**Action: Click on Rent Growth assumption, change from 3.0% to 2.5%**

**Script:**

> "I'm going to stress-test this. What if rent growth is only 2.5% instead of 3%?"

**Action: Press Enter**

**[Instant recalculation - <100ms]**

```
IRR:         19.2% → 18.1% (-1.1%)
EM:          1.89x → 1.81x (-0.08x)
LP IRR:      18.1% → 17.1% (-1.0%)

✓ Still exceeds minimum hurdles (14% IRR, 1.50x EM)
```

**Script:**

> "The recalculation happened instantly—under 100 milliseconds—because all the math is done in Python, not by the AI. This means:
> - No API cost for assumption changes
> - No waiting 5-10 seconds for AI to respond
> - Zero risk of hallucinated numbers
>
> Even with lower rent growth, we still exceed minimum hurdles. This deal has good downside protection."

**Action: Revert assumption back to 3.0%**

**Section 2: Property Tax Deep Dive**

**Action: Navigate to "Expenses" tab**

**Script:**

> "Let me show you something most analysts miss—property tax reassessment. This is one of DREAM AI's unique features."

```
🔍 Property Tax Detail
Current Assessed Value:      $18,500,000
Expected Reassessment:       $24,500,000 (70% of purchase)
Millage Rate:                1.02%
Projected Tax (Year 2):      $249,500

💡 Tennessee reassesses at ~65-70% of sale price. We're using
   70% (conservative). Consider filing appeal after purchase.
```

**Script:**

> "Most analysts use the current property tax number without modeling reassessment. That's a huge mistake.
>
> DREAM AI automatically models state-specific reassessment ratios. For Tennessee, properties typically reassess at 65-70% of sale price. We're using 70% to be conservative—that's an extra $100K per year in taxes.
>
> If we didn't model this, our returns would be off by 2-3 percentage points. This kind of rigor is what makes DREAM AI institutional-grade."

---

### [11:00-13:00] Investment Committee Memo (2 minutes)

**[Full UW processing completes]**

**Script:**

> "Alright, the full underwriting is complete. Let's generate the IC memo."

**Action: Click "Generate IC Memo"**

**[Processing - 90 seconds]**

**Script while processing:**

> "DREAM AI is now creating a 4-6 page Investment Committee memo with:
> - Executive summary and recommendation
> - Property overview with photos
> - Market analysis with key metrics
> - Financial summary with sources & uses
> - Risk factors and mitigations
> - Value creation thesis
>
> This is the exact structure institutional investors expect."

**[IC Memo PDF opens]**

**Script:**

> "Here's the memo. Let me walk through it quickly."

**Action: Scroll through PDF, highlighting sections:**

**Page 1: Executive Summary**
- Clear recommendation: BUY
- Key metrics summary
- Investment thesis in 2-3 sentences

**Page 2: Property Overview**
- Unit mix table
- Renovation scope
- Photos (exterior, interior, amenities)

**Page 3: Market Analysis**
- MSA overview (Nashville)
- Submarket fundamentals
- Employment drivers (top 5 employers)
- Supply pipeline analysis

**Page 4: Financial Summary**
- Sources & Uses table
- 5-year pro forma summary
- Returns waterfall (GP/LP splits)

**Page 5: Risk Factors & Mitigations**
- Property risks: Age, deferred maintenance
- Market risks: Supply, taxes
- Execution risks: Renovation timeline
- Mitigations for each

**Script:**

> "This memo is ready to present to our investment committee today. No additional formatting needed. We went from document upload to presentation-ready memo in under 10 minutes.
>
> Traditionally, this would take an analyst 4-8 hours to produce. With DREAM AI, it's 7 minutes and costs about $2 in AI API fees."

---

### [13:00-15:00] Additional Features & Wrap-Up (2 minutes)

**Script:**

> "Let me quickly show you a few more features before we wrap up."

**Feature 1: Sensitivity Analysis**

**Action: Navigate to "Sensitivity" tab**

```
IRR (%) by Exit Cap Rate and Rent Growth:

Exit Cap │  2.0%    2.5%    3.0%    3.5%
────────┼──────────────────────────────────
  5.75% │  21.0%   22.3%   23.5%   24.8%
  6.00% │  18.3%   19.5%   20.7%   21.9% ← Base
  6.25% │  15.8%   16.9%   18.0%   19.1%
  6.50% │  13.4%   14.4%   15.5%   16.5%

💡 Deal achieves 14% minimum hurdle in 88% of scenarios.
```

**Script:**

> "DREAM AI automatically generates sensitivity tables testing key variables—exit cap, rent growth, vacancy, renovation costs. This shows us the deal achieves our 14% minimum hurdle in 88% of tested scenarios. Strong downside protection."

**Feature 2: Excel Export**

**Action: Click "Export to Excel"**

**Script:**

> "Some teams still want to work in Excel. No problem—DREAM AI exports the complete pro forma with working formulas, not just values. All assumptions map to cells so you can tweak anything."

**Feature 3: Pipeline Management**

**Action: Navigate to Pipeline board**

**Script:**

> "DREAM AI also includes a deal pipeline CRM. You can track deals across stages, assign tasks to team members, collaborate on assumptions, and keep everything organized in one place."

**Feature 4: Team Collaboration**

**Script:**

> "For teams, DREAM AI supports real-time collaboration. Multiple analysts can work on the same deal, leave comments on assumptions, and track all changes. Everything is logged for auditability."

---

## Closing (1 minute)

**Script:**

> "To recap, DREAM AI gives you:
> 
> **Speed**
> - BOE analysis: 2 minutes
> - Full underwriting: 7 minutes
> - 90%+ time savings vs. manual process
>
> **Quality**
> - Institutional Shieldstone methodology
> - Transparent, defensible, conservative assumptions
> - All calculations deterministic (Python, not AI)
>
> **Cost**
> - $99-199/month (vs. $15K-50K/year for Argus)
> - <$2 AI cost per full underwriting
> - 10x cheaper than traditional tools
>
> The result: You can evaluate 5-10x more deals, respond to brokers faster, and make better investment decisions—all while maintaining institutional-quality output.
>
> Any questions?"

---

## Common Questions & Answers

### Q: "How accurate is the AI data extraction?"

**A:** DREAM AI achieves 85-95% accuracy on standard offering memorandums, depending on document quality. Every extracted field has a confidence score, and we flag uncertain values for your review. You can manually override any field. The key is: AI extracts, you verify, Python calculates.

### Q: "What if I don't agree with an assumption?"

**A:** Every assumption is editable. Click any number, change it, and the entire pro forma recalculates instantly (under 100ms). The AI suggests assumptions based on market data, but you have full control. Think of it as a very smart assistant that does the first draft, but you make the final decisions.

### Q: "Can I customize my investment criteria?"

**A:** Absolutely. DREAM AI lets you configure hard stops, target ranges, and soft preferences. You can set your own IRR hurdles, market preferences, property characteristics, and more. The screening engine then evaluates every deal against your specific criteria.

### Q: "How does DREAM AI handle different property types?"

**A:** The MVP focuses on conventional multifamily. Phase 11 will add SFR business purpose lending (fix & flip, DSCR rentals). Future phases will cover student housing, affordable/LIHTC, mobile home parks, senior housing, and other asset classes.

### Q: "What if I want to export to my existing Excel model?"

**A:** DREAM AI offers three tiers:
1. **Basic Export** (included): Complete pro forma with working formulas
2. **House Model** (premium): Our standardized institutional template
3. **Custom Template Mapping** (enterprise): We map assumptions to YOUR proprietary Excel model

### Q: "How much does it cost?"

**A:** Pricing is $99-199/month depending on team size and deal volume. This includes unlimited analyses. Compare that to Argus ($15K-50K/year) or the cost of an analyst spending 4-8 hours per deal. Most customers see ROI within the first month.

### Q: "Is my data secure?"

**A:** Yes. DREAM AI is SOC2 Type II compliant (planned), with end-to-end encryption, role-based access control, and audit logging. Your deal data is private and never shared. We do offer an opt-in program where anonymized data (stripped of property identifiers) contributes to aggregated market benchmarks that benefit all users.

### Q: "Can I try it before committing?"

**A:** Yes. We offer a 14-day free trial with full access to all features. You can analyze up to 10 deals during the trial period. No credit card required to start.

---

## Demo Variations by Audience

### For Technical/Engineering Audience

**Emphasize:**
- Python-first calculation architecture (no LLM hallucinations)
- Open-source Shieldstone library (testable, auditable)
- LLM cost optimization strategies
- API design and integrations
- Data models and database schema

**Show:**
- Code snippets from Shieldstone library
- API documentation (Swagger/OpenAPI)
- Test coverage reports

### For Financial/Investment Audience

**Emphasize:**
- Shieldstone methodology alignment with institutional standards
- Risk-adjusted return hurdles
- Property tax reassessment modeling
- Exit cap triangulation (3-method approach)
- Sensitivity analysis and downside protection

**Show:**
- Detailed assumption rationales
- Market data sources
- Comparable transactions
- Waterfall calculations (GP/LP splits)

### For Operations/Scaling Audience

**Emphasize:**
- Time savings (4-8 hours → 7 minutes)
- Cost savings vs. Argus/RedIQ
- Team collaboration features
- Pipeline management
- Integration with existing workflows (Excel export, Slack, Google Drive)

**Show:**
- Bulk deal processing
- Task assignment and tracking
- Activity logs
- Reporting dashboards

---

## Post-Demo Follow-Up

### Immediately After Demo

**Send:**
1. **Demo Recording** (if recorded)
2. **Sample BOE Memo** (Oakwood Apartments PDF)
3. **Sample IC Memo** (Oakwood Apartments PDF)
4. **Sample Excel Export** (with working formulas)
5. **Pricing Sheet** with package comparisons
6. **Trial Sign-Up Link** (14-day free trial)

### 24 Hours Later

**Email:**
- Thank you for attending
- Answer any questions raised during demo
- Offer to schedule follow-up call
- Share case study or customer testimonial
- Reminder of trial offer

### 1 Week Later (if no response)

**Email:**
- Check in: "Any questions about DREAM AI?"
- Share blog post or educational content on underwriting best practices
- Offer to demo on their own deal (bring your own OM)

---

## Troubleshooting

### If demo lags or fails to load:
- Have backup pre-recorded video ready
- Switch to pre-loaded sample deal (don't upload live)
- Walk through static screenshots if needed

### If audience has specific questions mid-demo:
- Note them and say "Great question—let me show you that at the end"
- Stay on script to avoid going over time
- Circle back in Q&A section

### If technical issues occur:
- Stay calm, acknowledge the issue
- Switch to backup plan (screenshots, video)
- Follow up with working demo later

---

## Success Metrics

Track after each demo:
- [ ] Did demo run smoothly? (no technical issues)
- [ ] Did audience engage? (asked questions)
- [ ] Did we stay on time? (15 minutes)
- [ ] Did they sign up for trial within 7 days?
- [ ] Did they convert to paying customer within 30 days?

**Target Conversion Rates:**
- Demo attendee → Trial signup: 40%
- Trial signup → Paying customer: 60%
- Overall demo → Customer: 24%

---

**Document Version:** 1.0  
**Last Updated:** December 20, 2025  
**Maintained By:** DREAM AI Sales & Product Teams

