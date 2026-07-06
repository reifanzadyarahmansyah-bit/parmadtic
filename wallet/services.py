from django.db import transaction
from decimal import Decimal
from .models import Wallet, WalletTransaction

class WalletService:
    
    @staticmethod
    def get_or_create_wallet(user):
        wallet, created = Wallet.objects.get_or_create(user=user)
        return wallet

    @staticmethod
    def process_transaction(user, amount: Decimal, transaction_type: str, description: str = "") -> WalletTransaction:
        """
        Memproses transaksi (Deposit, Withdraw, Bet, Cashout) secara aman
        menggunakan row-level locking (select_for_update).
        """
        # Pastikan amount selalu positif untuk input, logikanya kita atur di bawah
        amount = Decimal(str(amount))
        
        with transaction.atomic():
            # Mengunci wallet user di database sampai transaksi selesai
            wallet = Wallet.objects.select_for_update().get(user=user)
            
            if transaction_type in ['BET', 'WITHDRAW']:
                if wallet.balance < amount:
                    raise ValueError("Saldo tidak mencukupi untuk melakukan transaksi ini.")
                wallet.balance -= amount
            elif transaction_type in ['DEPOSIT', 'CASHOUT']:
                wallet.balance += amount
            else:
                raise ValueError("Tipe transaksi tidak valid.")
                
            wallet.save()
            
            # Mencatat ke dalam Ledger (Buku Besar)
            wallet_tx = WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type=transaction_type,
                amount=amount,
                balance_after=wallet.balance,
                description=description
            )
            
            return wallet_tx