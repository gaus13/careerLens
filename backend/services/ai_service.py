# import google.generativeai as genai
# from fastapi import HTTPException
# import json, os, re

# genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
# model = genai.GenerativeModel('gemini-2.0-flash-lite')


# # ── Gemini caller function  ─────────────────────────────────────────────────────

# def call_gemini(prompt: str) -> dict:
#     """
#     Every AI feature funnels through here.
#     Handles markdown stripping, JSON parsing, and error handling in one place.
#     """
#     try:
#         response = model.generate_content(prompt)
#         text = response.text

#         # Gemini sometimes wraps output in ```json ... ``` — striping that here
#         json_match = re.search(r'\{.*\}', text, re.DOTALL)
#         if json_match:
#             return json.loads(json_match.group())
#         return json.loads(text)

#     except json.JSONDecodeError:
#         raise HTTPException(500, 'AI returned an unreadable response. Please try again.')
#     except Exception as e:
#         raise HTTPException(503, f'AI service error: {str(e)}')


# # ── 1. Career Recommendations ─────────────────────────────────────────────────
# # IMPROVEMENTS:
# #   • Experience level detection  — inferred from years, job titles, project scope
# #   • Skill weighting             — frequency + recency + project complexity
# #   • Realistic fit scores        — rubric-based, not inflated

# def get_career_recommendations(resume_text: str) -> dict:
#     prompt = f"""You are a senior career advisor with 20 years of experience in tech hiring.
# Analyse the resume below with a critical, honest eye.

# STEP 1 — Detect experience level:
# Read job titles, years of experience, project scope, and tools used.
# Classify the candidate as one of: "Student / No Experience", "Junior (0–2 yrs)",
# "Mid-level (2–5 yrs)", "Senior (5–10 yrs)", "Lead / Principal (10+ yrs)".

# STEP 2 — Weigh skills honestly:
# - Skills mentioned multiple times across multiple projects = strong signal
# - Skills listed once with no project evidence = weak signal
# - Cutting-edge tools (Kubernetes, distributed systems, ML ops) = senior indicator
# - Basic tools only (HTML, CSS, basic Python) = junior indicator
# - DO NOT give a high fit_score just because many skills match — depth matters

# STEP 3 — Score realistically:
# fit_score rules (out of 100):
#   90–100 → almost perfect match, rare, requires deep experience + all key skills
#   75–89  → strong match, has most skills, some gaps
#   55–74  → moderate match, meaningful gaps but trainable
#   40–54  → weak match, significant reskilling needed
#   below 40 → poor fit, do not recommend

# Recommend 3 to 5 career paths. Favour paths that genuinely match what is IN the resume.
# Do NOT recommend senior roles to junior candidates.

# Return ONLY a valid JSON object — no markdown, no explanation, no preamble:
# {{
#   "experience_level": "Mid-level (2–5 yrs)",
#   "experience_summary": "3 years of Python development, 2 production Django projects, basic Docker usage",
#   "careers": [
#     {{
#       "title": "Backend Developer",
#       "fit_score": 74,
#       "salary_range": "₹8L–₹18L per year",
#       "demand": "High",
#       "fit_rationale": "Strong Python and REST API skills evidenced across 2 projects. Docker usage is shallow — only basic commands seen. No system design or cloud experience.",
#       "matched_skills": ["Python", "Django", "REST APIs", "PostgreSQL"],
#       "skill_gaps": ["Docker (deep)", "AWS/GCP", "System Design"],
#       "realistic_timeline_to_job_ready": "3–4 months with focused upskilling"
#     }}
#   ]
# }}

# Resume:
# {resume_text}"""
#     return call_gemini(prompt)


# # ── 2. Gap Analysis ───────────────────────────────────────────────────────────
# # IMPROVEMENTS:
# #   • readiness_percentage based on real math:
# #       (matched_skills / total_required_skills) × weight_adjustment
# #   • missing skill importance factored in — missing a core skill tanks the score
# #   • no score inflation

# def get_gap_analysis(resume_text: str, target_role: str) -> dict:
#     prompt = f"""You are a technical hiring manager evaluating a candidate for: '{target_role}'.

