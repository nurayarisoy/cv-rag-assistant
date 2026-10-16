from __future__ import annotations

from typing import Literal

Intent = Literal[
    "skills", "experience", "achievements", "education", "languages", "tools", "general"
]

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
        "programming",
        "programmiersprache",
        "programmiersprachen",
        "programlama",
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
    "achievements": {
        "achievement",
        "achievements",
        "success",
        "successes",
        "erfolg",
        "erfolge",
        "erreicht",
        "başarı",
        "basari",
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
    "achievements": set(),
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

PROGRAMMING_LANGUAGE_QUERY_TERMS = {
    "programming",
    "programmiersprache",
    "programlama",
    "coding language",
}
PROGRAMMING_LANGUAGES = ("JavaScript", "TypeScript", "Python")
PROJECT_QUERY_TERMS = {"project", "projekt", "proje"}
PROJECT_FACT_HINTS = {"cv-rag-chatbot", "project", "projekt", "proje"}
ACHIEVEMENT_FACT_HINTS = {
    "cv-rag-chatbot",
    "entwicklung eines",
    "api-integrationen",
    "api integrations",
    "workflow-automatisierung",
    "workflow automation",
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
            if raw_line.strip().startswith("**") and raw_line.strip().endswith("**"):
                continue
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

    lowered_question = question.lower()

    if intent == "skills" and any(
        term in lowered_question for term in PROGRAMMING_LANGUAGE_QUERY_TERMS
    ):
        all_facts = " ".join(facts).lower()
        languages = [
            language for language in PROGRAMMING_LANGUAGES
            if language.lower() in all_facts
        ]
        if languages:
            return intent, [", ".join(languages)]

    if intent == "experience" and any(
        term in lowered_question for term in PROJECT_QUERY_TERMS
    ):
        project_facts = [
            fact for fact in facts if any(hint in fact.lower() for hint in PROJECT_FACT_HINTS)
        ]
        return intent, project_facts[:limit]

    if intent == "achievements":
        achievement_facts = [
            fact
            for fact in facts
            if any(hint in fact.lower() for hint in ACHIEVEMENT_FACT_HINTS)
        ]
        return intent, achievement_facts[:limit]

    if intent == "skills":
        tech_matched = [
            fact for fact in facts if any(hint in fact.lower() for hint in TECH_HINTS)
        ]
        if tech_matched:
            return intent, tech_matched[:limit]

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

    if intent == "education":
        return intent, []

    return intent, []


def generate_answer(qa_model, question: str, documents: list[str]) -> str:
    intent, facts = select_relevant_facts(question, documents)

    if not facts:
        lowered_question = question.lower()
        is_turkish = any(
            term in lowered_question
            for term in ("hangi", "konuş", "konus", "diller", "eğitim", "egitim", "başarı", "basari")
        )
        is_german = any(
            term in lowered_question
            for term in ("welche", "sprache", "spricht", "ausbildung", "lebenslauf")
        )

        if intent == "education":
            if is_turkish:
                return "CV'de eğitim bilgisi belirtilmemiş."
            if is_german:
                return "Im Lebenslauf sind keine Angaben zur Ausbildung aufgeführt."
            return "The resume does not include education details."
        if intent == "languages":
            if is_turkish:
                return "CV'de konuşulan diller belirtilmemiş."
            if is_german:
                return "Im Lebenslauf sind keine gesprochenen Sprachen angegeben."
            return "The resume does not specify which languages the candidate speaks."
        if intent == "achievements":
            if is_turkish:
                return "CV'de belirtilen somut bir başarı bulunamadı."
            if is_german:
                return "Im Lebenslauf sind keine konkreten Erfolge aufgeführt."
            return "The resume does not list any specific achievements."
        return "I could not find this information in the resume."

    facts_block = "\n".join(f"- {fact}" for fact in facts)

    if intent == "skills":
        return "; ".join(facts[:4])

    if intent in {"experience", "achievements"}:
        return "; ".join(facts[:3])

    if intent == "languages":
        return "; ".join(facts[:4])

    if intent == "tools":
        return "; ".join(facts[:6])

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

    if len(response.split()) < 3:
        return "; ".join(facts[:3])

    return response
