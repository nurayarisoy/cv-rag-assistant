import unittest

from qa_service import generate_answer, select_relevant_facts


CV_DOCUMENT = """### SKILLS
**Frontend Development**
- HTML5, CSS3, JavaScript (ES6+), TypeScript
- React, Next.js, Redux
**Backend & Datenbanken**
- Python (Grundkenntnisse), Node.js (Grundkenntnisse), Flask, REST APIs
- MySQL, PostgreSQL, SQLite
**Tools & Methoden**
- Git, GitHub, Postman, Jira, Trello
- Entwicklung eines CV-RAG-Chatbots mit Python und Flask
- API-Integrationen und n8n-Workflow-Automatisierung
"""


class SelectRelevantFactsTests(unittest.TestCase):
    def test_programming_language_questions_select_skills(self):
        for question in (
            "Welche Programmiersprachen kennt der Kandidat?",
            "Hangi programlama dillerini biliyor?",
        ):
            with self.subTest(question=question):
                intent, facts = select_relevant_facts(question, [CV_DOCUMENT])

                self.assertEqual(intent, "skills")
                self.assertTrue(any("Python" in fact for fact in facts))
                self.assertTrue(any("JavaScript" in fact for fact in facts))

    def test_project_experience_selects_project_fact(self):
        intent, facts = select_relevant_facts(
            "What project experience does the candidate have?", [CV_DOCUMENT]
        )

        self.assertEqual(intent, "experience")
        self.assertEqual(len(facts), 1)
        self.assertIn("CV-RAG-Chatbots", facts[0])

    def test_missing_category_does_not_return_unrelated_facts(self):
        intent, facts = select_relevant_facts(
            "What education does the candidate have?", [CV_DOCUMENT]
        )

        self.assertEqual(intent, "education")
        self.assertEqual(facts, [])

    def test_sample_achievement_question_selects_concrete_results(self):
        intent, facts = select_relevant_facts(
            "Welche Erfolge werden im Lebenslauf genannt?", [CV_DOCUMENT]
        )

        self.assertEqual(intent, "achievements")
        self.assertTrue(any("CV-RAG-Chatbots" in fact for fact in facts))
        self.assertTrue(any("Workflow-Automatisierung" in fact for fact in facts))

        class UnusedModel:
            def __call__(self, *args, **kwargs):
                raise AssertionError("The model should not override selected achievement facts")

        answer = generate_answer(
            UnusedModel(), "Welche Erfolge werden im Lebenslauf genannt?", [CV_DOCUMENT]
        )
        self.assertIn("CV-RAG-Chatbots", answer)
        self.assertIn("Workflow-Automatisierung", answer)

    def test_missing_sample_answers_are_clear_and_in_german(self):
        class UnusedModel:
            def __call__(self, *args, **kwargs):
                raise AssertionError("The model should not be called when information is missing")

        self.assertEqual(
            generate_answer(UnusedModel(), "Welche Ausbildung hat sie?", [CV_DOCUMENT]),
            "Im Lebenslauf sind keine Angaben zur Ausbildung aufgeführt.",
        )
        self.assertEqual(
            generate_answer(UnusedModel(), "Welche Sprachen spricht sie?", [CV_DOCUMENT]),
            "Im Lebenslauf sind keine gesprochenen Sprachen angegeben.",
        )


if __name__ == "__main__":
    unittest.main()