import random
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from .models import Profile, NilaiEvaluasi, JawabanEvaluasi, KemajuanBelajar, NilaiEvaluasiPerMateri


# UTILITAS SOAL
def generate_soal_perkalian(jumlah_soal=5):
    """Generate soal perkalian"""
    soal = []
    for _ in range(jumlah_soal):
        a = random.randint(1, 12)
        b = random.randint(1, 12)
        jawaban = a * b

        pilihan = [str(jawaban)]
        pilihan.append(str(jawaban + random.randint(1, 10)))
        pilihan.append(str(jawaban - random.randint(1, 5)
                       if jawaban > 5 else jawaban + 5))
        pilihan.append(str(jawaban + random.randint(11, 20)))

        random.shuffle(pilihan)

        soal.append({
            'question': f'Berapakah {a} × {b}?',
            'choices': pilihan,
            'answer': str(jawaban)
        })
    return soal


def generate_soal_pembagian(jumlah_soal=5):
    """Generate soal pembagian"""
    soal = []
    for _ in range(jumlah_soal):
        b = random.randint(2, 9)
        jawaban = random.randint(1, 12)
        a = b * jawaban + random.randint(0, b - 1)
        hasil_bagi = a // b
        sisa_bagi = a % b

        if sisa_bagi == 0:
            kunci_jawaban = str(hasil_bagi)
        else:
            kunci_jawaban = f'{hasil_bagi} sisa {sisa_bagi}'

        pilihan = [kunci_jawaban]
        pilihan.append(str(hasil_bagi + 1))
        pilihan.append(
            f'{hasil_bagi} sisa {sisa_bagi + 1}' if sisa_bagi + 1 < b else f'{hasil_bagi + 1}')
        pilihan.append(str(hasil_bagi - 1) if hasil_bagi > 0 else '0')

        random.shuffle(pilihan)

        soal.append({
            'question': f'Berapakah {a} ÷ {b}?',
            'choices': pilihan,
            'answer': kunci_jawaban
        })
    return soal


