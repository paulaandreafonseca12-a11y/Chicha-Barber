from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from chat_ia.ai_service import obtener_respuesta_ia

@login_required
def vista_chat_ia(request):

    if "chat" not in request.session:
        request.session["chat"] = []

    if request.method == "POST":
        user_input = request.POST.get("pregunta")

        if user_input:
            chat = request.session["chat"]

            chat.append({"rol": "user", "texto": user_input})

            respuesta = obtener_respuesta_ia(user_input)

            chat.append({"rol": "ia", "texto": respuesta})

            request.session["chat"] = chat

    return render(request, "chat_ia/chat.html", {
        "chat": request.session["chat"]
    })