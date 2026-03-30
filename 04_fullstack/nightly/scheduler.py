import schedule
import time
import threading


def run_nightly_job():
    """Execute nightly adaptation job"""
    print("Running nightly adaptation...")

    try:
        from .adapter import nightly_adapter

        result = nightly_adapter.analyze_and_update()
        print(f"Nightly adaptation complete: {result}")
    except Exception as e:
        print(f"Nightly adaptation failed: {e}")


def start_scheduler():
    """Start the scheduler in background thread"""

    schedule.every().day.at("02:00").do(run_nightly_job)

    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(60)

    thread = threading.Thread(target=run_schedule, daemon=True)
    thread.start()

    print("Scheduler started - nightly job at 2:00 AM")


if __name__ == "__main__":
    run_nightly_job()
