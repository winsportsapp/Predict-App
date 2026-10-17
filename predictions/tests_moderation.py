from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from predictions.forms import RegistrationForm
from predictions.google_auth import generate_username
from predictions.moderation import (
    contains_prohibited_content,
    is_impersonating,
    normalize_text,
    validate_username,
)
from predictions.models import (
    Match,
    Prediction,
    Profile,
    ScoreAdjustment,
    Sport,
    Team,
    UsernameModerationLog,
)
from predictions.views import _all_time_profiles, _monthly_profiles


class ModerationEngineTests(TestCase):
    def test_normalize_text(self):
        self.assertEqual(normalize_text("4dm1n"), "admin")
        self.assertEqual(normalize_text("w1nsp0rts"), "winsports")
        self.assertEqual(normalize_text("A_D_M_I_N"), "admin")
        self.assertEqual(normalize_text("f.u.c.k"), "fuck")
        self.assertEqual(normalize_text("vvinsports"), "winsports")

    def test_reserved_exact_names(self):
        reserved = [
            "admin",
            "ADMIN",
            "administrator",
            "moderator",
            "mod",
            "winsports",
            "winsport",
            "winsports_support",
            "official_winsports",
            "support",
            "helpdesk",
            "staff",
            "webmaster",
            "root",
            "superuser",
        ]
        for name in reserved:
            with self.subTest(name=name):
                with self.assertRaises(ValidationError):
                    validate_username(name)

    def test_reserved_obfuscations(self):
        obfuscated = [
            "4dm1n",
            "Adm1n",
            "@dm!n",
            "a_d_m_i_n",
            "a.d.m.i.n",
            "aaddmmiinn",
            "w1nsp0rts",
            "w1nsp0rts_supp0rt",
            "0ff1c1al_w1nsp0rts",
            "m0d3r4t0r",
            "the_admin",
            "admin99",
            "winsports_official",
            "winsport_help",
        ]
        for name in obfuscated:
            with self.subTest(name=name):
                with self.assertRaises(ValidationError):
                    validate_username(name)

    def test_staff_bypass_for_official_names(self):
        # Staff can register or be renamed to official support accounts
        try:
            validate_username("winsports_support", is_staff=True)
            validate_username("official_winsports", is_staff=True)
        except ValidationError:
            self.fail("Staff should be allowed to use official reserved names.")

    def test_prohibited_obscenities_and_slurs(self):
        prohibited = [
            "fuck",
            "f.u.c.k",
            "f_u_c_k_y_o_u",
            "motherfucker",
            "bitch",
            "cunt",
            "whore",
            "nigger",
            "sh!t",
            "killall",
            "nazi",
        ]
        for name in prohibited:
            with self.subTest(name=name):
                with self.assertRaises(ValidationError):
                    validate_username(name)

    def test_false_positive_protections_for_legitimate_names(self):
        legitimate_names = [
            "Cassandra",
            "Nasser",
            "Harshit",
            "Harshit_Sharma",
            "Akshit",
            "Rishit",
            "Titus",
            "Dickson",
            "ArsenalFan",
            "ArunKumar",
            "MohammedAli",
            "JohnSmith",
            "Brad",
            "Tommy",
            "Winner2026",
            "SportPlayer",
        ]
        for name in legitimate_names:
            with self.subTest(name=name):
                try:
                    validate_username(name)
                except ValidationError as e:
                    self.fail(f"Legitimate name '{name}' was falsely blocked: {e}")

    def test_username_length_boundaries(self):
        with self.assertRaises(ValidationError):
            validate_username("ab")  # Too short (<3)
        with self.assertRaises(ValidationError):
            validate_username("a" * 31)  # Too long (>30)
        validate_username("abc")  # Min valid length


class RegistrationFormModerationTests(TestCase):
    def test_registration_blocks_reserved_username(self):
        data = {
            "username": "admin",
            "email": "player@example.com",
            "password1": "StrongPass123!@",
            "password2": "StrongPass123!@",
            "country": "India",
            "state": "Maharashtra",
            "age": 25,
            "accept_terms": True,
        }
        form = RegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_registration_blocks_profane_username(self):
        data = {
            "username": "f.u.c.k",
            "email": "player@example.com",
            "password1": "StrongPass123!@",
            "password2": "StrongPass123!@",
            "country": "India",
            "state": "Maharashtra",
            "age": 25,
            "accept_terms": True,
        }
        form = RegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_registration_blocks_case_insensitive_duplicate(self):
        User.objects.create_user(username="UniquePlayer", email="orig@example.com", password="pass")
        data = {
            "username": "uniqueplayer",
            "email": "new@example.com",
            "password1": "StrongPass123!@",
            "password2": "StrongPass123!@",
            "country": "India",
            "state": "Maharashtra",
            "age": 25,
            "accept_terms": True,
        }
        form = RegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("already exists", form.errors["username"][0])

    def test_registration_allows_valid_user(self):
        data = {
            "username": "Cassandra99",
            "email": "cassandra@example.com",
            "password1": "StrongPass123!@",
            "password2": "StrongPass123!@",
            "country": "India",
            "state": "Maharashtra",
            "age": 25,
            "accept_terms": True,
        }
        form = RegistrationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)


