from django.urls import path
from .views import criar_pedido

urlpatterns = [
    path('criar-pedido/', criar_pedido, name='criar_pedido'),
]