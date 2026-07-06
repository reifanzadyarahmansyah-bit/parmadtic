from django.urls import path
from .views import PlaceBetView

urlpatterns = [
    path('bet/', PlaceBetView.as_view(), name='place_bet'),
]