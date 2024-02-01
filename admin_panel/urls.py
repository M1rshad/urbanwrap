from django.urls import path
from . import views
urlpatterns = [
    path('admin_login', views.admin_login, name='admin_login'),
    path('admin_panel', views.admin_panel, name='admin_panel'),
    path('logout', views.log_out, name='logout'),
    path('user-management', views.user_management, name='user_management'),
    path('user-management/user_search', views.user_search, name='user_search'),
    path('user-management/block_user/<pk>', views.block_user, name='block_user'),
    path('user-management/unblock_user/<pk>', views.unblock_user, name='unblock_user'),
    path('category-management', views.category_management, name='category_management'),
    path('category-management/category-unlist/<pk>', views.unlist_category, name='unlist_category'),
    path('category-management/category-list/<pk>', views.list_category, name='list_category'),
    path('category-management/add_category', views.add_category, name='add_category'),
    path('category-management/edit_category/<pk>', views.edit_category, name='edit_category'),
    path('category-management/category_search', views.category_search, name='category_search'),
    path('product-management', views.product_management, name='product_management'),
    path('category-management/product-unlist/<pk>', views.unlist_product, name='unlist_product'),
    path('category-management/product-list/<pk>', views.list_product, name='list_product'),
    path('product-management/add_product', views.add_product, name='add_product'),
    path('product-management/edit_product/<pk>', views.edit_product, name='edit_product'),
    path('product-management/product_search', views.product_search, name='product_search'),
    path('variant-management', views.variant_management, name='variant_management'),
    path('variant-management/variant-delete/<pk>', views.delete_variant, name='delete_variant'),
    path('variant-management/add_variant', views.add_variant, name='add_variant'),
    path('variant-management/edit_variant/<pk>', views.edit_variant, name='edit_variant'),
    path('variant-management/variant_search', views.variant_search, name='variant_search'),
    path('coupon-management/', views.coupon_management, name='coupon_management'),
    path('coupon-management/add-coupon', views.add_coupon, name='add_coupon'),
    path('variant-management/delete-coupon/<pk>', views.delete_coupon, name='delete_coupon'),
    path('variant-management/edit-coupon/<pk>', views.edit_coupon, name='edit_coupon'),


]