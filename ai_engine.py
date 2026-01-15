from openai import OpenAI
import os
from dotenv import load_dotenv
import json

from github_leetcode import get_github_stats, get_leetcode_stats

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# github = get_github_stats("github_data")
# leetcode = get_leetcode_stats("leetcode_data")

import json

def run_career_ai(profile, assessment, career_list):
    careers_text = ", ".join(career_list)

    # Improved Prompt with clearer heuristics
    prompt = f"""
### SYSTEM TASK
You are an expert Career Placement Committee. Your goal is to match the user to exactly ONE career from the PROVIDED LIST based on their internal motivations.

### CONSTRAINTS
1. PRIORITY: User "Goal" and "Interests" override technical skills.
2. DISCOVERY: If a user wants 'Game Dev' but has 'Java' skills, match them to 'Game Development' and use the Roadmap to bridge the gap.
3. BIAS CONTROL: Do not default to 'AI/ML' or 'Backend' unless explicitly requested.
4. OUTPUT: You MUST return valid JSON.

### DATA
- COLLEGE: {profile.get("college")} ({profile.get("year")} year)
- GOALS: {profile.get("goal")}
- INTERESTS: {assessment.get("interests")}
- SKILLS: {assessment.get("skill_summary")}
- GITHUB/LEETCODE (For Roadmap Only): {assessment.get("github_data")}, {assessment.get("leetcode_data")}

### AVAILABLE CAREERS (Pick ONE from this list only):
{careers_text}

### INSTRUCTIONS
Step 1: Analyze user goals/interests to identify their "North Star" career.
Step 2: Map that North Star to the closest match in the AVAILABLE CAREERS list.
Step 3: Analyze GitHub/LeetCode to identify what they ALREADY know.
Step 4: Create a 12-week roadmap to bridge the gap between "Current Skills" and "Career Match".
Step 5: Provide a short "explanation" describing why this career was chosen.

### REQUIRED OUTPUT JSON
{{
  "career": "One career from the provided list",
  "explanation": "Why this career fits the user's goals and interests",
  "current_skills": ["Skill 1", "Skill 2"],
  "missing_skills": ["Skill 3", "Skill 4"],
  "learning_plan": ["Week 1...", "Week 2...", "Week 12..."]
}}

"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise career engine. You strictly follow the provided career list and output valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1, # Lowered for more consistent, deterministic matching
            max_tokens=1500,
            seed=42 # Ensures more consistent results across calls
        )

        result = json.loads(response.choices[0].message.content)

        # Better Normalization: Check if the AI's choice is valid (case-insensitive)
        chosen_career = result.get("career")
        matched = next((c for c in career_list if c.lower() == str(chosen_career).lower()), None)

        if matched:
            result["career"] = matched # Use the exact string from your database list
        else:
            # If no match, try to find if the goal exists in the list at least partially
            # otherwise fallback to the first item
            result["career"] = career_list[0]
            result["note"] = f"Original choice '{chosen_career}' was normalized to match database."

        return result

    except json.JSONDecodeError as e:
        return {"error": "Invalid JSON from AI", "details": str(e)}
    except Exception as e:
        # Catching specific API errors or connection issues
        return {"error": "Career Engine Error", "details": str(e)}

def find_resources_for_skills(skills):
    prompt = f"""
You are a learning resource expert.

For each of the following skills:
{skills}

Find 3 of the best online learning resources (courses, tutorials, or programs).
Prefer Coursera, Udemy, FreeCodeCamp, YouTube, Kaggle, or official docs.

Return JSON in this format:
{{
  "SQL": [
    {{"title":"...", "provider":"...", "link":"...", "level":"..."}},
    ...
  ],
  "Machine Learning": [
    ...
  ]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        response_format={"type":"json_object"}
    )

    return json.loads(response.choices[0].message.content)


def coach_reply(user_msg, state, resources):
    name = state.get("full_name", "You")
    career = state.get("current_career", "your target role")
    gaps = ", ".join(state.get("missing_skills", []))
    plan = "\n".join(state.get("learning_plan", []))

    system_instruction = (
        "You are a friendly, concise, and intelligent career mentor. "
        "You should NEVER dump the full learning plan unless the user explicitly asks for it. "
        "Answer ONLY what the user asks. "
        "If the user says hello, greet them. "
        "If the user asks what to study, give a short actionable answer for today. "
        "Always be brief, clear, and practical."
    )

    prompt = f"""
User name: {name}

Career target: {career}
Skill gaps: {gaps}

Learning plan:
{plan}

Available learning resources:
{resources}

User message:
"{user_msg}"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=400
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Sorry {name}, something went wrong. Please try again."
