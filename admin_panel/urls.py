from django.urls import path
from . import views
urlpatterns = [
    path('admin_login', views.admin_login, name='admin_login'),
    path('admin_panel', views.admin_panel, name='admin_panel'),
    path('logout', views.log_out, name='logout'),
    path('user-management', views.user_management, name='user_management'),
    path('user-management/user-delete/<pk>', views.delete_user, name='delete_user'),
    path('user-management/user_search', views.user_search, name='user_search'),
    path('user-management/add_user', views.add_user, name='add_user'),
    path('user-management/edit_user/<pk>', views.edit_user, name='edit_user'),
    path('user-management/block_user/<pk>', views.block_user, name='block_user'),
    path('user-management/unblock_user/<pk>', views.unblock_user, name='unblock_user'),

    
]