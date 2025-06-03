from django.urls import path
from . import views

urlpatterns = [
    path('', views.ad_list, name='ad_list'),
    path('ad/<int:pk>/', views.ad_detail, name='ad_detail'),
    path('ad/new/', views.ad_create, name='ad_create'),
    path('ad/<int:pk>/edit/', views.ad_update, name='ad_update'),
    path('ad/<int:pk>/delete/', views.ad_delete, name='ad_delete'),
    path('ad/<int:pk>/image/<int:image_id>/delete/', views.delete_ad_image, name='delete_ad_image'),
    path('ad/<int:pk>/image/<int:image_id>/set_main/', views.set_main_image, name='set_main_image'),    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('proposals/', views.proposal_list, name='proposal_list'),
    path('proposal/create/<int:ad_id>/', views.create_proposal, name='create_proposal'),    path('proposal/update/<int:proposal_id>/', views.update_proposal_status, name='update_proposal_status'),    # URL для комментариев
    path('ad/<int:ad_id>/comment/add/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/reply/', views.reply_comment, name='reply_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    # URL для сообщений
    path('messages/', views.messages_list, name='messages_list'),
    path('messages/<int:user_id>/', views.conversation_detail, name='conversation_detail'),
    path('send_message/<int:user_id>/', views.send_message, name='send_message'),    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock_user/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('blocked_users/', views.blocked_users, name='blocked_users'),
    # API для уведомлений
    path('api/notifications/', views.notifications_api, name='notifications_api'),
]
