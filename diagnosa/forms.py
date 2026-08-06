from django import forms
from django.contrib.auth.models import User
from .models import Gejala, Pasien

class GejalaMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.nama


class DiagnosaForm(forms.Form):
    gejala = GejalaMultipleChoiceField(
        queryset=Gejala.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Pilih gejala yang dialami"
    )

class RegisterPasienForm(forms.Form):
    nama = forms.CharField(
        max_length=255, label="Nama",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama lengkap'})
    )
    tanggal_lahir = forms.DateField(
        label="Tanggal Lahir",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    jenis_kelamin = forms.ChoiceField(
        label="Jenis Kelamin",
        choices=Pasien.JENIS_KELAMIN_CHOICES,
        widget=forms.RadioSelect,
    )
    alamat = forms.CharField(
        label="Alamat",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Masukkan alamat lengkap'})
    )
    no_kartu = forms.CharField(
        max_length=50, label="No Pendaftaran", required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'placeholder': 'Otomatis terisi setelah data lain lengkap',
        })
    )

    def clean_no_kartu(self):
        no_kartu = (self.cleaned_data.get('no_kartu') or '').strip()
 
        # Kalau kosong / tidak 6 digit angka (mis. JS gagal jalan), generate otomatis
        if not no_kartu or len(no_kartu) != 6 or not no_kartu.isdigit():
            return Pasien.generate_no_pendaftaran()
 
        if Pasien.objects.filter(no_kartu=no_kartu).exists():
            # Nomor kebetulan bentrok (sangat jarang) -> buatkan yang baru otomatis
            return Pasien.generate_no_pendaftaran()
 
        return no_kartu
    
class LoginPasienForm(forms.Form):
    nama = forms.CharField(
        max_length=255, label="Nama",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama lengkap'})
    )
    no_kartu = forms.CharField(
        max_length=50, label="No Kartu Pasien",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan no kartu pasien'})
    )