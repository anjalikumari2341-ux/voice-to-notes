import os
from dotenv import load_dotenv
from groq import Groq
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Rough token estimate: 1 token ≈ 4 characters
MAX_TOKENS = 5000


def chunk_text(text, max_tokens=MAX_TOKENS):
    words = text.split()
    chunks = []
    chunk = []
    token_count = 0

    for word in words:
        token_count += max(1, len(word) // 4)
        if token_count > max_tokens:
            chunks.append(" ".join(chunk))
            chunk = [word]
            token_count = len(word) // 4
        else:
            chunk.append(word)

    if chunk:
        chunks.append(" ".join(chunk))

    return chunks


def groq_generate(prompt, max_tokens=600):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens
    )
    return response.choices[0].message.content


# =========================
# CORE FUNCTIONS
# =========================

def generate_notes(content):
    notes = []
    for chunk in chunk_text(content):
        notes.append(
            groq_generate(
                f"Convert this lecture into clean notes:\n\n{chunk}"
            )
        )
    return "\n\n".join(notes)


def generate_mcqs(notes):
    return groq_generate(
        f"Create 10 MCQs with answers from these notes:\n\n{notes}"
    )


def generate_flashcards(notes):
    return groq_generate(
        f"Create flashcards (Front/Back) from these notes:\n\n{notes}"
    )


# =========================
# SAFE WRAPPERS (NO RE-CHUNKING)
# =========================

def generate_notes_safe(text):
    # Notes already chunk internally
    return generate_notes(text)


def generate_mcqs_safe(notes):
    # Notes are already safe-sized
    return generate_mcqs(notes)


def generate_flashcards_safe(notes):
    return generate_flashcards(notes)
