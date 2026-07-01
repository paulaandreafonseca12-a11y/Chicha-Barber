import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def obtener_respuesta_ia(prompt):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "Error: API Key no configurada."

    client = Groq(api_key=api_key)
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres un asistente experto para la gestión de Chicha Barber Studio."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Ocurrió un error al conectar con la IA: {str(e)}"