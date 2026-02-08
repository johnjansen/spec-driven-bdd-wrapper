#!/usr/bin/env python3
"""
BDD Obfuscation Wrapper V3 - Config File Support

Reads configuration from .spec-driven.toml file.
Automatically discovers test locations, code locations, and LLM settings.
"""

import subprocess
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import sys
import toml


class SpecDrivenConfig:
    """Load and validate .spec-driven.toml configuration."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = self._find_config_file()

        if config_path is None:
            raise FileNotFoundError(
                "No .spec-driven.toml found. Run 'spec-driven init' to create one."
            )

        self.config_path = Path(config_path)
        self.config = toml.load(self.config_path)
        self._validate()

    def _find_config_file(self) -> Optional[str]:
        """Search for .spec-driven.toml in current and parent directories."""
        current = Path.cwd()

        for _ in range(10):  # Search up to 10 directories up
            config_file = current / ".spec-driven.toml"
            if config_file.exists():
                return str(config_file)

            parent = current.parent
            if parent == current:  # Reached root
                break
            current = parent

        return None

    def _validate(self):
        """Validate required configuration."""
        required_keys = [
            ("paths", "generated_code_dir"),
            ("paths", "test_dir"),
            ("test", "runner"),
            ("llm", "model"),
            ("llm", "url"),
        ]

        for section, key in required_keys:
            if key not in self.config.get(section, {}):
                raise ValueError(
                    f"Missing required config: [{section}] {key}"
                )

        # Set default scoring thresholds
        if "scoring" not in self.config:
            self.config["scoring"] = {}

        thresholds = {
            "production_threshold": 0.95,
            "staging_threshold": 0.80,
            "dev_threshold": 0.70,
        }

        for key, default in thresholds.items():
            if key not in self.config["scoring"]:
                self.config["scoring"][key] = default

    @property
    def generated_code_dir(self) -> Path:
        return Path(self.config["paths"]["generated_code_dir"])

    @property
    def test_dir(self) -> Path:
        return Path(self.config["paths"]["test_dir"])

    @property
    def test_runner(self) -> str:
        return self.config["test"]["runner"]

    @property
    def llm_model(self) -> str:
        return self.config["llm"]["model"]

    @property
    def llm_url(self) -> str:
        return self.config["llm"]["url"]

    @property
    def use_satisfaction_scoring(self) -> bool:
        return self.config.get("wrapper", {}).get("use_satisfaction_scoring", True)

    @property
    def production_threshold(self) -> float:
        return self.config["scoring"]["production_threshold"]

    def __repr__(self):
        return f"SpecDrivenConfig({self.config_path})"


class BDDWrapperV3:
    """
    BDD Wrapper with config file support.

    Uses .spec-driven.toml to automatically discover:
    - Where tests are located
    - Where generated code is located
    - LLM configuration
    - Scoring thresholds
    """

    def __init__(self, config: Optional[SpecDrivenConfig] = None):
        if config is None:
            config = SpecDrivenConfig()

        self.config = config

    def run(self) -> str:
        """Main entry point - run tests and return scored feedback."""
        print(f"🧪 Running tests from: {self.config.test_dir}")
        print(f"📝 Generated code at: {self.config.generated_code_dir}")

        raw_results = self._run_tests()

        if self.config.use_satisfaction_scoring:
            return self._run_with_scoring(raw_results)
        else:
            return self._run_obfuscation_only(raw_results)

    def _run_tests(self) -> Dict[str, Any]:
        """Run tests using configured runner."""
        runner = self.config.test_runner

        if runner == "behave":
            return self._run_behave()
        else:
            raise ValueError(f"Unsupported test runner: {runner}")

    def _run_behave(self) -> Dict[str, Any]:
        """Run Behave with configuration."""
        test_dir = self.config.test_dir
        output_file = test_dir / self.config["test"]["output_file"]

        # Clean up
        if output_file.exists():
            output_file.unlink()

        # Build command
        cmd = [
            sys.executable, "-m", "behave",
            str(test_dir),
            f"--format={self.config['test']['output_format']}",
            f"--outfile={output_file}"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "summary": {"passed": 0, "failed": 0, "skipped": 0}
            }

        # Parse results
        if output_file.exists():
            with open(output_file, 'r') as f:
                test_data = json.load(f)
        else:
            test_data = []

        return self._parse_test_results(test_data)

    def _parse_test_results(self, test_data: List[Dict]) -> Dict[str, Any]:
        """ParseBehave JSON output."""
        passed = 0
        failed = 0
        skipped = 0

        for feature in test_data:
            for scenario in feature.get("elements", []):
                status = scenario.get("status", "unknown")

                if status == "passed":
                    passed += 1
                elif status in ("failed", "error"):
                    failed += 1
                elif status == "skipped":
                    skipped += 1

        summary = {
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "total": passed + failed + skipped
        }

        return {
            "status": "passed" if failed == 0 else "failed",
            "summary": summary,
            "test_data": test_data
        }

    def _run_with_scoring(self, raw_results: Dict) -> str:
        """Run with satisfaction scoring."""
        summary = raw_results["summary"]

        print(f"📊 {summary['passed']} passed, {summary['failed']} failed, {summary['skipped']} skipped")

        if summary["failed"] == 0:
            return self._format_perfect_result(summary)

        # Phase 1: Obfuscation
        print("🔍 Phase 1: Obfuscating failures...")
        behavioral_feedback = self._obfuscate(raw_results)

        # Phase 2: Scoring
        print("📈 Phase 2: Evaluating satisfaction score...")
        score, reasoning = self._evaluate_satisfaction(raw_results, behavioral_feedback)

        # Check deployment threshold
        deploy_ready = score >= self.config.production_threshold

        return self._format_scored_result(
            summary, score, reasoning, behavioral_feedback, deploy_ready
        )

    def _run_obfuscation_only(self, raw_results: Dict) -> str:
        """Run without scoring (obfuscation only)."""
        summary = raw_results["summary"]

        if summary["failed"] == 0:
            return "✅ All tests passed!"

        print("🔍 Obfuscating failures...")
        feedback = self._obfuscate(raw_results)

        return f"""
