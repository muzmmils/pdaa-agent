"""
Comprehensive test runner for PDAA Agent system
Runs all unit tests and generates detailed report.
"""

import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path


def run_tests():
    """Run all unit tests with detailed reporting."""
    
    print("\n" + "="*80)
    print("  PDAA AGENT - COMPREHENSIVE UNIT TEST SUITE")
    print("  Demonstrating Code Robustness")
    print("="*80 + "\n")
    
    # Test suites to run
    test_suites = [
        {
            "name": "Memory System Tests",
            "file": "tests/test_memory.py",
            "description": "SessionMemory, LongTermMemory, MemoryManager"
        },
        {
            "name": "Tool Tests",
            "file": "tests/test_tools.py",
            "description": "All 6 specialized tools (Intake, Reminder, Alert, Adherence, Risk, Recommendations)"
        },
        {
            "name": "Agent Tests",
            "file": "tests/test_agents.py",
            "description": "MonitorAgent, AnalyzerAgent, EscalatorAgent + Integration"
        }
    ]
    
    results = []
    total_passed = 0
    total_failed = 0
    total_tests = 0
    
    for suite in test_suites:
        print(f"\n{'─'*80}")
        print(f"📋 {suite['name']}")
        print(f"   {suite['description']}")
        print(f"{'─'*80}\n")
        
        # Run pytest for this test file
        result = subprocess.run(
            [sys.executable, "-m", "pytest", suite["file"], "-v", "--tb=short"],
            capture_output=True,
            text=True
        )
        
        # Parse output
        output_lines = result.stdout.split('\n')
        
        # Extract test results
        passed = 0
        failed = 0
        for line in output_lines:
            if " passed" in line:
                try:
                    passed = int(line.split()[0])
                except:
                    pass
            if " failed" in line:
                try:
                    failed = int(line.split()[0])
                except:
                    pass
        
        tests_run = passed + failed
        
        # Display results
        print(f"\n   ✓ Tests Passed: {passed}")
        if failed > 0:
            print(f"   ✗ Tests Failed: {failed}")
        print(f"   Total: {tests_run}\n")
        
        results.append({
            "suite": suite["name"],
            "file": suite["file"],
            "passed": passed,
            "failed": failed,
            "total": tests_run,
            "output": result.stdout
        })
        
        total_passed += passed
        total_failed += failed
        total_tests += tests_run
    
    # Summary
    print("\n" + "="*80)
    print("  TEST SUMMARY")
    print("="*80 + "\n")
    
    for result in results:
        status = "✓ PASSED" if result["failed"] == 0 else "✗ FAILED"
        print(f"  {status}  {result['suite']}: {result['passed']}/{result['total']} tests passed")
    
    print(f"\n{'─'*80}")
    print(f"  TOTAL: {total_passed}/{total_tests} tests passed")
    
    if total_failed == 0:
        print(f"  🎉 ALL TESTS PASSED - Code is robust!")
    else:
        print(f"  ⚠️  {total_failed} tests failed - review needed")
    
    print(f"{'─'*80}\n")
    
    # Generate report file
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "success_rate": round((total_passed / total_tests * 100) if total_tests > 0 else 0, 2)
        },
        "test_suites": [
            {
                "name": r["suite"],
                "file": r["file"],
                "passed": r["passed"],
                "failed": r["failed"],
                "total": r["total"]
            }
            for r in results
        ]
    }
    
    report_path = Path("test_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Detailed report saved to: {report_path}\n")
    
    # Return exit code
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
