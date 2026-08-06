from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import DiagnosaForm, RegisterPasienForm, LoginPasienForm
from .models import Rule, Pasien,  RiwayatDiagnosa
from .inference import forward_chaining
from datetime import date
from .models import GambarBeranda

def home_view(request):
    gambar = GambarBeranda.objects.first()
    return render(request, 'diagnosa/home.html', {'gambar': gambar})

@login_required(login_url='/login/')

def diagnosa_view(request):
    hasil = None
    riwayat = None
    pasien = Pasien.objects.get(user=request.user)

    umur = None
    if pasien.tanggal_lahir:
        today = date.today()
        umur = today.year - pasien.tanggal_lahir.year - (
            (today.month, today.day) < (pasien.tanggal_lahir.month, pasien.tanggal_lahir.day)
        )

    if request.method == 'POST':
        form = DiagnosaForm(request.POST)
        if form.is_valid():
            gejala_dipilih = form.cleaned_data['gejala']
            gejala_ids = [g.id for g in gejala_dipilih]
            rules = Rule.objects.all()
            hasil = forward_chaining(gejala_ids, rules)

            # simpan riwayat kalau ada hasil diagnosa
            if hasil:                
                penyakit_teratas = hasil[0]['penyakit']

                riwayat = RiwayatDiagnosa.objects.create(
                    pasien=pasien,
                    hasil_penyakit=penyakit_teratas
                )
                riwayat.gejala_dipilih.set(gejala_dipilih)
    else:
        form = DiagnosaForm()

    return render(request, 'diagnosa/diagnosa.html', {
        'form': form, 
        'hasil': hasil,
        'pasien': pasien,
        'riwayat': riwayat,
        'umur': umur,
        })

def register_pasien_view(request):
    step = request.POST.get('step')
 
    # ----- STEP 2: konfirmasi & simpan ke database -----
    if request.method == 'POST' and step == '2':
        nama = request.session.get('reg_nama')
        tanggal_lahir_str = request.session.get('reg_tanggal_lahir')
        jenis_kelamin = request.session.get('reg_jenis_kelamin')
        alamat = request.session.get('reg_alamat')
        no_kartu = request.session.get('reg_no_kartu')
 
        if not all([nama, tanggal_lahir_str, jenis_kelamin, no_kartu]):
            messages.error(request, 'Sesi pendaftaran sudah habis, silakan isi ulang form.')
            return redirect('register')
 
        tanggal_lahir = date.fromisoformat(tanggal_lahir_str)
 
        user = User.objects.create_user(username=no_kartu, password=no_kartu)
        Pasien.objects.create(
            user=user,
            nama=nama,
            jenis_kelamin=jenis_kelamin,
            no_kartu=no_kartu,
            tanggal_lahir=tanggal_lahir,
            alamat=alamat,
        )
 
        # bersihkan session pendaftaran
        for key in ['reg_nama', 'reg_tanggal_lahir', 'reg_jenis_kelamin', 'reg_alamat', 'reg_no_kartu']:
            request.session.pop(key, None)
 
        messages.success(
            request,
            f'Registrasi berhasil! No Pendaftaran Anda: {no_kartu}. '
            'Gunakan nomor ini untuk login.'
        )
        return redirect('login')
 
    # ----- STEP 1: validasi data awal, generate no pendaftaran -----
    if request.method == 'POST':
        form = RegisterPasienForm(request.POST)
        if form.is_valid():
            nama = form.cleaned_data['nama'].strip()
            tanggal_lahir = form.cleaned_data['tanggal_lahir']
            jenis_kelamin = form.cleaned_data['jenis_kelamin']
            alamat = form.cleaned_data['alamat']
 
            no_kartu = Pasien.generate_no_pendaftaran()
 
            request.session['reg_nama'] = nama
            request.session['reg_tanggal_lahir'] = tanggal_lahir.isoformat()
            request.session['reg_jenis_kelamin'] = jenis_kelamin
            request.session['reg_alamat'] = alamat
            request.session['reg_no_kartu'] = no_kartu
 
            jenis_kelamin_label = dict(Pasien.JENIS_KELAMIN_CHOICES).get(jenis_kelamin, jenis_kelamin)
 
            return render(request, 'diagnosa/register_konfirmasi.html', {
                'nama': nama,
                'tanggal_lahir': tanggal_lahir,
                'jenis_kelamin_label': jenis_kelamin_label,
                'alamat': alamat,
                'no_kartu': no_kartu,
            })
    else:
        form = RegisterPasienForm()
 
    return render(request, 'diagnosa/register.html', {'form': form})
 

def login_pasien_view(request):
    if request.method == 'POST':
        form = LoginPasienForm(request.POST)
        if form.is_valid():
            nama = form.cleaned_data['nama'].strip()
            no_kartu = form.cleaned_data['no_kartu'].strip()
            no_kartu_norm = no_kartu.upper()

            pasien = Pasien.objects.filter(
                nama__iexact=nama,
                no_kartu__iexact=no_kartu_norm
            ).first()

            if pasien:
                user = authenticate(request, username=no_kartu_norm, password=no_kartu_norm)
                if user:
                    login(request, user)
                    return redirect('diagnosa')

            messages.error(request, 'Nama atau No Kartu Pasien salah.')
    else:
        form = LoginPasienForm()

    return render(request, 'diagnosa/login.html', {'form': form})


def logout_pasien_view(request):
    logout(request)
    return redirect('login')