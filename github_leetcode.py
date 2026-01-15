import requests
from collections import Counter
from fastapi import APIRouter
router = APIRouter()

# ==========================================
# CONFIGURATION
# ==========================================
TIMEOUT_SECONDS = 10  # Increased for slow APIs
GITHUB_API_BASE = "https://api.github.com"
LEETCODE_API_BASE = "https://alfa-leetcode-api.onrender.com"


def clean_language(language):
    """Normalizes messy language names."""
    if not language: return "None"
    lang_lower = language.lower()
    if "jupyter" in lang_lower: return "Python"
    if "html" in lang_lower or "css" in lang_lower: return "Web Basics"
    if "c++" in lang_lower: return "C++"
    return language


# ==========================================
# GITHUB SCRAPER (VERBOSE MODE)
# ==========================================
def get_github_stats(username):
    print(f"\n🔍 [GITHUB] Starting fetch for user: {username}...")

    if not username:
        print("❌ [GITHUB] No username provided.")
        return None

    headers = {"Accept": "application/vnd.github.v3+json"}

    try:
        # 1. Fetch User Profile
        user_url = f"{GITHUB_API_BASE}/users/{username}"
        user_resp = requests.get(user_url, headers=headers, timeout=TIMEOUT_SECONDS)

        if user_resp.status_code == 404:
            print(f"❌ [GITHUB] User '{username}' NOT FOUND.")
            return None

        if user_resp.status_code == 403:
            print("⚠️ [GITHUB] Rate limit hit! (Using limited data)")
            return {"valid": True, "repos": 0, "stars": 0, "top_lang": "Unknown (Rate Limit)"}

        user_data = user_resp.json()

        # 2. Fetch Repos
        repos_url = f"{GITHUB_API_BASE}/users/{username}/repos?per_page=100"
        repos_resp = requests.get(repos_url, headers=headers, timeout=TIMEOUT_SECONDS)

        total_stars = 0
        all_languages = []

        if repos_resp.status_code == 200:
            repos_data = repos_resp.json()
            for repo in repos_data:
                total_stars += repo.get("stargazers_count", 0)
                lang = repo.get("language")
                if lang:
                    all_languages.append(clean_language(lang))

        top_lang = Counter(all_languages).most_common(1)[0][0] if all_languages else "None"

        # LOG SUCCESS
        print(f"✅ [GITHUB] Success! Repos: {user_data.get('public_repos')}, Stars: {total_stars}, Lang: {top_lang}")

        return {
            "valid": True,
            "username": username,
            "repos": user_data.get("public_repos", 0),
            "stars": total_stars,
            "top_lang": top_lang,
            "account_created": user_data.get("created_at", "")[:10]
        }

    except Exception as e:
        print(f"❌ [GITHUB] Error: {e}")
        return None


# ==========================================
# LEETCODE SCRAPER (VERBOSE MODE)
# ==========================================
def get_leetcode_stats(username):
    print(f"\n🔍 [LEETCODE] Starting fetch for user: {username}...")

    if not username:
        print("❌ [LEETCODE] No username provided.")
        return None

    url = f"{LEETCODE_API_BASE}/{username}/solved"

    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)

        if response.status_code != 200:
            print(f"❌ [LEETCODE] API Error (Status {response.status_code})")
            return None

        data = response.json()

        if "solvedProblem" not in data:
            print("❌ [LEETCODE] User not found or hidden profile.")
            return None

        total = data.get("solvedProblem", 0)
        print(f"✅ [LEETCODE] Success! Total Solved: {total}")

        return {
            "valid": True,
            "username": username,
            "total_solved": total,
            "easy": data.get("easySolved", 0),
            "medium": data.get("mediumSolved", 0),
            "hard": data.get("hardSolved", 0)
        }

    except Exception as e:
        print(f"❌ [LEETCODE] Connection failed: {e}")
        return None
# ============================
# FASTAPI ROUTES (API LAYER)
# ============================

@router.get("/github-stats/{username}")
def github_stats(username: str):
    data = get_github_stats(username)
    if not data:
        return {"valid": False}
    return data


@router.get("/leetcode-stats/{username}")
def leetcode_stats(username: str):
    data = get_leetcode_stats(username)
    if not data:
        return {"valid": False}
    return data
