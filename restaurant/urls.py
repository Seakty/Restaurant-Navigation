from django.urls import path
from . import views
from .views import FeedbackCreateView, profile

urlpatterns = [
    path('', views.RestaurantListView.as_view(), name='restaurant_list'),
    path('menu/<int:restaurant_id>/', views.MenuListView.as_view(), name='menu_list'),
    path('restaurant/<int:restaurant_id>/feedback/', FeedbackCreateView.as_view(), name='feedback-create'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('signup/', views.register_view, name='signup'),
    path('login/', views.login_view,name='login'),
    path('logout/', views.logout_view,name='logout'),
    path('profile/', profile, name='profile'),
]



