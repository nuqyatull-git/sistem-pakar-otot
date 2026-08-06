from django.db import models
from django.contrib.auth.models import User
import random

class Gejala(models.Model):
    kode = models.CharField(max_length=10, unique=True)  # G01, G02, dst
    nama = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.kode:
            last_gejala = Gejala.objects.order_by('-id').first()
            if last_gejala and last_gejala.kode:
                last_number = int(last_gejala.kode.replace('G', ''))
                new_number = last_number + 1
            else:
                new_number = 1
            self.kode = f"G{new_number:02d}"   
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.kode} - {self.nama}"


class Penyakit(models.Model):
    kode = models.CharField(max_length=10, unique=True)  # P01, P02, dst
    nama = models.CharField(max_length=255)
    deskripsi = models.TextField(blank=True)
    solusi = models.TextField()

    def save(self, *args, **kwargs):
        if not self.kode:
            last_penyakit = Penyakit.objects.order_by('-id').first()
            if last_penyakit and last_penyakit.kode:
                last_number = int(last_penyakit.kode.replace('P', ''))
                new_number = last_number + 1
            else:
                new_number = 1
            self.kode = f"P{new_number:02d}"   
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.kode} - {self.nama}"

class Pasien(models.Model):
    JENIS_KELAMIN_CHOICES = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255)
    jenis_kelamin = models.CharField(
        max_length=1, choices=JENIS_KELAMIN_CHOICES, blank=True
    )
    no_kartu = models.CharField(max_length=50, unique=True)
    tanggal_lahir = models.DateField(null=True, blank=True)
    alamat = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nama} - {self.no_kartu}"
    @staticmethod
    def generate_no_pendaftaran():
        """Bikin nomor pendaftaran 6 digit acak yang belum dipakai."""
        while True:
            kode = str(random.randint(100000, 999999))
            if not Pasien.objects.filter(no_kartu=kode).exists():
                return kode
            
class Rule(models.Model):
    kode = models.CharField(max_length=10, unique=True, blank=True)
    penyakit = models.ForeignKey(Penyakit, on_delete=models.CASCADE, related_name='rules')
    gejala = models.ManyToManyField(Gejala)
    gejala_or = models.ManyToManyField(Gejala, related_name='rule_or', blank=True)

    def save(self, *args, **kwargs):
        if not self.kode:
            last_rule = Rule.objects.order_by('-id').first()
            if last_rule and last_rule.kode:
                last_number = int(last_rule.kode.replace('R', ''))
                new_number = last_number + 1
            else:
                new_number = 1
            self.kode = f"R{new_number:02d}"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.kode} - Rule untuk {self.penyakit.nama}"


class RiwayatDiagnosa(models.Model):
    pasien = models.ForeignKey(Pasien, on_delete=models.CASCADE, related_name='riwayat')
    gejala_dipilih = models.ManyToManyField(Gejala)
    hasil_penyakit = models.ForeignKey(Penyakit, on_delete=models.SET_NULL, null=True)
    tanggal = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pasien.nama} - {self.hasil_penyakit} - {self.tanggal.strftime('%d-%m-%Y %H:%M')}"


class GambarBeranda(models.Model):
    judul = models.CharField(max_length=100, default="Gambar Beranda")
    gambar = models.ImageField(upload_to='beranda/')

    def __str__(self):
        return self.judul