# Analyse the resume carefully. Be honest and critical — do not inflate scores.

# SKILL MATCHING RULES:
# - Only mark a skill as "matched" if there is clear evidence in the resume
#   (project usage, job description, or explicit mention with context)
# - A skill listed once with zero project evidence = "weak match", not a full match
# - Missing a CORE skill for the role (e.g. missing SQL for a Backend role) is heavily penalised

# READINESS SCORE CALCULATION:
# Use this formula mentally:
#   base = (number of strong matches) / (total required skills for role) × 100
#   Then apply penalties:
#     - each High priority missing skill  → subtract 10 points
#     - each Medium priority missing skill → subtract 5 points
#     - each Low priority missing skill   → subtract 2 points
#   Floor at 10. Do not round up generously. Be honest.

# PRIORITY DEFINITIONS:
#   High   = without this skill you will be rejected at resume screening
#   Medium = expected at interviews, absence raises red flags
#   Low    = nice to have, not a dealbreaker

# Return ONLY a valid JSON object:
# {{
#   "matched_skills": [
#     {{"skill": "Python", "proficiency": "Strong", "evidence": "Used in 2 Django projects"}}
#   ],
#   "weak_matches": [
#     {{"skill": "Docker", "note": "Listed on resume but no project evidence found"}}
#   ],
#   "missing_skills": [
#     {{"skill": "System Design", "priority": "High", "why_needed": "Required for backend interviews at any mid+ company", "learn_weeks": 4}}
#   ],
#   "readiness_percentage": 58,
#   "readiness_label": "Partially Ready",
#   "score_explanation": "7 of 12 required skills matched strongly. Missing System Design (High) and AWS (Medium) reduced score by 15 points.",
#   "estimated_weeks_to_ready": 10,
#   "roadmap": [
#     {{
#       "week_range": "1–2",
#       "focus": "Docker — build and deploy a real container",
#       "goal": "Be able to explain Dockerfile, volumes, and docker-compose in an interview",
#       "resources": ["docs.docker.com/get-started", "TechWorld with Nana — Docker tutorial"]
#     }}
#   ]
# }}

# Resume:
# {resume_text}

# Target role: {target_role}"""
#     return call_gemini(prompt)


# # ── 3. Quiz Generation ────────────────────────────────────────────────────────
# # IMPROVEMENTS:
# #   • Explicit difficulty distribution: 3 easy, 4 medium, 3 hard
# #   • Each difficulty level defined clearly so Gemini doesn't just make everything medium
# #   • Distractors (wrong options) must be plausible, not obviously wrong

# def generate_quiz(gaps: dict, target_role: str) -> dict:
#     prompt = f"""You are a senior technical interviewer creating a skill assessment quiz
# for a '{target_role}' candidate based on their identified skill gaps.

# Generate exactly 10 questions with this EXACT difficulty distribution:
#   - Questions 1, 2, 3  → EASY   (foundational definitions, basic concepts)
#   - Questions 4, 5, 6, 7 → MEDIUM (applied knowledge, requires understanding why)
#   - Questions 8, 9, 10 → HARD   (edge cases, architecture decisions, tradeoffs)

# DIFFICULTY DEFINITIONS:
#   EASY   — "What does X do?" / "Which of these is Y?" — recall-level
#   MEDIUM — "Why would you use X over Y?" / "What happens when..." — understanding-level
#   HARD   — "You have 10M users and X bottleneck — what do you do?" / tradeoff questions — application-level

# OPTION QUALITY RULES:
#   - All 4 options must be plausible — no obviously silly distractors
#   - Wrong answers should be things a confused junior might actually believe
#   - Correct answer must be unambiguously correct

# Return ONLY a valid JSON object:
# {{
#   "questions": [
#     {{
#       "id": 1,
#       "difficulty": "easy",
#       "question": "What is the purpose of the Docker CMD instruction?",
#       "options": [
#         "A. Build the Docker image from a Dockerfile",
#         "B. Set the default command to run when the container starts",
#         "C. Copy files from the host machine into the container",
#         "D. Expose a port from the container to the host"
#       ],
#       "correct": "B",
#       "explanation": "CMD sets the default executable and arguments for a container. It can be overridden at runtime. COPY handles file copying, EXPOSE declares ports, and docker build handles image building."
#     }}
#   ]
# }}

