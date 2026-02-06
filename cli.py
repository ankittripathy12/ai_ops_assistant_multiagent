#!/usr/bin/env python3
"""
Command Line Interface for AI Operations Assistant
"""
import argparse
import json
import sys
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent


def main():
    parser = argparse.ArgumentParser(
        description="AI Operations Assistant - Execute natural language tasks"
    )
    parser.add_argument(
        "task",
        help="Natural language task to execute (enclose in quotes if it contains spaces)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output including execution plan"
    )
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )

    args = parser.parse_args()

    # Initialize agents
    planner = PlannerAgent()
    executor = ExecutorAgent()
    verifier = VerifierAgent()

    try:
        if args.output == "text":
            print(f"🔍 Task: {args.task}")
            print("=" * 60)

        # Step 1: Planning
        if args.output == "text":
            print("\n📋 1. Planning Phase...")
        plan = planner.create_plan(args.task)

        if args.verbose and args.output == "text":
            print(f"Plan generated:\n{json.dumps(plan, indent=2)}")

        # Step 2: Execution
        if args.output == "text":
            print("\n⚡ 2. Execution Phase...")
        execution_results = executor.execute_plan(plan["steps"])

        if args.output == "text":
            for result in execution_results:
                if result["success"]:
                    print(f"Step {result['step']}: Success")
                else:
                    print(f"Step {result['step']}: Failed - {result['error']}")

        # Step 3: Verification
        if args.output == "text":
            print("\n3.Verification & Formatting Phase...")
        final_result = verifier.verify_and_format(args.task, execution_results)

        # Output based on format
        if args.output == "json":
            # Return JSON output
            output = {
                "task": args.task,
                "plan": plan,
                "execution_results": execution_results,
                "final_result": final_result
            }
            print(json.dumps(output, indent=2))
        else:
            # Text output
            print("\n" + "=" * 60)
            print("FINAL RESULT")
            print("=" * 60)

            status_icons = {
                "success": "✅",
                "partial": "⚠️ ",
                "failed": "❌"
            }

            status = final_result["status"]
            icon = status_icons.get(status, "📌")
            print(f"{icon} Status: {status.upper()}")

            formatted = final_result["formatted_result"]
            if formatted:
                print(f"\n📝 Summary: {formatted.get('summary', 'N/A')}")

                if "details" in formatted and formatted["details"]:
                    print("\n📋 Details:")
                    for detail in formatted["details"]:
                        if isinstance(detail, str):
                            print(f"  • {detail}")
                        else:
                            print(f"  • {str(detail)}")

                if "data" in formatted and formatted["data"]:
                    print("\n Data:")
                    if isinstance(formatted["data"], dict):
                        for key, value in formatted["data"].items():
                            if isinstance(value, (dict, list)):
                                value = json.dumps(value, indent=2)
                                print(f"  {key}:\n{value}")
                            else:
                                print(f"  {key}: {value}")

                if "notes" in formatted and formatted["notes"]:
                    print(f"\n Notes: {formatted['notes']}")

            if final_result["failed_steps"]:
                print("\n Issues encountered:")
                for step in final_result["failed_steps"]:
                    print(f"  Step {step['step']}: {step['error']}")

            print("\n" + "=" * 60)
            print(" Task execution completed!")

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"error": str(e), "task": args.task}, indent=2))
        else:
            print(f"\n Error executing task: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()