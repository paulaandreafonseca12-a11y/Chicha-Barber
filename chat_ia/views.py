from django.http import JsonResponse
from chat_ia.ai_service import obtener_respuesta_ia

def vista_chat_ia(request):
    if "chat" not in request.session:
        request.session["chat"] = []

    if request.method == "POST":
        user_input = request.POST.get("pregunta")
        if user_input:
            chat = request.session["chat"]
            # Agregar mensaje usuario
            chat.append({"rol": "user", "texto": user_input})
            
            # Obtener respuesta IA
            respuesta = obtener_respuesta_ia(user_input)
            
            # Agregar mensaje IA
            chat.append({"rol": "ia", "texto": respuesta})
            
            request.session["chat"] = chat
            request.session.modified = True
            
            return JsonResponse({"status": "ok", "nuevo_mensaje": respuesta})

    return JsonResponse({"chat": request.session["chat"]})