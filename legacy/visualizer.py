import streamlit as st
import time
import pandas as pd
import numpy as np

class SudokuSolver:
    def __init__(self, size=16):
        self.n = size
        self.k = int(size**0.5)
        self.symbols = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXY"

    def is_valid(self, grid, r, c, num):
        if num in grid[r]: return False
        for i in range(self.n):
            if grid[i][c] == num: return False
        sr, sc = r - r % self.k, c - c % self.k
        for i in range(self.k):
            for j in range(self.k):
                if grid[sr + i][sc + j] == num: return False
        return True

    # --- SOLVER DENGAN VISUALISASI ---
    def solve_visual(self, grid, placeholder, delay=0.01):
        for r in range(self.n):
            for c in range(self.n):
                if grid[r][c] == 0:
                    for num in range(1, self.n + 1):
                        # Animasi: Tampilkan angka yang sedang dicoba
                        grid[r][c] = num
                        
                        # Update tampilan grid secara real-time
                        with placeholder.container():
                            st.write(f"Mencoba angka: **{self.symbols[num]}** di ({r+1}, {c+1})")
                            st.table(self.format_for_display(grid))
                        
                        time.sleep(delay) # Jeda agar terlihat mata

                        if self.is_valid_at(grid, r, c, num):
                            if self.solve_visual(grid, placeholder, delay):
                                return True
                        
                        # Backtrack: Ganti jadi 0 lagi kalau salah
                        grid[r][c] = 0
                    return False
        return True

    def is_valid_at(self, grid, r, c, num):
        # Validasi khusus untuk cek angka yang baru saja ditaruh
        # Cek Baris
        if grid[r].count(num) > 1: return False
        # Cek Kolom
        col = [grid[i][c] for i in range(self.n)]
        if col.count(num) > 1: return False
        # Cek Box
        sr, sc = r - r % self.k, c - c % self.k
        box = []
        for i in range(self.k):
            for j in range(self.k):
                box.append(grid[sr + i][sc + j])
        if box.count(num) > 1: return False
        return True

    def format_for_display(self, grid):
        df = pd.DataFrame(grid)
        return df.map(lambda v: self.symbols[int(v)] if v != 0 else "")

# --- UI STREAMLIT ---
st.set_page_config(page_title="Sudoku Visualizer Kelompok 25", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #fcfaff; }
    h1 { color: #4a148c; text-align: center; }
    div.stButton > button { background-color: #7b1fa2 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔮 Sudoku Visualizer & Solver")

# Sidebar
st.sidebar.title("💜 Kontrol")
mode = st.sidebar.selectbox("Ukuran", [16, 25])
visualize = st.sidebar.checkbox("Aktifkan Visualisasi (Lambat)", value=False)
speed = st.sidebar.slider("Kecepatan (detik per langkah)", 0.0, 0.5, 0.01)

if 'grid_data' not in st.session_state or st.session_state.grid_data.shape[0] != mode:
    st.session_state.grid_data = np.zeros((mode, mode), dtype=int)

# Input Grid
df_input = pd.DataFrame(st.session_state.grid_data)
edited_df = st.data_editor(df_input, use_container_width=True, hide_index=True)

# Tempat untuk animasi (Placeholder)
grid_placeholder = st.empty()

if st.button("🚀 JALANKAN SOLVER", use_container_width=True):
    puzzle = edited_df.values.astype(int).tolist()
    solver = SudokuSolver(size=mode)
    
    start_t = time.time()
    
    if visualize:
        st.info("Mode Visualisasi Aktif: Menampilkan proses coba-coba (Backtracking)...")
        success = solver.solve_visual(puzzle, grid_placeholder, speed)
    else:
        with st.spinner("Menghitung cepat..."):
            # Pakai logika hybrid yang cepat kalau tidak visualisasi
            # (Gunakan fungsi solve_hybrid dari kode sebelumnya di sini)
            from copy import deepcopy
            temp_puzzle = deepcopy(puzzle) 
            # Untuk demo visual, kita fokus ke solve_visual saja
            success = solver.solve_visual(puzzle, grid_placeholder, 0) # speed 0 tetap kelihatan cepat

    end_t = time.time()
    
    if success:
        st.success(f"Selesai dalam {round(end_t - start_t, 4)} detik!")
        st.balloons()
    else:
        st.error("Tidak ditemukan solusi.")