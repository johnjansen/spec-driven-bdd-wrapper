# BDD Obfuscation Wrapper V2: With Satisfaction Scoring

## What's New

The V2 wrapper adds **satisfaction scoring** based on StrongDM's Software Factory model.

### Key Difference

**V1 (Original):**
```
5 tests failed

CREATE_USER: user creation has issues.
GET_USER: user retrieval not working correctly.
...
```

**V2 (With Scoring):**
```
🔴 TEST RESULTS - Satisfaction: 0.00/1.00 (Poor)

Summary: 0 passed, 5 failed, 0 skipped

Reasoning: 0% of scenarios passed. All failures are critical,
affecting core CRUD operations. The application is completely non-functional.

BEHAVIORAL FEEDBACK:
1. The application failed to register a new user account...
2. The application did not prevent duplicate email registration...
...
```

---

## Two-Phase Evaluation

### Phase 1: Obfuscation

Same as V1 - translates technical errors to behavioral feedback:

**Technical:** `NotImplementedError at api.py:117`
**Behavioral:** `The application failed to register a new user account...`

### Phase 2: Satisfaction Scoring (NEW!)

Evaluates overall behavioral satisfaction (0.0-1.0) using LLM-as-judge.

**Score ranges:**
- < 0.3: 🟡 Poor - Major issues, needs significant rework
- 0.3-0.7: 🟠 Moderate - Partially working, moderate improvements needed
- 0.7-0.9: ⏺ Good - Mostly correct, minor issues
- 0.9-1.0: 🟢 Excellent - Deployment-ready

**What influences the score:**
1. Pass rate percentage
2. Severity of failures (critical bugs vs minor issues)
3. Core functionality (is it usable at all?)
4. Failure complexity (simple fixes vs architecture problems)

---

## Example Output

### With Stub Implementation (All Methods Raise NotImplementedError)

```
🧪 Running BDD tests...
📊 Tests completed: 0 passed, 5 failed, 0 skipped
🔍 Phase 1: Obfuscating test failures with LLM...
📈 Phase 2: Evaluating satisfaction score...

================================================================================
🔴 TEST RESULTS - Satisfaction: 0.00/1.00 (Poor)
================================================================================

Summary: 0 passed, 5 failed, 0 skipped

Reasoning: 0% of scenarios passed. All failures are critical, affecting
core CRUD operations. The application is completely non-functional.

================================================================================

BEHAVIORAL FEEDBACK:
1. The application failed to register a new user account despite receiving
   valid credentials.
2. The application did not prevent the registration of a user with an email
   address that already exists.
3. The application failed to retrieve user details when provided with a
   valid user ID.
4. The application failed to apply the requested changes to the user's
   email address.
5. The application failed to remove the user account from the system.

================================================================================
```

### With Partial Implementation (4/5 Tests Passing)

```
📊 Tests completed: 4 passed, 1 failed, 0 skipped
📈 Phase 2: Evaluating satisfaction score...

================================================================================
🟢 TEST RESULTS - Satisfaction: 0.85/1.00 (Good)
================================================================================

Summary: 4 passed, 1 failed, 0 skipped

Reasoning: 80% pass rate with mostly correct implementation. One failing
scenario related to user deletion - appears to be an edge case issue rather
than core functionality problem. The application is largely functional.

================================================================================

BEHAVIORAL FEEDBACK:
1. User deletion fails to properly clean up email tracking, preventing
   subsequent operations with the same email.

================================================================================
```

---

## Why Satisfaction Scoring Matters

### Boolean Pass/Fail is Brittle

**Old way (V1):**
```
Status: failed
5 tests failed
```

**Problem:** "failed" tells you nothing about:
- Is it broken or just needs polish?
- Are these quick fixes or architectural issues?
- Should I continue or start over?

### Probabilistic Scoring Provides Nuance

**New way (V2):**
```
Satisfaction: 0.85/1.00 (Good)

Reasoning: 80% pass rate with mostly correct implementation. One failing
scenario is a minor edge case, not a core functionality problem.
```

