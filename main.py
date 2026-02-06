"""
AI Operations Assistant
- FastAPI app
- Interactive CLI when run directly
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import uuid

from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent

# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(
    title="AI Operations Assistant",
    description="Multi-agent system for executing natural language tasks",
    version="1.0.0"
)

# Initialize agents
planner = PlannerAgent()
executor = ExecutorAgent()
verifier = VerifierAgent()


class TaskRequest(BaseModel):
    task: str
    max_steps: Optional[int] = 10


class TaskResponse(BaseModel):
    task_id: str
    status: str
    plan: Optional[Dict[str, Any]] = None
    execution_results: Optional[Dict[str, Any]] = None
    final_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# In-memory storage (replace with DB in production)
tasks_db = {}


@app.post("/execute", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    task_id = str(uuid.uuid4())[:8]

    try:
        plan = planner.create_plan(request.task)
        execution_results = executor.execute_plan(plan["steps"])
        final_result = verifier.verify_and_format(request.task, execution_results)

        tasks_db[task_id] = {
            "plan": plan,
            "execution_results": execution_results,
            "final_result": final_result
        }

        return TaskResponse(
            task_id=task_id,
            status="completed",
            plan=plan,
            execution_results={"steps": execution_results},
            final_result=final_result
        )

    except Exception as e:
        return TaskResponse(
            task_id=task_id,
            status="failed",
            error=str(e)
        )


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_result(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = tasks_db[task_id]

    return TaskResponse(
        task_id=task_id,
        status="completed",
        plan=task_data["plan"],
        execution_results={"steps": task_data["execution_results"]},
        final_result=task_data["final_result"]
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Operations Assistant"}


# ============================================================
# CLI MODE (runs when python main.py is executed)
# ============================================================

if __name__ == "__main__":
    print("AI Operations Assistant (CLI Mode)")
    print("Type your task below (or 'exit' to quit)\n")

    while True:
        try:
            task = input("Enter task > ").strip()

            if not task:
                print("Task cannot be empty\n")
                continue

            if task.lower() in {"exit", "quit"}:
                print("Exiting.")
                break

            print("\nPlanning...")
            plan = planner.create_plan(task)

            print("\nExecuting...")
            execution_results = executor.execute_plan(plan["steps"])

            print("\nVerifying...")
            final_result = verifier.verify_and_format(task, execution_results)

            print("\n" + "=" * 60)
            print("🤖 AI OPERATIONS ASSISTANT - RESULTS")
            print("=" * 60)

            status = final_result["status"]
            status_emoji = "✅" if status == "success" else "⚠️" if status == "partial" else "❌"
            print(f"\nStatus: {status_emoji} {status.upper()}")

            formatted = final_result.get("formatted_result", {})

            if formatted:
                # Display summary
                if "summary" in formatted:
                    print(f"\n📋 SUMMARY:")
                    print(f"  {formatted['summary']}")

                # Display details in natural language
                if "details" in formatted and formatted["details"]:
                    print(f"\n📝 DETAILS:")
                    for detail in formatted["details"]:
                        print(f"  • {detail}")

                # Display structured data (for reference)
                if "data" in formatted and formatted["data"]:
                    print(f"\n📊 DATA RETRIEVED:")
                    data = formatted["data"]

                    if "weather" in data:
                        weather = data["weather"]
                        print(f"  Weather Information:")
                        print(f"    Location: {weather.get('city', 'Unknown')}, {weather.get('country', '')}")
                        print(
                            f"    Temperature: {weather.get('temperature_c', 'N/A')}°C ({weather.get('temperature_f', 'N/A')}°F)")
                        print(f"    Condition: {weather.get('condition', 'N/A')}")
                        print(f"    Humidity: {weather.get('humidity', 'N/A')}%")
                        print(f"    Wind Speed: {weather.get('wind_kph', 'N/A')} km/h")

                    if "repositories" in data:
                        repos = data["repositories"]
                        print(f"\n  💻 GitHub Repositories ({len(repos)} found):")
                        for repo in repos[:5]:  # Show first 5
                            print(f"    • {repo.get('name', 'Unnamed')}")
                            print(f"      Stars: {repo.get('stars', 0)} | Language: {repo.get('language', 'N/A')}")
                            print(f"      URL: {repo.get('url', 'N/A')}")
                            if repo.get('description'):
                                print(f"      Description: {repo.get('description', '')[:80]}...")
                            print()

                    if "trending_repositories" in data:
                        repos = data["trending_repositories"]
                        print(f"\n  ⭐ Trending Repositories ({len(repos)} found):")
                        for repo in repos:
                            print(f"    • {repo.get('name', 'Unnamed')}")
                            print(f"      Stars: {repo.get('stars', 0)} | Language: {repo.get('language', 'N/A')}")
                            print(f"      URL: {repo.get('url', 'N/A')}")
                            print()

                # Display notes
                if "notes" in formatted and formatted["notes"]:
                    print(f"\n📌 NOTE:")
                    print(f"  {formatted['notes']}")

            if final_result.get("failed_steps"):
                print("\nISSUES ENCOUNTERED:")
                for step in final_result["failed_steps"]:
                    print(f"  Step {step['step']}: {step['error']}")

            print("\n" + "=" * 60)
            print(" TASK COMPLETED")
            print("=" * 60 + "\n")

        except KeyboardInterrupt:
            print("\nInterrupted. Exiting.")
            break

        except Exception as e:
            print(f"\n Error: {str(e)}\n")