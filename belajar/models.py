from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Profile(models.Model):
    KELAS_CHOICES = [
        ('kelas_2', 'Kelas 2'),
        ('kelas_3', 'Kelas 3'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    kelas = models.CharField(
        max_length=50,
        choices=KELAS_CHOICES,
        blank=True,
        null=True,
        verbose_name='Kelas'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profil Pengguna'
        verbose_name_plural = 'Profil Pengguna'
        db_table = 'profile'

    def __str__(self):
        kelas_display = self.get_kelas_display() if self.kelas else 'Belum Set Kelas'
        nama = self.user.get_full_name() or self.user.username
        return f'{nama} - {kelas_display}'


class NilaiEvaluasi(models.Model):
    """Model untuk menyimpan nilai evaluasi akhir (keseluruhan materi)"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='nilai_evaluasi'
    )
    nilai = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name='Nilai'
    )
    total_soal = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Total Soal'
    )
    jumlah_benar = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Jumlah Benar'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Nilai Evaluasi Akhir'
        verbose_name_plural = 'Nilai Evaluasi Akhir'
        db_table = 'nilai_evaluasi'
        ordering = ['-created_at']

    def __str__(self):
        nilai_str = f"{self.nilai:.1f}" if self.nilai else "Belum Ada"
        nama = self.user.get_full_name() or self.user.username
        return f'{nama} - Evaluasi Akhir - {nilai_str}'

    def get_grade(self):
        """Return letter grade based on score"""
        if self.nilai >= 90:
            return 'A'
        elif self.nilai >= 80:
            return 'B'
        elif self.nilai >= 70:
            return 'C'
        elif self.nilai >= 60:
            return 'D'
        else:
            return 'E'


class JawabanEvaluasi(models.Model):
    """Model untuk menyimpan detail jawaban evaluasi"""
    evaluasi = models.ForeignKey(
        NilaiEvaluasi,
        on_delete=models.CASCADE,
        related_name='jawaban_evaluasi'
    )
    nomor_soal = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Nomor Soal'
    )
    materi_soal = models.CharField(
        max_length=50,
        verbose_name='Materi Soal',
        help_text='Materi asal dari soal ini (contoh: materi_1)'
    )
    soal_pertanyaan = models.TextField(verbose_name='Soal Pertanyaan')
    jawaban_user = models.TextField(verbose_name='Jawaban User')
    jawaban_benar = models.TextField(verbose_name='Jawaban Benar')
    is_correct = models.BooleanField(default=False, verbose_name='Benar/Tidak')
    poin = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0)],
        verbose_name='Poin'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Jawaban Evaluasi'
        verbose_name_plural = 'Jawaban Evaluasi'
        db_table = 'jawaban_evaluasi'
        unique_together = ['evaluasi', 'nomor_soal']
        ordering = ['evaluasi', 'nomor_soal']

    def __str__(self):
        status = 'Benar' if self.is_correct else 'Salah'
        return f'Evaluasi ID: {self.evaluasi.id} - Soal No: {self.nomor_soal} - {status}'


class KemajuanBelajar(models.Model):
    """Model untuk tracking progress belajar per materi"""
    MATERI_CHOICES = [
        ('materi_1', 'Materi 1: Perkalian dengan 0, 10, 100'),
        ('materi_2', 'Materi 2: Perkalian Bersusun'),
        ('materi_3', 'Materi 3: Perkalian Lanjutan'),
        ('materi_4', 'Materi 4: Pembagian Bersusun'),
        ('materi_5', 'Materi 5: Pembagian dengan Sisa'),
        ('materi_6', 'Materi 6: Operasi Campuran'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='kemajuan_belajar'
    )
    materi = models.CharField(
        max_length=50,
        choices=MATERI_CHOICES,
        verbose_name='Materi'
    )
    is_selesai = models.BooleanField(default=False, verbose_name='Selesai')
    progress_persentase = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name='Progress (%)'
    )
    waktu_mulai = models.DateTimeField(auto_now_add=True)
    waktu_selesai = models.DateTimeField(null=True, blank=True)
    catatan = models.TextField(blank=True, verbose_name='Catatan')

    class Meta:
        verbose_name = 'Kemajuan Belajar'
        verbose_name_plural = 'Kemajuan Belajar'
        unique_together = ['user', 'materi']
        db_table = 'kemajuan_belajar'
        ordering = ['user', 'materi']

    def mark_completed(self):
        """Mark materi as completed"""
        self.is_selesai = True
        self.progress_persentase = 100.0
        self.waktu_selesai = timezone.now()
        self.save()

    def update_progress(self, persentase):
        """Update progress percentage"""
        if 0 <= persentase <= 100:
            self.progress_persentase = persentase
            if persentase >= 100:
                self.mark_completed()
            else:
                self.save()

    @classmethod
    def get_user_summary(cls, user):
        """Get summary of user's learning progress"""
        total_materi = len(cls.MATERI_CHOICES)
        selesai = cls.objects.filter(user=user, is_selesai=True).count()
        avg_progress = cls.objects.filter(user=user).aggregate(
            models.Avg('progress_persentase')
        )['progress_persentase__avg'] or 0

        return {
            'total_materi': total_materi,
            'materi_selesai': selesai,
            'persentase_keseluruhan': round((selesai / total_materi) * 100, 2),
            'rata_rata_progress': round(avg_progress, 2)
        }

    @classmethod
    def user_ready_for_evaluation(cls, user):
        """Check if user has completed all materials and ready for evaluation"""
        total_materi = len(cls.MATERI_CHOICES)
        selesai = cls.objects.filter(user=user, is_selesai=True).count()
        return selesai >= total_materi

    def __str__(self):
        status = 'Selesai' if self.is_selesai else f'{self.progress_persentase}%'
        nama = self.user.get_full_name() or self.user.username
        return f'{nama} - {self.get_materi_display()} ({status})'
