"""Username moderation and validation for Winsports.cc.

Enforces rules to prevent:
1. Impersonation of administrators, moderators, Winsports staff, or support.
2. Abusive, obscene, discriminatory, sexually explicit, or threatening usernames.
3. Evasion via leetspeak substitutions (e.g. 4dm1n, w1nsp0rts), punctuation, spaces, or repeated letters.
4. False-positive rejections of legitimate names (e.g. Cassandra, Harshit, Titus, Dickson).
"""

import re
from django.core.exceptions import ValidationError

# Character mappings for leetspeak and common substitution bypasses
LEET_MAP = {
    "0": "o",
    "1": "i",
    "!": "i",
    "|": "i",
    "3": "e",
    "4": "a",
    "@": "a",
    "5": "s",
    "$": "s",
    "7": "t",
    "+": "t",
    "8": "b",
    "9": "g",
    "v": "u",
}

# Reserved names and staff/support keywords (exact or root matches)
RESERVED_EXACT = {
    "admin",
    "administrator",
    "moderator",
    "mod",
    "webmaster",
    "root",
    "superuser",
    "support",
    "helpdesk",
    "staff",
    "official",
    "winsports",
    "winsport",
    "winsports_support",
    "official_winsports",
    "winsports_official",
    "winsports_admin",
    "winsports_mod",
    "owner",
}

# Unambiguous severe obscenities, slurs, threats, and explicit terms.
# If these appear anywhere in the normalized text (unless explicitly whitelisted), they are blocked.
UNAMBIGUOUS_PROHIBITED = {
    # Hate speech and slurs
    "nigger",
    "nigga",
    "kike",
    "spic",
    "chink",
    "faggot",
    "dyke",
    "retard",
    # Severe profanities and sexual terms
    "fuck",
    "fucker",
    "fucking",
    "motherfucker",
    "cunt",
    "twat",
    "pussy",
    "bitch",
    "whore",
    "slut",
    "blowjob",
    "handjob",
    "cumshot",
    "jerkoff",
    "deepthroat",
    "pedophile",
    "paedophile",
    # Extreme violence and hate
    "killall",
    "nazi",
    "hitler",
    "holocaust",
    "jihadist",
    "terrorist",
}

# Words that are offensive when used standalone or as separated tokens,
# but can naturally occur inside legitimate names or words (Scunthorpe problem).
# E.g.: "ass" in "Cassandra", "tit" in "Titus", "dick" in "Dickson", "anal" in "Arsenal",
# "shit" in "Harshit" or "Akshit".
TOKEN_PROHIBITED = {
    "ass",
    "asshole",
    "tit",
    "tits",
    "dick",
    "cock",
    "penis",
    "vagina",
    "dildo",
    "anus",
    "anal",
    "sex",
    "sexy",
    "porn",
    "porno",
    "bastard",
    "rape",
    "rapist",
    "murder",
    "kill",
    "die",
    "shit",
    "shitty",
    "crap",
}

# Known legitimate names / words that contain substrings of prohibited words
SAFE_SUBSTRING_ALLOWLIST = {
    "cassandra",
    "nasser",
    "harshit",
    "akshit",
    "rishit",
    "dikshit",
    "rakshit",
    "titus",
    "titan",
    "dickson",
    "dickens",
    "arsenal",
    "canal",
    "classic",
    "asset",
    "pass",
    "passenger",
    "babcock",
    "hitchcock",
    "peacock",
    "middlesex",
    "essex",
    "sussex",
    "skill",
    "skilled",
    "diesel",
    "grape",
    "draper",
    "shoes",
    "phoenix",
    "shell",
    "michelle",
    "hello",
    "tommy",
    "vladimir",
    "arun",
    "arunkumar",
    "mohammed",
    "mohammedali",
}


def normalize_text(text: str) -> str:
    """Normalize text by lowercasing, replacing leetspeak characters, and
    stripping punctuation and non-alphanumeric separators."""
    if not text:
        return ""
    text = text.lower()
    # Replace common leetspeak substitutions
    chars = []
    i = 0
    while i < len(text):
        # Handle 'vv' -> 'w'
        if i + 1 < len(text) and text[i : i + 2] == "vv":
            chars.append("w")
            i += 2
            continue
        c = text[i]
        chars.append(LEET_MAP.get(c, c))
        i += 1
    substituted = "".join(chars)
    # Strip spaces and punctuation
    cleaned = re.sub(r"[^a-z0-9]", "", substituted)
    return cleaned


