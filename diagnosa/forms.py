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
   
class LoginPasienForm(forms.Form):
    nama = forms.CharField(
        max_length=255, label="Nama",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama lengkap'})
    )
    no_kartu = forms.CharField(
        max_length=50, label="No Kartu Pasien",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan no kartu pasien'})
    )