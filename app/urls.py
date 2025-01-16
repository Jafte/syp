"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from knox import views as knox_views

from plans.views import UserEventsListView, AddUserEventView
from users.views import LoginView, UserView, AuthUserView, UserFriendsView, UserFriendRequestsView, TelegramLoginView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/telegram/', TelegramLoginView.as_view(), name='telegram_login'),
    path('api/auth/login/', LoginView.as_view(), name='knox_login'),
    path('api/auth/logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('api/auth/logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
    path('api/user/me/', AuthUserView.as_view(), name='my_detail'),
    path('api/user/friends/', UserFriendsView.as_view(), name='my_friends'),
    path('api/user/friends/requests/', UserFriendRequestsView.as_view(), name='my_friends_requests'),
    path('api/user/events/', UserEventsListView.as_view(), name='my_events'),
    path('api/user/events/add/', AddUserEventView.as_view(), name='my_events_add'),
    path('api/user/<uuid:user_uuid>/', UserView.as_view(), name='user_detail'),
    path('', TemplateView.as_view(template_name="index.html"), name='index'),
    # path('login/', UserLoginView.as_view(), name='login'),
    # path('logout/', UserLogoutView.as_view(), name='logout'),
    # path('me/', MyProfileView.as_view(), name='my_profile'),
    # path('friends/', MyFriendsView.as_view(), name='my_friends'),
    # path('friends/plans/', UserFriendsEventsListView.as_view(), name='my_friends_plans'),
    # path('friends/requests/', FriendshipRequestListView.as_view(), name='friendship_requests'),
    # path('friends/requests/<int:request_id>/', FriendshipRequestDetailView.as_view(), name='friendship_request'),
    # path('plans/', MyEventsListView.as_view(), name='my_plans'),
    # path('plans/add/', AddEventView.as_view(), name='add_event'),
    # path('plans/<int:event_id>/', EventDetailView.as_view(), name='event_detail'),
    # path('plans/<int:event_id>/request/', EventAttendeeRequestCreateFormView.as_view(), name='event_attendee_request_create'),
    # path('plans/<int:event_id>/request/<int:request_id>/', EventAttendeeRequestActionFormView.as_view(), name='event_attendee_request_action'),
    # path('user/<uuid:user_uuid>/', UserProfileView.as_view(), name='user_profile'),
    # path('user/<uuid:user_uuid>/friendship_request/', FriendshipRequestView.as_view(), name='user_profile_friendship_request'),

] + debug_toolbar_urls()
