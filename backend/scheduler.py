from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


def scheduled_crawl():
    from database import SessionLocal
    from crawler import run_all_crawlers

    print(f"[Scheduler] Starting crawl at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    db = SessionLocal()
    try:
        count = run_all_crawlers(db)
        print(f"[Scheduler] Done — {count} new articles saved")
    except Exception as e:
        print(f"[Scheduler] Error: {e}")
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")

    # Daily crawl at 07:00 UTC
    scheduler.add_job(
        scheduled_crawl,
        CronTrigger(hour=7, minute=0),
        id="daily_crawl",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    # Also run immediately on startup (as a background job)
    scheduler.add_job(
        scheduled_crawl,
        "date",
        run_date=datetime.now(),
        id="startup_crawl",
    )

    scheduler.start()
    print("[Scheduler] Started — daily crawl set for 07:00 UTC")
    return scheduler
