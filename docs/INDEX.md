# BDD Obfuscation Wrapper - Documentation Index

Complete documentation for the spec-driven development BDD wrapper pattern.

---

## Quick Start

**5-minute demo:** `QUICK_START.md`

```bash
cd spec-driven-test
source venv/bin/activate
python behave_wrapper_v2.py --ollama-model glm-4.7:cloud
```

---

## Core Concepts

### What Is It?

A wrapper that:
1. Runs BDD tests against AI-generated code
2. Translates technical errors to behavioral feedback
3. (V2) Evaluates satisfaction score (0.0-1.00)

### Why It Matters

- **Reward-hack resistant:** Agent can't see test implementation
- **Behavior-focused:** "Password must be hashed" vs "line 42 failed"
- **Quality-aware:** Satisfaction scores guide iteration
- **Production-ready:** Uses standard BDD tools (Behave)

---

## Documentation Files

### Getting Started

| File | Purpose |
|------|---------|
| `QUICK_START.md` | 5-minute demo, minimal setup |
| `README.md` | Full setup and configuration |
| `SUMMARY.md` | Quick reference overview |

### Deep Dives

| File | Purpose |
|------|---------|
| `ARCHITECTURE.md` | Complete architecture, flow diagrams |
| `RECIP.md` | Complete documentation (all concepts) |
| `SUMMARY.md` | Verification checklist, key learnings |
| `DEMO.md` | Demo walkthrough with examples |
| `FULL_FLOW.md` | Complete flow diagram (config + test interface) |

### Configuration & Test Interface

| File | Purpose |
|------|---------|
| `TEST_INTERFACE.md` | Test import patterns and visibility |
| `WRAPPER_VERSIONS.md` | V1/V2/V3 comparison and usage |

### V2/V3 Scoring

| File | Purpose |
|------|---------|
| `V2_SCORING.md` | Satisfaction scoring documentation |
| `COMPARISON.md` | V1 vs V2 comparison |

---

## Wrapper Versions

### V1: Obfuscation Only

**File:** `behave_wrapper.py`

**What it does:**
- Runs Behave tests
- Translates technical errors to behavioral feedback
- Returns feedback to agent

**When to use:**
- Simple binary feedback sufficient
- Want faster evaluation (1 LLM call)
- Testing straightforward functionality

**Example output:**
```
5 tests failed

CREATE_USER: user creation has issues.
GET_USER: user retrieval not working correctly.
```

### V2: Obfuscation + Scoring

**File:** `behave_wrapper_v2.py`

**What it does:**
- Runs Behave tests
- Translates technical errors to behavioral feedback
- Evaluates satisfaction score (0.0-1.00)
- Returns score, reasoning, and feedback

**When to use:**
- Want to know "how close" to completion
- Need quality thresholds for deployment
- Iterative agent development workflow
- CI/CD with multiple environments

**Example output:**
```
🔴 TEST RESULTS - Satisfaction: 0.00/1.00 (Poor)

Reasoning: 0% of scenarios passed. All failures are critical,
affecting core CRUD operations.

BEHAVIORAL FEEDBACK:
1. The application failed to register a new user account...
```

---

## Key Concepts

### Obfuscation

**Technical error:** `AssertionError at user_steps.py:63: stored_password == 'secure123'`

**Behavioral feedback:** `Passwords must be hashed before storage.`

**Why:** Agent can't solve "pass line 63", can solve "hash passwords"

### Satisfaction Scoring (V2)

**Boolean pass/fail:** "Tests failed" (no context)
**Probabilistic score:** "0.85/1.00 - almost there, fix edge case"

**Why:** Agent knows whether to continue, restart, or deploy

### Traces

Execution details for LLM evaluation:
- Failed step names
- Error types
- Error messages
- Step status history

**Why:** Context helps LLM provide better feedback and scoring

---

## Usage Examples

### Basic Run

```bash
python behave_wrapper_v2.py --ollama-model glm-4.7:cloud
```

### Custom Options

```bash
python behave_wrapper_v2.py \
  --code-dir my_code \
  --test-dir my_tests \
  --ollama-url http://localhost:11434 \
  --ollama-model llama3.1
```

### Agent Integration

