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


def get_mini_quiz(kelas, materi_id):
    soal = {}

    # ==========================================
    # KELAS 2 (DASAR PERKALIAN)
    # ==========================================
    if kelas == 'kelas_2':

        # Materi 1: Penjumlahan Berulang
        # Contoh: 3 + 3 + 3 + 3 = ... x ...
        if materi_id == 1:
            a = random.randint(2, 5)  # Jumlah kelompok (pengali)
            b = random.randint(2, 6)  # Angka yang dijumlah
            soal = {
                'pertanyaan': f"Bentuk perkalian dari: {' + '.join([str(b)] * a)} adalah...",
                'pilihan': [
                    f"{a} × {b}",  # Benar
                    f"{b} × {a}",  # Salah (konsep terbalik)
                    f"{a} + {b}",
                    f"{a * b}"
                ],
                'jawaban_benar': f"{a} × {b}"
            }

        # Materi 2: Sifat Komutatif (Pertukaran)
        # Contoh: 4 x 5 = ... x 4
        elif materi_id == 2:
            a = random.randint(3, 9)
            b = random.randint(2, 8)
            soal = {
                'pertanyaan': f"Sifat pertukaran: {a} × {b} = ... × {a}",
                'pilihan': [str(b), str(a), str(a + b), str(a * b)],
                'jawaban_benar': str(b)
            }

        # Materi 3: Perkalian 1 & 0
        # Contoh: 8 x 1 = ... atau 9 x 0 = ...
        elif materi_id == 3:
            angka = random.randint(5, 50)
            pengali = random.choice([0, 1])
            soal = {
                'pertanyaan': f"Berapakah hasil dari {angka} × {pengali} ?",
                'pilihan': [str(angka * pengali), str(angka), str(pengali), "10"],
                'jawaban_benar': str(angka * pengali)
            }

        # Materi 4: Perkalian 2 & 5
        # Contoh: 7 x 5 = ...
        elif materi_id == 4:
            a = random.randint(3, 9)
            b = random.choice([2, 5])
            soal = {
                'pertanyaan': f"Hitunglah: {a} × {b} = ...",
                'pilihan': [str(a * b), str(a * b + b), str(a * b - b), str(a + b)],
                'jawaban_benar': str(a * b)
            }

        # Materi 5: Perkalian 10
        # Contoh: 6 x 10 = ...
        elif materi_id == 5:
            a = random.randint(2, 9)
            soal = {
                'pertanyaan': f"Berapakah {a} × 10 ?",
                'pilihan': [f"{a}0", f"{a}00", f"{a + 10}", "100"],
                'jawaban_benar': f"{a}0"
            }

        # Materi 6: Tabel Perkalian (3, 4, 6, 7, 8, 9)
        # Soal acak yang agak sulit
        else:
            a = random.randint(3, 9)
            b = random.randint(3, 9)
            # Pastikan bukan perkalian mudah (1,2,5,10)
            while b in [1, 2, 5, 10]:
                b = random.randint(3, 9)

            soal = {
                'pertanyaan': f"Ayo tebak: {a} × {b} = ...",
                'pilihan': [str(a * b), str(a * b + 2), str(a * b - 1), str(a + b)],
                'jawaban_benar': str(a * b)
            }

    # ==========================================
    # KELAS 3 (LANJUTAN)
    # ==========================================
    elif kelas == 'kelas_3':

        # Materi 1: Perkalian 0, 10, 100
        # Contoh: 15 x 100 = ...
        if materi_id == 1:
            a = random.randint(2, 9)
            b = random.choice([10, 100])
            soal = {
                'pertanyaan': f"Hitung cepat: {a} × {b} = ...",
                'pilihan': [str(a * b), str(a * b * 10), str(a + b), str(b)],
                'jawaban_benar': str(a * b)
            }

        # Materi 2: Perkalian Bersusun
        # Contoh: 12 x 3 = ... (Angka puluhan x satuan)
        elif materi_id == 2:
            a = random.randint(11, 25)
            b = random.randint(2, 4)
            soal = {
                'pertanyaan': f"Berapa hasil dari {a} × {b} ?",
                'pilihan': [str(a * b), str(a * b + 2), str(a * b - 2), str(a + b)],
                'jawaban_benar': str(a * b)
            }

        # Materi 3: Pembagian 1 & 0
        # Contoh: 0 : 5 = ... atau 8 : 1 = ...
        elif materi_id == 3:
            tipe = random.choice(['nol', 'satu'])
            if tipe == 'nol':
                a = 0
                b = random.randint(2, 10)
                jawaban = 0
                pertanyaan = f"{a} ÷ {b} = ..."
            else:
                a = random.randint(5, 50)
                b = 1
                jawaban = a
                pertanyaan = f"{a} ÷ {b} = ..."

            soal = {
                'pertanyaan': pertanyaan,
                'pilihan': [str(jawaban), "1", "0", "Tidak Bisa"],
                'jawaban_benar': str(jawaban)
            }

        # Materi 4: Pembagian Bersusun
        # Contoh: 48 : 2 = ... (Pembagian habis)
        elif materi_id == 4:
            hasil = random.randint(11, 25)
            pembagi = random.randint(2, 4)
            angka_dibagi = hasil * pembagi
            soal = {
                'pertanyaan': f"Hitunglah: {angka_dibagi} ÷ {pembagi} = ...",
                'pilihan': [str(hasil), str(hasil + 2), str(hasil - 2), str(10)],
                'jawaban_benar': str(hasil)
            }

        # Materi 5: Operasi Campuran
        # Contoh: (3 x 4) + 5 = ...
        elif materi_id == 5:
            a = random.randint(2, 5)
            b = random.randint(2, 5)
            c = random.randint(1, 10)
            jawaban = (a * b) + c
            soal = {
                'pertanyaan': f"({a} × {b}) + {c} = ...",
                'pilihan': [str(jawaban), str(jawaban + 2), str(a * b), str(a + b + c)],
                'jawaban_benar': str(jawaban)
            }

        # Materi 6: Soal Cerita
        else:
            kotak = random.randint(3, 8)
            isi = random.randint(2, 6)
            total = kotak * isi
            soal = {
                'pertanyaan': f"Ibu beli {kotak} kotak donat. Tiap kotak isi {isi}. Berapa total donat?",
                'pilihan': [f"{total} donat", f"{total + 2} donat", f"{kotak + isi} donat", f"{isi} donat"],
                'jawaban_benar': f"{total} donat"
            }

    # Fallback (Jaga-jaga jika data kosong)
    if not soal:
        soal = {
            'pertanyaan': "2 x 2 = ...",
            'pilihan': ["4", "5", "6", "8"],
            'jawaban_benar': "4"
        }

    # Acak urutan pilihan jawaban
    # Agar kunci jawaban tidak selalu di tombol pertama
    random.shuffle(soal['pilihan'])

    return soal