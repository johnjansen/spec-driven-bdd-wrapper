# BDD Obfuscation Wrapper - Spec-Driven Development Test

Proof of concept for the BDD wrapper pattern using Ollama as the LLM judge.

## Concept

```
┌─────────────────────────────────────────────────────────────┐
│                    AI AGENT                                  │
│  "Implement a user management API"                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              generated_code/                                 │
│  api.py - Agent writes implementation here                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│         🛡️ behave_wrapper.py (Obfuscation Layer)             │
│  1. Runs Behave tests against code                          │
│  2. Sends failures to Ollama for obfuscation               │
│  3. Returns behavioral feedback to agent                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│         external_tests/ (Agent Can't See)                   │
│  features/user_management.feature                           │
│  features/steps/user_steps.py                               │
│  (Only BDD runner has access)                               │
└─────────────────────────────────────────────────────────────┘
```

## Setup

### 1. Install Dependencies with uv

```bash
cd spec-driven-test
uv sync
```

### 2. Install Ollama (if not already installed)

```bash
# macOS with Homebrew
brew install ollama

# Or download from https://ollama.com/

# Start Ollama
ollama serve

# Pull a model (in another terminal)
ollama pull llama3.1
# OR
ollama pull mistral
# OR
ollama pull llama3
```

### 3. Make Wrapper Executable

```bash
chmod +x behave_wrapper.py
```

## Usage

### Run Tests (All Fail - Implementation Needed)

```bash
python behave_wrapper.py
```

Expected output:
```
🧪 Running BDD tests...
📊 Tests completed. Status: failed
🔍 Obfuscating test failures with Ollama...

================================================================================
Test Results: Implementation Needed
================================================================================

1. The UserAPI.create_user, UserAPI.get_user, UserAPI.update_user, and UserAPI.delete_user methods must be implemented to support user management functionality.

2. A storage mechanism is needed to persist user data with unique identification.

...

================================================================================
```

### What the Agent Sees

The agent receives **behavioral feedback**, not implementation details:

**❌ Not:**
```
AssertionError at user_steps.py:42
  Expected: stored_password != 'secure123'
  Actual: stored_password == 'secure123'
```

**✅ Instead:**
```
The password should be hashed before storage, but it appears to be stored in plaintext.
```

This prevents:
- ✗ Agent rewriting tests to make them pass
- ✗ Agent optimizing against specific assertions
- ✗ Agent seeing test implementation details

## Example Workflow

### 1. Agent Reads the Spec

```python
# Agent would be given the specification and the stub code
# File: generated_code/api.py (TODO markers guide implementation)
```

### 2. Agent Generates Code

Agent completes the implementation in `generated_code/api.py`:
```python
import bcrypt

class UserAPI:
    def create_user(self, email: str, password: str) -> dict:
        # ... implementation
```

### 3. Run Wrapper Again

```bash
python behave_wrapper.py
```

### 4. Get Obfuscated Feedback

Wrapper tells agent what's wrong **behaviorally**, not **technically**:
- "Password should be hashed" (not "line 42 assertion failed")
- "Duplicate emails should be rejected" (not "KeyError in storage.py")
- "Update user endpoint fails" (not "AttributeError at api.py:89")

### 5. Iterate

Agent uses feedback to improve implementation. Repeat until all tests pass.

## Directory Structure

```
spec-driven-test/
├── behave_wrapper.py          # The obfuscation layer (main executable)
├── pyproject.toml             # uv dependencies
├── README.md                  # This file
│
├── generated_code/            # Agent writes code here
│   └── api.py                 # Stub API with TODO markers
│
└── external_tests/            # BDD tests (agent can't see these)
    ├── behave.ini             # Behave configuration
    ├── features/
    │   ├── user_management.feature   # Gherkin scenarios
    │   └── steps/
    │       └── user_steps.py         # Step definitions
    └── test_results.json       # Generated by Behave
```

## Configuration

### Changing Ollama Model

```bash
python behave_wrapper.py --ollama-model mistral
```

Available models:
- `llama3.1` (default, 8B, fast)
- `llama3` (8B)
- `mistral` (7B, good for code)
- `codellama` (if installed)

### Changing Ollama URL

```bash
python behave_wrapper.py --ollama-url http://localhost:11434
```

## Testing Without Ollama

If Ollama is unavailable, the wrapper falls back to basic error summaries:

```bash
# Will try Ollama first, then fallback
python behave_wrapper.py
```

## Key Points

1. **Tests are external** - Agent cannot see `external_tests/`
2. **Obfuscation layer** - Wrapper runs tests, sends failures to LLM
3. **Behavioral feedback** - Agent sees "what's wrong" not "where/why at code level"
4. **Reward-hack resistant** - Agent can't optimize against what it can't see
5. **Reuses BDD tools** - Standard Behave/Gherkin, no custom test framework needed

## Next Steps

1. Run the wrapper to see initial failures
2. Implement one method at a time
3. Watch the obfuscated feedback guide you
4. Observe how feedback changes as you implement more

## References

- StrongDM Software Factory: https://factory.strongdm.ai/
- Behave Documentation: https://behave.readthedocs.io/
- Ollama Documentation: https://ollama.com/docs/

## Documentation

- **QUICK_START.md** - 5-minute demo
- **SUMMARY.md** - Quick reference
- **ARCHITECTURE.md** - In-depth architecture
- **DEMO.md** - Demo walkthrough
- **RECIP.md** - Complete documentation
- **README.md** - This file