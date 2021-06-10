from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('product/add/', views.add_product, name='add_product'),
    path('product/detail/<int:id>/', views.product_detail, name='product_detail'),
    path('product/edit/<int:id>/', views.product_edit, name='product_edit'),
    path('product/bid/<int:p_id>/', views.auction, name='auction'),
    path('logout/', views.logout_user, name='logout'),
]