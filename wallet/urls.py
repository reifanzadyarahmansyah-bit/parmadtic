from django.urls import path
from .views import WalletInfoView, TransactionAPIView

urlpatterns = [
    path('info/', WalletInfoView.as_view(), name='wallet_info'),
    path('transaction/', TransactionAPIView.as_view(), name='wallet_transaction'),
]