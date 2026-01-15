from fastapi import FastAPI, Body
from supabase_client import supabase
from ai_engine import run_career_ai, find_resources_for_skills, coach_reply
from fastapi.middleware.cors import CORSMiddleware
from github_leetcode import get_github_stats, get_leetcode_stats

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def health():
    return {"status": "OnTrack backend running"}

# ============================
# PUBLIC SCRAPER ENDPOINTS
# ============================

@app.get("/github-stats/{username}")
def github_stats_api(username: str):
    data = get_github_stats(username)
    if not data:
        return {"valid": False}
    return data


@app.get("/leetcode-stats/{username}")
def leetcode_stats_api(username: str):
    data = get_leetcode_stats(username)
    if not data:
        return {"valid": False}
    return data


@app.post("/run-ai/{user_id}")
def run_ai(user_id: str):
    # Load user inputs
    onboarding = supabase.table("user_onboarding").select("*").eq("user_id", user_id).execute().data[0]
    rows = supabase.table("user_assessment").select("*").eq("user_id", user_id).execute().data
    assessment = rows[0] if rows else {}

    # 🔍 Fetch GitHub & LeetCode evidence
    github = get_github_stats(assessment.get("github_username"))
    leetcode = get_leetcode_stats(assessment.get("leetcode_username"))

    # 🔥 Save evidence
    supabase.table("user_assessment").update({
        "github_data": github,
        "leetcode_data": leetcode
    }).eq("user_id", user_id).execute()

    # Load career market
    careers = supabase.table("career_market").select("role_name").execute().data
    career_list = [c["role_name"] for c in careers]

    # Run AI
    result = run_career_ai(onboarding, assessment, career_list)

    # Save AI result
    supabase.table("users_state").update({
        "current_career": result["career"],
        "career_explanation": result["explanation"],
        "current_skills": result["current_skills"],
        "missing_skills": result["missing_skills"],
        "learning_plan": result["learning_plan"],

        # 🔥 THESE TWO LINES FIX EVERYTHING
        "has_completed_onboarding": True,
        "has_completed_assessment": True
    }).eq("user_id", user_id).execute()

    # 🔥 Find learning resources
    resources = find_resources_for_skills(result["missing_skills"])

    # 🔥 Store learning resources
    for skill, items in resources.items():
        for r in items:
            print("Saving:", skill, r["title"])
            supabase.table("user_resources").insert({
                "user_id": user_id,
                "skill": skill,
                "title": r["title"],
                "provider": r["provider"],
                "link": r["link"],
                "level": r["level"]
            }).execute()

    return {"status": "done"}


@app.post("/find-resources")
def find_resources(skills: list[str] = Body(...)):
    return find_resources_for_skills(skills)


@app.post("/coach/{user_id}")
def ai_coach(user_id: str, message: dict):
    user_msg = message["message"]

    state = supabase.table("users_state").select("*").eq("user_id", user_id).execute().data[0]
    resources = supabase.table("user_resources").select("*").eq("user_id", user_id).execute().data

    reply = coach_reply(user_msg, state, resources)

    return {"reply": reply}
