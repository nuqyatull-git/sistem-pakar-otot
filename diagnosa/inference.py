def forward_chaining(gejala_user_ids, rules):
    """
    gejala_user_ids: list ID gejala yang dipilih user
    rules: queryset Rule (semua rule dari database)
    return: list hasil (penyakit yang cocok + gejala yang match)
    """
    hasil = []
    gejala_user_set = set(gejala_user_ids)

    for rule in rules:
        gejala_and_set = set(rule.gejala.values_list('id', flat=True))
        gejala_or_set = set(rule.gejala_or.values_list('id', flat=True))

        # Syarat AND: semua gejala wajib harus ada
        syarat_and_terpenuhi = gejala_and_set.issubset(gejala_user_set)

        # Syarat OR: kalau rule punya gejala_or, minimal 1 harus terpilih.
        # Kalau rule tidak punya gejala_or (kosong), syarat ini otomatis lolos.
        if gejala_or_set:
            syarat_or_terpenuhi = len(gejala_or_set & gejala_user_set) > 0
        else:
            syarat_or_terpenuhi = True

        if syarat_and_terpenuhi and syarat_or_terpenuhi:
            total_cocok = len(gejala_and_set & gejala_user_set) + len(gejala_or_set & gejala_user_set)
            hasil.append({
                'penyakit': rule.penyakit,
                'jumlah_gejala_cocok': total_cocok,
                'total_gejala_rule': len(gejala_and_set) + len(gejala_or_set),
            })

    hasil.sort(key=lambda x: x['jumlah_gejala_cocok'], reverse=True)
    return hasil