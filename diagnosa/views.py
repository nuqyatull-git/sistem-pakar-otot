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
    if request.method == 'POST':
        form = RegisterPasienForm(request.POST)
        if form.is_valid():
            nama = form.cleaned_data['nama'].strip()
            jenis_kelamin = form.cleaned_data['jenis_kelamin']
            tanggal_lahir = form.cleaned_data['tanggal_lahir']
            alamat = form.cleaned_data['alamat']
            no_kartu = form.cleaned_data['no_kartu'].strip()

            """no_kartu_norm = no_kartu.upper()"""

            user = User.objects.create_user(username=no_kartu, password=no_kartu)
            Pasien.objects.create(
                user=user, 
                nama=nama, 
                jenis_kelamin=jenis_kelamin,
                no_kartu=no_kartu,
                tanggal_lahir=tanggal_lahir,
                alamat=alamat)

            messages.success(request, 'Registrasi berhasil, silakan login.')
            return redirect('login')
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