# Skill gaps to base questions on:
# {json.dumps(gaps)}
# Target role: {target_role}"""
#     return call_gemini(prompt)


# # ── 4. Interview Answer Evaluation ───────────────────────────────────────────
# # IMPROVEMENTS:
# #   • Explicit scoring rubric with weights
# #   • Score is calculated transparently, not guessed
# #   • Feedback is specific and actionable, not generic

# def evaluate_interview_answer(question: str, answer: str, role: str) -> dict:
#     prompt = f"""You are a principal engineer conducting a technical interview for '{role}'.
# Evaluate the candidate's answer using a strict, consistent rubric.

# SCORING RUBRIC (score out of 10):
#   Correctness  (40%) — Is the core answer factually right? Partial credit for partial correctness.
#   Depth        (30%) — Did they explain WHY, not just WHAT? Did they mention tradeoffs?
#   Clarity      (20%) — Was it structured and easy to follow? Would a teammate understand it?
#   Examples     (10%) — Did they use a concrete real-world or personal example?

# SCORE CALCULATION:
#   correctness_score  = X/10 × 0.40
#   depth_score        = X/10 × 0.30
#   clarity_score      = X/10 × 0.20
#   example_score      = X/10 × 0.10
#   final_score        = sum of above, rounded to 1 decimal

# SCORING HONESTY RULES:
#   - A vague answer that is technically correct scores max 5 — correctness alone is not enough
#   - A wrong answer with great structure still scores low — correctness is 40%
#   - "I don't know" or a blank answer = 1 out of 10
#   - Do not give 9 or 10 unless the answer is genuinely exceptional

# Return ONLY a valid JSON object:
# {{
#   "score": 6.5,
#   "breakdown": {{
#     "correctness": 7,
#     "depth": 6,
#     "clarity": 7,
#     "examples": 5
#   }},
#   "what_was_good": "Correctly identified that indexes speed up reads and explained B-tree structure briefly.",
#   "what_was_missing": "Did not mention the write performance tradeoff — indexes slow down INSERT and UPDATE. No mention of when NOT to use an index.",
#   "model_answer_hint": "A strong answer covers: how indexes work (B-tree/hash), read speedup, write slowdown tradeoff, cardinality considerations, and a real example like 'I added an index on user_id in my orders table and queries dropped from 800ms to 12ms'.",
#   "follow_up_question": "If indexes are so useful, why not index every column?"
# }}

# Interview question: {question}
# Candidate's answer: {answer}"""
#     return call_gemini(prompt)


# # ── 5. Final Report ───────────────────────────────────────────────────────────

# def generate_final_report(session_data: dict) -> dict:
#     prompt = f"""Generate an honest, specific final career readiness report.
# Do not use generic advice. Base everything on the actual data provided.

# Return ONLY a valid JSON object:
# {{
#   "strengths": [
#     "Demonstrated consistent Python proficiency across quiz and interview answers"
#   ],
#   "improvements": [
#     "System design answers lacked awareness of scalability tradeoffs — study CAP theorem and load balancing"
#   ],
#   "next_steps": [
#     {{
#       "action": "Complete a hands-on Docker + deployment project",
#       "why": "Docker was your highest-priority skill gap and appeared in 3 interview questions",
#       "resource": "docs.docker.com/get-started",
#       "weeks": 2
#     }}
#   ]
# }}

# Session data:
# {json.dumps(session_data)}"""
#     return call_gemini(prompt)

import httpx
from fastapi import HTTPException
import json, os, re

# ── OpenRouter configuration ──────────────────────────────────────────────────
# OpenRouter is a free AI gateway that works in all regions including India.
# It routes your request to Gemini (or any other model) via their servers.
# Sign up at openrouter.ai → Keys → Create Key → paste in .env

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_URL     = 'https://openrouter.ai/api/v1/chat/completions'

