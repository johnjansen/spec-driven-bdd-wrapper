# BDD Obfuscation Wrapper - Architecture

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        SPECIFICATION                             │
│  "Build a user management API with CRUD operations"             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ Agent receives spec
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI AGENT                                    │
│  Reads spec, generates implementation code                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ Writes code
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  generated_code/                                │
│  api.py (agent CAN see this)                                    │
│                                                                 │
│  class UserAPI:                                                 │
│      def create_user(self, email, password):                    │
│          # Agent's code here                                    │
│          pass                                                   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ Wrapper invoked
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│            🛡️ BEHAVE_WRAPPER.PY (Obfuscation Layer)              │
├─────────────────────────────────────────────────────────────────┤
│  Step 1: Run Behave tests                                       │
│    $ behave external_tests/features/                            │
│                                                                  │
│  Step 2: Capture raw results                                    │
│    ✅ Passed: 0, ❌ Failed: 5                                    │
│                                                                  │
│  Step 3: Extract failures                                       │
│    Scenario: "Create a new user"                                │
│    Error: NotImplementedError at api.py:117                     │
│                                                                  │
│  Step 4: Send to Ollama for obfuscation                         │
│    Prompt: "Translate this error into behavioral feedback..."    │
│                                                                  │
│  Step 5: Receive obfuscated feedback                            │
│    "User creation method needs to be implemented with"          │
│    "password hashing and duplicate email checking."             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ Behavioral feedback (no technical details)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI AGENT                                    │
│  Receives: "User creation needs implementation"                 │
│            (NOT: "line 117: NotImplementedError")               │
│                                                                  │
│  Updates api.py...                                               │
│  Iterates until all tests pass                                  │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│         external_tests/ (Agent CANNOT See)                      │
├─────────────────────────────────────────────────────────────────┤
│  features/user_management.feature                               │
│    Scenario: Create a new user                                  │
│      Given the user database is empty                           │
│      When I create a user with email "alice@example.com"        │
│      Then the user should be created successfully               │
│      And the password should be hashed                          │
│                                                                  │
│  features/steps/user_steps.py                                  │
│    @given("the user database is empty")                         │
│    def step_impl(context):                                      │
│        storage = MemoryUserStorage()                            │
│        state.api = UserAPI(storage)                             │
│                                                                  │
│    @then("the password should be hashed")                       │
│    def step_impl(context):                                     │
│        assert stored_password != "secure123"  ← Test assertion  │
└─────────────────────────────────────────────────────────────────┘
```

## Translation Examples

### What the Wrapper Sees

```
Feature: User Management
  Scenario: Create a new user with valid credentials
    ...
    Traceback (most recent call last):
      File "external_tests/features/steps/user_steps.py", line 49
        state.response = state.api.create_user(email, password)
      File "generated_code/api.py", line 117
        raise NotImplementedError("TODO: Implement create_user")
    NotImplementedError: TODO: Implement create_user
```

### What the Agent Receives

```
TEST RESULTS:

1. User creation functionality needs to be implemented. The API should
   accept email and password, hash the password securely, and store the
   user with a unique ID.
```

### Another Example

**Wrapper receives:**
```
AssertionError at user_steps.py:63: stored_password == 'secure123'
Expected: stored_password != 'secure123'
```

**Agent receives:**
```
2. Passwords are being stored in plaintext. The password must be
   hashed (e.g., using bcrypt) before storage for security.
```

### Another Example

**Wrapper receives:**
```
KeyError: 'email' in api.py line 89
```

**Agent receives:**
```
3. User response is missing the email field. Ensure user objects
   returned by get_user include all required fields (id, email).
```

## Why Obfuscation Matters

### Without Obfuscation (Vulnerable to Reward Hacking)

```
Agent: "I see the test checks `stored_password != 'secure123'`
Solution: I'll change the stored password to 'hashed_password'!"

# Agent bypasses the intent of the test
stored_password = 'hashed_password'  # Passes test, but not actually hashed
```

### With Obfuscation (Reward-Hack Resistant)

```
Agent reads: "Passwords must be hashed before storage"
Agent thinks: "I need to implement bcrypt hashing"

# Agent must solve the actual problem
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

## Security Model

```
┌─────────────────────────────────────────────────────────────┐
│                Trusted Boundary                              │
│  Wrapper runs code in sandbox                                │
│  Tests live in external location                             │
│  LLM has access to test definitions                          │
└─────────────────────────────────────────────────────────────┘

            ↓  Obfuscated feedback only

┌─────────────────────────────────────────────────────────────┐
│                Untrusted Agent                               │
│  Generates code                                              │
│  Receives behavioral feedback only                           │
│  CANNOT see:                                                │
│    - Test file paths                                         │
│    - Line numbers                                            │
│    - Test implementation details                             │
│    - Assertion conditions                                    │
└─────────────────────────────────────────────────────────────┘

Result: Agent must solve the BUSINESS problem,
        not the TEST problem.
```

## Implementation Details

### Wrapper Responsibilities

1. **Test Execution**
   - Run Behave with JSON output
   - Parse results to find failures
   - Track pass/fail/skip counts

2. **Obfuscation**
   - Extract error messages and stack traces
   - Send to Ollama with instruction to hide technical details
   - Receive behavioral feedback

3. **Feedback Delivery**
   - Format feedback clearly for agent
   - Group failures by category when possible
   - Provide actionable improvement suggestions

### Test Runner Responsibilities

1. **Isolation**
   - Import generated code
   - Run scenarios in clean state
   - Reset between scenarios

2. **Assertion**
   - Verify behavior matches specification
   - Capture detailed error information
   - Pass to wrapper via JSON

### Ollama LLM Responsibilities

1. **Translation**
   - Understand code-level errors
   - Translate to business-level problems
   - Hide implementation details

2. **Context Awareness**
   - Understand the scenario context
   - Map errors to expectations
   - Provide helpful guidance

## Configuration

```python
wrapper = BDDObfuscationWrapper(
    code_dir="generated_code",      # Agent's code
    test_dir="external_tests",      # Secret tests
    ollama_url="http://localhost:11434",
    ollama_model="llama3.1"         # LLM for obfuscation
)

feedback = wrapper.run_tests_and_obfuscate()
```

## Extensions

### Multiple Test Suites

```python
# Run different test suites
for suite in ["user_management", "auth", "billing"]:
    feedback = wrapper.run_tests_and_obfuscate(suite)
```

### Custom Obfuscation Prompts

```python
def _build_obfuscation_prompt(self, results):
    prompt = "Translate failures into security-focused feedback..."
    # Or: focus on performance, UX, etc.
```

### Integration with AI Agents

```python
# Send feedback to agent
agent.improve(feedback)

# Check completion status
while not feedback.startswith("✅ All tests passed"):
    code = agent.implement(feedback)
    feedback = wrapper.run_tests_and_obfuscate()
```

---

*This architecture demonstrates how standard BDD tools (Behave) combined with an LLM judge (Ollama) create a robust spec-driven development system.*