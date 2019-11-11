from django.urls import path
from . import views

app_name = 'mystore'
urlpatterns = [
    path('', views.IndexView, name='index'),
    path('<int:order_id>/', views.detail, name='detail'),
    path('inventory/', views.InventoryListView.as_view(), name='inventory'),
    path('add_order/', views.add_order, name='add_order'),
    path('add_item/', views.add_item, name='add_item'),
    path('<int:order_id>/<slug:institution>/<slug:size>/<int:item_rmv>/', views.detail, name='item_removed'),
    path('<int:order_id>/<slug:institution>/<slug:size>/<int:item_dispatch>/<int:item_pending>', views.detail, name='item_dispatch'),
    path('<int:order_id>/<slug:institution>/<slug:size>/<int:item_missing>/<int:item_pending>/add', views.detail, name='items_pending'),
    path('<int:order_id>/<slug:institution>/', views.detail, name='institution'),
    path('<int:order_id>/<slug:institution>/<slug:size>/', views.detail, name='size'),
    path('confirmation/<int:order_id>/', views.confirmation, name='confirmation'),
    path('receipt/<int:order_id>/', views.receipt, name='receipt'),
    path('order_update/<int:order_id>/', views.order_update, name='order_update'),
    path('order_update/<int:order_id>/<int:item_missing>/<int:item_pending>/return', views.order_update, name='order_return'),
    path('order_update/<int:order_id>/<int:item_dispatch>/<int:item_pending>/remove', views.order_update, name='order_dispatch'),
    path('confirmation/<int:order_id>/share/', views.order_share, name='order_share'),
    path('order_search/', views.order_search, name='order_search'),
    path('item_search/', views.ItemSearchListView.as_view(), name='item_search'),
    path('client_search/', views.client_search, name='client_search'),
    path('client_detail/<int:client>', views.client_detail, name='client_detail'),
    path('add_client/', views.add_client, name='add_client'),
    path('order_receipt/<int:order_id>/pdf', views.order_pdf, name='order_receipt'),
    path('payments/', views.order_payments, name='order_payments'),
]