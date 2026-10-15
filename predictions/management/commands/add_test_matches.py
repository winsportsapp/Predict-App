from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from predictions.models import Match, Sport, Team


class Command(BaseCommand):
    help = "Adds open test matches for testing the prediction UI, scrolling, and sticky menus."

    def handle(self, *args, **options):
        now = timezone.now()

        # Define test fixtures across sports
        fixtures = [
            # Football (6 matches for rich scrolling test)
            {
                "sport": "Football",
                "event": "Premier League",
                "team_a": "AC Milan",
                "team_b": "AZ Alkmaar",
                "hours_offset": 2,
                "team_a_win": 12,
                "team_a_lose": -5,
                "team_b_win": 15,
                "team_b_lose": -6,
                "draw_win": 10,
                "draw_lose": -4,
            },
            {
                "sport": "Football",
                "event": "Premier League",
                "team_a": "1899 Hoffenheim",
                "team_b": "Aarhus",
                "hours_offset": 4,
                "team_a_win": 10,
                "team_a_lose": -4,
                "team_b_win": 14,
                "team_b_lose": -5,
                "draw_win": 11,
                "draw_lose": -4,
            },
            {
                "sport": "Football",
                "event": "Champions League",
                "team_a": "AL Nasr SC",
                "team_b": "22 de Julio",
                "hours_offset": 6,
                "team_a_win": 11,
                "team_a_lose": -5,
                "team_b_win": 16,
                "team_b_lose": -7,
                "draw_win": 12,
                "draw_lose": -5,
            },
            {
                "sport": "Football",
                "event": "Champions League",
                "team_a": "AC Milan",
                "team_b": "1899 Hoffenheim",
                "hours_offset": 24,
                "team_a_win": 13,
                "team_a_lose": -6,
                "team_b_win": 13,
                "team_b_lose": -6,
                "draw_win": 10,
                "draw_lose": -4,
            },
            {
                "sport": "Football",
                "event": "Europa League",
                "team_a": "AZ Alkmaar",
                "team_b": "Aarhus",
                "hours_offset": 27,
                "team_a_win": 10,
                "team_a_lose": -4,
                "team_b_win": 15,
                "team_b_lose": -6,
                "draw_win": 11,
                "draw_lose": -4,
            },
            {
                "sport": "Football",
                "event": "Club Friendly",
                "team_a": "22 de Julio",
                "team_b": "AL Nasr SC",
                "hours_offset": 30,
                "team_a_win": 14,
                "team_a_lose": -5,
                "team_b_win": 12,
                "team_b_lose": -5,
                "draw_win": 10,
                "draw_lose": -4,
            },
            # Cricket
            {
                "sport": "Cricket",
                "event": "T20 International Cup",
                "team_a": "India",
                "team_b": "Australia",
                "hours_offset": 3,
                "team_a_win": 10,
                "team_a_lose": -5,
                "team_b_win": 12,
                "team_b_lose": -5,
                "draw_win": 25,
                "draw_lose": -10,
            },
            {
                "sport": "Cricket",
                "event": "ODI Series",
                "team_a": "England",
                "team_b": "New Zealand",
                "hours_offset": 8,
                "team_a_win": 11,
                "team_a_lose": -5,
                "team_b_win": 11,
                "team_b_lose": -5,
                "draw_win": 30,
                "draw_lose": -10,
            },
            {
                "sport": "Cricket",
                "event": "Asia Championship",
                "team_a": "India",
                "team_b": "Pakistan",
                "hours_offset": 26,
                "team_a_win": 10,
                "team_a_lose": -5,
                "team_b_win": 13,
                "team_b_lose": -6,
                "draw_win": 25,
                "draw_lose": -10,
            },
            # Tennis
            {
                "sport": "Tennis",
                "event": "ATP Masters 1000",
                "team_a": "Carlos Alcaraz",
                "team_b": "Jannik Sinner",
                "hours_offset": 5,
                "team_a_win": 10,
                "team_a_lose": -5,
                "team_b_win": 11,
                "team_b_lose": -5,
            },
            {
                "sport": "Tennis",
                "event": "Grand Slam",
                "team_a": "Djokovic",
                "team_b": "Daniil Medvedev",
                "hours_offset": 25,
                "team_a_win": 10,
                "team_a_lose": -5,
                "team_b_win": 12,
                "team_b_lose": -6,
            },
            # Badminton
            {
                "sport": "Badminton",
                "event": "All England Open",
                "team_a": "Lakshya Sen",
                "team_b": "Viktor Axelsen",
                "hours_offset": 7,
                "team_a_win": 15,
                "team_a_lose": -6,
                "team_b_win": 10,
                "team_b_lose": -5,
            },
            {
                "sport": "Badminton",
                "event": "World Tour Finals",
                "team_a": "Shi Yuqi",
                "team_b": "Anders Antonsen",
                "hours_offset": 28,
                "team_a_win": 11,
                "team_a_lose": -5,
                "team_b_win": 11,
                "team_b_lose": -5,
            },
            # Hockey
            {
                "sport": "Hockey",
                "event": "FIH Pro League",
                "team_a": "India",
                "team_b": "Germany",
                "hours_offset": 9,
                "team_a_win": 11,
                "team_a_lose": -5,
                "team_b_win": 12,
                "team_b_lose": -5,
                "draw_win": 12,
                "draw_lose": -5,
            },
            {
                "sport": "Hockey",
                "event": "World Cup",
                "team_a": "Belgium",
                "team_b": "Netherlands",
                "hours_offset": 31,
                "team_a_win": 11,
                "team_a_lose": -5,
                "team_b_win": 11,
                "team_b_lose": -5,
                "draw_win": 10,
                "draw_lose": -4,
            },
        ]

        created_count = 0
        for f in fixtures:
            sport = Sport.objects.get(name=f["sport"])
            team_a, _ = Team.objects.get_or_create(name=f["team_a"], sport=sport)
            team_b, _ = Team.objects.get_or_create(name=f["team_b"], sport=sport)

            start = now + timedelta(hours=f["hours_offset"])
            deadline = start

            match, created = Match.objects.update_or_create(
                sport=sport,
                team_a=team_a,
                team_b=team_b,
                event_name=f["event"],
                defaults={
                    "start_time": start,
                    "prediction_deadline": deadline,
                    "status": Match.Status.SCHEDULED,
                    "is_published": True,
                    "winner": None,
                    "is_draw": False,
                    "is_scored": False,
                    "team_a_win_points": f.get("team_a_win", 10),
                    "team_a_lose_points": f.get("team_a_lose", -5),
                    "team_b_win_points": f.get("team_b_win", 10),
                    "team_b_lose_points": f.get("team_b_lose", -5),
                    "draw_win_points": f.get("draw_win", 10),
                    "draw_lose_points": f.get("draw_lose", -5),
                },
            )
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"[{f['sport']}] {match.team_a} vs {match.team_b} ({match.event_name}) - Deadline: {match.prediction_deadline.strftime('%Y-%m-%d %H:%M')}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f"\nSuccessfully added/updated {created_count} test matches!")
        )
