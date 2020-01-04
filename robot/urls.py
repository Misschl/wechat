from rest_framework.routers import DefaultRouter
from . import views

route = DefaultRouter(trailing_slash=False)

route.register('login', views.LoginView, basename='login')

urlpatterns = route.urls
