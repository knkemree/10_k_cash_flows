from django.urls import path

from EaganJones import views

app_name = 'EaganJones'
urlpatterns = [
    path('', views.company_list, name='company_list'),
    path('<int:id>/<str:primarysymbol>/', views.company_detail, name='company_detail'),

    ]