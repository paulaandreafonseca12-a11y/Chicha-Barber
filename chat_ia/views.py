from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Importamos directamente desde el paquete chat_ia
from chat_ia.ai_service import obtener_respuesta_ia

@login_required
def vista_chat_ia(request):
    respuesta = None
    if request.method == "POST":
        user_input = request.POST.get("pregunta")
        if user_input:
            respuesta = obtener_respuesta_ia(user_input)
    
    return render(request, 'chat_ia/chat.html', {'respuesta': respuesta})