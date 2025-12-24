import pandas as pd
import random
import numpy as np


def generate_realisitic_data(original_file_path, output_filename, n_students=200):
    print(f"--- Memproses {original_file_path} ---")

    # 1. LOAD DATA ASLI (Ambil Kunci Jawaban & Nama Materi)
    try:
        df = pd.read_csv(original_file_path)
    except:
        print("File tidak ditemukan!")
        return

    if 'NAMA' not in df.columns:
        if 'Unnamed: 0' in df.columns:
            df.rename(columns={'Unnamed: 0': 'NAMA'}, inplace=True)
        else:
            df.rename(columns={df.columns[0], 'NAMA'}, inplace=True)

    # Ambil Kunci Jawaban
    try:
        key_row = df[df['NAMA'].astype(str).str.contains(
            'Kunci', case=False, na=False)].iloc[0]
    except IndexError:
        print("Error: Tidak menemukan baris 'Kunci Jawaban' di file csv.")
        return

    q_cols = [f'Q{i}' for i in range(1, 19)]  # Q1 s/d Q18
    answer_key = key_row[q_cols].values
    options = ['A', 'B', 'C', 'D']

    # Mapping Nama Materi
    existing_recs = df['REKOMENDASI_MATERI'].dropna().unique()
    material_map = {}
    for rec in existing_recs:
        for i in range(1, 7):  # Asumsi ada 6 materi
            if f"Materi {i}" in rec:
                material_map[i] = rec

    # Fallback nama materi jika tidak lengkap
    for i in range(1, 7):
        if i not in material_map:
            material_map[i] = f"Materi {i}: Topik {i}"

    dummy_data = []

    # 2. GENERATE DATA SISWA BERDASARKAN PROFIL
    for i in range(n_students):
        student_id = i + 1

        # --- MENENTUKAN PROFIL KEMAMPUAN SISWA (RAHASIA DAPUR) ---
        # Kita acak, siswa ini tipe yang mana?

        # Skill Dasar (0.0 - 1.0): Seberapa pintar siswa ini secara umum?
        # Rata-rata siswa ada di 0.6 - 0.9. Ada sedikit siswa yang lemah (<0.5)
        # Distribusi condong ke kanan (pintar)
        base_skill = np.random.beta(5, 2)

        # Tentukan Kelemahan Spesifik (Satu materi yang dia paling gak bisa)
        weakness_idx = random.randint(1, 6)

        # Buat array probabilitas "Bisa Menjawab Benar" untuk tiap materi (1-6)
        probs_per_materi = {}

        for m in range(1, 7):
            skill = base_skill

            # Jika ini materi kelemahannya, kurangi skill secara drastis
            if m == weakness_idx:
                skill -= random.uniform(0.2, 0.5)

            # EFEK KORELASI (PENTING BUAT SKRIPSI!)
            # Jika lemah di Materi 1 (Dasar), kemungkinan besar lemah di Materi 2 & 3
            if weakness_idx == 1 and m in [2, 3]:
                skill -= random.uniform(0.1, 0.3)

            # Jika lemah di Materi 2 (Perkalian Susun), mungkin lemah di Materi 4 (Pembagian)
            if weakness_idx == 2 and m == 4:
                skill -= random.uniform(0.1, 0.3)

            # Batasi skill antara 0.1 (ngawur) sampai 0.98 (hampir sempurna)
            skill = max(0.1, min(0.98, skill))
            probs_per_materi[m] = skill

        # --- SIMULASI MENJAWAB SOAL ---
        student_answers = []
        scores = {}
        raw_scores_list = []

        for m in range(1, 7):  # Loop per materi
            # Ambil probabilitas benar untuk materi ini
            prob_correct = probs_per_materi[m]

            # Simulasi jawab 3 soal per materi
            correct_count = 0
            # Index soal di Excel (Q1-Q3 utk mat 1, Q4-Q6 utk mat 2, dst)
            start_idx = (m - 1) * 3

            for k in range(3):
                q_idx = start_idx + k
                correct_ans = answer_key[q_idx]

                # Roll dice: Benar atau Salah?
                if random.random() < prob_correct:
                    ans = correct_ans  # Jawab benar
                    correct_count += 1
                else:
                    # Jawab Salah (pilih acak opsi yang bukan jawaban benar)
                    wrong_opts = [o for o in options if o != correct_ans]
                    ans = random.choice(wrong_opts)

                student_answers.append(ans)

            # Hitung Nilai Per Materi
            score = round((correct_count / 3) * 100, 2)
            scores[f'NILAI_{m}'] = score
            raw_scores_list.append(score)

        # --- LOGIKA GURU (AUTO LABELING) ---
        # Disini kita tentukan label BUKAN secara acak, tapi berdasarkan nilai yang barusan terbentuk.

        min_val = min(raw_scores_list)

        # Cari materi apa saja yang nilainya terendah (bisa jadi ada 2 materi nilainya sama2 0)
        min_indices = [idx+1 for idx,
                       v in enumerate(raw_scores_list) if v == min_val]

        # ATURAN PRIORITAS GURU:
        # Jika ada nilai yang sama rendahnya, prioritaskan materi yang lebih awal (Materi 1 > Materi 6)
        # Karena materi awal adalah fondasi.
        final_rec_idx = min_indices[0]
        final_rec = material_map[final_rec_idx]

        # --- SUSUN DATASET ---
        row = {
            'NAMA': f"Siswa_Gen_{student_id}",
            'KELAS': df['KELAS'].mode()[0] if not df['KELAS'].mode().empty else "-"
        }

        # Masukkan Q1-Q18
        for idx, ans in enumerate(student_answers):
            row[f'Q{idx+1}'] = ans

        # Masukkan Nilai
        row.update(scores)

        # Masukkan Total & Label
        row['TOTAL_NILAI'] = round(sum(raw_scores_list) / 6, 2)
        row['REKOMENDASI_MATERI'] = final_rec

        dummy_data.append(row)

    # Simpan ke CSV
    df_dummy = pd.DataFrame(dummy_data)
    df_dummy.to_csv(output_filename, index=False)
    print(
        f"✅ Berhasil generate {n_students} data realistis ke: {output_filename}")
    print(df_dummy['REKOMENDASI_MATERI'].value_counts())
    print("-" * 30)


# --- EKSEKUSI ---
# Generate data Kelas 2
generate_realisitic_data(
    original_file_path="nilai_kelas_2.csv",
    output_filename="nilai_dummy_kelas_2_v2.csv",
    n_students=300
)


# Generate data Kelas 3
generate_realisitic_data(
    original_file_path="nilai_kelas_3.csv",
    output_filename="nilai_dummy_kelas_3_v2.csv",
    n_students=300
)
