from django.db import models
from django.contrib.auth.models import User
from wallet.models import Wallet
import uuid

class SimulationRound(models.Model):
    STATE_CHOICES = (
        ('WAITING', 'Waiting'),
        ('COUNTDOWN', 'Countdown'),
        ('RUNNING', 'Running'),
        ('CRASHED', 'Crashed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='WAITING')
    crash_point = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Provably Fair System (Edukasi Transparansi Algoritma)
    server_seed = models.CharField(max_length=64, blank=True)
    client_seed = models.CharField(max_length=64, blank=True)
    nonce = models.IntegerField(default=0)
    hash_result = models.CharField(max_length=64, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['state', 'created_at'])]

    def __str__(self):
        return f"Round {self.id.hex[:8]} - {self.state} ({self.crash_point}x)"

class Bet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    simulation_round = models.ForeignKey(SimulationRound, on_delete=models.CASCADE, related_name='bets')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    auto_cashout_at = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status setelah ronde selesai
    is_cashed_out = models.BooleanField(default=False)
    cashout_multiplier = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    profit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['simulation_round', 'user'])]

    def __str__(self):
        return f"{self.user.username} - Bet: {self.amount} - Win: {self.profit}"