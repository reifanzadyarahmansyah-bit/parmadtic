from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .services import WalletService
from .serializers import WalletSerializer, WalletTransactionSerializer

class WalletInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet = WalletService.get_or_create_wallet(request.user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

class TransactionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        action = request.data.get('action') # 'DEPOSIT' atau 'WITHDRAW'
        amount = request.data.get('amount')

        if not amount or float(amount) <= 0:
            return Response({"error": "Jumlah tidak valid."}, status=status.HTTP_400_BAD_REQUEST)

        if action not in ['DEPOSIT', 'WITHDRAW']:
            return Response({"error": "Aksi tidak valid."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Panggil layanan yang sudah memiliki sistem locking database
            tx = WalletService.process_transaction(
                user=request.user, 
                amount=amount, 
                transaction_type=action, 
                description=f"User requested {action}"
            )
            return Response({
                "message": f"{action} berhasil.",
                "transaction": WalletTransactionSerializer(tx).data
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            # Menangkap error jika saldo tidak cukup
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)