import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SimulationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Nama 'room' atau grup siaran (broadcast group)
        self.room_group_name = 'simulation_engine'

        # Gabungkan client yang konek ke grup siaran ini
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Terima koneksi WebSocket
        await self.accept()

    async def disconnect(self, close_code):
        # Keluarkan client dari grup saat mereka menutup browser
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Fungsi ini dipanggil setiap kali ada pesan masuk ke channel layer grup 'simulation_engine'
    async def game_tick(self, event):
        # Ekstrak data dari event (dikirim oleh Game Engine kita nanti)
        state = event['state']
        multiplier = event.get('multiplier', 1.00)
        round_id = event.get('round_id')

        # Kirim data tersebut ke Frontend (AlpineJS/HTMX) dalam bentuk JSON
        await self.send(text_data=json.dumps({
            'type': 'tick',
            'state': state,
            'multiplier': f"{multiplier:.2f}",
            'round_id': round_id
        }))