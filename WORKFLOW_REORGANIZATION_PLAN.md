# Content Optimization Workflow Reorganization Plan

## Current Structure (BROKEN)
```
Step 0: Competitor Analysis (lines 2553-2735)
Step 1: Import & Analyze (lines 2737-2900)
Step 2: Content Brief (lines 2900-3300)
Step 3: Research Gaps (lines 3300-3500)
Step 4: Generate/Optimize (lines 3500-3700)
Step 5: Quality Check (lines 3700-3900)
Step 6: Export (lines 3900-4100)
```

## New Structure (CORRECT)
```
Step 1: Import Content (NEW - combines old Step 1)
  - Enter existing article URL
  - Enter primary keyword
  - Fetch and parse content
  - Display structure
  - Next button to Step 2

Step 2: Competitor Analysis (OLD Step 0 moved here)
  - Add 3-7 competitor URLs
  - Analyze against existing content
  - Show Keep/Improve/Add/Remove recommendations
  - Next to Step 3

Step 3: Content Brief (OLD Step 2, enhanced)
  - Auto-populated from Step 2 recommendations
  - Side-by-side comparison
  - Edit/approve structure
  - Next to Step 4

Step 4: Generate/Optimize (UNCHANGED)
  - Handle Keep/Improve/Add/Remove actions
  - Generate content

Step 5: Quality Check (UNCHANGED)
  - Before/after comparison

Step 6: Export (UNCHANGED)
  - Export optimized content
```

## Code Changes Required

### 1. Update Step Numbers
- [x] Change optimization_steps dict from 0-6 to 1-6
- [x] Change progress columns from 7 to 6
- [x] Update current_step initialization for optimization mode (0 → 1)

### 2. Reorganize Step Content

#### NEW Step 1: Import Content
**Location:** ~line 2552
**Content:** Simplified version of old Step 1
- URL input
- Keyword input
- Fetch button
- Display parsed structure
- Remove manual HTML paste option (not needed)

#### NEW Step 2: Competitor Analysis
**Location:** Move old Step 0 content here
**Changes needed:**
- Remove duplicate URL/keyword inputs (already in Step 1)
- Use keyword from optimization_data
- Use existing_url from Step 1
- Just add competitor URLs and analyze

#### NEW Step 3: Content Brief
**Location:** Old Step 2 location
**Changes needed:**
- Remove old Step 3 (Research Gaps) - merge into analysis
- Keep auto-population logic
- Keep action selectors

#### Steps 4-6: Minimal changes
- Update any step number references
- Keep core logic the same

## Implementation Order
1. ✅ Update step dictionary and progress bar
2. ✅ Update mode switching logic
3. ⏳ Reorganize Step 1 (Import)
4. ⏳ Move Step 0 to Step 2 (Competitor Analysis)
5. ⏳ Update Step 3 (Content Brief)
6. ⏳ Remove old Step 3 (Research Gaps)
7. ⏳ Test complete flow
