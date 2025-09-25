from . import views
from django.urls import path

urlpatterns = [
    path('', views.beranda, name='beranda'),
    path('materi/', views.materi, name='materi'),
    path('latihan/', views.latihan, name='latihan'),
    path('hasil/', views.hasil, name='hasil'),
    # path('dasbor/', views.dasbor, name='dasbor'),

    # Autentikasi
    path('masuk/', views.masuk, name='masuk'),
    path('daftar/', views.daftar, name='daftar'),
    path('keluar/', views.keluar, name='keluar'),
]
