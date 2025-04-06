from django.urls import path
from trail import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='homepage'),
    path('home', views.home, name='homepage'),
    path('bus',views.buspage, name='bus'),
    path('train',views.trainpage, name='train'),
    path('flight',views.flightpage, name='flight'),
    path('aboutus',views.about, name='aboutus'),
    path('login',views.login, name='login'),
    path('signup',views.signup, name='signup'),
    path('searchplaces',views.searchplaces, name='searchplaces'),
    path('payment/<int:booking_id>/',views.payment, name='paymentOption'),
    path('searchbus',views.searchbus, name='searchbus'),
    path('searchtrain',views.searchtrain, name='searchtrain'),
    path('searchflight',views.searchflight, name='searchflight'),
    path('selectbusseat/<int:bus_id>/',views.selectbusseat, name='selectbusseat'),
    path('selecttrainseat/<int:train_id>/',views.selecttrainseat, name='selecttrainseat'),
    path('selectflightseat/<int:flight_id>/',views.selectflightseat, name='selectflightseat'),
    path('confirm-booking/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('book-seats/<str:vehicle_type>/<int:vehicle_id>/', views.book_seats, name='book_seats'),
    path('passengerinfo/<int:booking_id>/',views.passengerinfo, name='passengerinfo'),
    path('signup',views.signup, name='signup'),
    path('login',views.login, name='login'),
    path('booking-success/<int:booking_id>/', views.booking_success, name='booking_success'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('search-place/', views.search_place, name='search_place'),
]