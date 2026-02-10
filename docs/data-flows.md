# Quanta Insights — Recruiter Workflow Data Flows

> **Living Document** — Updated as we discover new data relationships and refine
> the AI agent's read patterns. Last updated: 2026-02-10.

---

## Overview

This document maps how data flows between the four integrated systems in the
recruiter workflow, and how an AI agent should read across them to generate
context-aware insights.

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐     ┌──────────────┐
│   FATHOM     │ ──▶ │   SOURCEWHALE    │ ──▶ │   BULLHORN   │ ◀── │   LINKEDIN   │
│              │     │                  │     │   ATS        │     │   RECRUITER  │
│  Discovery   │     │  Outreach &      │     │  Applicant   │     │  Talent      │
│  Calls       │     │  Follow-up       │     │  Tracking    │     │  Sourcing    │
└──────────────┘     └──────────────────┘     └──────────────┘     └──────────────┘
     Step 1               Step 2                  Step 3               Step 3b
```

---

## The Recruiter Workflow

### Step 1: Discovery (Fathom)

**What happens:** Recruiters conduct discovery calls with candidates and clients.
Fathom records these meetings, generates AI summaries, extracts action items, and
provides full transcripts.

**Data produced:**
- Meeting summaries (AI-generated markdown)
- Full transcripts with speaker attribution and timestamps
- Action items with assignees and recording timestamps
- Calendar invitee metadata (names, emails, domains, internal/external)
- CRM matches (if CRM is connected)

**Key entities:**
- `Meeting` — the recorded call
- `Transcript` — timestamped speaker turns
- `Summary` — AI-generated meeting summary
- `ActionItem` — extracted next steps

**How AI agent uses this:**
- Retrieve context from a discovery call before outreach
- Summarize key points from a candidate screen
- Extract action items to inform next steps
- Identify which company domains have been discussed recently

---

### Step 2: Outreach & Follow-up (Sourcewhale)

**What happens:** After discovery calls, recruiters use Sourcewhale to send
personalized outreach sequences to candidates and manage client sales messaging.
Sourcewhale tracks email opens, replies, and LinkedIn message engagement.

**Data produced:**
- Outreach sequences (multi-step email/LinkedIn campaigns)
- Candidate engagement metrics (opens, clicks, replies)
- Response tracking and conversation threads
- Campaign analytics (aggregate performance)

**Key entities:**
- `Sequence` — an outreach campaign (multi-step)
- `SequenceStep` — individual touchpoint (email, LinkedIn message)
- `CandidateOutreach` — a candidate's journey through a sequence
- `CampaignAnalytics` — aggregate metrics

**How AI agent uses this:**
- Check if a candidate has already been contacted
- Review outreach history before re-engaging
- Analyze which sequences are performing best
- Correlate outreach timing with Fathom discovery calls

---

### Step 3: ATS Tracking (Bullhorn)

**What happens:** Bullhorn is the system of record for the recruiting pipeline.
Candidates, job orders, placements, and submissions are tracked here. This is
where the business outcomes (placements, revenue) are recorded.

**Data produced:**
- Candidate profiles and history
- Job orders (open positions)
- Submissions (candidates submitted to job orders)
- Placements (successful hires)
- Client corporation details
- Revenue and fee tracking

**Key entities:**
- `Candidate` — person being recruited
- `JobOrder` — open position at a client
- `Submission` — candidate submitted for a job order
- `Placement` — successful hire (the revenue event)
- `ClientCorporation` — the hiring company
- `ClientContact` — person at the client company

**How AI agent uses this:**
- Look up a candidate's full history across job orders
- Check placement trends by client or time period
- Calculate submission-to-placement conversion rates
- Identify which job orders need more candidates

---

### Step 3b: Talent Sourcing (LinkedIn Recruiter)

**What happens:** LinkedIn Recruiter is used in parallel with Bullhorn for
sourcing new candidates. Recruiters search for talent, manage recruiter projects
(pipelines), and track InMail conversations.

**Data produced:**
- Candidate search results (skills, experience, location)
- Recruiter project pipelines
- InMail conversation history
- Profile data

**Key entities:**
- `LinkedInProfile` — candidate's LinkedIn profile
- `RecruiterProject` — a pipeline/project in LinkedIn Recruiter
- `CandidateSearchResult` — search result with match metadata
- `InMailThread` — messaging history

**How AI agent uses this:**
- Find candidates matching open Bullhorn job orders
- Check if a LinkedIn candidate already exists in Bullhorn
- Review InMail history before re-engaging
- Source candidates for roles discussed in Fathom discovery calls

---

## Cross-System Data Relationships

### Linking Keys

The primary way to correlate data across systems:

| From → To | Linking Key | Notes |
|-----------|-------------|-------|
| **Fathom → Sourcewhale** | `email` (calendar invitee) | Match meeting attendees to outreach recipients |
| **Fathom → Bullhorn** | `email` or `company domain` | Match meeting attendees to candidates/clients in ATS |
| **Sourcewhale → Bullhorn** | `email` | Match outreach recipients to ATS candidates |
| **LinkedIn → Bullhorn** | `email` or `name` | Match LinkedIn profiles to ATS candidates |
| **Fathom → LinkedIn** | `company domain` | Find LinkedIn candidates at companies discussed in calls |

### Data Correlation Patterns

#### Pattern 1: Discovery-to-Outreach Pipeline
```
1. AI reads Fathom: "Get summary of latest call with Acme Corp"
2. AI reads Fathom: "Extract action items from that call"
3. AI reads Sourcewhale: "Has anyone from Acme Corp been contacted recently?"
4. AI reads Bullhorn: "What open job orders exist for Acme Corp?"
→ Insight: "You discussed 3 open roles with Acme Corp. 2 have active
   Sourcewhale sequences. 1 role (Senior Engineer) has no outreach yet."
