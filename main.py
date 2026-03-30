from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

app = FastAPI()

client = genai.Client(api_key="AIzaSyB_lqYJyJhB9ok8ow9wr-IqKOud_5ji4JA")

class IdeaRequest(BaseModel):
    category: str


@app.post("/generate")
def generate(req: IdeaRequest):
    try:
        print("REQUEST:", req.category)

        prompt = f"""
            Ты генератор идей.

            Категория: {req.category}

            Правила:
            - Сгенерируй только одну идею по категории
            - Только одно предложение
            - Без списков, без объяснений
            - Максимум 6-10 слов
            - Идея должна быть уникальной и креативной
            - Пиши понятным и несложным языком
            """

        response = client.models.generate_content_stream(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        idea = ""

        for chunk in response:
            if chunk.text:
                print(chunk.text, end="", flush=True)
                idea += chunk.text

        print("\nRESPONSE OK")

        return {"idea": idea.strip()}

    except Exception as e:
        print("ERROR:", str(e))
        return {"error": str(e)}