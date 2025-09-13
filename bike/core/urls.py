# core/urls.py
from django.urls import path
from . import views   # <--- import module

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),
    path('about/', views.about, name='about'),
    path('buy-bike/', views.buy_bike, name='buy-bike'),
    path('bike/<int:pk>/', views.bike_detail, name='bike-detail'),
   path("bike/<int:pk>/payment/", views.bike_payment, name="bike-payment"),
    path('bike/<int:pk>/book-test-ride/', views.book_test_ride, name='book-test-ride'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('sell-bike/', views.sell_bike_view, name='sell-bike'),
    path('sell-bike/get-price/', views.sell_get_price, name='sell-get-price'),
]
