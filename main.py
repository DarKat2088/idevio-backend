from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
import os
import time

app = FastAPI()

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

class IdeaRequest(BaseModel):
    category: str

cache = {}


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
            time.sleep(2)

    return "Идея временно недоступна, попробуйте позже"


@app.post("/generate")
def generate(req: IdeaRequest):
    try:
        category = req.category.lower().strip()

        print("REQUEST:", category)

        if category in cache:
            print("CACHE HIT ⚡")
            return {"idea": cache[category]}

        print("CACHE MISS ❌")

        prompt = f"""
            Ты генератор идей.

            Категория: {category}

            Правила:
            - Сгенерируй только одну идею
            - Одно предложение
            - 6-10 слов
            - Без списков и объяснений
            - Креативно и понятно
            """

        idea = generate_with_retry(prompt)

        cache[category] = idea

        print("\nRESPONSE OK")

        return {"idea": idea}

    except Exception as e:
        print("ERROR:", str(e))
        return {"error": str(e)}