# Wrapper Versions - Quick Reference

All wrapper implementations with their capabilities and use cases.

---

## Version Matrix

| Version | Config File | Scoring | Obfuscation | Trace Collection | LLM Calls | Best For |
|---------|-------------|---------|-------------|------------------|-----------|----------|
| **V1** | ❌ No | ❌ No | ✅ Yes | Basic | 1 | Simple, fast |
| **V2** | ❌ No | ✅ Yes | ✅ Yes | Detailed | 2 | Iterative development |
| **V3** | ✅ Yes | ✅ Yes | ✅ Yes | Detailed | 2 | Production use |

---

## Detailed Comparison

### V1: behave_wrapper.py

**File:** `behave_wrapper.py`

**Features:**
- ✅ Runs Behave tests
- ✅ Translates technical errors to behavioral feedback
- ✅ Basic trace collection
- ✅ Fallback on LLM failure

**CLI:**
```bash
python behave_wrapper.py --ollama-model glm-4.7:cloud
```

**When to Use:**
- Quick feedback loops
- Learning the pattern
- Simple binary feedback sufficient
- Don't need progress tracking

**Output:**
```
5 tests failed

CREATE_USER: user creation has issues.
GET_USER: user retrieval not working correctly.
...
```

---

### V2: behave_wrapper_v2.py

**File:** `behave_wrapper_v2.py`

**Features:**
- ✅ Everything from V1
- ✅ Satisfaction scoring (0.0-1.00)
- ✅ Detailed trace collection
- ✅ Score reasoning
- ✅ Deployment thresholds

**CLI:**
```bash
python behave_wrapper_v2.py --ollama-model llama3.1
```

**When to Use:**
- Iterative agent development
- Need to know "how close" to completion
- Want quality thresholds for deployment
- Tracking progress over time

**Output:**
```
🔴 TEST RESULTS - Satisfaction: 0.85/1.00 (Good)

Reasoning: 80% pass rate, mostly correct implementation.
         One failing scenario is a minor edge case.

Deployment status: ❌ Not ready (need 95% to deploy)

BEHAVIORAL FEEDBACK:
1. User deletion fails to clean up email tracking...
```

---

### V3: behave_wrapper_v3.py

**File:** `behave_wrapper_v3.py`

**Features:**
- ✅ Everything from V2
- ✅ Config file support (`.spec-driven.toml`)
- ✅ Auto-discovery (searches upward)
- ✅ Versionable configuration
- ✅ Project isolation
- ✅ `spec-driven init` command

**CLI:**
```bash
# Auto-discover .spec-driven.toml
spec-driven test

# Create example config
spec-driven init

# Specify custom config
spec-driven test --config /path/to/.spec-driven.toml
```

**When to Use:**
- Production deployment
- Multiple projects with different configs
- CI/CD integration
- Team collaboration
- Want one tool for all projects

**Output:**
```
🧪 Running tests from: /path/to/myproject/features
📝 Generated code at: /path/to/myproject/generated_code

🔴 TEST RESULTS - Satisfaction: 0.85/1.00 (NEEDS WORK)

Reasoning: 80% pass rate...

Deployment status: ❌ Not ready (< 95% threshold)

BEHAVIORAL FEEDBACK:
...
```

---

## Configuration File (.spec-driven.toml)

**Auto-discovered by V3.**

```toml
[project]
name = "my-user-api"

[paths]
generated_code_dir = "generated_code"
test_dir = "features"

[test]
runner = "behave"
features_path = "user_management.feature"

[test.interface]
type = "http_test_client"  # or "direct_import"

[llm]
model = "llama3.1"
url = "http://localhost:11434"
timeout = 20

[scoring]
production_threshold = 0.95
staging_threshold = 0.80
dev_threshold = 0.70

[wrapper]
use_satisfaction_scoring = true
verbose = false
```

---

## Performance Comparison

| Metric | V1 | V2 | V3 |
|--------|----|----|----|
| **Startup** | Fast | Fast | Fast (config lookup) |
| **Test execution** | Normal | Normal | Normal |
| **LLM calls** | 1 | 2 | 2 |
| **Runtime** | ~15-30s | ~30-60s | ~30-60s |
| **Memory** | Low | Low | Low |
| **Tokens used** | ~1K | ~2-3K | ~2-3K |