# This is the free Gemini model available through OpenRouter.
# No billing required. Generous free tier.
MODEL = 'openrouter/free'


# ── Central AI caller ─────────────────────────────────────────────────────────

def call_gemini(prompt: str) -> dict:
    """
    Every AI feature funnels through here.
    Sends prompt to OpenRouter → Gemini, strips markdown, parses JSON.

    Why httpx instead of the Gemini SDK?
    httpx is a standard HTTP client. OpenRouter exposes a REST API
    compatible with OpenAI's format — so we just make an HTTP POST.
    This also means switching to any other model (GPT-4, Claude, etc.)
    is a one-line change: just update MODEL above.
    """
    try:
        response = httpx.post(
            OPENROUTER_URL,
            headers={
                'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                'Content-Type':  'application/json',
                # OpenRouter uses these to track usage in their dashboard
                'HTTP-Referer':  'http://localhost:8000',
                'X-Title':       'CareerLens AI'
            },
            json={
                'model':    MODEL,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.4   # lower = more consistent JSON output
            },
            timeout=60   # Gemini can be slow on long prompts — give it time
        )

        # OpenRouter returns OpenAI-compatible format:
        # response.json()['choices'][0]['message']['content'] = the text
        data = response.json()

        if response.status_code != 200:
            raise Exception(f"OpenRouter error {response.status_code}: {data}")

        text = data['choices'][0]['message']['content']

        # Strip markdown fences if model wrapped output in ```json ... ```
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(text)

    except json.JSONDecodeError:
        raise HTTPException(500, 'AI returned an unreadable response. Please try again.')
    except httpx.TimeoutException:
        raise HTTPException(503, 'AI request timed out. Please try again.')
    except Exception as e:
        raise HTTPException(503, f'AI service error: {str(e)}')


# ── 1. Career Recommendations ─────────────────────────────────────────────────
# IMPROVEMENTS:
#   • Experience level detection  — inferred from years, job titles, project scope
#   • Skill weighting             — frequency + recency + project complexity
#   • Realistic fit scores        — rubric-based, not inflated

def get_career_recommendations(resume_text: str) -> dict:
    prompt = f"""You are a senior career advisor with 20 years of experience in tech hiring.
Analyse the resume below with a critical, honest eye.

STEP 1 — Detect experience level:
Read job titles, years of experience, project scope, and tools used.
Classify the candidate as one of: "Student / No Experience", "Junior (0–2 yrs)",
"Mid-level (2–5 yrs)", "Senior (5–10 yrs)", "Lead / Principal (10+ yrs)".

STEP 2 — Weigh skills honestly:
- Skills mentioned multiple times across multiple projects = strong signal
- Skills listed once with no project evidence = weak signal
- Cutting-edge tools (Kubernetes, distributed systems, ML ops) = senior indicator
- Basic tools only (HTML, CSS, basic Python) = junior indicator
- DO NOT give a high fit_score just because many skills match — depth matters

STEP 3 — Score realistically:
fit_score rules (out of 100):
  90–100 → almost perfect match, rare, requires deep experience + all key skills
  75–89  → strong match, has most skills, some gaps
  55–74  → moderate match, meaningful gaps but trainable
  40–54  → weak match, significant reskilling needed
  below 40 → poor fit, do not recommend

Recommend 3 to 5 career paths. Favour paths that genuinely match what is IN the resume.
Do NOT recommend senior roles to junior candidates.

Return ONLY a valid JSON object — no markdown, no explanation, no preamble:
{{
  "experience_level": "Mid-level (2–5 yrs)",
  "experience_summary": "3 years of Python development, 2 production Django projects, basic Docker usage",
  "careers": [
    {{
      "title": "Backend Developer",
      "fit_score": 74,
      "salary_range": "₹8L–₹18L per year",
      "demand": "High",
      "fit_rationale": "Strong Python and REST API skills evidenced across 2 projects. Docker usage is shallow — only basic commands seen. No system design or cloud experience.",
      "matched_skills": ["Python", "Django", "REST APIs", "PostgreSQL"],
      "skill_gaps": ["Docker (deep)", "AWS/GCP", "System Design"],
      "realistic_timeline_to_job_ready": "3–4 months with focused upskilling"
    }}
  ]
}}

Resume:
{resume_text}"""
    return call_gemini(prompt)


