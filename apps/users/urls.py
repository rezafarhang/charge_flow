from django.urls import path

from apps.users import views

app_name = 'users'

urlpatterns = [
    path(
        'register/',
        views.RegisterView.as_view(),
        name='register'
    ),
    path(
        'login/',
        views.LoginView.as_view(),
        name='login'
    ),
    path(
        'logout/',
        views.LogoutView.as_view(),
        name='logout'
    ),
    path('phone-number/',
         views.PhoneNumberListCreateView.as_view(),
         name='phone_number_list_create'
    ),
]
