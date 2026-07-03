import os
from groq import Groq
from dotenv import load_dotenv
from .contexto import CONTEXTO

load_dotenv()

SYSTEM_PROMPT = CONTEXTO

def obtener_respuesta_ia(prompt, historial=None):

    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return "❌ No se encontró la API Key."

    client = Groq(api_key=api_key)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    if historial:
        for msg in historial:
            if "role" in msg and "content" in msg:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

    messages.append({
        "role": "user",
        "content": prompt
    })

    try:
        respuesta = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=120,
            top_p=0.9,
            messages=messages
        )

        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ Error: {e}"