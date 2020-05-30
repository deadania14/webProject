from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    # path('', views.postlist, name='post_list'),
    
    # path('post/<int:pk>/', views.post_detail, name='post_detail'),
    
    path('<int:year>/<slug:slug>/', views.article, name='article'),
    path('', views.home, name='home'),
]