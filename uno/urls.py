from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("uno/matching", views.uno_matching, name='matching'),
    path("uno/<str:room_name>/", views.uno_game, name="game_room")
]