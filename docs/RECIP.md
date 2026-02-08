# RECIP Spec-Driven Development - BDD Wrapper

## What It Is

A working implementation of the BDD wrapper pattern for spec-driven development with AI agents.

**Core concept:** Wrap BDD test results with an LLM to provide behavioral feedback without exposing implementation details.

---

## Why This Matters

### The Traditional Approach

```
Agent sees tests → Writes code to pass tests → Can game the tests
```

**Problem:** Agent can optimize against specific assertions:
```python
# Agent sees this test:
assert stored_password != "secure123"

# Agent writes:
stored_password = "hashed_password"  # Passes test, but not actually hashed!
```

### Our Approach

```
Agent sees behavioral feedback → Writes code to solve problem → Can't hack tests
```

**Solution:** Agent sees what's wrong, not where/why:
```
"Passwords must be hashed before storage"
```

**Not:**
```
"AssertionError at user_steps.py:63: stored_password == 'secure123'"
```

---

## How It Works

```
┌──────────────────┐
│  AI Agent        │
│  Receives spec   │
└────────┬─────────┘
         │
         │ Writes code
         ▼
┌──────────────────┐
│  generated_code/ │
│  api.py          │  ← Agent CAN see this
└────────┬─────────┘
         │
         │ Wrapper invoked
         ▼
┌──────────────────────────────────────────────────┐
│  🛡️ behave_wrapper.py (Obfuscation Layer)         │
│                                                  │
│  1. Run: behave external_tests/                 │
│  2. Parse: 5 failures                            │
│  3. Send: Errors to Ollama                      │
│  4. Get: "Create user needs implementation"     │
└────────┬─────────────────────────────────────────┘
         │
         │ Behavioral feedback (no technical details)
         ▼
┌──────────────────────────────────────────────────┐
│  AI Agent                                        │
│  Improve implementation...                       │
└──────────────────────────────────────────────────┘

┌──────────────────┐
│  external_tests/ │  ← Agent CANNOT see this
│  features/       │     (tests live here)
│  *.feature       │
└──────────────────┘
```

---

## Demo Walkthrough

### Step 1: Run with Stub Implementation

```bash
cd spec-driven-test
source venv/bin/activate
python behave_wrapper.py --ollama-model glm-4.7:cloud
```

**Output:**
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

**What happened:**
1. Wrapper ran Behave tests against stub API
2. All 5 scenarios failed (methods raise NotImplementedError)
3. Errors categorized by functionality
4. Agent receives behavioral feedback

### Step 2: Implement the API

```bash
cp example_partial_implementation.py generated_code/api.py
```

### Step 3: Run Again

```bash
python behave_wrapper.py --ollama-model glm-4.7:cloud
```

**Output:**
```
📊 Tests completed. Status: passed
✅ All tests passed! Implementation is correct.
```

---

## Translation Examples

### Example 1: Password Hashing

**Wrapper receives:**
```python
Traceback (most recent call last):
  File "external_tests/features/steps/user_steps.py", line 63
    assert stored_password != "secure123"
AssertionError: Password stored as plaintext, not hashed
```

**Agent receives:**
```
1. Passwords must be hashed before storage. The password should not
   be stored in plaintext form for security reasons.
```

### Example 2: Duplicate Email

**Wrapper receives:**
```python
KeyError: Email already exists in storage
```

**Agent receives:**
```
2. The system should reject attempts to create users with duplicate
   email addresses and return an appropriate error message.
```

### Example 3: Missing Field

**Wrapper receives:**
```python
KeyError: 'email' at api.py line 89
```

**Agent receives:**
```
3. User responses must include the email field. Ensure user objects
   returned by get_user contain all required properties.
```

---

## Key Features

### ✅ Separation of Concerns

- **generated_code/** → Agent writes code here
- **external_tests/** → Tests live here (agent can't see)
- **behave_wrapper.py** → Obfuscation layer

### ✅ Obfuscation of Technical Details

Agent sees behavioral feedback:
- "User creation needs implementation"
- "Passwords must be hashed"
- "Duplicate emails should be rejected"

NOT technical details:
- ❌ File paths
- ❌ Line numbers
- ❌ Function names
- ❌ Stack traces

### ✅ Graceful Degradation

If Ollama is unavailable:
- Tests still run
- Basic categorization provided
- System continues to function

### ✅ Standard BDD Tools

Uses:
- **Gherkin syntax** (Given/When/Then)
- **Behave** framework
- No custom test framework needed

---

## How to Use

### Basic Usage

```bash
python behave_wrapper.py --ollama-model glm-4.7:cloud
```

### Custom Options

```bash
# Use different model
python behave_wrapper.py --ollama-model llama3.1

# Custom Ollama URL
python behave_wrapper.py --ollama-url http://localhost:11434

# Custom directories
python behave_wrapper.py --code-dir my_code --test-dir my_tests
```

---

## Integration with Agents

### Simple Agent Workflow

```python
from behave_wrapper import BDDObfuscationWrapper

# Initialize wrapper
wrapper = BDDObfuscationWrapper()

# Agent receives spec
spec = "Build a user management API"

# Implementation loop
code = ""
while True:
    # Agent generates/improves code
    code = agent.implement(spec, code)

    # Write to generated area
    write("generated_code/api.py", code)

    # Validate with wrapper
    feedback = wrapper.run_tests_and_obfuscate()

    # Check completion
    if feedback.startswith("✅"):
        print("Implementation complete!")
        break

    print(f"Feedback: {feedback}")

    # Spec update with feedback (closed loop)
    spec += f"\n\n# FEEDBACK\n{feedback}"
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `behave_wrapper.py` | Main obfuscation layer |
| `external_tests/features/user_management.feature` | BDD scenarios |
| `external_tests/features/steps/user_steps.py` | Step definitions |
| `generated_code/api.py` | Agent implementation area |
| `example_partial_implementation.py` | Working example |
| `README.md` | Setup instructions |
| `QUICK_START.md` | 5-minute demo guide |
| `ARCHITECTURE.md` | Detailed architecture |
| `SUMMARY.md` | Quick reference |
| `DEMO.md` | Demo walkthrough |
| `RECIP.md` | This file |

---

## Verification

### What We Built

- ✅ Wrapper runs BDD tests against generated code
- ✅ Tests live in external directory (agent can't see)
- ✅ Technical errors translated to behavioral feedback
- ✅ Agent sees "what's wrong" not "where/why at code level"
- ✅ Fallback works if LLM unavailable
- ✅ Uses standard BDD tools (Behave)
- ✅ Demonstrates reward-hack resistance
- ✅ Provides actionable feedback for iteration

### Why This Matters

This is the **practical implementation** of StrongDM's Software Factory concept:

- **Spec-driven:** Humans write specs, agents write code
- **Scenario-based:** End-to-end scenarios, not brittle test suites
- **Agent-safe:** Can't rewrite tests to pass them
- **Production-ready:** Can be deployed today

---

## Next Steps

1. **Explore the code:** Read through `behave_wrapper.py`
2. **Try different models:** `ollama pull llama3.1` or `mistral`
3. **Implement more:** Add new scenarios to test suite
4. **Integrate agents:** Connect to actual agent workflow

---

## Credits

- **Concept:** StrongDM Software Factory (https://factory.strongdm.ai/)
- **BDD Framework:** Behave (https://behave.readthedocs.io/)
- **LLM:** Ollama (https://ollama.com/)
- **Implementation:** Built for #spec-driven-development research

---

*This is a working demo of the BDD wrapper pattern for spec-driven AI development.*