# ── 2. Gap Analysis ───────────────────────────────────────────────────────────
# IMPROVEMENTS:
#   • readiness_percentage based on real math:
#       (matched_skills / total_required_skills) × weight_adjustment
#   • missing skill importance factored in — missing a core skill tanks the score
#   • no score inflation

def get_gap_analysis(resume_text: str, target_role: str) -> dict:
    prompt = f"""You are a technical hiring manager evaluating a candidate for: '{target_role}'.

Analyse the resume carefully. Be honest and critical — do not inflate scores.

SKILL MATCHING RULES:
- Only mark a skill as "matched" if there is clear evidence in the resume
  (project usage, job description, or explicit mention with context)
- A skill listed once with zero project evidence = "weak match", not a full match
- Missing a CORE skill for the role (e.g. missing SQL for a Backend role) is heavily penalised

READINESS SCORE CALCULATION:
Use this formula mentally:
  base = (number of strong matches) / (total required skills for role) × 100
  Then apply penalties:
    - each High priority missing skill  → subtract 10 points
    - each Medium priority missing skill → subtract 5 points
    - each Low priority missing skill   → subtract 2 points
  Floor at 10. Do not round up generously. Be honest.

PRIORITY DEFINITIONS:
  High   = without this skill you will be rejected at resume screening
  Medium = expected at interviews, absence raises red flags
  Low    = nice to have, not a dealbreaker

Return ONLY a valid JSON object:
{{
  "matched_skills": [
    {{"skill": "Python", "proficiency": "Strong", "evidence": "Used in 2 Django projects"}}
  ],
  "weak_matches": [
    {{"skill": "Docker", "note": "Listed on resume but no project evidence found"}}
  ],
  "missing_skills": [
    {{"skill": "System Design", "priority": "High", "why_needed": "Required for backend interviews at any mid+ company", "learn_weeks": 4}}
  ],
  "readiness_percentage": 58,
  "readiness_label": "Partially Ready",
  "score_explanation": "7 of 12 required skills matched strongly. Missing System Design (High) and AWS (Medium) reduced score by 15 points.",
  "estimated_weeks_to_ready": 10,
  "roadmap": [
    {{
      "week_range": "1–2",
      "focus": "Docker — build and deploy a real container",
      "goal": "Be able to explain Dockerfile, volumes, and docker-compose in an interview",
      "resources": ["docs.docker.com/get-started", "TechWorld with Nana — Docker tutorial"]
    }}
  ]
}}

Resume:
{resume_text}

Target role: {target_role}"""
    return call_gemini(prompt)


# ── 3. Quiz Generation ────────────────────────────────────────────────────────
# IMPROVEMENTS:
#   • Explicit difficulty distribution: 3 easy, 4 medium, 3 hard
#   • Each difficulty level defined clearly so Gemini doesn't just make everything medium
#   • Distractors (wrong options) must be plausible, not obviously wrong

