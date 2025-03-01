from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("matching", views.uno_matching, name='matching'),
    path("game/<str:room_name>/", views.uno_game, name="game"),
    path("room_index", views.uno_room_index, name="room_index"),
    path("room_index/<str:room_name>/", views.uno_room, name="room"),
    #path("room_index/<str:room_name>/<str:player_name>/", views.uno_room, name="room"),
]