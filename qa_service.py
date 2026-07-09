from __future__ import annotations

from typing import Literal

Intent = Literal["skills", "experience", "education", "languages", "tools", "general"]

INTENT_KEYWORDS: dict[Intent, set[str]] = {
    "skills": {
        "skill",
        "skills",
        "technical",
        "technology",
        "technologie",
        "technologien",
        "tech",
        "stack",
        "framework",
        "frontend",
        "backend",
        "fahigkeit",
        "fahigkeiten",
        "fähigkeiten",
        "kenntnis",
        "kenntnisse",
        "beceri",
        "beceriler",
        "teknik",
        "kompetenz",
    },
    "experience": {
        "experience",
        "work",
        "career",
        "job",
        "position",
        "worked",
        "beruf",
        "berufserfahrung",
        "projekt",
        "deneyim",
        "tecrube",
        "arbeit",
        "erfahrung",
    },
    "education": {
        "education",
        "degree",
        "university",
        "school",
        "graduation",
        "ausbildung",
        "hochschule",
        "universität",
        "universitaet",
        "egitim",
        "okul",
        "universite",
        "diploma",
        "studium",
    },
    "languages": {
        "language",
        "languages",
        "speak",
        "fluent",
        "linguistic",
        "sprach",
        "deutsch",
        "englisch",
        "telc",
        "dil",
        "diller",
        "sprache",
        "sprachen",
    },
    "tools": {
        "tool",
        "tools",
        "werkzeug",
        "git",
        "github",
        "jira",
        "trello",
        "postman",
    },
    "general": set(),
}

EXCLUDE_KEYWORDS_BY_INTENT: dict[Intent, set[str]] = {
    "skills": {"sprachkurs", "deutschkurs", "zuwanderer", "telc", "esl", "englisch"},
    "languages": set(),
    "tools": {"sprachkurs", "deutschkurs", "zuwanderer", "telc"},
    "experience": set(),
    "education": set(),
    "general": set(),
}

TECH_HINTS = {
    "html",
    "css",
    "javascript",
    "react",
    "next.js",
    "typescript",
    "tailwind",
    "bootstrap",
    "material ui",
    "ant design",
    "node.js",
    "python",
    "firebase",
    "rest api",
    "mysql",
    "postgresql",
    "sqlite",
    "llm",
    "n8n",
}


def detect_intent(question: str) -> Intent:
    lowered = question.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if intent == "general":
            continue
        if any(keyword in lowered for keyword in keywords):
            return intent
    return "general"


def normalize_facts(documents: list[str]) -> list[str]:
    facts: list[str] = []
    seen: set[str] = set()

    for doc in documents:
        for raw_line in doc.splitlines():
            line = raw_line.strip().strip("-*\u2022 ")
            if not line:
                continue
            # Skip section headings like "SKILLS" or "Frontend:"
            if line.endswith(":") or line.upper() == line:
                continue
            lowered = line.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            facts.append(line)

    return facts


def select_relevant_facts(question: str, documents: list[str], limit: int = 5) -> tuple[Intent, list[str]]:
    facts = normalize_facts(documents)
    if not facts:
        return "general", []

    intent = detect_intent(question)
    if intent == "general":
        return intent, facts[:limit]

    keywords = INTENT_KEYWORDS[intent]
    matched = [fact for fact in facts if any(keyword in fact.lower() for keyword in keywords)]

    exclude_keywords = EXCLUDE_KEYWORDS_BY_INTENT[intent]
    if exclude_keywords:
        matched = [
            fact
            for fact in matched
            if not any(excluded in fact.lower() for excluded in exclude_keywords)
        ]

    if matched:
        return intent, matched[:limit]

    if intent == "skills":
        tech_matched = [
            fact for fact in facts if any(hint in fact.lower() for hint in TECH_HINTS)
        ]
        if tech_matched:
            return intent, tech_matched[:limit]

    if intent == "education":
        return intent, []

    return intent, facts[:limit]


def generate_answer(qa_model, question: str, documents: list[str]) -> str:
    intent, facts = select_relevant_facts(question, documents)

    if not facts:
        if intent == "education":
            return "The resume does not include education details."
        return "I could not find this information in the resume."

    facts_block = "\n".join(f"- {fact}" for fact in facts)
    prompt = f"""
You are answering questions about a candidate resume.
Only use the facts below. If the answer is missing, say it is not specified.
Keep the answer concise (1-2 sentences).

Facts:
{facts_block}

Question: {question}
Answer:
"""

    response = qa_model(prompt, truncation=True)[0]["generated_text"].strip()

    if intent == "skills":
        return "; ".join(facts[:4])

    if intent == "experience":
        return "; ".join(facts[:3])

    if intent == "languages":
        return "; ".join(facts[:4])

    if intent == "tools":
        return "; ".join(facts[:6])

    if len(response.split()) < 3:
        return "; ".join(facts[:3])

    return response
