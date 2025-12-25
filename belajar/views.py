import random
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib import messages
from .models import Profile, NilaiEvaluasi, JawabanEvaluasi, KemajuanBelajar, NilaiEvaluasiPerMateri
from django.http import HttpResponse
from openpyxl import Workbook
from .forms import UserUpdateForm, ProfileUpdateForm
import os
import joblib
import pandas as pd
from django.conf import settings



# FUNGSI HELPER UNTUK CEK GURU
def is_guru(user):
    """Cek apakah user ada di grup 'Guru'"""
    return user.is_authenticated and user.groups.filter(name='Guru').exists()


def generate_soal_evaluasi_akhir(jumlah_soal=20, kelas='kelas_2'):  # Terima parameter 'kelas'
    """Hasilkan soal evaluasi komprehensif berdasarkan kelas siswa."""
    soal = []

    # ---------------------------------------------------
    # SOAL UNTUK KELAS 2
    # ---------------------------------------------------
    if kelas == 'kelas_2':
        # Materi K2: 1: Penjumlahan Berulang, 2: Komutatif, 3: 1&0, 4: 2&5, 5: 10, 6: Tabel
        kategori_k2 = ['visual', 'komutatif', 'nol_satu', 'dua_lima_sepuluh', 'tabel']
        for i in range(jumlah_soal):
            question_data = {}
            tipe_soal = random.choice(kategori_k2)

            if tipe_soal == 'visual':  # (Materi 1 & 3)
                a = random.randint(2, 5)  # Angka kecil untuk visual
                b = random.randint(2, 4)  # Angka kecil untuk visual
                jawaban = a * b
                question_data = {
                    'type': 'visual', 'question_text': 'Berapa hasil dari apel di atas?',
                    'a_range': [1] * a, 'b_range': [1] * b, 'op': '×', 'icon': '🍎',
                }
            elif tipe_soal == 'komutatif':  # (Materi 2)
                a = random.randint(3, 9)
                b = random.randint(2, 8)
                jawaban = a * b
                question_data = {
                    'type': 'text', 'question_text': f'Berapakah {b} × {a}?',  # Dibalik
                }
            elif tipe_soal == 'nol_satu':  # (Materi 3)
                a = random.randint(5, 20)
                b = random.choice([0, 1])
                jawaban = a * b
                question_data = {'type': 'text', 'question_text': f'Berapakah {a} × {b}?', }
            elif tipe_soal == 'dua_lima_sepuluh':  # (Materi 4 & 5)
                a = random.randint(3, 9)
                b = random.choice([2, 5, 10])
                jawaban = a * b
                question_data = {'type': 'text', 'question_text': f'Berapakah {a} × {b}?', }
            else:  # 'tabel' (Materi 6)
                a = random.randint(3, 9)
                b = random.randint(3, 9)
                jawaban = a * b
                question_data = {'type': 'text', 'question_text': f'Berapakah {a} × {b}?', }

            # Buat pilihan jawaban untuk K2
            pilihan = [str(jawaban)]
            while len(pilihan) < 4:
                wrong = jawaban + random.randint(-5, 5)
                if wrong != jawaban and wrong >= 0 and str(wrong) not in pilihan:
                    pilihan.append(str(wrong))
            random.shuffle(pilihan)
            question_data.update({
                'choices': pilihan, 'correct_answer': str(jawaban),
                'materi': f'materi_{random.randint(1, 6)}',
            })
            soal.append(question_data)

    # ---------------------------------------------------
    # SOAL UNTUK KELAS 3
    # ---------------------------------------------------
    elif kelas == 'kelas_3':
        soal_per_materi = jumlah_soal // 6
        sisa_soal = jumlah_soal % 6
        for materi_id in range(1, 7):
            jumlah_untuk_materi = soal_per_materi + (1 if materi_id <= sisa_soal else 0)
            for _ in range(jumlah_untuk_materi):
                question_data = {}
                if materi_id == 1:  # Perkalian dengan 0, 10, 100
                    a = random.randint(1, 12);
                    b = random.choice([0, 10, 100]);
                    jawaban = a * b
                    question_data = {'type': 'text', 'question_text': f'Berapakah {a} × {b}?', }
                elif materi_id == 2:  # Perkalian bersusun
                    a = random.randint(10, 99);
                    b = random.randint(2, 9);
                    jawaban = a * b
                    question_data = {'type': 'text', 'question_text': f'Berapakah {a} × {b}?', }
                elif materi_id == 3:  # Pembagian dengan 1
                    a = random.randint(5, 50);
                    b = 1;
                    jawaban = a // b
                    question_data = {'type': 'text', 'question_text': f'Berapakah {a} ÷ {b}?', }
                elif materi_id == 4:  # Pembagian bersusun (Porogapit)
                    divisor = random.randint(2, 9);
                    quotient = random.randint(10, 99);
                    dividend = divisor * quotient
                    jawaban = quotient
                    question_data = {'type': 'text', 'question_text': f'Berapakah {dividend} ÷ {divisor}?', }
                elif materi_id == 5:  # Operasi Campuran
                    a = random.randint(2, 9);
                    b = random.randint(2, 9);
                    c = random.randint(1, 20)
                    jawaban = (a * b) + c
                    question_data = {'type': 'text', 'question_text': f'Berapakah ({a} × {b}) + {c}?', }
                else:  # Materi 6: Soal Cerita
                    items = random.randint(3, 8);
                    per_group = random.randint(2, 6);
                    given_away = random.randint(1, items * per_group // 2)
                    jawaban = (items * per_group) - given_away
                    question_data = {'type': 'text',
                                     'question_text': f'Ana punya {items} kotak. Tiap kotak isi {per_group} permen. Diberikan {given_away}. Berapa sisanya?', }

                # Pilihan jawaban untuk K3
                pilihan = [str(jawaban)]
                while len(pilihan) < 4:
                    wrong = jawaban + random.randint(-10, 10)
                    if wrong != jawaban and wrong >= 0 and str(wrong) not in pilihan:
                        pilihan.append(str(wrong))
                random.shuffle(pilihan)
                question_data.update({
                    'choices': pilihan, 'correct_answer': str(jawaban),
                    'materi': f'materi_{materi_id}',
                })
                soal.append(question_data)

    random.shuffle(soal)
    return soal


# HALAMAN UTAMA
@login_required
def beranda(request):
    if is_guru(request.user):
        try:
            guru_kelas = request.user.profile.kelas
        except Profile.DoesNotExist:
            guru_kelas = None
        if guru_kelas:
            siswa_list = User.objects.filter(groups__name='Siswa', profile__kelas=guru_kelas)
        else:
            siswa_list = User.objects.none()
        context = {
            'total_siswa': siswa_list.count(),
            'siswa_list': siswa_list,
            'guru_kelas': guru_kelas,
        }
        return render(request, 'pages/dasbor_guru.html', context)
    else:
        progress_summary = KemajuanBelajar.get_user_summary(request.user)
        ready_for_evaluation = KemajuanBelajar.user_ready_for_evaluation(request.user)
        latest_evaluation = NilaiEvaluasi.objects.filter(
            user=request.user).order_by('-created_at').first()
        context = {
            'progress_summary': progress_summary,
            'ready_for_evaluation': ready_for_evaluation,
            'latest_evaluation': latest_evaluation,
        }
        return render(request, 'pages/beranda.html', context)


@login_required
def materi(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    kelas = profile.kelas or 'kelas_2'
    if kelas == 'kelas_3':
        materi_info = {
            'materi_1': {'id': 1, 'title': 'Perkalian 0, 10, 100', 'icon': '💯'},
            'materi_2': {'id': 2, 'title': 'Perkalian Bersusun', 'icon': '📝'},
            'materi_3': {'id': 3, 'title': 'Pembagian 1 & 0', 'icon': '🧠'},
            'materi_4': {'id': 4, 'title': 'Pembagian Bersusun', 'icon': '🏠'},
            'materi_5': {'id': 5, 'title': 'Operasi Campuran', 'icon': '🧮'},
            'materi_6': {'id': 6, 'title': 'Soal Cerita', 'icon': '🌍'},
        }
        header_title = "Matematika Kelas 3"
        header_desc = "Pilih materi untuk melanjutkan petualanganmu!"
    else:
        materi_info = {
            'materi_1': {'id': 1, 'title': 'Penjumlahan Berulang', 'icon': '🍎'},
            'materi_2': {'id': 2, 'title': 'Sifat Komutatif', 'icon': '🔄'},
            'materi_3': {'id': 3, 'title': 'Perkalian 1 & 0', 'icon': '⭕'},
            'materi_4': {'id': 4, 'title': 'Perkalian 2 & 5', 'icon': '✌️'},
            'materi_5': {'id': 5, 'title': 'Perkalian 10', 'icon': '🔟'},
            'materi_6': {'id': 6, 'title': 'Tabel Perkalian', 'icon': '📊'},
        }
        header_title = "Matematika Kelas 2"
        header_desc = "Belajar matematika yang menyenangkan! Mulai dari sini!"
    progress_db = KemajuanBelajar.objects.filter(user=request.user)
    progress_data = {p.materi: p for p in progress_db}
    learning_path = []
    active_lesson_found = False
    total_selesai = 0
    for key in sorted(materi_info.keys()):
        info = materi_info[key]
        progress = progress_data.get(key)
        is_selesai = progress.is_selesai if progress else False
        status = "locked"
        if is_selesai:
            status = "completed"
            total_selesai += 1
        elif not active_lesson_found:
            status = "active"
            active_lesson_found = True
        info['status'] = status
        info['key'] = key
        learning_path.append(info)
    total_materi = len(materi_info)
    progress_percentage = (total_selesai / total_materi) * 100 if total_materi > 0 else 0
    context = {
        'learning_path': learning_path, 'header_title': header_title,
        'header_desc': header_desc, 'total_selesai': total_selesai,
        'total_materi': total_materi, 'progress_percentage': progress_percentage,
    }
    return render(request, 'pages/materi.html', context)


@login_required
def materi_detail(request, materi_id):
    # 1. Validasi Materi
    if materi_id not in range(1, 7):
        messages.error(request, 'Materi tidak ditemukan!')
        return redirect('materi')

    # 2. Ambil Profil & Kelas
    profile, created = Profile.objects.get_or_create(user=request.user)
    kelas = profile.kelas or 'kelas_2'

    # 3. Update Progress Belajar
    kemajuan, created = KemajuanBelajar.objects.get_or_create(
        user=request.user, materi=f'materi_{materi_id}',
        defaults={'progress_persentase': 50.0}
    )
    if created or kemajuan.progress_persentase < 50:
        kemajuan.progress_persentase = 50.0
        kemajuan.save()

    # 4. Tentukan Template
    template_name = f'pages/materi/{kelas}/materi_{materi_id}.html'

    # 5. [BARU] Ambil Data Quiz untuk Popup
    quiz_data = get_mini_quiz(kelas, materi_id)

    # 6. Kirim ke Template
    context = {
        'materi_id': materi_id,
        'quiz_data': quiz_data
    }
    return render(request, template_name, context)

@login_required
def mark_materi_completed(request, materi_id):
    if materi_id not in range(1, 7):
        messages.error(request, 'Materi tidak ditemukan!')
        return redirect('materi')
    kemajuan, created = KemajuanBelajar.objects.get_or_create(
        user=request.user, materi=f'materi_{materi_id}',
        defaults={'progress_persentase': 0.0}
    )
    kemajuan.mark_completed()
    messages.success(request, f'Materi {materi_id} berhasil ditandai sebagai selesai!')
    return redirect('materi')


# EVALUASI AKHIR
@login_required
def evaluasi(request):
    # 1. Cek apakah user sudah menyelesaikan semua materi
    if not KemajuanBelajar.user_ready_for_evaluation(request.user):
        messages.error(request,'Ups! Kamu harus menyelesaikan semua materi dulu sebelum ikut Evaluasi Akhir. Semangat! 🚀')
        return redirect('materi')
    latest_evaluasi = NilaiEvaluasi.objects.filter(
        user=request.user).order_by('-created_at').first()
    try:
        profile = request.user.profile
        kelas_siswa = profile.kelas
    except Profile.DoesNotExist:
        kelas_siswa = 'kelas_2'
    if request.method == 'GET':
        if 'page' not in request.GET or request.GET.get('start') == '1':
            soal = generate_soal_evaluasi_akhir(jumlah_soal=20, kelas=kelas_siswa)
            request.session['soal_evaluasi'] = soal
            request.session['jawaban_evaluasi'] = []
        soal = request.session.get('soal_evaluasi', [])
        if not soal:
            return redirect('/evaluasi/?start=1')
        paginator = Paginator(soal, 1)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        progress_percentage = int((page_obj.number / len(soal)) * 100)
        jawaban_user = request.session.get('jawaban_evaluasi', [])
        jawaban_chosen = jawaban_user[page_obj.number -
                                      1] if page_obj.number <= len(jawaban_user) else None
        context = {
            'page_obj': page_obj, 'progress_percentage': progress_percentage,
            'jawaban_chosen': jawaban_chosen, 'latest_evaluasi': latest_evaluasi,
        }
        return render(request, 'pages/evaluasi.html', context)
    elif request.method == 'POST':
        jawaban = request.POST.get('jawaban')
        current_page = int(request.GET.get('page', 1))
        if jawaban:
            jawaban_user = request.session.get('jawaban_evaluasi', [])
            while len(jawaban_user) < current_page:
                jawaban_user.append(None)
            jawaban_user[current_page - 1] = jawaban
            request.session['jawaban_evaluasi'] = jawaban_user
        soal = request.session.get('soal_evaluasi', [])
        if current_page >= len(soal):
            return finalize_evaluasi(request)
        else:
            next_page = current_page + 1
            return redirect(f'/evaluasi/?page={next_page}')


def get_ai_recommendation(evaluasi, kelas_siswa):
    """
    Fungsi untuk memprediksi rekomendasi materi menggunakan model ML.
    """
    try:
        # 1. Tentukan path model berdasarkan kelas
        model_filename = ''
        if kelas_siswa == 'kelas_2':
            model_filename = 'model_dummy_kelas_2.joblib'
        elif kelas_siswa == 'kelas_3':
            model_filename = 'model_dummy_kelas_3.joblib'
        else:
            return "Kelas tidak dikenali"

        # Construct full path (sesuaikan path folder ml_models Anda)
        # Asumsi folder ml_models ada di dalam folder aplikasi 'belajar'
        model_path = os.path.join(settings.BASE_DIR, 'belajar', 'ml_models', model_filename)

        if not os.path.exists(model_path):
            return f"Model tidak ditemukan: {model_filename}"

        # 2. Load Model
        model = joblib.load(model_path)

        # 3. Siapkan Data Input (Features)
        # Model dilatih dengan urutan kolom Nilai Materi 1 s/d 6
        # Kita harus mengambil nilai dari database dengan urutan yang SAMA

        # Ambil breakdown nilai yang sudah dihitung sebelumnya
        breakdown = NilaiEvaluasiPerMateri.objects.filter(evaluasi_utama=evaluasi)

        # Buat dictionary untuk akses cepat: {'materi_1': 80.0, 'materi_2': 70.0, ...}
        nilai_map = {item.materi: item.nilai for item in breakdown}

        # Urutkan nilai menjadi list [nilai_m1, nilai_m2, ..., nilai_m6]
        # PENTING: Urutan list harus sama persis dengan urutan kolom saat training di create_model.py
        input_features = []
        for i in range(1, 7):
            materi_key = f'materi_{i}'
            # Default 0 jika tidak ada nilai (walaupun seharusnya ada)
            nilai = nilai_map.get(materi_key, 0.0)
            input_features.append(nilai)

        # Format data ke DataFrame (karena model dilatih pake DF dgn nama kolom tertentu)
        # Nama kolom harus mengandung kata "NILAI" agar sesuai logic di create_model.py
        feature_names = [f'NILAI_{i}' for i in range(1, 7)]
        X_input = pd.DataFrame([input_features], columns=feature_names)

        # 4. Lakukan Prediksi
        prediction = model.predict(X_input)

        # Hasil prediksi berupa array, ambil elemen pertama
        return prediction[0]

    except Exception as e:
        print(f"Error Prediction: {e}")
        return "Gagal memproses rekomendasi"

def finalize_evaluasi(request):
    soal = request.session.get('soal_evaluasi', [])
    jawaban_user = request.session.get('jawaban_evaluasi', [])
    if not soal or not jawaban_user:
        messages.error(request, 'Data evaluasi tidak ditemukan!')
        return redirect('materi')
    total_soal = len(soal)
    jumlah_benar = 0
    evaluasi = NilaiEvaluasi.objects.create(
        user=request.user, total_soal=total_soal,
        jumlah_benar=0, nilai=0.0
    )
    for i, soal_item in enumerate(soal):
        user_answer = jawaban_user[i] if i < len(jawaban_user) else None
        correct_answer = soal_item['correct_answer']
        is_correct = str(user_answer) == str(correct_answer)
        if is_correct:
            jumlah_benar += 1
        JawabanEvaluasi.objects.create(
            evaluasi=evaluasi, nomor_soal=i + 1,
            materi_soal=soal_item['materi'],
            soal_pertanyaan=soal_item['question_text'],  # Perbaikan KeyError
            pilihan_jawaban=soal_item['choices'],
            jawaban_user=user_answer or '',
            jawaban_benar=correct_answer,
            is_correct=is_correct,
            poin=1.0 if is_correct else 0.0
        )
    evaluasi.jumlah_benar = jumlah_benar
    evaluasi.nilai = (jumlah_benar / total_soal) * 100
    evaluasi.save()
    evaluasi.calculate_material_breakdown()
    try:
        profile = request.user.profile
        kelas_siswa = profile.kelas

        # Panggil fungsi prediksi
        rekomendasi = get_ai_recommendation(evaluasi, kelas_siswa)

        # Simpan ke database
        evaluasi.rekomendasi_materi = rekomendasi
        evaluasi.save()

    except Exception as e:
        print(f"Error saat menjalankan ML: {e}")
    request.session['evaluasi_id'] = evaluasi.id
    for key in ['soal_evaluasi', 'jawaban_evaluasi']:
        if key in request.session:
            del request.session[key]
    return redirect('hasil_evaluasi')


@login_required
def hasil_evaluasi(request):
    evaluasi_id = request.session.get('evaluasi_id')
    if not evaluasi_id:
        messages.error(request, 'Hasil evaluasi tidak ditemukan!')
        return redirect('materi')
    evaluasi = get_object_or_404(
        NilaiEvaluasi, id=evaluasi_id, user=request.user)
    jawaban_detail = JawabanEvaluasi.objects.filter(
        evaluasi=evaluasi).order_by('nomor_soal')
    breakdown_per_materi = NilaiEvaluasiPerMateri.objects.filter(
        evaluasi_utama=evaluasi
    ).order_by('materi')
    benar = evaluasi.jumlah_benar
    salah = evaluasi.total_soal - evaluasi.jumlah_benar
    total = evaluasi.total_soal
    percentage = int(evaluasi.nilai)
    benar_width = int((benar / total) * 100) if total > 0 else 0
    salah_width = int((salah / total) * 100) if total > 0 else 0
    grade = evaluasi.get_grade()
    grade_color = evaluasi.get_grade_color()
    if percentage >= 90:
        message = '🎉 Excellent! Pemahaman kamu sangat luar biasa!'
    elif percentage >= 80:
        message = '👏 Very Good! Kamu sudah memahami materi dengan sangat baik!'
    elif percentage >= 70:
        message = '👍 Good! Hasil yang cukup memuaskan!'
    elif percentage >= 60:
        message = '😐 Perlu improvement. Coba pelajari materi yang masih kurang!'
    else:
        message = '😟 Perlu belajar lebih giat. Jangan menyerah, ulangi lagi!'
    weak_materials = [b for b in breakdown_per_materi if b.nilai < 70]
    if 'evaluasi_id' in request.session:
        del request.session['evaluasi_id']
    context = {
        'evaluasi': evaluasi, 'jawaban_detail': jawaban_detail,
        'breakdown_per_materi': breakdown_per_materi,
        'weak_materials': weak_materials, 'benar': benar,
        'salah': salah, 'total': total, 'percentage': percentage,
        'benar_width': benar_width, 'salah_width': salah_width,
        'grade': grade, 'grade_color': grade_color, 'message': message,
    }
    return render(request, 'pages/hasil_evaluasi.html', context)


# FUNGSI HALAMAN GURU
@login_required
@user_passes_test(is_guru, login_url='beranda')
def guru_nilai(request):
    try:
        guru_kelas = request.user.profile.kelas
    except Profile.DoesNotExist:
        guru_kelas = None
    if guru_kelas:
        students = User.objects.filter(groups__name='Siswa', profile__kelas=guru_kelas).prefetch_related(
            'profile', 'nilai_evaluasi', 'nilai_evaluasi__breakdown_per_materi'
        )
    else:
        students = User.objects.none()
    student_grades = []
    for student in students:
        latest_eval = student.nilai_evaluasi.order_by('-created_at').first()
        grades = {'materi_1': None, 'materi_2': None, 'materi_3': None,
                  'materi_4': None, 'materi_5': None, 'materi_6': None, }
        final_score = None
        if latest_eval:
            final_score = latest_eval.nilai
            breakdown = latest_eval.breakdown_per_materi.all()
            for b in breakdown:
                if b.materi in grades:
                    grades[b.materi] = b.nilai
        student_grades.append({
            'student': student, 'final_score': final_score, 'grades': grades
        })
    context = {
        'student_data': student_grades, 'guru_kelas': guru_kelas,
    }
    return render(request, 'pages/guru_nilai.html', context)


# AUTHENTICATION
def masuk(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        peran = request.POST.get('peran')  # Ambil peran dari form (siswa/guru)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Pengguna valid, sekarang cek peran mereka
            is_siswa = user.groups.filter(name='Siswa').exists()
            is_guru_check = is_guru(user)  # Menggunakan fungsi is_guru()

            # KASUS 1: Login sebagai SISWA di form SISWA
            if peran == 'siswa' and is_siswa:
                login(request, user)
                return redirect('beranda')

            # KASUS 2: Login sebagai GURU di form GURU
            elif peran == 'guru' and is_guru_check:
                login(request, user)
                return redirect('beranda')

            # KASUS 3: Peran tidak cocok (Misal: Guru login di form Siswa)
            elif peran == 'siswa' and not is_siswa:
                messages.error(request, 'Akun ini bukan akun Siswa. Silakan gunakan tab Login Guru.')
            elif peran == 'guru' and not is_guru_check:
                messages.error(request, 'Akun ini bukan akun Guru. Silakan gunakan tab Login Siswa.')

            # KASUS 4: Pengguna tidak punya peran (jarang terjadi)
            else:
                messages.error(request, 'Peran akun Anda tidak terdefinisi.')

        else:
            # Username atau password salah
            messages.error(request, 'Username atau password salah!')

    # Jika login gagal (POST) atau jika method GET, tampilkan halaman login
    return render(request, 'pages/auth/masuk.html')


def daftar(request):
    SECRET_TEACHER_CODE = 'BIMBAKA2025'
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        peran = request.POST.get('peran')
        kelas = request.POST.get('kelas')
        kode_guru = request.POST.get('kode_guru')

        if password != confirm_password:
            messages.error(request, 'Password tidak sesuai!')
            return redirect('daftar')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah terdaftar!')
            return redirect('daftar')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah terdaftar!')
            return redirect('daftar')

        role_name = ''
        if not kelas:
            messages.error(request, 'Silakan pilih kelas Anda (atau kelas yang Anda ajar)!')
            return redirect('daftar')
        if peran == 'guru':
            if kode_guru == SECRET_TEACHER_CODE:
                role_name = 'Guru'
            else:
                messages.error(request, 'Kode Pendaftaran Guru salah!')
                return redirect('daftar')
        elif peran == 'siswa':
            role_name = 'Siswa'
        else:
            messages.error(request, 'Silakan pilih peran Anda (Siswa/Guru)!')
            return redirect('daftar')

        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name
        )
        group, _ = Group.objects.get_or_create(name=role_name)
        user.groups.add(group)
        Profile.objects.create(user=user, kelas=kelas)
        messages.success(request, 'Akun berhasil dibuat! Silakan masuk.')
        return redirect('masuk')
    return render(request, 'pages/auth/daftar.html')


@login_required
def riwayat_evaluasi(request):
    # Hanya ambil riwayat untuk siswa yang sedang login
    # Pastikan yang diambil BUKAN guru
    if is_guru(request.user):
        return redirect('beranda')  # Guru tidak punya riwayat, arahkan ke dasbor

    # Ambil semua evaluasi user, urutkan dari yang terbaru
    riwayat_list = NilaiEvaluasi.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'riwayat_list': riwayat_list
    }
    return render(request, 'pages/riwayat_evaluasi.html', context)


@login_required
@user_passes_test(is_guru, login_url='beranda')
def guru_riwayat_siswa(request, siswa_id):
    """Halaman untuk guru melihat detail riwayat evaluasi seorang siswa."""

    # 1. Dapatkan guru dan kelasnya
    try:
        guru_kelas = request.user.profile.kelas
    except Profile.DoesNotExist:
        messages.error(request, 'Profil guru tidak ditemukan.')
        return redirect('beranda')

    # 2. Dapatkan siswa yang diminta
    siswa = get_object_or_404(User, id=siswa_id, groups__name='Siswa')

    # 3. Validasi: Pastikan guru ini mengajar siswa tsb
    if siswa.profile.kelas != guru_kelas:
        messages.error(request, 'Anda tidak memiliki izin untuk melihat siswa ini.')
        return redirect('guru_nilai')

    # 4. Ambil semua riwayat evaluasi siswa, prefetch jawaban terkait
    #    Ini mengambil SEMUA percobaan evaluasi siswa, diurutkan dari yang terbaru
    evaluasi_list = NilaiEvaluasi.objects.filter(
        user=siswa
    ).prefetch_related(
        'jawaban_evaluasi'  # Ini akan mengambil semua detail jawaban untuk setiap evaluasi
    ).order_by('-created_at')  # Terbaru di atas

    context = {
        'siswa': siswa,
        'evaluasi_list': evaluasi_list
    }
    return render(request, 'pages/guru_riwayat_siswa.html', context)


# --- TAMBAHKAN FUNGSI BARU INI ---
@login_required
@user_passes_test(is_guru, login_url='beranda')
def export_nilai_excel(request):
    """Menangani ekspor data nilai siswa ke file Excel."""

    # 1. Dapatkan kelas guru
    try:
        guru_kelas = request.user.profile.kelas
    except Profile.DoesNotExist:
        messages.error(request, 'Profil guru tidak ditemukan.')
        return redirect('guru_nilai')

    # 2. Siapkan file Excel (Workbook)
    wb = Workbook()
    ws = wb.active
    ws.title = f"Nilai {request.user.profile.get_kelas_display()}"

    # 3. Buat Header
    headers = [
        "Nama Siswa", "Username",
        "Materi 1", "Materi 2", "Materi 3",
        "Materi 4", "Materi 5", "Materi 6",
        "Nilai Akhir"
    ]
    ws.append(headers)

    # 4. Ambil data siswa (logika yang sama dengan halaman 'guru_nilai')
    if guru_kelas:
        students = User.objects.filter(groups__name='Siswa', profile__kelas=guru_kelas).prefetch_related(
            'profile', 'nilai_evaluasi', 'nilai_evaluasi__breakdown_per_materi'
        )
    else:
        students = User.objects.none()

    # 5. Isi data siswa ke baris Excel
    for student in students:
        latest_eval = student.nilai_evaluasi.order_by('-created_at').first()

        grades = {
            'materi_1': None, 'materi_2': None, 'materi_3': None,
            'materi_4': None, 'materi_5': None, 'materi_6': None,
        }
        final_score = None

        if latest_eval:
            final_score = latest_eval.nilai
            breakdown = latest_eval.breakdown_per_materi.all()
            for b in breakdown:
                if b.materi in grades:
                    grades[b.materi] = b.nilai

        # Buat baris data
        row_data = [
            student.get_full_name(),
            student.username,
            grades['materi_1'],
            grades['materi_2'],
            grades['materi_3'],
            grades['materi_4'],
            grades['materi_5'],
            grades['materi_6'],
            final_score
        ]
        # Tambahkan baris ke sheet
        ws.append(row_data)

    # 6. Buat Respon HTTP untuk mengunduh file
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    # Tentukan nama file
    filename = f"daftar_nilai_{guru_kelas}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Simpan workbook ke respon
    wb.save(response)

    return response

def keluar(request):
    logout(request)
    return redirect('masuk')


# Tambahkan import random jika belum ada di file (sudah ada di snippet Anda)

def get_mini_quiz(kelas, materi_id):
    """
    Menghasilkan 3 pasang soal dan jawaban untuk mode Drag & Drop (Match Pairs).
    """
    pairs = []
    generated_answers = set()  # Untuk mencegah duplikat jawaban

    # Loop untuk membuat 3 pasang soal
    target_pairs = 3
    attempts = 0

    while len(pairs) < target_pairs and attempts < 20:
        attempts += 1
        q_text = ""
        a_text = ""

        # ================= KELAS 2 =================
        if kelas == 'kelas_2':
            if materi_id == 1:  # Penjumlahan Berulang
                n = random.randint(2, 5)
                val = random.randint(2, 5)
                q_text = " + ".join([str(val)] * n)
                a_text = f"{n} × {val}"
            elif materi_id == 2:  # Komutatif
                a = random.randint(3, 9);
                b = random.randint(2, 8)
                q_text = f"{a} × {b}"
                a_text = f"{b} × {a}"
            elif materi_id == 3:  # 1 & 0
                val = random.randint(5, 20)
                pengali = random.choice([0, 1])
                q_text = f"{val} × {pengali}"
                a_text = str(val * pengali)
            elif materi_id == 4:  # 2 & 5
                a = random.randint(3, 9)
                b = random.choice([2, 5])
                q_text = f"{a} × {b}"
                a_text = str(a * b)
            elif materi_id == 5:  # 10
                a = random.randint(2, 9)
                q_text = f"{a} × 10"
                a_text = f"{a}0"
            else:  # Tabel Lain
                a = random.randint(3, 8);
                b = random.randint(3, 8)
                q_text = f"{a} × {b}"
                a_text = str(a * b)

        # ================= KELAS 3 =================
        elif kelas == 'kelas_3':
            if materi_id == 1:  # 0, 10, 100
                a = random.randint(2, 9)
                b = random.choice([10, 100])
                q_text = f"{a} × {b}"
                a_text = str(a * b)
            elif materi_id == 2:  # Bersusun (Angka simpel)
                a = random.randint(11, 20);
                b = random.choice([2, 3])
                q_text = f"{a} × {b}"
                a_text = str(a * b)
            elif materi_id == 3:  # Bagi 1 & 0
                if random.choice([True, False]):
                    q_text = f"0 ÷ {random.randint(2, 9)}"
                    a_text = "0"
                else:
                    val = random.randint(5, 20)
                    q_text = f"{val} ÷ 1"
                    a_text = str(val)
            elif materi_id == 4:  # Porogapit Simpel
                res = random.randint(10, 20);
                div = random.randint(2, 3)
                q_text = f"{res * div} ÷ {div}"
                a_text = str(res)
            elif materi_id == 5:  # Campuran
                a = random.randint(2, 5);
                b = random.randint(2, 4);
                c = random.randint(1, 5)
                q_text = f"({a}×{b}) + {c}"
                a_text = str((a * b) + c)
            else:  # Soal Cerita (Versi Pendek)
                item = random.randint(3, 6);
                price = random.randint(2, 5)
                q_text = f"{item} kotak isi {price}"
                a_text = str(item * price)

        # Cek Duplikat Jawaban (Agar unik saat di-match)
        if a_text not in generated_answers:
            generated_answers.add(a_text)
            pairs.append({
                'id': len(pairs) + 1,
                'question': q_text,
                'answer': a_text
            })

    # Pisahkan soal dan jawaban untuk dikirim ke template
    questions = pairs[:]
    answers = pairs[:]

    # Acak urutan jawaban agar tidak bersebelahan langsung dengan soalnya
    random.shuffle(answers)

    return {
        'type': 'drag_drop',  # Penanda untuk template
        'questions': questions,
        'answers': answers,
        'total_pairs': len(pairs)
    }

@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        # Perhatikan penambahan request.FILES di baris bawah ini untuk menangani gambar
        profile, created = Profile.objects.get_or_create(user=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profil berhasil diperbarui!')
            return redirect('edit_profile')
    else:
        profile, created = Profile.objects.get_or_create(user=request.user)
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'pages/auth/edit_profile.html', context)


@login_required
def hapus_foto_profil(request):
    """Menghapus foto profil pengguna."""
    try:
        profile = request.user.profile
        if profile.foto:
            # Hapus file fisik dan set field ke None
            profile.foto.delete(save=False)
            profile.foto = None
            profile.save()
            messages.success(request, 'Foto profil berhasil dihapus.')
        else:
            messages.warning(request, 'Anda belum memiliki foto profil.')
    except Profile.DoesNotExist:
        messages.error(request, 'Profil tidak ditemukan.')

    return redirect('edit_profile')