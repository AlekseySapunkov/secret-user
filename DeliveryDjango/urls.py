"""
URL configuration for DeliveryDjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from DeliveryDjango import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register', views.register, name='register'),
    path('login', views.login_view, name='login'),
    path('', views.restaurant_list, name='restaurant_list'),  # Новый URL-маршрут
    path('restaurant/<int:restaurant_id>/', views.menu_restaurant, name='restaurant_menu'),
    path('dish_detail/<int:pk>/', views.DishDetail.as_view(), name='dish_detail_page'),
    path('add_to_cart/<int:dish_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('order/', views.order, name='order'),
    path('thank_you/', views.thank_you, name='thank_you'),
    path('logout', auth_views.LogoutView.as_view(next_page='restaurant_list'), name='logout'),
    path('user_orders/', views.user_orders, name='user_orders'),
    path('rate_order/<int:order_id>/', views.rate_order, name='rate_order'),
    path('rate_secret_order/<int:order_id>/', views.rate_secret_order, name='rate_secret_order'),
    path('rate_restaurant/<int:restaurant_id>/', views.rate_restaurant, name='rate_restaurant'),
    path('api/orders-chart-data/', views.orders_chart_data, name='orders_chart_data'),
    path('api/restaurants-rating-data/', views.restaurants_rating_data, name='restaurants_rating_data'),
    path('api/revenue_chart_data/', views.revenue_chart_data, name='revenue_chart_data'),
    path('ratings/', views.restaurant_ratings, name='restaurant_ratings'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('restaurant_revenue_ratings/', views.restaurant_revenue_ratings, name='restaurant_revenue_ratings'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