---

## Feature Comparison by Use Case

### For Learning

| Feature | V1 | V2 | V3 |
|---------|----|----|----|
| Simple to understand | ✅ Best | ✅ Good | ⏺ Moderate |
| Minimal setup | ✅ Best | ✅ Good | ⏺ Moderate |
| Clear output | ✅ | ✅ | ✅ |

**Winner:** V1

---

### For Rapid Iteration

| Feature | V1 | V2 | V3 |
|---------|----|----|----|
| Quick feedback | ✅ Best | ✅ | ✅ |
| Progress tracking | ❌ | ✅ Best | ✅ Best |
| Config management | ❌ | ❌ | ✅ Best |

**Winner:** V3 (if need config), V1 (if simple)

---

### For Production

| Feature | V1 | V2 | V3 |
|---------|----|----|----|
| Config file | ❌ | ❌ | ✅ Best |
| Deployment thresholds | ❌ | ✅ Good | ✅ Best |
| Auto-discovery | ❌ | ❌ | ✅ Best |
| Team friendly | ⏺ | ⏺ | ✅ Best |
| Versionable | ❌ | ❌ | ✅ Best |

**Winner:** V3

---

### For Agent Integration

| Feature | V1 | V2 | V3 |
|---------|----|----|----|
| Programmatic API | ✅ | ✅ | ✅ |
| Score extraction | ❌ | ✅ Best | ✅ Best |
| Config parsing | N/A | N/A | ✅ Best |
| Threshold logic | Manual | Manual | Built-in |

**Winner:** V3

---

## Migration Path

### V1 → V2

**Why?** Add satisfaction scoring

**Code change:**
```python
# Before
from behave_wrapper import BDDObfuscationWrapper
wrapper = BDDObfuscationWrapper()
feedback = wrapper.run_tests_and_obfuscate()

# After
from behave_wrapper_v2 import BDDObfuscationWrapperWithScoring
wrapper = BDDObfuscationWrapperWithScoring()
feedback = wrapper.run_tests_with_scoring()
score = extract_score(feedback)
```

**Benefits:**
- Know "how close" to completion
- Use thresholds for deployment decisions
- Track progress over iterations

---

### V2 → V3

**Why?** Add config file support

**Code change:**
```python
# Before
from behave_wrapper_v2 import BDDObfuscationWrapperWithScoring
wrapper = BDDObfuscationWrapperWithScoring(
    code_dir="generated_code",
    test_dir="features",
    ollama_url="http://localhost:11434",
    ollama_model="llama3.1"
)

# After
from behave_wrapper_v3 import BDDWrapperV3, SpecDrivenConfig
config = SpecDrivenConfig()  # Auto-discovers .spec-driven.toml
wrapper = BDDWrapperV3(config)
```

**Benefits:**
- No hardcoded paths in code
- Versionable configuration
- Project isolation
- One tool for all projects

---

## Recommendation

### Start with V3

**Reasons:**
1. Most feature-complete
2. Production-ready
3. Scalable to multiple projects
4. Future-proof
5. Only slight complexity increase

**When to downgrade:**
- Simplify for learning → Use V1
- Don't need config file → Use V2
- Performance-critical → Use V1 (1 LLM call)

---

## Quick Decision Guide

```
Need...
├─ Config file versioning?
│  └─ YES → V3
│  └─ NO  → ↓
├─ Satisfaction scoring?
│  └─ YES → V2
│  └─ NO  → ↓
└─ Simple/learn?
   └─ YES → V1
```

---

## File Locations

| Wrapper | Location |
|---------|----------|
| V1 | `spec-driven-test/behave_wrapper.py` |
| V2 | `spec-driven-test/behave_wrapper_v2.py` |
| V3 | `spec-driven-test/behave_wrapper_v3.py` |
| Config | `spec-driven-test/.spec-driven.toml` |

---

## Summary

| Wrapper | When to Use |
|---------|------------|
| **V1** | Learning, simple projects, fast iteration |
| **V2** | Single project, need scoring, no config file |
| **V3** | Production, multiple projects, team collaboration |

**Recommendation:** Start with V3 for production use.

---

*All wrappers use standard BDD tools (Behave) and Ollama for LLM-based obfuscation.*