def collapse_repeated_characters(text: str) -> str:
    """Collapse consecutive duplicate characters to prevent evasion like 'aaddmmiinn'."""
    return re.sub(r"(.)\1+", r"\1", text)


def extract_tokens(text: str) -> list[str]:
    """Split username into words/tokens across delimiters, underscores, hyphens, and digits."""
    lowered = text.lower()
    # Replace leetspeak on tokens as well
    translated = "".join(LEET_MAP.get(c, c) for c in lowered)
    return [t for t in re.split(r"[^a-z]+", translated) if t]


def is_impersonating(username: str, is_staff: bool = False) -> tuple[bool, str | None]:
    """Check if username impersonates staff, administrators, moderators, or official Winsports support."""
    if is_staff:
        # Staff members are authorized to have official/admin accounts
        return False, None

    normalized = normalize_text(username)
    collapsed = collapse_repeated_characters(normalized)

    # 1. Exact matches or collapsed exact matches against reserved list
    if normalized in RESERVED_EXACT or collapsed in RESERVED_EXACT:
        return True, "This username is reserved and cannot be registered."

    # 2. Contains winsports or winsport
    if "winsport" in normalized or "winsport" in collapsed:
        return True, "Usernames containing 'winsport' or 'winsports' are reserved for official site accounts."

    # 3. Impersonation of admin, administrator, moderator
    admin_terms = ("admin", "administrator", "moderator")
    for term in admin_terms:
        # Standalone or with digits/suffixes: e.g. admin1, admin99, admin_qa, the_admin
        if normalized == term or collapsed == term:
            return True, "This username is reserved for site administrators or moderators."
        # If it starts with the term or ends with the term, or is bounded
        if re.search(rf"(^|_|\d){term}($|_|\d)", username.lower()):
            return True, "This username is reserved for site administrators or moderators."
        if normalized.startswith(term) or normalized.endswith(term):
            return True, "This username is reserved for site administrators or moderators."
        if collapsed.startswith(term) or collapsed.endswith(term):
            return True, "This username is reserved for site administrators or moderators."

    # 4. Support and Official keywords
    support_terms = ("support", "official", "helpdesk")
    for term in support_terms:
        if normalized == term or collapsed == term:
            return True, "This username is reserved for site support."
        if re.search(rf"(^|_|\d){term}($|_|\d)", username.lower()):
            return True, "This username is reserved for site support."

    return False, None


def contains_prohibited_content(username: str) -> tuple[bool, str | None]:
    """Check if username contains abusive, obscene, discriminatory, or threatening terms."""
    normalized = normalize_text(username)
    collapsed = collapse_repeated_characters(normalized)

    # If the whole normalized username is in the safe allowlist, allow it
    if normalized in SAFE_SUBSTRING_ALLOWLIST:
        return False, None

    # Check unambiguous slurs and severe obscenities (substring match)
    for term in UNAMBIGUOUS_PROHIBITED:
        if term in normalized or term in collapsed:
            # Check if this match is part of an allowed safe word
            is_safe = False
            for safe in SAFE_SUBSTRING_ALLOWLIST:
                if safe in normalized and term in safe:
                    is_safe = True
                    break
            if not is_safe:
                return True, "This username contains inappropriate or prohibited language."

    # Check token-based / boundary-based prohibited words
    tokens = extract_tokens(username)
    for token in tokens:
        token_collapsed = collapse_repeated_characters(token)
        if token in TOKEN_PROHIBITED or token_collapsed in TOKEN_PROHIBITED:
            # If the token is not a recognized safe word
            if token not in SAFE_SUBSTRING_ALLOWLIST and token_collapsed not in SAFE_SUBSTRING_ALLOWLIST:
                return True, "This username contains inappropriate or prohibited language."

    return False, None


def validate_username(username: str, is_staff: bool = False) -> None:
    """Validate a username against moderation rules.

    Raises:
        ValidationError: If the username violates moderation rules, contains
        prohibited language, or attempts to impersonate administrators/staff.
    """
    if not username or not username.strip():
        raise ValidationError("Username is required.")

    cleaned = username.strip()

    if len(cleaned) < 3:
        raise ValidationError("Username must be at least 3 characters long.")
    if len(cleaned) > 30:
        raise ValidationError("Username cannot exceed 30 characters.")

    # Impersonation check
    impersonating, imp_reason = is_impersonating(cleaned, is_staff=is_staff)
    if impersonating:
        raise ValidationError(imp_reason)

    # Prohibited content check
    prohibited, pro_reason = contains_prohibited_content(cleaned)
    if prohibited:
        raise ValidationError(pro_reason)
