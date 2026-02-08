#!/usr/bin/env python3
"""
BDD Obfuscation Wrapper with Satisfaction Scoring for Spec-Driven Development

Based on StrongDM's Software Factory model:
1. Runs BDD tests against generated code
2. Captures raw test results and traces
3. Obfuscates implementation details using LLM
4. Evaluates satisfaction score (0.0-1.0) of behavior
5. Returns scored behavioral feedback to agents

The satisfaction score provides nuance beyond pass/fail:
- 0.0-0.3: Major issues, needs significant rework
- 0.3-0.7: Partially working, moderate improvements needed
- 0.7-0.9: Mostly correct, minor issues
- 0.9-1.0: Excellent, deployment-ready
"""

import subprocess
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Tuple
import sys


class BDDObfuscationWrapperWithScoring:
    """
    Extended wrapper that includes satisfaction scoring per StrongDM's model.

    Two-phase evaluation:
    1. Obfuscation: Translate technical errors to behavioral feedback
    2. Scoring: Evaluate overall behavioral satisfaction (0.0-1.0)
    """

    def __init__(
        self,
        code_dir: str = "generated_code",
        test_dir: str = "external_tests",
        ollama_url: str = "http://localhost:11434",
        ollama_model: str = "llama3.1"
    ):
        self.code_dir = Path(code_dir)
        self.test_dir = Path(test_dir)
        self.ollama_url = ollama_url
        self.ollama_model = ollama_model

    def run_tests_with_scoring(self) -> str:
        """
        Main entry point with satisfaction scoring.

        Returns:
            Formatted feedback including satisfaction score
        """
        print("🧪 Running BDD tests...")
        raw_results = self._run_behave()

        summary = raw_results['summary']
        print(f"📊 Tests completed: {summary['passed']} passed, {summary['failed']} failed, {summary['skipped']} skipped")

        # If all tests pass, perfect score
        if summary['failed'] == 0:
            return self._format_perfect_result(summary)

        # Phase 1: Obfuscation - translate technical errors to behavioral feedback
        print("🔍 Phase 1: Obfuscating test failures with LLM...")
        behavioral_feedback = self._obfuscate_results(raw_results)

        # Phase 2: Scoring - evaluate satisfaction (0.0-1.0)
        print("📈 Phase 2: Evaluating satisfaction score...")
        satisfaction_score, satisfaction_reasoning = self._evaluate_satisfaction(raw_results, behavioral_feedback)

        # Combine into formatted output
        return self._format_scored_result(
            summary,
            satisfaction_score,
            satisfaction_reasoning,
            behavioral_feedback
        )

    def _run_behave(self) -> Dict[str, Any]:
        """Run Behave and return structured results with traces."""
        results_path = self.test_dir / "test_results.json"

        # Clean up previous results
        if results_path.exists():
            results_path.unlink()

        # Run behave
        cmd = [
            sys.executable, "-m", "behave",
            str(self.test_dir / "features"),
            "--format=json.pretty",
            f"--outfile={results_path}"
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
                "error": "Tests timed out after 30 seconds"
            }

        # Parse the JSON output
        if results_path.exists():
            with open(results_path, 'r') as f:
                test_data = json.load(f)
        else:
            test_data = []

        return self._parse_test_results(test_data, result)

    def _parse_test_results(self, test_data: List[Dict], command_result: subprocess.CompletedProcess) -> Dict[str, Any]:
        """Parse Behave JSON output and extract failures with traces."""
        failures = []
        passed = 0
        failed = 0
        skipped = 0

        for feature in test_data:
            feature_name = feature.get("name", "Unknown Feature")

            for scenario in feature.get("elements", []):
                scenario_name = scenario.get("name", "Unknown Scenario")
                status = scenario.get("status", "unknown")

                if status == "passed":
                    passed += 1
                elif status in ("failed", "error"):
                    failed += 1

                    # Collect "traces" - execution details for LLM evaluation
                    failure_traces = self._collect_traces(scenario, feature_name, scenario_name)
                    failures.append(failure_traces)
                elif status == "skipped":
                    skipped += 1

        return {
            "status": "passed" if failed == 0 else "failed",
            "summary": {
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "total": passed + failed + skipped
            },
            "failures": failures,
            "raw_output": command_result.stdout,
            "stderr": command_result.stderr
        }

    def _collect_traces(self, scenario: Dict, feature_name: str, scenario_name: str) -> Dict:
        """
        Collect execution traces (the "trace" StrongDM refers to).
        These traces provide context for LLM evaluation.
        """
        failure_details = {
            "feature": feature_name,
            "scenario": scenario_name,
            "steps": [],
            "traces": {
                "failed_step": None,
                "error_type": None,
                "error_message": None,
                "file_location": None,
                "step_status": []
            }
        }

        for step in scenario.get("steps", []):
            step_status = step.get("status", "")
            step_info = {
                "keyword": step.get("keyword", ""),
                "name": step.get("name", ""),
                "status": step_status
            }
            failure_details["steps"].append(step_info)
            failure_details["traces"]["step_status"].append(step_status)

            if step_status in ("failed", "error"):
                error_match = step.get("match", {})
                if error_match:
                    failure_details["traces"]["failed_step"] = step.get("name", "")
                    failure_details["traces"]["error_type"] = "AssertionError" if "assert" in str(error_match.get("message", "")).lower() else "RuntimeError"
                    failure_details["traces"]["error_message"] = error_match.get("message", "")
                    failure_details["traces"]["file_location"] = error_match.get("location", "")

            if "error_message" in step:
                failure_details["traces"]["error_message"] = step["error_message"]

        return failure_details

    def _obfuscate_results(self, raw_results: Dict[str, Any]) -> str:
        """
        Phase 1: Obfuscation
        Translate code-level failures into behavioral feedback.
        """
        prompt = self._build_obfuscation_prompt(raw_results)

        try:
            response = self._call_ollama(prompt)
            return self._clean_and_format_response(response)
        except Exception as e:
            print(f"⚠️  Obfuscation failed: {e}")
            return self._fallback_obfuscation(raw_results)

    def _build_obfuscation_prompt(self, results: Dict[str, Any]) -> str:
        """Build obfuscation prompt for behavioral translation."""
        prompt = """You are translating test failures into behavioral feedback for an AI developer.

Your job: Convert code-level failures into business/specification-level problems.
- HIDE: File names, line numbers, function names, stack traces
- SHOW: What behavior failed, what was expected vs. actual
- BE CONCISE: Each failure should be 1-3 sentences
- USE CLARITY: Focus on what the spec expects, not how it's implemented

Examples translation:
  ❌ "AssertionError at user_steps.py:42: expected password_hash != None\n     Actual: stored_password == 'secure123'"
  ✅ "The password should be hashed before storage, but it appears to be stored in plaintext."

  ❌ "KeyError: 'email' in api.py line 15"
  ✅ "The user email field is missing from the user response."

Here are the test failures to translate:

"""

        for failure in results["failures"]:
            prompt += f"\n📍 Feature: {failure['feature']}\n"
            prompt += f"   Scenario: {failure['scenario']}\n"

            if failure["traces"]["error_message"]:
                prompt += f"   Error: {failure['traces']['error_message']}\n"

            if failure["traces"]["failed_step"]:
                prompt += f"   Failed Step: {failure['traces']['failed_step']}\n"

            prompt += "\n"

        prompt += """Translate each failure into behavioral feedback. Format as a numbered list:
1. [Behavior problem description]
2. [Behavior problem description]

Return ONLY the translated feedback, nothing else.
"""
        return prompt

    def _evaluate_satisfaction(self, raw_results: Dict, behavioral_feedback: str) -> Tuple[float, str]:
        """
        Phase 2: Scoring
        Evaluate satisfaction score (0.0-1.0) based on:
        - Number of passed vs failed tests
        - Severity of failures (from traces)
        - Behavioral feedback from obfuscation phase

        This is LLM-as-judge evaluation per StrongDM's model.
        """
        summary = raw_results['summary']
        total = summary['total']

        if total == 0:
            return 0.0, "No tests to evaluate"

        # Base score from pass rate
        base_pass_rate = summary['passed'] / total if total > 0 else 0

        # Build prompt for LLM to refine score based on failure severity
        prompt = f"""You are evaluating the behavioral satisfaction of a software implementation.

Context:
- Total scenarios: {total}
- Passed: {summary['passed']}
- Failed: {summary['failed']}
- Skipped: {summary['skipped']}

Behavioral feedback from obfuscation phase:
{behavioral_feedback}

Evaluate the overall satisfaction score (0.0-1.0) considering:
1. What percentage of scenarios passed? ({base_pass_rate:.1%})
2. How severe are the failures? (critical bugs vs minor issues)
3. Is the core functionality working? (partial usability vs broken)
4. Are failures simple fixes or architectural problems?

Return your response in this JSON format:
{{
  "score": 0.XX,
  "reasoning": "Brief explanation of why this score was given"
}}

Consider:
- 0.0-0.3: Major issues, needs significant rework (most tests failing)
- 0.3-0.7: Partially working, moderate improvements needed (mixed results)
- 0.7-0.9: Mostly correct, minor issues (most tests passing, edge cases failing)
- 0.9-1.0: Excellent, deployment-ready (minor or no issues)

Return ONLY the JSON, nothing else.
"""

        try:
            response = self._call_ollama(prompt)
            return self._parse_score_response(response)
        except Exception as e:
            print(f"⚠️  Scoring failed: {e}")
            # Fallback: use pass rate as score
            return base_pass_rate, f"Used pass rate ({base_pass_rate:.1%}) as fallback score"

    def _parse_score_response(self, response: str) -> Tuple[float, str]:
        """Parse LLM score response."""
        try:
            # Try to extract JSON from response
            data = json.loads(response)
            score = float(data.get("score", 0.0))
            reasoning = data.get("reasoning", "No reasoning provided")
            return score, reasoning
        except json.JSONDecodeError:
            # Try to extract score from text
            import re
            match = re.search(r'score["\s:]+(\d+\.?\d*)', response.lower())
            if match:
                score = float(match.group(1))
                reasoning = response[:200]
                return score, reasoning

        # Fallback
        return 0.0, "Failed to parse score response"

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API."""
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 2000
            }
        }

        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json=payload,
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        result = data.get("response", "") or data.get("thinking", "")
        return result

    def _format_perfect_result(self, summary: Dict) -> str:
        """Format output for perfect score case."""
        return f"""
