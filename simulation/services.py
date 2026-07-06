import hashlib
import hmac
import math
import secrets
from decimal import Decimal

class ProvablyFairService:
    
    @staticmethod
    def generate_seeds():
        """Menghasilkan server seed (rahasia) dan client seed (publik) secara acak"""
        server_seed = secrets.token_hex(32)
        client_seed = secrets.token_hex(16)
        return server_seed, client_seed

    @staticmethod
    def calculate_crash_point(server_seed: str, client_seed: str, nonce: int) -> Decimal:
        """
        Algoritma standar industri untuk menghitung Crash Multiplier.
        Menggunakan HMAC_SHA256 untuk memastikan hasilnya deterministik
        namun tidak bisa diprediksi tanpa server_seed.
        """
        # Gabungkan client seed dan nonce
        message = f"{client_seed}:{nonce}"
        
        # Buat hash HMAC
        hash_obj = hmac.new(
            server_seed.encode('utf-8'), 
            message.encode('utf-8'), 
            hashlib.sha256
        ).hexdigest()
        
        # Ambil 13 karakter heksadesimal pertama, ubah ke integer (desimal)
        h = int(hash_obj[:13], 16)
        e = 2**52
        
        # --- EDUKASI PROBABILITAS: House Edge ---
        # Jika h habis dibagi 33 (sekitar ~3% probabilitas), game langsung crash di 1.00x.
        # Ini adalah cara platform (house) mendapatkan keuntungan matematika jangka panjang.
        if h % 33 == 0:
            return Decimal("1.00")
        
        # Kalkulasi multiplier (maksimal dibatasi di angka wajar untuk simulasi)
        multiplier = math.floor((100 * e - h) / (e - h)) / 100.0
        
        # Kita kembalikan sebagai Decimal agar sinkron dengan model database
        return Decimal(str(max(1.00, multiplier)))
        
    @staticmethod
    def verify_hash(server_seed: str, client_seed: str, nonce: int, expected_multiplier: float) -> bool:
        """Fungsi untuk edukasi user, memverifikasi apakah multiplier sesuai dengan hash"""
        calculated = ProvablyFairService.calculate_crash_point(server_seed, client_seed, nonce)
        return calculated == Decimal(str(expected_multiplier))