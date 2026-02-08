# Quick Start Guide

## 5-Minute Demo

```bash
# 1. Navigate to the project
cd spec-driven-test

# 2. Activate the virtual environment
source venv/bin/activate

# 3. Run the wrapper (tests will fail - expected)
python behave_wrapper.py --ollama-model glm-4.7:cloud
```

**Expected output:**
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

## See Working Implementation

```bash
# Copy the working example
cp example_partial_implementation.py generated_code/api.py

# Run tests again
python behave_wrapper.py --ollama-model glm-4.7:cloud
```

**Expected output:**
```
📊 Tests completed. Status: passed
✅ All tests passed! Implementation is correct.
```

## Understanding the Wrapper

### What the Wrapper Does

1. **Runs Behave tests** against `generated_code/api.py`
2. **Captures failures** with full stack traces
3. **Sends to Ollama** for behavioral translation
4. **Returns feedback** without technical details

### What the Agent Sees

**❌ Not:**
```
AssertionError at user_steps.py:42: stored_password == 'secure123'
```

**✅ Instead:**
```
Passwords must be hashed before storage.
```

## Project Structure

```
spec-driven-test/
├── behave_wrapper.py              # Obfuscation layer
├── ├── generated_code/           # Agent writes code here
│   └── api.py                    # Implementation
├── ├── external_tests/           # Agent CANNOT see
│   └── features/
│       ├── user_management.feature
│       └── steps/
│           └── user_steps.py
└── README.md                     # Full documentation
```

## Key Concept

**Agent CANNOT see the tests.**

The wrapper is the only thing that:
- Knows where the tests are
- Runs the tests
- Translates technical errors into behavioral feedback
- Tells the agent "what's wrong" without showing "where/why at code level"

This prevents:
- ✗ Agent rewriting tests to make them pass
- ✗ Agent optimizing against specific assertions
- ✗ Agent seeing test implementation details

## Troubleshooting

### Ollama not running?
```bash
brew install ollama
ollama serve
```

### No models available?
```bash
ollama pull llama3.1
# OR
ollama pull mistral
```

### Tests timing out?
The wrapper has a fallback - if Ollama times out, it still provides categorized feedback!

## Next Steps

1. Read `SUMMARY.md` for overview
2. Read `ARCHITECTURE.md` for deep dive
3. Try implementing the other scenarios
4. Integrate with agent workflow

---

*For full documentation, see `README.md`*