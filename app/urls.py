from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:id>/edit', views.category_edit, name='category_edit'),
    path('categories/<int:id>/delete', views.category_delete, name='category_delete'),
    path('categories/export/', views.category_export, name='category_export'),
    path('categories/import/', views.category_import, name='category_import'),

    path('accounts/', views.account_list, name='account_list'),
    path('accounts/create/', views.account_create, name='account_create'),
    path('accounts/<int:id>/edit', views.account_edit, name='account_edit'),
    path('accounts/<int:id>/delete', views.account_delete, name='account_delete'),
    path('accounts/<int:id>/toggle-status', views.account_toggle_status, name='account_toggle_status'),
    path('accounts/export/', views.account_export, name='account_export'),
    path('accounts/import/', views.account_import, name='account_import'),

    path('products/', views.product_list, name='product_list'),
    path('products/<int:id>/detail', views.product_detail, name='product_detail'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:id>/edit', views.product_edit, name='product_edit'),
    path('products/<int:id>/delete', views.product_delete, name='product_delete'),
    path('products/export/', views.product_export, name='product_export'),
    path('products/import/', views.product_import, name='product_import'),

    path('cart/', views.cart, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('api/cart/update/', views.update_cart_api, name='update_cart_api'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/process/', views.checkout_process, name='checkout_process'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),

    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
]