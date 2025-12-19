from django.urls import path

from apps.transaction import views

urlpatterns = [
    path('credit-request/', views.CreateCreditRequestView.as_view(), name='create_credit_request'),
    path('status/', views.UpdateCreditRequestView.as_view(), name='update_credit_request_status'),
]