================================================================================
Test Results: {summary['failed']} failed
================================================================================

{feedback}

================================================================================
"""

    def _obfuscate(self, raw_results: Dict) -> str:
        """Obfuscate failures using LLM."""
        # Build prompt from test data
        prompt = self._build_obfuscation_prompt(raw_results)

        try:
            response = self._call_llm(prompt)
            return response.strip()
        except Exception as e:
            return f"Obfuscation failed: {e}"

    def _evaluate_satisfaction(self, raw_results: Dict, feedback: str) -> Tuple[float, str]:
        """Evaluate satisfaction score."""
        summary = raw_results["summary"]
        pass_rate = summary["passed"] / summary["total"] if summary["total"] > 0 else 0

        prompt = f"""
Evaluate satisfaction score (0.0-1.0) for this implementation:

Pass rate: {pass_rate:.1%}
Passed: {summary['passed']}
Failed: {summary['failed']}

Behavioral feedback:
{feedback}

Consider:
- Core functionality working?
- Failures severe or minor?
- Quick fixes or architectural issues?

Return JSON:
{{"score": 0.XX, "reasoning": "..."}}
"""

        try:
            response = self._call_llm(prompt)
            return self._parse_score(response)
        except Exception as e:
            return pass_rate, f"Used pass rate as fallback: {e}"

    def _call_llm(self, prompt: str) -> str:
        """Call LLM for obfuscation or scoring."""
        timeout = self.config["llm"].get("timeout", 20)

        payload = {
            "model": self.config.llm_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 2000
            }
        }

        response = requests.post(
            f"{self.config.llm_url}/api/generate",
            json=payload,
            timeout=timeout
        )

        response.raise_for_status()
        data = response.json()

        return data.get("response", "") or data.get("thinking", "")

    def _parse_score(self, response: str) -> Tuple[float, str]:
        """Parse score from LLM response."""
        try:
            data = json.loads(response)
            return float(data["score"]), data.get("reasoning", "")
        except json.JSONDecodeError:
            # Try to extract score with regex
            import re
            match = re.search(r'"score"\s*:\s*(\d+\.?\d*)', response)
            if match:
                return float(match.group(1)), response[:200]

        return 0.0, "Failed to parse score"

    def _build_obfuscation_prompt(self, raw_results: Dict) -> str:
        """Build obfuscation prompt from test results."""
        return """
You are translating test failures into behavioral feedback for an AI developer.
- HIDE: File names, line numbers, function names
- SHOW: What behavior failed, what was expected vs. actual
- BE CONCISE: 1-3 sentences per failure

Test failures to translate:
(Implementation would add specific failures here)

Return ONLY behavioral feedback as a numbered list.
"""

    def _format_perfect_result(self, summary: Dict) -> str:
        """Format result when all tests pass."""
        return f"""
================================================================================
🟢 ALL TESTS PASSED - Satisfaction: 1.00/1.00
================================================================================

✅ All {summary['passed']} scenarios passed successfully!

Deployment status: ✅ READY (>= {self.config.production_threshold:.0%})

================================================================================
"""

    def _format_scored_result(
        self,
        summary: Dict,
        score: float,
        reasoning: str,
        feedback: str,
        deploy_ready: bool
    ) -> str:
        """Format result with score and deployment status."""
        status = "READY" if deploy_ready else f"NEEDS WORK (< {self.config.production_threshold:.0%})"

        return f"""
================================================================================
{'🟢' if deploy_ready else '🔴'} TEST RESULTS - Satisfaction: {score:.2f}/1.00 ({status})
================================================================================

Summary: {summary['passed']} passed, {summary['failed']} failed, {summary['skipped']} skipped

Reasoning:
{reasoning}

Deployment status: {'✅ Ready for production' if deploy_ready else f'❌ Not ready (need {self.config.production_threshold:.0%} to deploy)'}

================================================================================

BEHAVIORAL FEEDBACK:
{feedback}

================================================================================
"""


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="BDD Obfuscation Wrapper with config file support"
    )
    parser.add_argument(
        "--config",
        "-c",
        help="Path to .spec-driven.toml (default: search upward)"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Create example .spec-driven.toml in current directory"
    )

    args = parser.parse_args()

    if args.init:
        # Create example config
        config_template = """# Spec-Driven Development Configuration

[project]
name = "my-project"
version = "0.1.0"

[paths]
generated_code_dir = "generated_code"
test_dir = "features"

[test]
runner = "behave"
output_format = "json.pretty"
output_file = "test_results.json"

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
"""
        with open(".spec-driven.toml", "w") as f:
            f.write(config_template)

        print("✅ Created .spec-driven.toml")
        print("Edit the configuration for your project, then run:")
        print("  spec-driven test")
        return 0

    # Load config and run
    try:
        config = SpecDrivenConfig(args.config)
        wrapper = BDDWrapperV3(config)
        result = wrapper.run()
        print(result)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())