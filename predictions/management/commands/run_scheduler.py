"""Continuous background scheduler daemon for sports sync.

Schedules and executes:
- 06:30 IST: Morning Results sync (sync_external_matches --results --slot 06:30)
- 06:35 IST: Morning Fixtures & Odds sync (sync_external_matches --fixtures --new-day-only --slot 06:30)
- 20:30 IST: Evening Results sync (sync_external_matches --results --slot 20:30)
- 20:35 IST: Evening Fixtures & Odds sync (sync_external_matches --fixtures --new-day-only --slot 20:30)
"""

import logging
import time
from datetime import datetime, timedelta, timezone as dt_timezone
from django.core.management import call_command
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)
IST = dt_timezone(timedelta(hours=5, minutes=30))

SCHEDULE_SLOTS = [
    {"hour": 6, "minute": 30, "action": "results", "slot": "06:30", "name": "Morning Results"},
    {"hour": 6, "minute": 35, "action": "fixtures", "slot": "06:30", "name": "Morning Fixtures & Odds"},
    {"hour": 20, "minute": 30, "action": "results", "slot": "20:30", "name": "Evening Results"},
    {"hour": 20, "minute": 35, "action": "fixtures", "slot": "20:30", "name": "Evening Fixtures & Odds"},
]


def get_next_slot(now_ist=None):
    if now_ist is None:
        now_ist = datetime.now(IST)

    candidates = []
    for item in SCHEDULE_SLOTS:
        target = now_ist.replace(hour=item["hour"], minute=item["minute"], second=0, microsecond=0)
        if target <= now_ist:
            target += timedelta(days=1)
        candidates.append((target, item))

    candidates.sort(key=lambda x: x[0])
    return candidates[0]


class Command(BaseCommand):
    help = "Run the automated sports match sync schedule daemon (06:30/06:35 & 20:30/20:35 IST)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--once",
            action="store_true",
            help="Run the upcoming scheduled task immediately once and exit.",
        )
        parser.add_argument(
            "--slot",
            choices=["06:30", "20:30"],
            help="Force a specific slot when using --once.",
        )

    def handle(self, *args, **options):
        if options["once"]:
            now_ist = datetime.now(IST)
            target_dt, task = get_next_slot(now_ist)
            slot = options.get("slot") or task["slot"]
            self.stdout.write(
                self.style.SUCCESS(
                    f"Running on-demand sync for slot {slot} (Current IST: {now_ist.strftime('%Y-%m-%d %I:%M:%S %p IST')})..."
                )
            )
            self._execute_task(task["action"], slot)
            return

        self.stdout.write(
            self.style.SUCCESS(
                "Starting PredictApp Background Scheduler Daemon...\n"
                "Schedule:\n"
                "  • 06:30 IST: Morning Results\n"
                "  • 06:35 IST: Morning Fixtures & Odds\n"
                "  • 20:30 IST: Evening Results\n"
                "  • 20:35 IST: Evening Fixtures & Odds\n"
                "Press Ctrl+C to terminate."
            )
        )

        last_executed = None
        while True:
            try:
                now_ist = datetime.now(IST)
                target_dt, task = get_next_slot(now_ist)
                wait_seconds = (target_dt - now_ist).total_seconds()

                self.stdout.write(
                    f"[{now_ist.strftime('%I:%M:%S %p IST')}] Next run: {task['name']} at "
                    f"{target_dt.strftime('%b %d %I:%M %p IST')} (in {int(wait_seconds // 60)}m {int(wait_seconds % 60)}s)"
                )

                # Sleep in short increments for responsive interrupt handling
                while wait_seconds > 0:
                    sleep_chunk = min(wait_seconds, 15)
                    time.sleep(sleep_chunk)
                    now_ist = datetime.now(IST)
                    wait_seconds = (target_dt - now_ist).total_seconds()

                task_key = (target_dt.date(), task["hour"], task["minute"])
                if last_executed != task_key:
                    last_executed = task_key
                    self.stdout.write(
                        self.style.WARNING(
                            f"\n[{now_ist.strftime('%I:%M:%S %p IST')}] Executing scheduled: {task['name']}..."
                        )
                    )
                    self._execute_task(task["action"], task["slot"])

            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("\nScheduler daemon stopped by user."))
                break
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"Scheduler daemon error: {exc}"))
                time.sleep(10)

    def _execute_task(self, action, slot):
        try:
            if action == "results":
                call_command("sync_external_matches", results=True, slot=slot)
            elif action == "fixtures":
                call_command("sync_external_matches", fixtures=True, new_day_only=True, slot=slot)
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"Task execution failed: {exc}"))
