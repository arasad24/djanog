from django.urls import path,include
from .views import HomeView,ItemDetailView,add_to_cart,remove_from_cart,remove_single_item_from_cart,OrderSummeryView,CheckOutView,PaymentView,RefundView

urlpatterns = [
    path('',HomeView.as_view(),name='home'),
    path('product/<slug>/',ItemDetailView.as_view(),name='product'),
    path('checkout/',CheckOutView.as_view(),name='checkout'),
    path('order-summary/',OrderSummeryView.as_view(),name='order-summary'),
    path('refund-request/',RefundView.as_view(),name='refund-request'),
    path('add-to-cart/<slug>/',add_to_cart,name='add-to-cart'),
    path('remove-from-cart/<slug>/',remove_from_cart,name='remove-from-cart'),
    path('payment/<payment_option>/',PaymentView.as_view(),name='payment'),
    path('remove-single-item-from-cart/<slug>/',remove_single_item_from_cart,name='remove-single-item-from-cart'),
]

