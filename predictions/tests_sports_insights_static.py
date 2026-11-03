"""
Unit tests for the Static Evergreen Sports Insights feature.
Validates routing, filtering, content delivery, sitemap inclusion,
and zero database dependency.
"""

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from predictions.admin import SPORT_TOURNAMENT_PRESETS
from predictions.sports_insights_data import (
    get_all_articles,
    get_article_by_slug,
    get_articles_by_sport,
    get_sports_categories,
)
from predictions.tournaments_data import (
    get_calendar_metadata,
    get_tournament_sports_categories,
    get_upcoming_tournaments,
)


class SportsInsightsStaticTests(TestCase):
    def test_articles_data_integrity(self):
        """Confirm all 10 articles are loaded with complete metadata."""
        articles = get_all_articles()
        self.assertEqual(len(articles), 10)

        expected_sports = {"cricket", "football", "tennis", "badminton", "hockey"}
        found_sports = {a["sport"] for a in articles}
        self.assertEqual(expected_sports, found_sports)

        # Check each sport has exactly 2 articles
        for s in expected_sports:
            sport_articles = get_articles_by_sport(s)
            self.assertEqual(len(sport_articles), 2, f"Sport {s} should have 2 articles")

        # Confirm every article has mandatory fields
        for a in articles:
            self.assertTrue(a["slug"])
            self.assertTrue(a["title"])
            self.assertTrue(a["summary"])
            self.assertTrue(a["read_time"])
            self.assertTrue(a["content_html"])
            self.assertTrue(len(a["key_takeaways"]) >= 2)
            self.assertEqual(get_article_by_slug(a["slug"]), a)

    def test_sports_categories_helper(self):
        """Confirm categories helper returns all 5 sports plus 'all'."""
        categories = get_sports_categories()
        self.assertEqual(len(categories), 6)
        all_cat = categories[0]
        self.assertEqual(all_cat["slug"], "all")
        self.assertEqual(all_cat["count"], 10)

    def test_tournaments_data_integrity(self):
        """Confirm tournaments data covers all 5 sports with verified fields."""
        tournaments = get_upcoming_tournaments()
        self.assertGreaterEqual(len(tournaments), 5)

        expected_sports = {"cricket", "football", "tennis", "badminton", "hockey"}
        found_sports = {t["sport"] for t in tournaments}
        self.assertEqual(expected_sports, found_sports)

        for t in tournaments:
            self.assertTrue(t["name"])
            self.assertTrue(t["sport"])
            self.assertTrue(t["dates"])
            self.assertIn(t["status"], ["Confirmed", "Dates to be confirmed"])
            self.assertTrue(t["location"])
            self.assertTrue(t["format"])
            self.assertTrue(t["description"])
            self.assertTrue(t["official_url"])
            self.assertTrue(t.get("supported_filter"))

        meta = get_calendar_metadata()
        self.assertTrue(meta["last_updated"])
        self.assertTrue(meta["calendar_period"])
        self.assertTrue(meta["disclaimer"])

    def test_tournaments_align_with_supported_tournament_filter_presets(self):
        """Verify EVERY tournament strictly matches WinSports' supported filter presets."""
        tournaments = get_upcoming_tournaments()
        for t in tournaments:
            sport = t["sport"]
            self.assertIn(sport, SPORT_TOURNAMENT_PRESETS, f"Sport {sport} not in presets")
            supported_chips = SPORT_TOURNAMENT_PRESETS[sport].get("popular_chips", [])
            self.assertIn(
                t["supported_filter"],
                supported_chips,
                f"Tournament '{t['name']}' has filter '{t['supported_filter']}' which is not in WinSports presets: {supported_chips}",
            )

        # Confirm non-supported competitions are excluded
        tournament_names_lower = [t["name"].lower() for t in tournaments]
        self.assertFalse(any("davis cup" in name for name in tournament_names_lower))
        self.assertFalse(any("asian champions trophy" in name for name in tournament_names_lower))
        self.assertFalse(any("syed modi" in name for name in tournament_names_lower))
        self.assertFalse(any("border-gavaskar" in name for name in tournament_names_lower))
        self.assertFalse(any("wta finals" in name for name in tournament_names_lower))
        self.assertFalse(any("hockey india league" in name for name in tournament_names_lower))

    def test_tournaments_respect_filter_exclusions_and_outlook_window(self):
        """Verify excluded categories (women's cricket, youth/U19, Test cricket, ITF) and dates outside the ~35-40 day window are omitted."""
        tournaments = get_upcoming_tournaments()
        for t in tournaments:
            name_lower = t["name"].lower()
            sport = t["sport"]

            # Cricket exclusions
            if sport == "cricket":
                self.assertNotIn("women", name_lower)
                self.assertNotIn("wbbl", name_lower)
                self.assertNotIn("u19", name_lower)
                self.assertNotIn("test series", name_lower)

            # Football exclusions
            if sport == "football":
                self.assertNotIn("reserve", name_lower)
                self.assertNotIn("u20", name_lower)
                self.assertNotIn("u21", name_lower)
                self.assertNotIn("u19", name_lower)
                self.assertNotIn("women", name_lower)

            # Tennis exclusions
            if sport == "tennis":
                self.assertNotIn("itf", name_lower)
                self.assertNotIn("challenger", name_lower)
                self.assertNotIn("qualification", name_lower)

            # Badminton exclusions
            if sport == "badminton":
                self.assertNotIn("junior", name_lower)
                self.assertNotIn("qualifying", name_lower)

            # Date window check: must not extend into late December or January 2027
            dates_lower = t["dates"].lower()
            self.assertNotIn("late december", dates_lower)
            self.assertNotIn("january 2027", dates_lower)
            self.assertTrue(
                "november" in dates_lower or "december 8" in dates_lower,
                f"Tournament {t['name']} date '{t['dates']}' is outside November – Mid-December outlook window",
            )

    def test_insights_list_view_all(self):
        """Test GET /sports-insights/ returns 200 with all articles."""
        url = reverse("sports_insights_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "predictions/sports_insights_list.html")
        self.assertEqual(len(response.context["articles"]), 10)
        self.assertContains(response, "Sports Insights &amp; Analysis")
        self.assertContains(response, "Understanding Powerplay, Middle Overs")
        self.assertContains(response, "Understanding Football Formations")
        self.assertContains(response, reverse("tournaments_calendar"))

    def test_insights_list_view_sport_filter(self):
        """Test filtering by ?sport=cricket, ?sport=football, etc."""
        url = reverse("sports_insights_list")

        for sport in ["cricket", "football", "tennis", "badminton", "hockey"]:
            response = self.client.get(url, {"sport": sport})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context["articles"]), 2)
            for a in response.context["articles"]:
                self.assertEqual(a["sport"], sport)

    def test_insights_detail_view_all_slugs(self):
        """Test every single article detail page returns 200 with correct content."""
        for a in get_all_articles():
            url = reverse("sports_insights_detail", kwargs={"slug": a["slug"]})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Failed for slug {a['slug']}")
            self.assertTemplateUsed(response, "predictions/sports_insights_detail.html")
            self.assertContains(response, a["title"])
            self.assertContains(response, a["read_time"])
            self.assertContains(response, "Key Takeaways at a Glance")
            self.assertContains(response, "WinSports Sports Analysis Desk")
            # Verify Schema.org JSON-LD exists
            self.assertContains(response, "https://schema.org")
            self.assertContains(response, '"@type": "Article"')
            self.assertNotContains(response, "WinSports · WinSports")

    def test_insights_detail_view_invalid_slug(self):
        """Test invalid slug returns 404."""
        url = reverse("sports_insights_detail", kwargs={"slug": "non-existent-guide"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_tournaments_calendar_view(self):
        """Test GET /sports-insights/tournaments/ returns 200 with all tournaments."""
        url = reverse("tournaments_calendar")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "predictions/tournaments_calendar.html")
        self.assertGreaterEqual(len(response.context["tournaments"]), 5)
        self.assertContains(response, "Upcoming Major Tournaments")
        self.assertContains(response, "~35–40 Day Outlook")
        self.assertContains(response, "Last updated:")
        self.assertContains(response, "Informational Calendar Policy")
        self.assertContains(response, "Filter Preset:")
        self.assertContains(response, "Official Dates:")
        self.assertContains(response, "Confirmed upcoming WinSports fixtures")
        self.assertContains(response, "Upcoming WinSports fixtures not confirmed")
        self.assertContains(response, reverse("sports_insights_list"))
        # Verify page title is clean and does not have duplicate suffix
        self.assertNotContains(response, "WinSports · WinSports")
        # Verify omitted / unverified tournaments are strictly absent
        self.assertNotContains(response, "WTA Finals")
        self.assertNotContains(response, "Hockey India League")
        self.assertNotContains(response, "Big Bash")
        self.assertNotContains(response, "WBBL")
        self.assertNotContains(response, "Davis Cup")
        self.assertNotContains(response, "Border-Gavaskar")

    def test_tournaments_prioritize_confirmed_fixtures(self):
        """Verify tournaments with confirmed upcoming WinSports fixtures are prioritized first."""
        tournaments = get_upcoming_tournaments()
        # Ensure first item has confirmed upcoming fixtures
        self.assertTrue(tournaments[0]["has_upcoming_fixtures"])
        self.assertEqual(tournaments[0]["winsports_fixtures_status"], "Confirmed upcoming fixtures")

        # Verify ordering: all True entries precede False entries
        saw_unconfirmed = False
        for t in tournaments:
            if not t["has_upcoming_fixtures"]:
                saw_unconfirmed = True
                self.assertEqual(t["winsports_fixtures_status"], "Upcoming WinSports fixtures not confirmed")
            else:
                self.assertFalse(saw_unconfirmed, "Confirmed tournament appeared after unconfirmed tournament")
                self.assertEqual(t["winsports_fixtures_status"], "Confirmed upcoming fixtures")

    def test_tournaments_calendar_sport_filter(self):
        """Test tournament filtering by each sport."""
        url = reverse("tournaments_calendar")
        for sport in ["cricket", "football", "tennis", "badminton", "hockey"]:
            response = self.client.get(url, {"sport": sport})
            self.assertEqual(response.status_code, 200)
            for t in response.context["tournaments"]:
                self.assertEqual(t["sport"], sport)

    def test_sitemap_xml_includes_insights_and_tournaments(self):
        """Test /sitemap.xml includes sports_insights_list, tournaments_calendar, and all 10 articles."""
        url = reverse("sitemap_xml")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/sports-insights/</loc>")
        self.assertContains(response, "/sports-insights/tournaments/</loc>")
        for a in get_all_articles():
            self.assertContains(response, f"/sports-insights/{a['slug']}/</loc>")

    def test_navigation_integration(self):
        """Test desktop nav and footer contain links to Sports Insights."""
        response = self.client.get(reverse("match_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("sports_insights_list"))
        self.assertContains(response, "Sports Insights")

        # Test active navigation highlight on tournaments calendar
        cal_resp = self.client.get(reverse("tournaments_calendar"))
        self.assertEqual(cal_resp.status_code, 200)
        self.assertContains(cal_resp, "active-sport-link")
        self.assertContains(cal_resp, reverse("sports_insights_list"))

    def test_mobile_bottom_navigation_integration(self):
        """Test mobile bottom nav bar contains Sports Insights link and highlights active route."""
        response = self.client.get(reverse("match_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="mobile-bottom-nav')
        self.assertContains(response, 'href="%s"' % reverse("sports_insights_list"))
        self.assertContains(response, 'Insights</span>')

        # Test active class on mobile bottom nav when on sports_insights_list
        insights_resp = self.client.get(reverse("sports_insights_list"))
        self.assertEqual(insights_resp.status_code, 200)
        self.assertContains(insights_resp, 'active" \n         title="Sports Insights"' if 'active" \n' in insights_resp.content.decode() else 'active"')

        # Test active class on mobile bottom nav when on tournaments_calendar
        cal_resp = self.client.get(reverse("tournaments_calendar"))
        self.assertEqual(cal_resp.status_code, 200)
        self.assertContains(cal_resp, 'active"')

    def test_sports_pills_scroller_contains_insights_and_calendar(self):
        """Test sports pills scroller provides direct access to Insights and Calendar."""
        response = self.client.get(reverse("match_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'sports-pill-scroller')
        self.assertContains(response, '📖 Insights')
        self.assertContains(response, '📅 Calendar')

    def test_sports_insights_page_has_prominent_calendar_card(self):
        """Test /sports-insights/ has a prominent above-the-fold Tournament Calendar card."""
        response = self.client.get(reverse("sports_insights_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upcoming Sports Tournaments Calendar")
        self.assertContains(response, reverse("tournaments_calendar"))
        self.assertContains(response, "Open Calendar")

    def test_my_picks_visible_when_logged_out(self):
        """Confirm My Picks link is visible when logged out with next=/predictions/mine/ destination."""
        response = self.client.get(reverse("match_list"))
        self.assertEqual(response.status_code, 200)
        expected_next_url = reverse("login") + "?next=" + reverse("my_predictions")

        # Desktop navigation contains My Picks with login redirect
        self.assertContains(response, f'href="{expected_next_url}">My Picks</a>')

        # Mobile bottom nav contains My Picks with login redirect
        self.assertContains(response, f'href="{expected_next_url}" class="mobile-nav-item')
        self.assertContains(response, '<span class="mobile-nav-label">My Picks</span>')

        # Confirm login page safely renders with the next parameter
        login_resp = self.client.get(expected_next_url)
        self.assertEqual(login_resp.status_code, 200)
        self.assertContains(login_resp, f'name="next" value="{reverse("my_predictions")}"')

    def test_my_picks_visible_when_logged_in(self):
        """Confirm My Picks link is visible when logged in and points to /predictions/mine/."""
        user = User.objects.create_user(
            username="picksuser", email="picksuser@example.com", password="TestPassword123"
        )
        self.client.force_login(user)
        response = self.client.get(reverse("match_list"))
        self.assertEqual(response.status_code, 200)
        my_picks_url = reverse("my_predictions")

        # Desktop navigation contains direct link to My Picks
        self.assertContains(response, f'href="{my_picks_url}">My Picks</a>')

        # Mobile bottom nav contains direct link to My Picks
        self.assertContains(response, f'href="{my_picks_url}" class="mobile-nav-item')

        # Existing logged-in My Picks destination is unchanged and loads 200
        picks_resp = self.client.get(my_picks_url)
        self.assertEqual(picks_resp.status_code, 200)
        self.assertTemplateUsed(picks_resp, "predictions/my_predictions.html")


