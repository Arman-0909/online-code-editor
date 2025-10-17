from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/execute/', views.execute_code, name='execute_code'),
    path('api/save/', views.save_code, name='save_code'),
    path('api/load/', views.load_file, name='load_file'),
    path('api/list/', views.list_files, name='list_files'),
]