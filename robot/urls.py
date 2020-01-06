from rest_framework.routers import DefaultRouter
from . import views

route = DefaultRouter(trailing_slash=False)

route.register('message', views.MessageApi, basename='message')
route.register('login', views.LoginView, basename='login')
route.register('groups', views.GroupApi, basename='groups')
route.register('friends', views.FriendsApi, basename='friends')
route.register('members', views.MembersApi, basename='members')
route.register('send', views.SendMessageApi, basename='send')


urlpatterns = route.urls
