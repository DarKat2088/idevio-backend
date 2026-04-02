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
            Ты генератор занятий для свободного времени.

            Категория: {category}

            ВАЖНО: генерируй разнообразно, не повторяй прошлые варианты.

            Твоя задача — предложить конкретное занятие, которое человек может выполнить прямо сейчас.

            Правила:
            - Только одно занятие
            - Одно предложение
            - 3-6 слов
            - Начинай с глагола (Сделай, Попробуй, Составь, Пройди и т.д.)
            - Пиши простыми и понятными словами
            - Без сложных терминов и сленга
            - Без объяснений и списков
            - Должно звучать как действие, а не идея приложения
            - Должно быть реально выполнимо в жизни
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