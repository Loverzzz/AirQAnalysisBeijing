import pandas as pd
from pathlib import Path

def combine_data_files():
    """
    Menggabungkan semua file data_1.csv sampai data_12.csv
    """
    print("Memulai proses penggabungan data...")
    
    # List untuk menyimpan semua dataframe
    dfs = []
    
    # Baca setiap file data_1.csv sampai data_12.csv
    for i in range(1, 13):
        file_path = f'data/data_{i}.csv'
        print(f"Membaca file: {file_path}")
        
        try:
            # Baca file CSV
            df = pd.read_csv(file_path)
            dfs.append(df)
            print(f"Berhasil membaca file data_{i}.csv dengan {len(df)} baris")
            
        except FileNotFoundError:
            print(f"File data_{i}.csv tidak ditemukan")
            continue
        except Exception as e:
            print(f"Error saat membaca file data_{i}.csv: {str(e)}")
            continue
    
    # Gabungkan semua dataframe
    if dfs:
        print("\nMenggabungkan semua data...")
        combined_df = pd.concat(dfs, ignore_index=True)
        print(f"Total data setelah penggabungan: {len(combined_df)} baris")
        
        # Buat folder dashboard jika belum ada
        Path("dashboard").mkdir(exist_ok=True)
        
        # Simpan hasil gabungan
        output_path = 'dashboard/main_data.csv'
        combined_df.to_csv(output_path, index=False)
        print(f"\nFile berhasil disimpan di: {output_path}")
        
        # Tampilkan informasi dasar
        print("\nInformasi dataset:")
        print(f"Jumlah baris: {len(combined_df)}")
        print(f"Jumlah kolom: {len(combined_df.columns)}")
        print("\nKolom yang tersedia:")
        for col in combined_df.columns:
            print(f"- {col}")
            
    else:
        print("Tidak ada data yang bisa digabungkan!")

if __name__ == "__main__":
    combine_data_files()