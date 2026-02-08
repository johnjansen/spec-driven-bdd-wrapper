# V1 vs V2: Wrapper Comparison

## Quick Reference

| Feature | V1 (behave_wrapper.py) | V2 (behave_wrapper_v2.py) |
|---------|------------------------|---------------------------|
| **Obfuscation** | ✅ Yes | ✅ Yes |
| **Scoring** | ❌ No | ✅ Yes (0.0-1.00) |
| **Traces** | Basic | Detailed (context for LLM) |
| **Reasoning** | None | Yes ( explains score) |
| **Output format** | Behavioral feedback | Score + Reasoning + Feedback |
| **LLM calls** | 1 (obfuscation) | 2 (obfuscation + scoring) |

---

## Output Comparison

### V1 Output

```
🧪 Running BDD tests...
📊 Tests completed. Status: failed

Implementation issues detected (5 test(s) failed)

CREATE_USER:
  - user creation has issues.
GET_USER:
  - user retrieval is not working correctly.
UPDATE_USER:
  - user updates are not functioning.
DELETE_USER:
  - user deletion has issues.
```

### V2 Output

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

---

## Score Interpretation

### V1 Agent Perspective

```
"What do I do? Tests failed. Are they simple bugs or major issues? Am I close?"
```

**Uncertainty about:**
- How broken is it?
- Should I fix or restart?
- How much more work?

### V2 Agent Perspective

```
"Satisfaction: 0.00/1.00 (Poor)
Reasoning: 0% of scenarios passed. All failures are critical, core
           CRUD operations non-functional.

Decision: Start over, build all CRUD operations first."
```

**Clear guidance:**
- 0.00 = Completely broken, restart
- 0.50 = Mixed results, continue iterating
- 0.85 = Almost there, fix edge cases
- 0.95 = Deployment-ready

---

## Use Cases

### Use V1 When

- Simple binary feedback is sufficient
- Want faster evaluation (1 LLM call instead of 2)
- Testing straightforward functionality
- Don't need progress tracking

### Use V2 When

- Want to know "how close" to completion
- Need quality thresholds for deployment
- Iterative agent development workflow
- Want to track progress over time
- CI/CD with multiple environments (dev/staging/prod)

---

## Integration Examples

### V1: Simple Pass/Fail

```python
wrapper = BDDObfuscationWrapper()

code = agent.implement(spec)
write("api.py", code)

feedback = wrapper.run_tests_and_obfuscate()

if feedback.startswith("✅"):
    deploy()
else:
    agent.improve(code, feedback)
```

### V2: Threshold-Based

```python
wrapper = BDDObfuscationWrapperWithScoring()

satisfaction = 0.0
code = ""

while satisfaction < 0.90:
    code = agent.improve(spec, code)
    write("api.py", code)

    feedback = wrapper.run_tests_with_scoring()
    satisfaction = extract_score(feedback)
    reasoning = extract_reasoning(feedback)

    print(f"Score: {satisfaction:.2f}")
    print(f"Reasoning: {reasoning}")

    if satisfaction < 0.30:
        # Score too low, restart
        code = ""
        print("Restarting from scratch...")

# Deploy when satisfaction >= 0.90
deploy(code)
```

### V2: Environment-Based Deployment

```python
feedback = wrapper.run_tests_with_scoring()
score = extract_score(feedback)

if score >= 0.95:
    deploy_to_production()
elif score >= 0.80:
    deploy_to_staging()
elif score >= 0.70:
    deploy_to_dev()
else:
    continue_development()
```

---

## Performance

| Metric | V1 | V2 |
|--------|----|----|
| **LLM calls** | 1 | 2 |
| **Runtime** | ~15-30s | ~30-60s |
| **Tokens used** | ~1K | ~2-3K |
| **Feedback quality** | Good | Better (with context) |

**Recommendation:** Use V2 for development where quality matters, V1 for fast iteration.

---

## Migration Guide

### From V1 to V2

```python
# Before (V1)
from behave_wrapper import BDDObfuscationWrapper

wrapper = BDDObfuscationWrapper()
feedback = wrapper.run_tests_and_obfuscate()

# After (V2)
from behave_wrapper_v2 import BDDObfuscationWrapperWithScoring

wrapper = BDDObfuscationWrapperWithScoring()
feedback = wrapper.run_tests_with_scoring()

# Extract score (V2 only)
score = extract_satisfaction_score(feedback)
reasoning = extract_reasoning(feedback)
```

---

## Summary

**V1:** Simple, fast, obfuscation-only
- Good for: Quick feedback, simple functionality
- Limitation: No insight into "how close" to complete

**V2:** Rich feedback with satisfaction scoring
- Good for: Iterative development, quality thresholds, progress tracking
- Advantage: Quantified progress, reasoned scores

**Recommendation:** Start with V2 for spec-driven development - the satisfaction scoring provides guidance that's invaluable for iterative refinement.

---

*Both wrappers use standard BDD tools (Behave) and Ollama for LLM-based obfuscation.*