**Benefits:**
- Agent knows "I'm close, just fix the edge case"
- Human reviewers see "85% satisfied, almost there"
- Iteration guidance: "Keep going" vs "Start over"

---

## Implementation Details

### Trace Collection

The wrapper collects execution traces (context for LLM evaluation):

```python
"traces": {
    "failed_step": "I create a user with email...",
    "error_type": "NotImplementedError",
    "error_message": "TODO: Implement create_user",
    "file_location": "api.py:117",
    "step_status": ["passed", "failed", "skipped", ...]
}
```

### LLM-as-Judge Scoring Prompt

```python
"""
Evaluate the overall satisfaction score (0.0-1.0) considering:
1. What percentage of scenarios passed? (80.0%)
2. How severe are the failures?
3. Is the core functionality working?
4. Are failures simple fixes or architectural problems?

Return JSON:
{
  "score": 0.85,
  "reasoning": "80% pass rate, minor edge case..."
}
"""
```

---

## Usage

### Run V2 Wrapper

```bash
cd spec-driven-test
source venv/bin/activate
python behave_wrapper_v2.py --ollama-model glm-4.7:cloud
```

### Compare V1 vs V2

```bash
# V1: Just behavioral feedback
python behave_wrapper.py --ollama-model glm-4.7:cloud

# V2: Behavioral feedback + satisfaction score
python behave_wrapper_v2.py --ollama-model glm-4.7:cloud
```

---

## Files

| File | What it does |
|------|--------------|
| `behave_wrapper.py` | V1: Obfuscation only |
| `behave_wrapper_v2.py` | V2: Obfuscation + Scoring |

---

## Integration with Agent Workflow

### Simple Loop

```python
wrapper = BDDObfuscationWrapperWithScoring()
code = ""

satisfaction = 0.0

while satisfaction < 0.90:
    # Agent improves code
    code = agent.improve(spec, code)
    write("generated_code/api.py", code)

    # Evaluate
    feedback = wrapper.run_tests_with_scoring()

    # Parse satisfaction
    satisfaction = extract_score(feedback)

    print(f"Current satisfaction: {satisfaction:.2f}/1.00")

    if satisfaction >= 0.90:
        print("✅ Deployment threshold reached!")
        break

    # Continue iterating based on score
    if satisfaction < 0.30:
        print("🔴 Needs major rework - starting over")
        code = ""
```

### Threshold-Based Deployment

```python
# Pre-defined satisfaction thresholds for production

PRODUCTION_THRESHOLD = 0.95
STAGING_THRESHOLD = 0.80
DEV_THRESHOLD = 0.70

feedback = wrapper.run_tests_with_scoring()
score = extract_score(feedback)

if score >= PRODUCTION_THRESHOLD:
    print("🚀 Deploy to production!")
elif score >= STAGING_THRESHOLD:
    print("🧪 Deploy to staging...")
elif score >= DEV_THRESHOLD:
    print("💻 Deploy to dev environment...")
else:
    print("⚠️  Score too low, continue development")
```

---

## Key Advantages

### For Agents

| V1 | V2 |
|----|----|
| "Tests failed" | "Satisfaction: 0.85 - just fix edge case" |
| Don't know if close | Quantified progress |
| Binary outcome | Graded feedback |

### For Humans

| V1 | V2 |
|----|----|
| No sense of quality | 85% satisfied |
| Can't track improvement | See score increase over iterations |
| Hard to decide when done | Threshold: 0.95 = deploy |

### For CI/CD

| V1 | V2 |
|----|----|
| Pass/fail branch | Score-based branching |
| All-or-nothing | Multiple environments |
| Binary gates | Graded gates |

---

## Next Steps

1. **Try it:** Run with stub implementation to see 0.00 score
2. **Implement:** Use example_partial_implementation.py for 0.85+ score
3. **Integrate:** Use satisfaction thresholds in agent workflow
4. **Tune:** Adjust score interpretation based on your domain

---

*This is the complete StrongDM Software Factory pattern:*
- *Phase 1: Obfuscation (hide technical details)*
- *Phase 2: Scoring (evaluate behavioral satisfaction)*
- *Result: Probabilistic, not brittle*