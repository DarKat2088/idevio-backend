from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

class IdeaRequest(BaseModel):
    category: str


def generate_with_retry(prompt, retries=3):
    for i in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )

            return response.text.strip()

        except Exception as e:
            print(f"Attempt {i+1} failed:", e)
            time.sleep(2 ** i)

    return "Идея временно недоступна, попробуйте позже"


@app.post("/generate")
def generate(req: IdeaRequest):
    try:
        category = req.category.lower().strip()

        print("API KEY:", api_key)
        print("REQUEST:", category)

        prompt = f"""
            Ты генератор идей.

            Категория: {category}

            ВАЖНО: используй случайность и не повторяй предыдущие идеи.
            Сгенерируй уникальную идею.

            Правила:
            - Сгенерируй только одну идею
            - Одно предложение
            - 6-10 слов
            - Без списков и объяснений
            - Креативно и понятно
            """

        idea = generate_with_retry(prompt)

        if not idea or not idea.strip():
            return {"error": "Empty AI response"}

        return {"idea": idea.strip()}

    except Exception as e:
        error_text = str(e)
        print("ERROR:", error_text)

        if "429" in error_text:
            return {"error": "Лимит API исчерпан"}

        return {"error": error_text}