import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score


def train_model(file_path, title):
    # 1. Load Dataset Bersih
    df = pd.read_csv(file_path)

    # 2. Tentukan Fitur (X) dan Target (y)
    # Mengambil semua kolom yang mengandung kata 'NILAI' sebagai fitur
    feature_cols = [col for col in df.columns if 'NILAI' in col]
    X = df[feature_cols]
    y = df['REKOMENDASI_MATERI']

    # 3. Bagi Data (Split) - 70% Training, 30% Testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42)

    # 4. Latih Model
    model = DecisionTreeClassifier(random_state=42, max_depth=5)
    model.fit(X_train, y_train)

    # 5. Cek Akurasi
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Akurasi Model {title}: {acc*100:.1f}%")

    # 6. Visualisasi Pohon Keputusan
    plt.figure(figsize=(20, 10))
    plot_tree(model, feature_names=feature_cols,
              class_names=model.classes_, filled=True, rounded=True, fontsize=10)
    plt.title(f"Decision Tree - {title}")
    plt.show()

    return model


# --- Jalankan Kode ---
# Pastikan file .csv berada di folder yang sama dengan script ini
file_kelas_2 = "dataset_dummy_kelas_2.csv"
file_kelas_3 = "dataset_dummy_kelas_3.csv"

print("--- Hasil Training ---")
model_kelas_2 = train_model(file_kelas_2, "Kelas 2")
model_kelas_3 = train_model(file_kelas_3, "Kelas 3")
