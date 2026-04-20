import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_script(script_path: str, args=None) -> bool:
    if args is None:
        args = []

    full_path = PROJECT_ROOT / script_path

    if not full_path.exists():
        print(f"Missing script: {full_path}")
        return False

    result = subprocess.run(
        [sys.executable, str(full_path), *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print("ERROR OUTPUT:")
        print(result.stderr)

    return result.returncode == 0


def main():
    print("\nTT&R ELITE FULL WEEK RUNNER")
    print("=" * 70)

    monday_date = input("Enter the Monday date for this content week (YYYY-MM-DD): ").strip()

    steps = [
        ("Scan folders", "scripts/scan_folders.py", []),
        ("Generate week plan", "scripts/generate_week_plan.py", []),
        ("Save folder usage", "scripts/save_folder_usage.py", []),
        ("Generate post tasks", "scripts/generate_post_tasks.py", []),
        ("Generate weekly prompts", "scripts/generate_weekly_prompts.py", []),
        ("Assign scheduled dates", "scripts/assign_scheduled_dates.py", [monday_date]),
        ("Generate weekly dashboard", "scripts/generate_weekly_dashboard.py", []),
        ("Export Buffer CSV", "scripts/export_buffer_csv.py", []),
    ]

    for step_name, script_path, args in steps:
        print("\n" + "=" * 70)
        print(f"STEP: {step_name}")
        print("=" * 70)

        success = run_script(script_path, args)

        if not success:
            print(f"\nWorkflow stopped at step: {step_name}")
            return

        print(f"{step_name} completed successfully.")

    print("\n" + "=" * 70)
    print("FULL WEEKLY RUN COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print("\nGenerated:")
    print("- updated weekly posts")
    print("- updated task list")
    print("- weekly prompts")
    print("- scheduled dates")
    print("- dashboard")
    print("- Buffer CSV")


if __name__ == "__main__":
    main()