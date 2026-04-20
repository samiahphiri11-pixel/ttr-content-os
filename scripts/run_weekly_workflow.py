import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SCRIPTS_TO_RUN = [
    ("Scan folders", "scripts/scan_folders.py"),
    ("Generate week plan", "scripts/generate_week_plan.py"),
    ("Save folder usage", "scripts/save_folder_usage.py"),
    ("Generate post tasks", "scripts/generate_post_tasks.py"),
    ("Generate weekly prompts", "scripts/generate_weekly_prompts.py"),
    ("Generate weekly dashboard", "scripts/generate_weekly_dashboard.py"),
]


def run_script(step_name: str, script_path: str) -> bool:
    print("\n" + "=" * 70)
    print(f"STEP: {step_name}")
    print("=" * 70)

    full_path = PROJECT_ROOT / script_path

    if not full_path.exists():
        print(f"Missing script: {full_path}")
        return False

    result = subprocess.run(
        [sys.executable, str(full_path)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print("ERROR OUTPUT:")
        print(result.stderr)

    if result.returncode != 0:
        print(f"{step_name} failed with exit code {result.returncode}")
        return False

    print(f"{step_name} completed successfully.")
    return True


def main():
    print("Starting TT&R Elite weekly workflow...")

    for step_name, script_path in SCRIPTS_TO_RUN:
        success = run_script(step_name, script_path)
        if not success:
            print("\nWorkflow stopped because a step failed.")
            return

    print("\n" + "=" * 70)
    print("TT&R Elite weekly workflow completed successfully.")
    print("=" * 70)
    print("\nYour weekly system is updated.")


if __name__ == "__main__":
    main()