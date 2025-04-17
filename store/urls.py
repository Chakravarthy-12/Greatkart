from django.urls import path
from . import views
 

urlpatterns = [
    path('', views.store, name='store'),  # Add this line to include the home view
    path('<slug:category_slug>/', views.store, name='product_by_category'),  # Add this line to include the home view
    path('<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),  # Add this line to include the home view
]