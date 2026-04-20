import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MENU_OPTIONS = {
    "1": ("Run weekly workflow", "scripts/run_weekly_workflow.py"),
    "2": ("View weekly plan", "scripts/view_week_plan.py"),
    "3": ("View tasks", "scripts/view_tasks.py"),
    "4": ("Generate weekly dashboard", "scripts/generate_weekly_dashboard.py"),
    "9": ("View post statuses", "scripts/view_post_statuses.py"),
    "10": ("View post progress summary", "scripts/post_progress_summary.py"),
}


def run_script(script_path: str):
    full_path = PROJECT_ROOT / script_path

    if not full_path.exists():
        print(f"Script not found: {full_path}")
        return

    result = subprocess.run(
        [sys.executable, str(full_path)],
        cwd=PROJECT_ROOT
    )

    if result.returncode != 0:
        print(f"Script exited with code {result.returncode}")


def main():
    while True:
        print("\nTT&R ELITE CONTROL CENTER")
        print("=" * 50)

        print("1. Run weekly workflow")
        print("2. View weekly plan")
        print("3. View tasks")
        print("4. Generate weekly dashboard")
        print("5. Mark task status")
        print("6. Generate post brief")
        print("7. Build agent prompt")
        print("8. Update post status")
        print("9. View post statuses")
        print("10. View post progress summary")
        print("11. Recommend post statuses")
        print("12. Sync post statuses from tasks")
        print("13. Export Buffer CSV")
        print("14. Save caption text")
        print("15. View saved captions")
        print("16. Save agent output")
        print("17. View agent outputs")
        print("18. Export post package")
        print("19. View post completion checklist")
        print("20. View ready posts")
        print("21. Assign scheduled dates")
        print("22. View schedule")
        print("0. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "0":
            print("Goodbye.")
            break

        elif choice in MENU_OPTIONS:
            _, script_path = MENU_OPTIONS[choice]
            run_script(script_path)

        elif choice == "5":
            task_id = input("Enter task ID: ").strip()
            status = input("Enter status (todo, in_progress, done): ").strip()

            result = subprocess.run(
                [sys.executable, "scripts/update_task_status.py", task_id, status],
                cwd=PROJECT_ROOT
            )

            if result.returncode != 0:
                print("Failed to update task.")

        elif choice == "6":
            post_id = input("Enter post ID: ").strip()

            result = subprocess.run(
                [sys.executable, "scripts/generate_post_brief.py", post_id],
                cwd=PROJECT_ROOT
            )

            if result.returncode != 0:
                print("Failed to generate post brief.")

        elif choice == "7":
            post_id = input("Enter post ID: ").strip()
            agent_name = input(
                "Enter agent name (Messi, Ronaldo, Neymar, Xavi, Mbappé, Modrić, De Bruyne): "
            ).strip()

            result = subprocess.run(
                [sys.executable, "scripts/agent_prompt_builder.py", post_id, agent_name],
                cwd=PROJECT_ROOT
            )

            if result.returncode != 0:
                print("Failed to build agent prompt.")

        elif choice == "8":
            post_id = input("Enter post ID: ").strip()
            status = input(
                "Enter post status (idea, planned, editing, caption_ready, scheduled, posted): "
            ).strip()

            result = subprocess.run(
                [sys.executable, "scripts/update_post_status.py", post_id, status],
                cwd=PROJECT_ROOT
            )

            if result.returncode != 0:
                print("Failed to update post status.")

        elif choice == "9":
            result = subprocess.run(
                [sys.executable, "scripts/view_post_statuses.py"],
                cwd=PROJECT_ROOT
            )
            if result.returncode != 0:
                print("Failed to view post statuses.")
                
        elif choice == "10":
            result = subprocess.run(
                [sys.executable, "scripts/post_progress_summary.py"],
                cwd=PROJECT_ROOT
            )
            if result.returncode != 0:
                print("Failed to view post progress summary.")

        elif choice == "11":
            result = subprocess.run(
                [sys.executable, "scripts/recommend_post_statuses.py"],
                cwd=PROJECT_ROOT
            )
            if result.returncode != 0:
                print("Failed to recommend post statuses.")

        elif choice == "12":
            result = subprocess.run(
                [sys.executable, "scripts/sync_post_statuses.py"],
                cwd=PROJECT_ROOT
            )
            if result.returncode != 0:
                print("Failed to sync post statuses.")

        elif choice == "13":
            result = subprocess.run(
                [sys.executable, "scripts/export_buffer_csv.py"],
                cwd=PROJECT_ROOT
            )
            if result.returncode != 0:
                print("Failed to export Buffer CSV.")

        elif choice == "14":
            post_id = input("Enter post ID: ").strip()
            caption_type = input("Enter type (ig, tiktok, hashtags): ").strip()
            text = input("Paste the text: ").strip()
            result = subprocess.run(
                [sys.executable, "scripts/save_caption.py", post_id, caption_type, text],
                cwd=PROJECT_ROOT
            )
            if result.returncode != 0:
                print("Failed to save caption text.")

        elif choice == "15":
            result = subprocess.run(
                [sys.executable, "scripts/view_captions.py"],
                cwd=PROJECT_ROOT
            )
            if result.returncode != 0:
                print("Failed to view captions.")

        elif choice == "16":
            post_id = input("Enter post ID: ").strip()
            agent_name = input("Enter agent name: ").strip()
            output_type = input("Enter output type (strategy, video_plan, design_brief, story_sequence, repurpose_ideas, analytics): ").strip()
            content = input("Paste the output: ").strip()
            result = subprocess.run(
                [sys.executable, "scripts/save_agent_output.py", post_id, agent_name, output_type, content],
                cwd=PROJECT_ROOT
            )
            if result.returncode != 0:
                print("Failed to save agent output.")

        elif choice == "17":
            result = subprocess.run(
                [sys.executable, "scripts/view_agent_outputs.py"],
                cwd=PROJECT_ROOT
            )
            if result.returncode != 0:
                print("Failed to view agent outputs.")

        elif choice == "18":
            post_id = input("Enter post ID: ").strip()
            result = subprocess.run(
                [sys.executable, "scripts/export_post_package.py", post_id],
                cwd=PROJECT_ROOT
            )
            if result.returncode != 0:
                print("Failed to export post package.")

        elif choice == "19":
            result = subprocess.run(
                [sys.executable, "scripts/view_post_checklist.py"],
                cwd=PROJECT_ROOT
            )
            if result.returncode != 0:
                print("Failed to view post checklist.")

        elif choice == "20":
            result = subprocess.run(
                [sys.executable, "scripts/view_ready_posts.py"],
                cwd=PROJECT_ROOT
            )
            if result.returncode != 0:
                print("Failed to view ready posts.")

        elif choice == "21":
            start_date = input("Enter the Monday date for this week (YYYY-MM-DD): ").strip()
            result = subprocess.run(
                [sys.executable, "scripts/assign_scheduled_dates.py", start_date],
                cwd=PROJECT_ROOT
            )
            if result.returncode != 0:
                print("Failed to assign scheduled dates.")

        elif choice == "22":
            result = subprocess.run(
                [sys.executable, "scripts/view_schedule.py"],
                cwd=PROJECT_ROOT
            )
            if result.returncode != 0:
                print("Failed to view schedule.")

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()