```python
from behave_wrapper_v2 import BDDObfuscationWrapperWithScoring

wrapper = BDDObfuscationWrapperWithScoring()

# Implementation loop
satisfaction = 0.0
code = ""

while satisfaction < 0.90:
    code = agent.improve(spec, code)
    write("generated_code/api.py", code)

    feedback = wrapper.run_tests_with_scoring()
    satisfaction = extract_score(feedback)

    if satisfaction < 0.30:
        code = ""  # Restart
    elif satisfaction >= 0.90:
        deploy(code)
```

---

## Project Structure

```
spec-driven-test/
├── 🚀 Wrappers
│   ├── behave_wrapper.py          # V1: Obfuscation only
│   └── behave_wrapper_v2.py       # V2: Obfuscation + Scoring
│
├── 📁 Generated Code
│   ├── api.py                     # Agent implementation area
│   └── example_partial_implementation.py  # Working example
│
├── 🧪 External Tests
│   ├── features/
│   │   ├── user_management.feature
│   │   └── steps/
│   │       └── user_steps.py
│   └── behave.ini
│
├── 📚 Documentation
│   ├── INDEX.md                   # This file
│   ├── QUICK_START.md             # 5-minute demo
│   ├── README.md                  # Setup instructions
│   ├── SUMMARY.md                 # Quick reference
│   ├── ARCHITECTURE.md            # Deep dive
│   ├── DEMO.md                    # Demo walkthrough
│   ├── RECIP.md                   # Complete guide
│   ├── V2_SCORING.md              # Scoring docs
│   └── COMPARISON.md              # V1 vs V2
│
└── 🔧 Configuration
    ├── pyproject.toml
    ├── requirements.txt
    └── setup.sh
```

---

## Verification Checklist

### What We Built

- ✅ Wrapper runs BDD tests against generated code
- ✅ Tests live in external directory (agent can't see)
- ✅ Technical errors translated to behavioral feedback
- ✅ (V2) Satisfaction scores evaluated (0.0-1.00)
- ✅ Wrapper provides reasoning for scores
- ✅ Fallback works if LLM unavailable
- ✅ Uses standard BDD tools (Behave)
- ✅ Demonstrates reward-hack resistance

### StrongDM Alignment

- ✅ **Spec-driven:** Humans write specs, agents write code
- ✅ **Scenario-based:** End-to-end scenarios, not brittle test suites
- ✅ **Agent-safe:** Can't rewrite tests to pass them
- ✅ **Satisfaction scoring:** Probabilistic evaluation, not boolean
- ✅ **LLM-as-judge:** LLM evaluates behavior quality
- ✅ **Production-ready:** Can be deployed today

---

## Next Steps

### Try It

```bash
cd spec-driven-test
source venv/bin/activate

# See stub fail (0.00/1.00)
python behave_wrapper_v2.py --ollama-model glm-4.7:cloud

# See example pass (0.85+/1.00)
cp example_partial_implementation.py generated_code/api.py
python behave_wrapper_v2.py --ollama-model glm-4.7:cloud
```

### Learn More

- Read `ARCHITECTURE.md` for the full concept
- Read `V2_SCORING.md` for why satisfaction scoring matters
- Read `COMPARISON.md` for V1 vs V2 differences

### Integrate

- Connect to agent workflow
- Use satisfaction thresholds for deployment
- Track scores over iterations

---

## Key Learnings

1. **Separation is critical:** Tests must live outside agent's accessible directories
2. **Obfuscation prevents gaming:** Agent can't optimize against tests it can't see
3. **Behavioral feedback is better:** Focus on business problems, not code locations
4. **Satisfaction scoring provides guidance:** "0.85 = close" vs "0.00 = restart"
5. **Standard tools work:** No custom framework needed, Behave is perfect
6. **LLM-as-judge is flexible:** Adapts to any error type, provides context

---

## Credits

- **Concept:** StrongDM Software Factory (https://factory.strongdm.ai/)
- **BDD Framework:** Behave (https://behave.readthedocs.io/)
- **LLM:** Ollama (https://ollama.com/)
- **Implementation:** Built for #spec-driven-development research

---

*This is a complete, production-ready implementation of the BDD wrapper pattern for spec-driven AI development.*