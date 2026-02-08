# Full Flow Diagram - Config File + Test Interface

## Complete Architecture with Configuration Auto-Discovery

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI                                  │
│  $ spec-driven test                                         │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    │ BehaveWrapperV3()
                    │ └─ config.load()
                    ▼
┌─────────────────────────────────────────────────────────────┐
│           .spec-driven.toml (Auto-discovered)              │
├─────────────────────────────────────────────────────────────┤
│  [paths]                                                    │
│    generated_code_dir = "generated_code"                   │
│    test_dir = "features"                                   │
│                                                            │
│  [test]                                                     │
│    runner = "behave"                                       │
│    interface.type = "http_test_client"                     │
│                                                            │
│  [llm]                                                      │
│    model = "llama3.1"                                      │
│    url = "http://localhost:11434"                          │
│                                                            │
│  [scoring]                                                  │
│    production_threshold = 0.95                             │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    │ Read config
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    🛡️ Wrapper                               │
├─────────────────────────────────────────────────────────────┤
│  config = SpecDrivenConfig()  # Auto-searches upward      │
│                                                            │
│  code_dir = config.generated_code_dir                      │
│  test_dir = config.test_dir                                │
│                                                            │
│  results = runner.run(test_dir)                            │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    │ Two paths for test execution
                    ▼
        ┌────────────────────────┐
        │                        │
        ▼                        ▼
┌───────────────────┐  ┌───────────────────┐
│  Approach A       │  │  Approach B       │
│  Direct Import    │  │  HTTP Interface   │
├───────────────────┤  ├───────────────────┤
│  from api import  │  │  from api import  │
│       UserAPI     │  │       create_app  │
│                   │  │                   │
│  api = UserAPI()  │  │  app = create_app │
│  api.create_user()│  │  client = app...  │
│                   │  │  client.post(...) │
└───────────────────┘  └───────────────────┘
        │                        │
        ▼                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Test Execution (Behave)                        │
│  Location: features/ (Agent CANNOT see)                     │
│                                                            │
│  user_management.feature:                                  │
│    When I POST to /users...                                │
│    Then I receive 201...                                   │
│                                                            │
│  steps/user_steps.py:                                      │
│    ✅ from api import create_app  ← ONE-WAY IMPORT         │
│    ❌ import tests               ← PROHIBITED               │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    │ Results + Traces
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                 Two-Phase Evaluation                        │
├─────────────────────────────────────────────────────────────┤
│  Phase 1: Obfuscation                                       │
│    Input:  "AssertionError at line 42"                      │
│    Output: "Password must be hashed"                        │
│                                                            │
│  Phase 2: Satisfaction Scoring                              │
│    Input:  4 passed, 1 failed                              │
│    Output: 0.85/1.00 (Good - fix edge case)                │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    │ Scored feedback
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Receives                            │
│                                                            │
│  🔴 Satisfaction: 0.85/1.00 (Good)                         │
│                                                            │
│  Reasoning: 80% pass rate, mostly correct. One failing     │
│            scenario is a minor edge case.                  │
│                                                            │
│  Behavioral feedback:                                      │
│    1. User deletion fails to clean up...                   │
│                                                            │
│  Deployment status: ❌ Not ready (need 95% to deploy)      │
└─────────────────────────────────────────────────────────────┘
```

---

## Auto-Discovery Flow

```
User runs: $ spec-driven test
                  │
                  ▼
         SpecDrivenConfig()
         └─ search_upward()
             │
             ├─ Check: /Users/claw/.openclaw/workspace/test/.spec-driven.toml
             │
             ├─ Check: /Users/claw/.openclaw/workspace/.spec-driven.toml
             │
             └─ Found! ✓
                  │
                  ▼
           Load config
           └─ Read paths, LLM settings, thresholds
                  │
                  ▼
           Use config for entire run
```

---

## Security & Visibility

### What Agent Can Do

```
┌─────────────────────────────────────────┐
│  Agent Permissions                     │
├─────────────────────────────────────────┤
│  ✅ READ  generated_code/              │
│  ✅ WRITE generated_code/              │
│  ✅ READ  .spec-driven.toml            │
│  ❌ READ  features/                    │
│  ❌ WRITE features/                    │
│  ❌ READ  test_results.json            │
└─────────────────────────────────────────┘
```

### What Tests Can Do

```
┌─────────────────────────────────────────┐
│  Test Permissions                     │
├─────────────────────────────────────────┤
│  ✅ READ  generated_code/              │
│  ✅ IMPORT from generated_code/        │
│  ✅ READ  .spec-driven.toml            │
│  ✅ WRITE test_results.json            │
│  ❌ WRITE generated_code/              │
│  ❌ MODIFIED by Agent                  │
└─────────────────────────────────────────┘
```

### One-Way Flow

```
┌──────────────────┐         ┌──────────────────┐
│  Agent           │  ✅      │  Tests           │
│  Writes          │  -----> │  Import          │
│  generated_code/ │         │  generated_code/ │
└──────────────────┘         └──────────────────┘

┌──────────────────┐         ┌──────────────────┐
│  Tests           │  ❌      │  Agent           │
│  Export          │  ------ │  Cannot see      │
│  (no mechanism)  │         │  test directory  │
└──────────────────┘         └──────────────────┘
```

---

## Decision Tree

### Which Test Interface to Use?

```
Need to test internal logic?
│
├─ YES: Use direct import
│  - Faster iteration
│  - Test data structures directly
│  - Debug easier
│
└─ NO: Use HTTP interface
   - Tests external contract
   - Production parity
   - Decoupled implementation
```

### When to Use Each?

| Scenario | Approach |
|----------|----------|
| Rapid prototyping | Direct Import |
| Testing HTTP APIs | HTTP Interface |
| Unit tests | Direct Import |
| Integration tests | HTTP Interface |
| Contract testing | HTTP Interface |
| Data structure testing | Direct Import |
| End-to-end testing | HTTP Interface |

---

## Summary

### Configuration (.spec-driven.toml)

**Benefits:**
- ✅ Auto-discovery from any directory
- ✅ No hardcoded paths in code
- ✅ Versionable with project
- ✅ Defaults via `spec-driven init`

### Test Interface (Imports)

**Key principle:** One-way imports only
- Tests → Import → Code ✅
- Code → Export → Tests ❌

**Two approaches:**
- Direct Import: Simple, fast, tests internals
- HTTP Interface: Realistic, tests contract, production parity

**Recommendation for spec-driven:**
- Use HTTP interface
- Tests validate the external contract
- Matches spec: "POST to /users" → implement `/users`

---

*This is the complete picture: config files + test patterns + security boundaries.*