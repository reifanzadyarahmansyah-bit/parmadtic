from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import SimulationRound, Bet
from wallet.models import Wallet
from wallet.services import WalletService

# ==========================================
# 1. VIEW UNTUK HALAMAN UTAMA (UI HTML)
# ==========================================
def home_view(request):
    wallet_balance = 0
    username = "Guest"
    
    if request.user.is_authenticated:
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        wallet_balance = wallet.balance
        username = request.user.username

    context = {
        'username': username,
        'wallet_balance': wallet_balance,
    }
    
    return render(request, 'home.html', context)

# ==========================================
# 2. VIEW UNTUK API TARUHAN (REST API)
# ==========================================
class PlaceBetView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        auto_cashout = request.data.get('auto_cashout_at')
        
        # Cari ronde yang sedang dalam status WAITING atau COUNTDOWN
        active_round = SimulationRound.objects.filter(state__in=['WAITING', 'COUNTDOWN']).first()
        
        if not active_round:
            return Response({"error": "Tidak ada ronde yang terbuka untuk taruhan."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Kunci saldo dan potong balance user untuk taruhan
            WalletService.process_transaction(
                user=request.user,
                amount=amount,
                transaction_type='BET',
                description=f"Bet for round {active_round.id.hex[:8]}"
            )
            
            # Catat taruhan ke dalam tabel Bet
            bet = Bet.objects.create(
                user=request.user,
                simulation_round=active_round,
                amount=amount,
                auto_cashout_at=auto_cashout
            )
            
            return Response({"message": "Taruhan berhasil dipasang!", "bet_id": bet.id}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)