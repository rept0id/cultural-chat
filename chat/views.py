import os
from django.shortcuts import render
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from mistralai.client import Mistral

load_dotenv()

CHARACTERS = [
    {"id": 0, "name": "Ani", "image": "images/characters/ani.jpg", "agent_id": "ag_019de46864dd70f6894216fe50939d9f"},
    {"id": 1, "name": "Nebuchadnezzar I", "image": "images/characters/nebuchadnezzar-i.jpg", "agent_id": "ag_019de47333d577c2972b1b6dc6db13ec"},
    {"id": 2, "name": "Odysseus", "image": "images/characters/odysseus.jpg", "agent_id": "ag_019de46fafbc773ba6bc5d8eec964725"},
    {"id": 3, "name": "Alexander the Great", "image": "images/characters/alexander-the-great.jpg", "agent_id": "ag_019de47619597366825b29887bbae265"},
    {"id": 4, "name": "Wazir", "image": "images/characters/wazir.jpg", "agent_id": "ag_019de47a4e7c7140898db863b66b5bda"},
    {"id": 5, "name": "Nefertiti", "image": "images/characters/nefertiti.jpg", "agent_id": "ag_019de48322817444b47fa352a9287aab"},
    {"id": 6, "name": "Ariadne", "image": "images/characters/ariadne.jpg", "agent_id": "ag_019de48133a77743abe06381b7c2d6a0"},
]

def home(request):
    return render(request, 'chat/home.html', {"characters": CHARACTERS})

def chat_page(request, character_id):
    character = next((c for c in CHARACTERS if c["id"] == character_id), None)
    return render(request, 'chat/chat.html', {"character": character})

@csrf_exempt
def chat_api(request, character_id):
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

    if request.method != 'POST':
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    if not MISTRAL_API_KEY:
        return JsonResponse({"error": "API key not configured"}, status=500)

    mistral_client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))

    character = next((c for c in CHARACTERS if c["id"] == character_id), None)
    if not character:
        return JsonResponse({"error": "Character not found"}, status=404)
    agent_id = character["agent_id"]
    if not agent_id:
        return JsonResponse({"error": "Character does not have agent_id"}, status=400)

    user_message = request.POST.get('message', '').strip()
    if not user_message:
        return JsonResponse({"error": "No message provided"}, status=400)
    user_conversation_id = request.POST.get('conversationId', '').strip()

    try:
        if user_conversation_id:
            mistral_client_res = mistral_client.beta.conversations.append(
                conversation_id=user_conversation_id,
                inputs=[{"role": "user", "content": user_message}],
            )
        else:
            mistral_client_res = mistral_client.beta.conversations.start(
                agent_id=agent_id,
                inputs=[{"role": "user", "content": user_message}],
            )

        return JsonResponse({
            "conversationId": mistral_client_res.conversation_id,
            "characterName": character["name"],
            "response": mistral_client_res.outputs[0].content
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
