import random
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages


# UTILITAS
def generate_soal_perkalian(jumlah_soal=5):
    soal = []
    for _ in range(jumlah_soal):
        a = random.randint(1, 5)
        b = random.randint(1, 5)
        jawaban = f'{a * b}'

        pilihan = [jawaban,
                   f'{int(jawaban) + random.randint(1, 2)}',
                   f'{int(jawaban) - random.randint(1, 2)}',
                   f'{int(jawaban) + random.randint(3, 5)}']
        pilihan = list(set(pilihan))  # Hapus duplikat

        while len(pilihan) < 4:
            pilihan.append(f'{int(jawaban) + random.randint(6, 10)}')
        random.shuffle(pilihan)

        soal.append({
            'question': f'Berapakah {a} x {b} ?',
            'choices': pilihan,
            'answer': jawaban
        })

    return soal


def generate_soal_pembagian(jumlah_soal=5):
    soal = []
    for _ in range(jumlah_soal):
        b = random.randint(1, 5)
        jawaban = random.randint(1, 5)
        # Pastikan a tidak selalu kelipatan b
        a = b * jawaban + random.randint(0, b - 1)
        hasil_bagi = a // b
        sisa_bagi = a % b

        if sisa_bagi == 0:
            kunci_jawaban = f'{hasil_bagi}'
        else:
            kunci_jawaban = f'{hasil_bagi} sisa {sisa_bagi}'

        pilihan = [kunci_jawaban,
                   f'{hasil_bagi + 1}',
                   f'{hasil_bagi} sisa {sisa_bagi + 1}' if sisa_bagi +
                   1 < b else f'{hasil_bagi + 1}',
                   f'{hasil_bagi - 1}' if hasil_bagi > 0 else '0']
        pilihan = list(set(pilihan))  # Hapus duplikat

        while len(pilihan) < 4:
            pilihan.append(f'{hasil_bagi + random.randint(2, 5)}')
        random.shuffle(pilihan)

        soal.append({
            'question': f'Berapakah {a} : {b} ?',
            'choices': pilihan,
            'answer': kunci_jawaban
        })

    return soal


def generate_soal(jumlah_soal_perkalian=5, jumlah_soal_pembagian=5):
    soal_perkalian = generate_soal_perkalian(jumlah_soal_perkalian)
    soal_pembagian = generate_soal_pembagian(jumlah_soal_pembagian)
    semua_soal = soal_perkalian + soal_pembagian
    random.shuffle(semua_soal)
    return semua_soal

# HALAMAN UTAMA


@login_required
def beranda(request):
    return render(request, 'pages/beranda.html')


@login_required
def materi(request):
    return render(request, 'pages/materi.html')


@login_required
def latihan(request):
    if request.method == 'GET':
        # Initialize new practice session
        if 'page' not in request.GET or request.GET.get('start') == '1':
            jumlah_soal = 10  # Total soal yang akan dihasilkan
            soal = generate_soal(jumlah_soal_perkalian=jumlah_soal // 2,
                                 jumlah_soal_pembagian=jumlah_soal // 2)
            # Store questions and answers in session
            request.session['soal_latihan'] = soal
            request.session['jawaban_user'] = []

        # Get current questions from session
        soal = request.session.get('soal_latihan', [])
        if not soal:
            # Redirect to start if no questions in session
            return redirect('latihan')

        paginator = Paginator(soal, 1)  # Satu soal per halaman
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Calculate progress percentage
        progress_percentage = (
            page_obj.number * 100) // page_obj.paginator.count

        # Check if this page has answer already
        jawaban_user = request.session.get('jawaban_user', [])
        jawaban_chosen = jawaban_user[page_obj.number -
                                      1] if page_obj.number <= len(jawaban_user) else None

        return render(request, 'pages/latihan.html', {
            'page_obj': page_obj,
            'progress_percentage': progress_percentage,
            'jawaban_chosen': jawaban_chosen
        })

    elif request.method == 'POST':
        # Get current answer and page number
        jawaban = request.POST.get('jawaban')
        current_page = int(request.GET.get('page', 1))

        if jawaban:
            jawaban_user = request.session.get('jawaban_user', [])

            # Ensure jawaban_user list has enough elements
            while len(jawaban_user) < current_page:
                jawaban_user.append(None)

            # Update answer for current page (index = page - 1)
            jawaban_user[current_page - 1] = jawaban
            request.session['jawaban_user'] = jawaban_user

        # Check if this was the last question
        soal = request.session.get('soal_latihan', [])
        jawaban_user = request.session.get('jawaban_user', [])

        if current_page >= len(soal):
            # This is the last question, calculate results
            benar = 0
            salah = 0

            for i, soal_item in enumerate(soal):
                if i < len(jawaban_user) and jawaban_user[i] is not None:
                    if str(jawaban_user[i]) == str(soal_item['answer']):
                        benar += 1
                    else:
                        salah += 1

            request.session['benar'] = benar
            request.session['salah'] = salah

            # Clean up session
            if 'soal_latihan' in request.session:
                del request.session['soal_latihan']
            if 'jawaban_user' in request.session:
                del request.session['jawaban_user']

            return redirect('hasil')
        else:
            # Go to next question (current page + 1)
            next_page = current_page + 1
            return redirect(f'/latihan/?page={next_page}')


@login_required
def hasil(request):
    benar = request.session.get('benar', 0)
    salah = request.session.get('salah', 0)
    total = benar + salah

    # Calculate percentage and progress bar widths
    percentage = (benar * 100) // total if total > 0 else 0
    benar_width = (benar * 100) // total if total > 0 else 0
    salah_width = (salah * 100) // total if total > 0 else 0

    # Clean up session
    if 'benar' in request.session:
        del request.session['benar']
    if 'salah' in request.session:
        del request.session['salah']

    return render(request, 'pages/hasil.html', {
        'benar': benar,
        'salah': salah,
        'total': total,
        'percentage': percentage,
        'benar_width': benar_width,
        'salah_width': salah_width
    })


# AUTHENTIKASI

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
        role = 'Siswa'  # Default role

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

        messages.success(
            request, 'Akun berhasil dibuat! Silakan masuk.')

        return redirect('masuk')

    return render(request, 'pages/auth/daftar.html')


def keluar(request):
    logout(request)
    return redirect('masuk')
