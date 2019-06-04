from django.urls import path

from . import views

app_name = 'mystore'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:order_id>/', views.detail, name='detail'),
    path('add_order/', views.add_order, name='add_order'),
    path('<int:order_id>/<int:item_rmv>/', views.detail, name='item_removed'),
    path('<int:order_id>/<int:item_dispatch>/<int:item_pending>', views.detail, name='item_dispatch'),
    path('<int:order_id>/<slug:institution>/', views.detail, name='institution'),
    path('<int:order_id>/<slug:institution>/<slug:size>', views.detail, name='size'),
   ]