def generate_quiz(gaps: dict, target_role: str) -> dict:
    prompt = f"""You are a senior technical interviewer creating a skill assessment quiz
for a '{target_role}' candidate based on their identified skill gaps.

Generate exactly 10 questions with this EXACT difficulty distribution:
  - Questions 1, 2, 3  → EASY   (foundational definitions, basic concepts)
  - Questions 4, 5, 6, 7 → MEDIUM (applied knowledge, requires understanding why)
  - Questions 8, 9, 10 → HARD   (edge cases, architecture decisions, tradeoffs)

DIFFICULTY DEFINITIONS:
  EASY   — "What does X do?" / "Which of these is Y?" — recall-level
  MEDIUM — "Why would you use X over Y?" / "What happens when..." — understanding-level
  HARD   — "You have 10M users and X bottleneck — what do you do?" / tradeoff questions — application-level

OPTION QUALITY RULES:
  - All 4 options must be plausible — no obviously silly distractors
  - Wrong answers should be things a confused junior might actually believe
  - Correct answer must be unambiguously correct

Return ONLY a valid JSON object:
{{
  "questions": [
    {{
      "id": 1,
      "difficulty": "easy",
      "question": "What is the purpose of the Docker CMD instruction?",
      "options": [
        "A. Build the Docker image from a Dockerfile",
        "B. Set the default command to run when the container starts",
        "C. Copy files from the host machine into the container",
        "D. Expose a port from the container to the host"
      ],
      "correct": "B",
      "explanation": "CMD sets the default executable and arguments for a container. It can be overridden at runtime. COPY handles file copying, EXPOSE declares ports, and docker build handles image building."
    }}
  ]
}}

Skill gaps to base questions on:
{json.dumps(gaps)}
Target role: {target_role}"""
    return call_gemini(prompt)


# ── 4. Interview Answer Evaluation ───────────────────────────────────────────
# IMPROVEMENTS:
#   • Explicit scoring rubric with weights
#   • Score is calculated transparently, not guessed
#   • Feedback is specific and actionable, not generic

def evaluate_interview_answer(question: str, answer: str, role: str) -> dict:
    prompt = f"""You are a principal engineer conducting a technical interview for '{role}'.
Evaluate the candidate's answer using a strict, consistent rubric.

SCORING RUBRIC (score out of 10):
  Correctness  (40%) — Is the core answer factually right? Partial credit for partial correctness.
  Depth        (30%) — Did they explain WHY, not just WHAT? Did they mention tradeoffs?
  Clarity      (20%) — Was it structured and easy to follow? Would a teammate understand it?
  Examples     (10%) — Did they use a concrete real-world or personal example?

SCORE CALCULATION:
  correctness_score  = X/10 × 0.40
  depth_score        = X/10 × 0.30
  clarity_score      = X/10 × 0.20
  example_score      = X/10 × 0.10
  final_score        = sum of above, rounded to 1 decimal

SCORING HONESTY RULES:
  - A vague answer that is technically correct scores max 5 — correctness alone is not enough
  - A wrong answer with great structure still scores low — correctness is 40%
  - "I don't know" or a blank answer = 1 out of 10
  - Do not give 9 or 10 unless the answer is genuinely exceptional

Return ONLY a valid JSON object:
{{
  "score": 6.5,
  "breakdown": {{
    "correctness": 7,
    "depth": 6,
    "clarity": 7,
    "examples": 5
  }},
  "what_was_good": "Correctly identified that indexes speed up reads and explained B-tree structure briefly.",
  "what_was_missing": "Did not mention the write performance tradeoff — indexes slow down INSERT and UPDATE. No mention of when NOT to use an index.",
  "model_answer_hint": "A strong answer covers: how indexes work (B-tree/hash), read speedup, write slowdown tradeoff, cardinality considerations, and a real example like 'I added an index on user_id in my orders table and queries dropped from 800ms to 12ms'.",
  "follow_up_question": "If indexes are so useful, why not index every column?"
}}

Interview question: {question}
Candidate's answer: {answer}"""
    return call_gemini(prompt)


# ── 5. Final Report ───────────────────────────────────────────────────────────

def generate_final_report(session_data: dict) -> dict:
    prompt = f"""Generate an honest, specific final career readiness report.
Do not use generic advice. Base everything on the actual data provided.

Return ONLY a valid JSON object:
{{
  "strengths": [
    "Demonstrated consistent Python proficiency across quiz and interview answers"
  ],
  "improvements": [
    "System design answers lacked awareness of scalability tradeoffs — study CAP theorem and load balancing"
  ],
  "next_steps": [
    {{
      "action": "Complete a hands-on Docker + deployment project",
      "why": "Docker was your highest-priority skill gap and appeared in 3 interview questions",
      "resource": "docs.docker.com/get-started",
      "weeks": 2
    }}
  ]
}}

Session data:
{json.dumps(session_data)}"""
    return call_gemini(prompt)