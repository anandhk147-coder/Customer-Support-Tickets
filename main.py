"""
Unified Runner for Customer Support Tickets Assignment
Executes:
1. Part A: Data Cleaning & Analytics Pipeline
2. Part B.1: LLM Summary Evaluation
3. Part B.2: Neo4j Graph Model & Multi-Product Customer Query
4. Unit Tests Suite
"""

import sys
import unittest
from pathlib import Path

# Add project root and subdirectories to sys.path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "part_a"))
sys.path.insert(0, str(root_dir / "part_b"))

import part_a.run_part_a as part_a_runner
import part_b.evaluate_summaries as part_b1_runner
import part_b.graph_simulation as part_b2_runner


def run_all():
    print("#" * 80)
    print(" STEP 1: EXECUTING PART A (DATA CLEANING & ANALYTICS)")
    print("#" * 80)
    part_a_runner.main()

    print("\n\n" + "#" * 80)
    print(" STEP 2: EXECUTING PART B.1 (LLM SUMMARY EVALUATION)")
    print("#" * 80)
    part_b1_runner.evaluate_all()

    print("\n\n" + "#" * 80)
    print(" STEP 3: EXECUTING PART B.2 (GRAPH MODEL & CYPHER QUERY)")
    print("#" * 80)
    part_b2_runner.main()

    print("\n\n" + "#" * 80)
    print(" STEP 4: EXECUTING UNIT TEST SUITE")
    print("#" * 80)
    loader = unittest.TestLoader()
    suite = loader.discover(str(root_dir / "tests"))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "#" * 80)
    if result.wasSuccessful():
        print(" ALL CHECKS, PIPELINES, AND TESTS PASSED SUCCESSFULLY!")
    else:
        print(" SOME TESTS FAILED.")
    print("#" * 80)


if __name__ == "__main__":
    run_all()
