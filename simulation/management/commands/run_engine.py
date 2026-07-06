import time
from django.core.management.base import BaseCommand
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from simulation.models import SimulationRound
from simulation.services import ProvablyFairService

class Command(BaseCommand):
    help = 'Menjalankan Realtime Simulation Engine PARMADTIC'

    def handle(self, *args, **kwargs):
        channel_layer = get_channel_layer()
        self.stdout.write(self.style.SUCCESS("Engine started. Press CTRL+C to stop."))

        while True:
            # 1. PERSIAPAN RONDE (GENERATE SEED & CRASH POINT)
            server_seed, client_seed = ProvablyFairService.generate_seeds()
            nonce = 1 # Untuk simulasi, kita pakai 1 dulu. Nantinya bisa increment berdasarkan ronde global.
            
            crash_point = ProvablyFairService.calculate_crash_point(server_seed, client_seed, nonce)
            
            # Buat record di Database
            current_round = SimulationRound.objects.create(
                state='WAITING',
                crash_point=crash_point,
                server_seed=server_seed,
                client_seed=client_seed,
                nonce=nonce,
                # hash_result sengaja disembunyikan sampai ronde selesai untuk provably fair
            )
            
            round_id = current_round.id.hex
            self.stdout.write(f"--- ROUND {round_id[:8]} STARTED (Target Crash: {crash_point}x) ---")

            # 2. STATE: WAITING (5 Detik untuk User Pasang Taruhan)
            self.broadcast(channel_layer, 'WAITING', 1.00, round_id)
            time.sleep(5)

            # 3. STATE: COUNTDOWN (3 Detik hitung mundur)
            current_round.state = 'COUNTDOWN'
            current_round.save()
            for i in range(3, 0, -1):
                self.broadcast(channel_layer, 'COUNTDOWN', float(i), round_id)
                time.sleep(1)

            # 4. STATE: RUNNING (Roket Meluncur)
            current_round.state = 'RUNNING'
            current_round.save()
            
            multiplier = 1.00
            # Kecepatan naiknya multiplier (semakin tinggi, makin cepat pertambahannya)
            tick_rate = 0.1 # detik
            
            while multiplier < float(crash_point):
                self.broadcast(channel_layer, 'RUNNING', multiplier, round_id)
                time.sleep(tick_rate)
                # Kurva eksponensial sederhana agar makin tinggi makin cepat naik
                multiplier += (multiplier * 0.01) 
                
                # Memastikan tidak melampaui crash point
                if multiplier >= float(crash_point):
                    multiplier = float(crash_point)
                    break

            # 5. STATE: CRASHED (Roket Meledak)
            current_round.state = 'CRASHED'
            current_round.save()
            self.broadcast(channel_layer, 'CRASHED', float(crash_point), round_id)
            self.stdout.write(self.style.ERROR(f"CRASHED AT {crash_point}x!"))
            
            # Jeda 4 detik untuk melihat hasil crash sebelum ronde baru
            time.sleep(4) 

    def broadcast(self, channel_layer, state, multiplier, round_id):
        """Fungsi helper untuk mengirim pesan ke Redis Channel Layer"""
        async_to_sync(channel_layer.group_send)(
            'simulation_engine',
            {
                'type': 'game_tick', # Menunjuk ke fungsi game_tick di consumers.py
                'state': state,
                'multiplier': multiplier,
                'round_id': round_id
            }
        )