class GoogleAuthUsernameGenerationTests(TestCase):
    def test_google_clean_name(self):
        name = "Arun Kumar"
        uname = generate_username(name)
        self.assertEqual(uname, "ArunKumar")

    def test_google_reserved_name_falls_back_to_player(self):
        uname = generate_username("Winsports Admin")
        self.assertTrue(uname.startswith("Player"))

    def test_google_profane_name_falls_back_to_player(self):
        uname = generate_username("Fuck You")
        self.assertTrue(uname.startswith("Player"))


class AdminModerationAndAuditLogTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="adminmoderator",
            email="adminmod@example.com",
            password="adminpass123",
        )
        self.regular_user = User.objects.create_user(
            username="targetplayer",
            email="player@example.com",
            password="playerpass123",
        )
        self.profile = self.regular_user.profile
        self.profile.points = 50
        self.profile.save()
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_admin_flag_and_clear_flag_action(self):
        # Flag user
        change_url = reverse("admin:predictions_profile_changelist")
        response = self.client.post(
            change_url,
            {"action": "flag_selected_users", "_selected_action": [self.profile.pk]},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.is_flagged_for_review)

        log = UsernameModerationLog.objects.filter(
            user=self.regular_user, action=UsernameModerationLog.Action.FLAG
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.moderator, self.admin_user)

        # Clear flag
        response = self.client.post(
            change_url,
            {"action": "clear_flag_selected_users", "_selected_action": [self.profile.pk]},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.is_flagged_for_review)

        clear_log = UsernameModerationLog.objects.filter(
            user=self.regular_user, action=UsernameModerationLog.Action.CLEAR_FLAG
        ).first()
        self.assertIsNotNone(clear_log)

    def test_admin_suspend_and_reactivate_action(self):
        change_url = reverse("admin:predictions_profile_changelist")
        # Suspend
        self.client.post(
            change_url,
            {"action": "suspend_selected_users", "_selected_action": [self.profile.pk]},
            follow=True,
        )
        self.regular_user.refresh_from_db()
        self.assertFalse(self.regular_user.is_active)

        suspend_log = UsernameModerationLog.objects.filter(
            user=self.regular_user, action=UsernameModerationLog.Action.SUSPEND
        ).first()
        self.assertIsNotNone(suspend_log)

        # Reactivate
        self.client.post(
            change_url,
            {"action": "reactivate_selected_users", "_selected_action": [self.profile.pk]},
            follow=True,
        )
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.is_active)

    def test_admin_rename_user_flow(self):
        rename_url = reverse("admin:predictions_profile_rename", args=[self.profile.pk])
        # GET form
        response = self.client.get(rename_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "targetplayer")

        # POST invalid username
        bad_response = self.client.post(
            rename_url,
            {"new_username": "admin", "reason": "Testing reserved rejection"},
        )
        self.assertEqual(bad_response.status_code, 200)
        self.assertContains(bad_response, "reserved")

        # POST valid new username
        good_response = self.client.post(
            rename_url,
            {"new_username": "PolitePlayer", "reason": "Renamed for testing"},
            follow=True,
        )
        self.assertEqual(good_response.status_code, 200)

        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.username, "PolitePlayer")
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.points, 50)  # Points preserved!

        rename_log = UsernameModerationLog.objects.filter(
            user=self.regular_user, action=UsernameModerationLog.Action.RENAME
        ).first()
        self.assertIsNotNone(rename_log)
        self.assertEqual(rename_log.old_username, "targetplayer")
        self.assertEqual(rename_log.new_username, "PolitePlayer")
        self.assertEqual(rename_log.moderator, self.admin_user)
        self.assertEqual(rename_log.reason, "Renamed for testing")


class LeaderboardModerationIntegrityTests(TestCase):
    def setUp(self):
        self.active_user = User.objects.create_user(
            username="ActiveLeader", email="active@example.com", password="pass"
        )
        self.active_profile = self.active_user.profile
        self.active_profile.points = 100
        self.active_profile.save()

        self.suspended_user = User.objects.create_user(
            username="SuspendedPlayer", email="suspended@example.com", password="pass", is_active=False
        )
        self.suspended_profile = self.suspended_user.profile
        self.suspended_profile.points = 90
        self.suspended_profile.save()

    def test_leaderboard_excludes_suspended_users(self):
        profiles = _all_time_profiles()
        usernames = [p.user.username for p in profiles]
        self.assertIn("ActiveLeader", usernames)
        self.assertNotIn("SuspendedPlayer", usernames)

    def test_renaming_user_preserves_leaderboard_points_and_displays_new_name(self):
        self.active_user.username = "BrandNewLeaderName"
        self.active_user.save()

        profiles = _all_time_profiles()
        usernames = [p.user.username for p in profiles]
        self.assertIn("BrandNewLeaderName", usernames)
        self.assertNotIn("ActiveLeader", usernames)

        renamed_profile = next(p for p in profiles if p.user.username == "BrandNewLeaderName")
        self.assertEqual(renamed_profile.points, 100)