```

#### Pattern 2: Candidate Pipeline Review
```
1. AI reads Bullhorn: "Show all submissions for Job Order #1234"
2. AI reads Sourcewhale: "What's the outreach status for each candidate?"
3. AI reads Fathom: "Were there any discovery calls with these candidates?"
4. AI reads LinkedIn: "Find additional candidates matching this job order"
→ Insight: "Job Order #1234 has 5 submissions. 3 candidates were sourced
   via Sourcewhale (2 replied). 1 had a Fathom screen call last week.
   LinkedIn shows 12 additional matches not yet in the pipeline."
```

#### Pattern 3: Client Relationship Intelligence
```
1. AI reads Fathom: "List all meetings with client domain 'techcorp.com'"
2. AI reads Bullhorn: "Show placement history with Tech Corp"
3. AI reads Sourcewhale: "Show outreach campaigns targeting Tech Corp contacts"
→ Insight: "You've had 8 meetings with Tech Corp this quarter. 3 placements
   YTD ($75K in fees). Active outreach to 2 new hiring managers."
```

#### Pattern 4: Recruiter Performance
```
1. AI reads Bullhorn: "Show placement stats by recruiter this quarter"
2. AI reads Sourcewhale: "Show outreach volume and reply rates by recruiter"
3. AI reads Fathom: "Show meeting frequency by recruiter"
→ Insight: "Top performer: Jane (12 placements, 85% reply rate, 40 calls).
   Opportunity: Bob has high call volume but low Sourcewhale follow-up."
```

---

## AI Agent Read Sequence Guidelines

When the AI agent needs to answer a question, it should follow these general
patterns for reading data in the right order:

### For candidate-related questions:
1. **Bullhorn first** — check if candidate exists in ATS
2. **Sourcewhale** — check outreach history
3. **Fathom** — check for discovery/screen calls
4. **LinkedIn** — check profile for additional context

### For client/company-related questions:
1. **Bullhorn first** — check client corporation, job orders, placements
2. **Fathom** — check for recent meetings with client contacts
3. **Sourcewhale** — check outreach to client contacts
4. **LinkedIn** — find additional contacts at the company

### For pipeline/performance questions:
1. **Bullhorn first** — placement and submission data (the outcomes)
2. **Sourcewhale** — outreach metrics (the activity)
3. **Fathom** — meeting data (the discovery effort)

### For sourcing new candidates:
1. **Bullhorn first** — understand the job order requirements
2. **LinkedIn** — search for matching candidates
3. **Sourcewhale** — check if candidates have been contacted before
4. **Fathom** — check for any prior conversations

---

## Open Questions & Discovery Items

> Add items here as we discover new data relationships or edge cases.

- [ ] **Sourcewhale API structure** — What entities and endpoints are available?
  Need API docs to confirm data model assumptions.
- [ ] **Fathom webhook reliability** — How quickly do webhooks fire after a
  meeting ends? Is there a delay for transcript processing?
- [ ] **Cross-system deduplication** — How do we handle the same person appearing
  in multiple systems with different email addresses?
- [ ] **Bullhorn ATS vs back-office data scope** — What entities are available
  via the ATS API vs the full back-office API? Need to confirm after scoping.
- [ ] **LinkedIn RSC data freshness** — How current is the data returned by the
  RSC API? Are there caching/staleness concerns?
- [ ] **Fathom CRM matches** — If Fathom has CRM integration, can we use its
  `crm_matches` field to link meetings to Bullhorn records automatically?
- [ ] **Rate limit coordination** — If multiple tools hit the same API in rapid
  succession, do we need request queuing per connector?

---

## Revision History

| Date | Change |
|------|--------|
| 2026-02-10 | Initial version — mapped 4-system recruiter workflow |
