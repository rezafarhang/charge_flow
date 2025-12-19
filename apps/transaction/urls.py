from django.urls import path

from apps.transaction import views

urlpatterns = [
    path('credit-request/', views.CreateCreditRequestView.as_view(), name='create_credit_request'),
    path('approve/', views.ApproveCreditRequestView.as_view(), name='approve_credit_request'),
]
