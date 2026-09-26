import ollama

from app.settings import settings


# Local Ollama model
OLLAMA_MODEL = "qwen2.5:0.5b"


def generate(question: str, context: str):

    if not question or not question.strip():
        return None

    if not context or not context.strip():
        return None

    # Keep the RAG context reasonably small
    context = context[:6000]

    prompt = f"""
You are an enterprise IT helpdesk assistant.

Use ONLY the approved enterprise knowledge provided below.

Do not invent troubleshooting steps.
Do not use outside knowledge.
Give a concise, practical answer.
If the knowledge is insufficient, say that the approved
knowledge base does not contain enough information.

APPROVED ENTERPRISE KNOWLEDGE:

{context}

EMPLOYEE QUESTION:

{question}

Provide the final IT helpdesk answer.
"""

    try:

        print("=" * 60)
        print("GENERATING RESPONSE WITH OLLAMA")
        print(f"Model: {OLLAMA_MODEL}")
        print("=" * 60)

        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an enterprise IT helpdesk assistant. "
                        "Use only the provided enterprise knowledge. "
                        "Never invent information."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            options={
                "temperature": 0,
                "num_predict": 120,
            },
        )

        answer = response["message"]["content"].strip()

        print("=" * 60)
        print("LLM ANSWER:")
        print(answer)
        print("=" * 60)

        if not answer:
            return None

        bad_answers = {
            "",
            "unanswerable",
            "unknown",
            "n/a",
            "none",
            "null",
        }

        if answer.lower().strip() in bad_answers:
            return None

        return answer

    except Exception as e:

        print("=" * 60)
        print("OLLAMA GENERATION ERROR")
        print(str(e))
        print("=" * 60)

        return None