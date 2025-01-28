from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "uno/index.html")

def uno_matching(request):
    return render(request, 'uno/matching.html')

def uno_game(request, room_name):
    return render(request, 'uno/game_room.html', {"room_name": room_name})