================================================================================
🟢 TESTS PASSED - Satisfaction: 1.00/1.00
================================================================================

✅ All {summary['passed']} scenarios passed successfully!

Implementation is correct and ready for deployment.

================================================================================
"""

    def _format_scored_result(
        self,
        summary: Dict,
        score: float,
        reasoning: str,
        feedback: str
    ) -> str:
        """Format output with satisfaction score."""
        # Determine score emoji and label
        if score >= 0.9:
            emoji = "🟢"
            label = "Excellent"
        elif score >= 0.7:
            emoji = "🟡"
            label = "Good"
        elif score >= 0.4:
            emoji = "🟠"
            label = "Moderate"
        else:
            emoji = "🔴"
            label = "Poor"

        header = f"""
================================================================================
{emoji} TEST RESULTS - Satisfaction: {score:.2f}/1.00 ({label})
================================================================================

Summary: {summary['passed']} passed, {summary['failed']} failed, {summary['skipped']} skipped

{reasoning}

================================================================================

BEHAVIORAL FEEDBACK:
{feedback}

================================================================================
"""
        return header

    def _clean_and_format_response(self, response: str) -> str:
        """Clean up LLM response."""
        return response.strip()

    def _fallback_obfuscation(self, results: Dict[str, Any]) -> str:
        """Fallback obfuscation."""
        failures = results["failures"]
        summary = [
            f"Implementation issues detected ({results['summary']['failed']} test(s) failed)\n"
        ]

        patterns = {
            "create_user": [],
            "get_user": [],
            "update_user": [],
            "delete_user": []
        }

        for failure in failures:
            scenario = failure['scenario']
            error = failure.get("traces", {}).get("error_message", "")

            if "create" in scenario.lower():
                if "NotImplementedError" in str(error):
                    patterns["create_user"].append("the create_user method is not implemented yet.")
                elif "hash" in scenario.lower() or "password" in scenario.lower():
                    patterns["create_user"].append("passwords need to be hashed, not stored in plaintext.")
                elif "duplicate" in scenario.lower():
                    patterns["create_user"].append("duplicate emails should be rejected.")
                else:
                    patterns["create_user"].append("user creation has issues.")
            elif "fetch" in scenario.lower() or "get" in scenario.lower():
                patterns["get_user"].append("user retrieval is not working correctly.")
            elif "update" in scenario.lower():
                patterns["update_user"].append("user updates are not functioning.")
            elif "delete" in scenario.lower():
                patterns["delete_user"].append("user deletion has issues.")

        for category, messages in patterns.items():
            if messages:
                unique_messages = list(set(messages))
                summary.append(f"{category.upper()}:")
                for msg in unique_messages:
                    summary.append(f"  - {msg}")

        return "\n".join(summary)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="BDD Obfuscation Wrapper with Satisfaction Scoring")
    parser.add_argument("--code-dir", default="generated_code", help="Directory containing generated code")
    parser.add_argument("--test-dir", default="external_tests", help="Directory containing BDD tests")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama API URL")
    parser.add_argument("--ollama-model", default="llama3.1", help="Ollama model to use")

    args = parser.parse_args()

    wrapper = BDDObfuscationWrapperWithScoring(
        code_dir=args.code_dir,
        test_dir=args.test_dir,
        ollama_url=args.ollama_url,
        ollama_model=args.ollama_model
    )

    feedback = wrapper.run_tests_with_scoring()
    print(feedback)

    return 0


if __name__ == "__main__":
    sys.exit(main())