from django.urls import re_path
from simulation import consumers

websocket_urlpatterns = [
    # Semua koneksi ke ws://domain.com/ws/simulation/ akan ditangkap oleh Consumer ini
    re_path(r'ws/simulation/$', consumers.SimulationConsumer.as_asgi()),
]