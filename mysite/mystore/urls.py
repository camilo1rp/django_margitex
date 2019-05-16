from django.urls import path

from . import views

app_name = 'mystore'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:order_id>/', views.detail, name='detail'),
    path('add_order/', views.add_order, name='add_order'),
]
