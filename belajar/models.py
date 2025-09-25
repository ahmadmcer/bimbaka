from django.db import models
from django.contrib.auth.models import User


# Hasil Jawaban
# Siswa: ForeignKey ke User
# Topik: Enum Perkalian atau Pembagian
# Materi: Array materi yang diambil sesuai topik
# Pertanyaan: Soal yang dikerjakan
# Jawaban: Jawaban yang diberikan
# Benar: Boolean apakah jawaban benar atau salah
# Waktu: Timestamp kapan jawaban diberikan

# class HasilJawaban(models.Model):
#     siswa = models.ForeignKey(User, on_delete=models.CASCADE)
#     topik = models.CharField(max_length=50)
#     materi = models.CharField(max_length=255)
#     pertanyaan = models.CharField(max_length=255)
#     jawaban = models.CharField(max_length=50)
#     benar = models.BooleanField(default=False)
#     waktu = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'{self.siswa.first_name} {self.siswa.last_name} - {self.pertanyaan} = {self.jawaban}'

class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=50)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} - {self.question} = {self.answer}'
