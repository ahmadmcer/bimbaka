from . import views
from django.urls import path

urlpatterns = [
    # Main Pages
    path('', views.beranda, name='beranda'),
    path('materi/', views.materi, name='materi'),
    path('materi/<int:materi_id>/', views.materi_detail, name='materi_detail'),
    path('selesai-materi/<int:materi_id>/',
         views.mark_materi_completed, name='mark_materi_completed'),

    # Practice
    path('latihan/', views.latihan, name='latihan'),
    path('hasil-latihan/', views.hasil_latihan, name='hasil_latihan'),

    # Final Evaluation (untuk keseluruhan materi)
    path('evaluasi/', views.evaluasi, name='evaluasi'),
    path('hasil-evaluasi/', views.hasil_evaluasi, name='hasil_evaluasi'),

    # Authentication
    path('masuk/', views.masuk, name='masuk'),
    path('daftar/', views.daftar, name='daftar'),
    path('keluar/', views.keluar, name='keluar'),
]
