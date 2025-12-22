from . import views
from django.urls import path

urlpatterns = [
    # Main Pages
    path('', views.beranda, name='beranda'),
    path('materi/', views.materi, name='materi'),
    path('materi/<int:materi_id>/', views.materi_detail, name='materi_detail'),
    path('selesai-materi/<int:materi_id>/',
         views.mark_materi_completed, name='mark_materi_completed'),

    # Practice (REMOVED)
    # path('latihan/', views.latihan, name='latihan'),
    # path('hasil-latihan/', views.hasil_latihan, name='hasil_latihan'),

    # Final Evaluation (untuk keseluruhan materi)
    path('evaluasi/', views.evaluasi, name='evaluasi'),
    path('hasil-evaluasi/', views.hasil_evaluasi, name='hasil_evaluasi'),
    path('riwayat-evaluasi/', views.riwayat_evaluasi, name='riwayat_evaluasi'),
    path('export-nilai-excel/', views.export_nilai_excel, name='export_nilai_excel'),

    # Halaman Khusus Guru
    path('guru-nilai/', views.guru_nilai, name='guru_nilai'),
    path('riwayat-siswa/<int:siswa_id>/', views.guru_riwayat_siswa, name='guru_riwayat_siswa'),
    # Authentication
    path('masuk/', views.masuk, name='masuk'),
    path('daftar/', views.daftar, name='daftar'),
    path('keluar/', views.keluar, name='keluar'),
    path('profil/edit/', views.edit_profile, name='edit_profile'),
    path('profil/hapus-foto/', views.hapus_foto_profil, name='hapus_foto_profil'),
]