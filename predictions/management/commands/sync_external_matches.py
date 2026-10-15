from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from predictions.importers.base import ProviderError
from predictions.importers.flashlive import FlashLiveProvider
from predictions.importers.registry import get_providers, provider_for
from predictions.models import Sport
from predictions.services import import_fixtures, sync_results


class Command(BaseCommand):
    help = (
        "Import upcoming fixtures (as unpublished matches) and suggested "
        "results from the configured sports data provider. Results are only "
        "suggested: confirm them in the admin to score predictions."
    )

    def add_arguments(self, parser):
        parser.add_argument("--fixtures", action="store_true", help="Import upcoming fixtures.")
        parser.add_argument("--results", action="store_true", help="Fetch results for matches awaiting one.")
        parser.add_argument(
            "--sport",
            help="Only this sport (e.g. Football) or comma-separated list. Default: all.",
        )
        parser.add_argument(
            "--exclude-sport",
            help="Exclude this sport (or comma-separated list, e.g. Hockey).",
        )
        parser.add_argument(
            "--slot",
            choices=["06:30", "20:30"],
            help="Scheduled run slot to apply sport-level auto-sync controls (06:30 or 20:30).",
        )
        parser.add_argument("--days-ahead", type=int, default=7, help="Fixture window in days (max 7).")
        parser.add_argument(
            "--new-day-only",
            action="store_true",
            help="Fetch only the day --days-ahead from today (1 request per sport). "
            "For daily scheduled runs.",
        )
        parser.add_argument(
            "--no-odds",
            action="store_true",
            help="Do not fetch odds when importing fixtures (enabled by default).",
        )
        parser.add_argument("--dry-run", action="store_true", help="Show what would change, then roll back.")
        parser.add_argument("--list-sports", action="store_true", help="Print FlashLive's sport IDs and exit.")
        parser.add_argument(
            "--list-tournaments",
            action="store_true",
            help="Print the tournament names for --sport (default Football) on "
            "--day, for FLASHLIVE_TOURNAMENTS. 1 request.",
        )
        parser.add_argument("--day", type=int, default=0, help="Day for --list-tournaments (0 = today).")
        parser.add_argument(
            "--force",
            action="store_true",
            help="Sync even if the sport is paused in the admin (is_active=False).",
        )

    def handle(self, *args, **options):
        if options["list_sports"]:
            try:
                for sport_id, name in FlashLiveProvider().list_sports():
                    self.stdout.write(f"{sport_id}\t{name}")
            except ProviderError as exc:
                raise CommandError(str(exc)) from exc
            return

        if options["list_tournaments"]:
            sport_name = (options["sport"] or "Football").title()
            providers = get_providers()
            provider = provider_for(sport_name, providers)
            if not provider or not hasattr(provider, "list_tournaments"):
                raise CommandError(f"No configured provider with list_tournaments support for {sport_name}.")
            try:
                for name, count in provider.list_tournaments(sport_name, options["day"]):
                    plural = "es" if count != 1 else ""
                    self.stdout.write(f"{name}\t({count} match{plural})")
            except ProviderError as exc:
                raise CommandError(str(exc)) from exc
            finally:
                self._report_requests([provider])
            return

        if not (options["fixtures"] or options["results"]):
            raise CommandError("Pass --fixtures, --results, or both.")

        providers = get_providers()
        if not providers:
            raise CommandError("No provider is configured: set API_FOOTBALL_KEY or RAPIDAPI_KEY.")

        sports = Sport.objects.all()
        if options["sport"]:
            sport_names = [s.strip() for s in options["sport"].split(",") if s.strip()]
            q = Q()
            for name in sport_names:
                q |= Q(name__iexact=name)
            sports = sports.filter(q)
            if not sports:
                raise CommandError(f"Unknown sport: {options['sport']}")
        elif not options["force"]:
            sports = sports.filter(is_active=True)

        if options.get("exclude_sport"):
            exclude_names = [s.strip() for s in options["exclude_sport"].split(",") if s.strip()]
            for name in exclude_names:
                sports = sports.exclude(name__iexact=name)

        slot = options.get("slot")
        if not slot:
            if options["fixtures"]:
                slot = "20:30" if options.get("days_ahead") == 1 else "06:30"
            elif options["results"]:
                now_ist = timezone.now().astimezone(timezone.get_fixed_timezone(330))
                slot = "20:30" if now_ist.hour >= 13 else "06:30"

        failed = False
        with transaction.atomic():
            for sport in sports:
                if not sport.is_active and not options["force"]:
                    self.stdout.write(
                        self.style.WARNING(
                            f"{sport.name}: sync is paused in admin (is_active=False). "
                            "Pass --force to sync anyway."
                        )
                    )
                    continue
                provider = provider_for(sport.name, providers)
                if provider is None:
                    continue
                try:
                    if options["fixtures"]:
                        should_sync_fixtures = (
                            options["force"]
                            or bool(options["sport"])
                            or (slot == "06:30" and getattr(sport, "auto_fixture_0630", True))
                            or (slot == "20:30" and getattr(sport, "auto_fixture_2030", True))
                            or (not slot and sport.is_active)
                        )
                        if should_sync_fixtures:
                            with_odds = (
                                not options["no_odds"]
                                and (
                                    options["force"]
                                    or bool(options["sport"])
                                    or (slot == "06:30" and getattr(sport, "auto_odds_0630", True))
                                    or (slot == "20:30" and getattr(sport, "auto_odds_2030", True))
                                    or (not slot)
                                )
                            )
                            self._report_fixtures(
                                sport,
                                import_fixtures(
                                    provider,
                                    sport,
                                    days_ahead=options["days_ahead"],
                                    download_images=not options["dry_run"],
                                    new_day_only=options["new_day_only"],
                                    with_odds=with_odds,
                                    force=options["force"],
                                ),
                            )
                    if options["results"]:
                        should_sync_results = (
                            options["force"]
                            or bool(options["sport"])
                            or (slot == "06:30" and getattr(sport, "auto_results_0630", True))
                            or (slot == "20:30" and getattr(sport, "auto_results_2030", True))
                            or (not slot and sport.is_active)
                        )
                        if should_sync_results:
                            self._report_results(
                                sport, sync_results(provider, sport, force=options["force"])
                            )

                except ProviderError as exc:
                    # Keep going: one sport failing shouldn't block the rest.
                    failed = True
                    self.stderr.write(self.style.ERROR(f"{sport.name}: {exc}"))

            if options["dry_run"]:
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING("Dry run: nothing was saved."))

        self._report_requests(providers)
        if failed:
            raise CommandError("Some sports failed; see errors above.")

    def _safe_write(self, msg):
        try:
            self.stdout.write(msg)
        except UnicodeEncodeError:
            encoding = getattr(self.stdout, "encoding", None) or "ascii"
            safe = str(msg).encode(encoding, errors="replace").decode(encoding)
            self.stdout.write(safe)

    def _report_requests(self, providers):
        breakdown = [
            f"{p.name}: {getattr(p, 'requests_made', 0)}"
            for p in providers
            if getattr(p, "requests_made", 0) > 0
        ]
        total = sum(getattr(p, "requests_made", 0) for p in providers)
        if breakdown:
            self.stdout.write(f"API requests used this run: {total} ({', '.join(breakdown)})")
        else:
            self.stdout.write("API requests used this run: 0")

    def _report_fixtures(self, sport, summary):
        odds_count = summary.get("odds_filled", 0)
        odds_info = f", {odds_count} odds & points filled" if odds_count else ""
        self._safe_write(
            f"{sport.name} fixtures: {summary['created']} created, "
            f"{summary['updated']} kickoff times updated{odds_info}, "
            f"{summary['skipped']} skipped"
        )
        for name in summary["new_teams"]:
            self._safe_write(f"  new team (please review): {name}")
        for match in summary["called_off"]:
            self._safe_write(self.style.WARNING(f"  postponed/cancelled at source: {match}"))

    def _report_results(self, sport, summary):
        self._safe_write(
            f"{sport.name} results: {summary['suggested']} suggested, awaiting admin confirmation"
        )
        for match in summary["enter_by_hand"]:
            self._safe_write(
                self.style.WARNING(f"  no result from source, enter it by hand: {match}")
            )
        for match in summary["called_off"]:
            self._safe_write(self.style.WARNING(f"  postponed/cancelled at source: {match}"))
