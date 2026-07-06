from rest_framework import serializers
from .models import SimulationRound, Bet

class SimulationRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationRound
        # Kita sembunyikan server_seed agar tidak bocor ke frontend sebelum ronde selesai
        fields = ['id', 'state', 'crash_point', 'client_seed', 'nonce', 'hash_result', 'created_at']

class BetSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Bet
        fields = ['id', 'username', 'amount', 'auto_cashout_at', 'is_cashed_out', 'cashout_multiplier', 'profit']