def generate_soal_evaluasi_akhir(jumlah_soal=20):
    """Generate comprehensive evaluation questions from all materials"""
    soal = []

    # Distribute questions across all 6 materials
    soal_per_materi = jumlah_soal // 6
    sisa_soal = jumlah_soal % 6

    for materi_id in range(1, 7):
        jumlah_untuk_materi = soal_per_materi + \
            (1 if materi_id <= sisa_soal else 0)

        for _ in range(jumlah_untuk_materi):
            if materi_id in [1, 2, 3]:  # Perkalian materials
                if materi_id == 1:  # Perkalian dengan 0, 10, 100
                    operators = [0, 10, 100]
                    a = random.randint(1, 12)
                    b = random.choice(operators)
                    jawaban = a * b
                elif materi_id == 2:  # Perkalian bersusun
                    a = random.randint(10, 99)
                    b = random.randint(2, 9)
                    jawaban = a * b
                else:  # materi_id == 3, perkalian biasa
                    a = random.randint(1, 12)
                    b = random.randint(1, 12)
                    jawaban = a * b

                # Generate wrong choices
                pilihan = [str(jawaban)]
                pilihan.append(str(jawaban + random.randint(1, 10)))
                pilihan.append(str(jawaban - random.randint(1, 5)
                               if jawaban > 5 else jawaban + 5))
                pilihan.append(str(jawaban + random.randint(11, 20)))
                random.shuffle(pilihan)

                soal.append({
                    'question': f'Berapakah {a} × {b}?',
                    'choices': pilihan,
                    'correct_answer': str(jawaban),
                    'materi': f'materi_{materi_id}',
                    'explanation': f'{a} × {b} = {jawaban}'
                })

            elif materi_id in [4, 5]:  # Pembagian materials
                divisor = random.randint(2, 9)
                if materi_id == 4:  # Pembagian bersusun (no remainder)
                    quotient = random.randint(10, 99)
                    dividend = divisor * quotient
                    remainder = 0
                else:  # materi_id == 5, pembagian dengan sisa
                    dividend = random.randint(20, 100)
                    quotient = dividend // divisor
                    remainder = dividend % divisor

                if remainder == 0:
                    jawaban = str(quotient)
                    explanation = f'{dividend} ÷ {divisor} = {quotient}'
                else:
                    jawaban = f'{quotient} sisa {remainder}'
                    explanation = f'{dividend} ÷ {divisor} = {quotient} sisa {remainder}'

                # Generate wrong choices
                pilihan = [jawaban]
                pilihan.append(str(quotient + 1))
                if remainder > 0:
                    pilihan.append(f'{quotient} sisa {remainder + 1}')
                    pilihan.append(str(quotient))
                else:
                    pilihan.append(f'{quotient} sisa 1')
                    pilihan.append(str(quotient - 1))
                random.shuffle(pilihan)

                soal.append({
                    'question': f'Berapakah {dividend} ÷ {divisor}?',
                    'choices': pilihan,
                    'correct_answer': jawaban,
                    'materi': f'materi_{materi_id}',
                    'explanation': explanation
                })

            else:  # materi_id == 6, operasi campuran
                operation_type = random.choice(
                    ['simple_mixed', 'story_problem'])

                if operation_type == 'simple_mixed':
                    a = random.randint(2, 9)
                    b = random.randint(2, 9)
                    c = random.randint(1, 20)
                    operation = random.choice(['+', '-'])

                    if operation == '+':
                        jawaban = (a * b) + c
                        question = f'Berapakah ({a} × {b}) + {c}?'
                        explanation = f'({a} × {b}) + {c} = {a * b} + {c} = {jawaban}'
                    else:
                        jawaban = (a * b) - c
                        question = f'Berapakah ({a} × {b}) - {c}?'
                        explanation = f'({a} × {b}) - {c} = {a * b} - {c} = {jawaban}'

                else:  # story_problem
                    items = random.randint(3, 8)
                    per_group = random.randint(2, 6)
                    given_away = random.randint(1, items * per_group // 2)

                    total = items * per_group
                    remaining = total - given_away
                    jawaban = remaining

                    question = f'Ana punya {items} kotak permen. Setiap kotak berisi {per_group} permen. Jika Ana memberikan {given_away} permen, berapa permen yang tersisa?'
                    explanation = f'Total permen = {items} × {per_group} = {total}. Sisa = {total} - {given_away} = {jawaban}'

                # Generate wrong choices
                pilihan = [str(jawaban)]
                pilihan.append(str(jawaban + random.randint(1, 5)))
                pilihan.append(str(jawaban - random.randint(1, 3)
                               if jawaban > 3 else jawaban + 3))
                pilihan.append(str(jawaban + random.randint(6, 10)))
                random.shuffle(pilihan)

                soal.append({
                    'question': question,
                    'choices': pilihan,
                    'correct_answer': str(jawaban),
                    'materi': f'materi_{materi_id}',
                    'explanation': explanation
                })

    # Shuffle all questions
    random.shuffle(soal)
    return soal


# HALAMAN UTAMA
@login_required
def beranda(request):
    # Get user progress summary
    progress_summary = KemajuanBelajar.get_user_summary(request.user)
    ready_for_evaluation = KemajuanBelajar.user_ready_for_evaluation(
        request.user)

    # Get latest evaluation score
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

    # Get progress for each material
    progress_data = {}
    for materi_choice in KemajuanBelajar.MATERI_CHOICES:
        materi_code = materi_choice[0]
        kemajuan = KemajuanBelajar.objects.filter(
            user=request.user,
            materi=materi_code
        ).first()

        progress_data[materi_code] = {
            'is_selesai': kemajuan.is_selesai if kemajuan else False,
            'progress_persentase': kemajuan.progress_persentase if kemajuan else 0,
        }

    context = {
        'progress_data': progress_data,
        'kelas': kelas,
    }

    template_name = f'pages/materi/{kelas}/daftar_materi.html'
    return render(request, template_name, context)


@login_required
def materi_detail(request, materi_id):
    if materi_id not in range(1, 7):
        messages.error(request, 'Materi tidak ditemukan!')
        return redirect('materi')

    profile, created = Profile.objects.get_or_create(user=request.user)
    kelas = profile.kelas or 'kelas_2'

    # Mark as viewed (update progress)
    kemajuan, created = KemajuanBelajar.objects.get_or_create(
        user=request.user,
        materi=f'materi_{materi_id}',
        defaults={'progress_persentase': 50.0}  # 50% for viewing
    )

    if created or kemajuan.progress_persentase < 50:
        kemajuan.progress_persentase = 50.0
        kemajuan.save()

    template_name = f'pages/materi/{kelas}/materi_{materi_id}.html'
    return render(request, template_name, {'materi_id': materi_id})


@login_required
def mark_materi_completed(request, materi_id):
    """Mark a specific material as completed"""
    if materi_id not in range(1, 7):
        messages.error(request, 'Materi tidak ditemukan!')
        return redirect('materi')

    kemajuan, created = KemajuanBelajar.objects.get_or_create(
        user=request.user,
        materi=f'materi_{materi_id}',
        defaults={'progress_persentase': 0.0}
    )

    kemajuan.mark_completed()
    messages.success(
        request, f'Materi {materi_id} berhasil ditandai sebagai selesai!')

    return redirect('materi')


# LATIHAN SOAL
@login_required
def latihan(request):
    if request.method == 'GET':
        # Initialize new practice session
        if 'page' not in request.GET or request.GET.get('start') == '1':
            jumlah_soal = 10
            soal_perkalian = generate_soal_perkalian(jumlah_soal // 2)
            soal_pembagian = generate_soal_pembagian(jumlah_soal // 2)
            soal = soal_perkalian + soal_pembagian
            random.shuffle(soal)

            request.session['soal_latihan'] = soal
            request.session['jawaban_user'] = []

        # Get current questions from session
        soal = request.session.get('soal_latihan', [])
        if not soal:
            return redirect('latihan')

        paginator = Paginator(soal, 1)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        progress_percentage = (
            page_obj.number * 100) // page_obj.paginator.count

        jawaban_user = request.session.get('jawaban_user', [])
        jawaban_chosen = jawaban_user[page_obj.number -
                                      1] if page_obj.number <= len(jawaban_user) else None

        return render(request, 'pages/latihan.html', {
            'page_obj': page_obj,
            'progress_percentage': progress_percentage,
            'jawaban_chosen': jawaban_chosen
        })

    elif request.method == 'POST':
        jawaban = request.POST.get('jawaban')
        current_page = int(request.GET.get('page', 1))

        if jawaban:
            jawaban_user = request.session.get('jawaban_user', [])
            while len(jawaban_user) < current_page:
                jawaban_user.append(None)
            jawaban_user[current_page - 1] = jawaban
            request.session['jawaban_user'] = jawaban_user

        soal = request.session.get('soal_latihan', [])

        if current_page >= len(soal):
            # Calculate results
            benar = 0
            jawaban_user = request.session.get('jawaban_user', [])

            for i, soal_item in enumerate(soal):
                if i < len(jawaban_user) and jawaban_user[i] is not None:
                    if str(jawaban_user[i]) == str(soal_item['answer']):
                        benar += 1

            request.session['benar'] = benar
            request.session['salah'] = len(soal) - benar

            # Clean up
            if 'soal_latihan' in request.session:
                del request.session['soal_latihan']
            if 'jawaban_user' in request.session:
                del request.session['jawaban_user']

            return redirect('hasil_latihan')
        else:
            next_page = current_page + 1
            return redirect(f'/latihan/?page={next_page}')


@login_required
def hasil_latihan(request):
    benar = request.session.get('benar', 0)
    salah = request.session.get('salah', 0)
    total = benar + salah

    percentage = (benar * 100) // total if total > 0 else 0
    benar_width = (benar * 100) // total if total > 0 else 0
    salah_width = (salah * 100) // total if total > 0 else 0

    # Clean up session
    if 'benar' in request.session:
        del request.session['benar']
    if 'salah' in request.session:
        del request.session['salah']

    return render(request, 'pages/hasil_latihan.html', {
        'benar': benar,
        'salah': salah,
        'total': total,
        'percentage': percentage,
        'benar_width': benar_width,
        'salah_width': salah_width
    })


# EVALUASI AKHIR
@login_required
def evaluasi(request):
    """Evaluasi akhir untuk semua materi"""
    # Check if user has completed all materials
    # if not KemajuanBelajar.user_ready_for_evaluation(request.user):
    #     messages.warning(
    #         request, 'Kamu harus menyelesaikan semua materi terlebih dahulu sebelum mengikuti evaluasi akhir!')
    #     return redirect('materi')

    # Get latest evaluation
    latest_evaluasi = NilaiEvaluasi.objects.filter(
        user=request.user).order_by('-created_at').first()

    if request.method == 'GET':
        # Start new evaluation session
        if 'page' not in request.GET or request.GET.get('start') == '1':
            soal = generate_soal_evaluasi_akhir(jumlah_soal=20)
            request.session['soal_evaluasi'] = soal
            request.session['jawaban_evaluasi'] = []

        # Get current questions from session
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
            'page_obj': page_obj,
            'progress_percentage': progress_percentage,
            'jawaban_chosen': jawaban_chosen,
            'latest_evaluasi': latest_evaluasi,
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
    """Finalize evaluation and save results with material breakdown"""
    soal = request.session.get('soal_evaluasi', [])
    jawaban_user = request.session.get('jawaban_evaluasi', [])

    if not soal or not jawaban_user:
        messages.error(request, 'Data evaluasi tidak ditemukan!')
        return redirect('materi')

    # Calculate results
    total_soal = len(soal)
    jumlah_benar = 0

    # Create evaluation record
    evaluasi = NilaiEvaluasi.objects.create(
        user=request.user,
        total_soal=total_soal,
        jumlah_benar=0,
        nilai=0.0
    )

    # Check answers and create detailed records
    for i, soal_item in enumerate(soal):
        user_answer = jawaban_user[i] if i < len(jawaban_user) else None
        correct_answer = soal_item['correct_answer']
        is_correct = str(user_answer) == str(correct_answer)

        if is_correct:
            jumlah_benar += 1

        JawabanEvaluasi.objects.create(
            evaluasi=evaluasi,
            nomor_soal=i + 1,
            materi_soal=soal_item['materi'],
            soal_pertanyaan=soal_item['question'],
            pilihan_jawaban=soal_item['choices'],  # Store choices
            jawaban_user=user_answer or '',
            jawaban_benar=correct_answer,
            is_correct=is_correct,
            poin=1.0 if is_correct else 0.0
        )

    # Update final score
    evaluasi.jumlah_benar = jumlah_benar
    evaluasi.nilai = (jumlah_benar / total_soal) * 100
    evaluasi.save()

    # IMPORTANT: Calculate and save material breakdown
    evaluasi.calculate_material_breakdown()

    # Store for result page
    request.session['evaluasi_id'] = evaluasi.id

    # Clean up
    for key in ['soal_evaluasi', 'jawaban_evaluasi']:
        if key in request.session:
            del request.session[key]

    return redirect('hasil_evaluasi')


@login_required
def hasil_evaluasi(request):
    """Display evaluation results with material breakdown"""
    evaluasi_id = request.session.get('evaluasi_id')

    if not evaluasi_id:
        messages.error(request, 'Hasil evaluasi tidak ditemukan!')
        return redirect('materi')

    evaluasi = get_object_or_404(
        NilaiEvaluasi, id=evaluasi_id, user=request.user)
    jawaban_detail = JawabanEvaluasi.objects.filter(
        evaluasi=evaluasi).order_by('nomor_soal')

    # Get material breakdown
    breakdown_per_materi = NilaiEvaluasiPerMateri.objects.filter(
        evaluasi_utama=evaluasi
    ).order_by('materi')

    # Calculate statistics
    benar = evaluasi.jumlah_benar
    salah = evaluasi.total_soal - evaluasi.jumlah_benar
    total = evaluasi.total_soal
    percentage = int(evaluasi.nilai)

    benar_width = int((benar / total) * 100) if total > 0 else 0
    salah_width = int((salah / total) * 100) if total > 0 else 0

    # Determine grade and recommendations
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

    # Get weak materials for recommendations
    weak_materials = [b for b in breakdown_per_materi if b.nilai < 70]

    # Clean up session
    if 'evaluasi_id' in request.session:
        del request.session['evaluasi_id']

    context = {
        'evaluasi': evaluasi,
        'jawaban_detail': jawaban_detail,
        'breakdown_per_materi': breakdown_per_materi,
        'weak_materials': weak_materials,
        'benar': benar,
        'salah': salah,
        'total': total,
        'percentage': percentage,
        'benar_width': benar_width,
        'salah_width': salah_width,
        'grade': grade,
        'grade_color': grade_color,
        'message': message,
    }

    return render(request, 'pages/hasil_evaluasi.html', context)


# AUTHENTICATION
def masuk(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('beranda')
        else:
            messages.error(request, 'Username atau password salah!')

    return render(request, 'pages/auth/masuk.html')


def daftar(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        kelas = request.POST.get('kelas')
        role = 'Siswa'

        if password != confirm_password:
            messages.error(request, 'Password tidak sesuai!')
            return redirect('daftar')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah terdaftar!')
            return redirect('daftar')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah terdaftar!')
            return redirect('daftar')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)

        Profile.objects.create(user=user, kelas=kelas)

        messages.success(request, 'Akun berhasil dibuat! Silakan masuk.')
        return redirect('masuk')

    return render(request, 'pages/auth/daftar.html')


def keluar(request):
    logout(request)
    return redirect('masuk')
