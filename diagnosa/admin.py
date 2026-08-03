from django.contrib import admin
from .models import Gejala, Penyakit, Rule, RiwayatDiagnosa, Pasien
from .models import GambarBeranda


class GejalaAdmin(admin.ModelAdmin):
    readonly_fields = ('kode',)
    list_display = ('id','kode', 'nama')

class PenyakitAdmin(admin.ModelAdmin):
    readonly_fields = ('kode',)
    list_display = ('id','kode', 'nama')

class RuleAdmin(admin.ModelAdmin):
    readonly_fields = ('kode',)
    list_display = ('id', 'kode', 'penyakit', 'jumlah_gejala', 'jumlah_gejala_or')
    filter_horizontal = ('gejala', 'gejala_or') 

    def jumlah_gejala(self, obj):
        return obj.gejala.count()
    jumlah_gejala.short_description = 'Gejala (AND)'

    def jumlah_gejala_or(self, obj):
        return obj.gejala_or.count()
    jumlah_gejala_or.short_description = 'Gejala (OR)'
    
class RiwayatDiagnosaAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_no_kartu', 'get_nama', 'hasil_penyakit', 'tanggal')
    list_filter = ('hasil_penyakit', 'tanggal')
    search_fields = ('pasien__nama', 'pasien__no_kartu')

    def get_no_kartu(self, obj):
        return obj.pasien.no_kartu
    get_no_kartu.short_description = 'No Kartu Pasien'

    def get_nama(self, obj):
        return obj.pasien.nama
    get_nama.short_description = 'Nama Pengguna'

class PasienAdmin(admin.ModelAdmin):
    list_display = ('id', 'nama', 'no_kartu', 'tanggal_lahir', 'alamat')
    search_fields = ('nama', 'no_kartu')

admin.site.register(Gejala, GejalaAdmin)
admin.site.register(Penyakit, PenyakitAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(RiwayatDiagnosa, RiwayatDiagnosaAdmin)
admin.site.register(Pasien, PasienAdmin)
admin.site.register(GambarBeranda)