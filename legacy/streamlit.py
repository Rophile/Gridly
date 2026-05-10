import streamlit as st
import time
import pandas as pd
import numpy as np

# --- 1. KELAS SOLVER DENGAN BERBAGAI METODE ---
class SudokuSolver:
    def __init__(self, size=16):
        self.n = size
        self.k = int(size**0.5)
        self.symbols = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXY"

    def is_valid(self, grid, r, c, num):
        # Cek Baris
        if num in grid[r]: return False
        # Cek Kolom
        for i in range(self.n):
            if grid[i][c] == num: return False
        # Cek Box
        sr, sc = r - r % self.k, c - c % self.k
        for i in range(self.k):
            for j in range(self.k):
                if grid[sr + i][sc + j] == num: return False
        return True

    # --- A. METODE BACKTRACKING MURNI (Brute Force) ---
    def solve_backtracking(self, grid):
        for r in range(self.n):
            for c in range(self.n):
                if grid[r][c] == 0:
                    for num in range(1, self.n + 1):
                        if self.is_valid(grid, r, c, num):
                            grid[r][c] = num
                            if self.solve_backtracking(grid): return True
                            grid[r][c] = 0
                    return False
        return True

    # --- B. METODE GREEDY ---
    # Greedy dalam Sudoku biasanya hanya mengisi sel yang "pasti" benar saat itu juga.
    # Jika tidak ada yang pasti, ia akan menebak angka pertama yang valid.
    def solve_greedy(self, grid):
        for r in range(self.n):
            for c in range(self.n):
                if grid[r][c] == 0:
                    for num in range(1, self.n + 1):
                        if self.is_valid(grid, r, c, num):
                            grid[r][c] = num # Langsung pilih yang pertama valid
                            return self.solve_greedy(grid)
        return True

    # --- C. METODE MRV (Minimum Remaining Values) ---
    def get_possibilities(self, grid, r, c):
        used = set()
        for i in range(self.n):
            used.add(grid[r][i]); used.add(grid[i][c])
        sr, sc = r - r % self.k, c - c % self.k
        for i in range(self.k):
            for j in range(self.k): used.add(grid[sr + i][sc + j])
        return [n for n in range(1, self.n + 1) if n not in used]

    def find_mrv_cell(self, grid):
        min_p = self.n + 1
        best_cell = None
        for r in range(self.n):
            for c in range(self.n):
                if grid[r][c] == 0:
                    p_len = len(self.get_possibilities(grid, r, c))
                    if p_len < min_p:
                        min_p = p_len
                        best_cell = (r, c)
        return best_cell

    def solve_mrv(self, grid):
        cell = self.find_mrv_cell(grid)
        if not cell: return True
        r, c = cell
        possibilities = self.get_possibilities(grid, r, c)
        for num in possibilities:
            grid[r][c] = num
            if self.solve_mrv(grid): return True
            grid[r][c] = 0
        return False

    # --- D. GABUNGAN (Hybrid: MRV + Forward Checking/Optimized) ---
    def solve_hybrid(self, grid):
        # Ini menggunakan logika tercepat yang kita buat sebelumnya
        min_p = self.n + 1
        best_cell, best_p = None, []
        for r in range(self.n):
            for c in range(self.n):
                if grid[r][c] == 0:
                    p = self.get_possibilities(grid, r, c)
                    if len(p) == 0: return False
                    if len(p) < min_p:
                        min_p, best_cell, best_p = len(p), (r, c), p
                    if min_p == 1: break # Heuristic: Singleton
            if min_p == 1: break
            
        if not best_cell: return True
        
        for num in best_p:
            grid[best_cell[0]][best_cell[1]] = num
            if self.solve_hybrid(grid): return True
            grid[best_cell[0]][best_cell[1]] = 0
        return False

# --- 2. UI STREAMLIT ---
st.set_page_config(page_title="Kelompok 25: Multi-Method Solver", layout="wide")

# CSS Tema Ungu
st.markdown("""
    <style>
    .stApp { background-color: #fdfaff; }
    h1 { color: #4a148c; }
    .stButton > button { background-color: #7b1fa2 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔮 Sudoku Multi-Method Solver")
st.write("UAS Strategi Algoritma - Pilih Metode untuk melihat perbedaannya.")

# Sidebar
st.sidebar.title("💜 Kontrol")
mode = st.sidebar.selectbox("Ukuran Sudoku", [16, 25])
method = st.sidebar.radio("Pilih Metode Strategi Algoritma:", 
                         ["Backtracking Murni", "Greedy Saja", "MRV Saja", "Gabungan (Hybrid)"])

# Main Grid
if 'grid_data' not in st.session_state or st.session_state.grid_data.shape[0] != mode:
    st.session_state.grid_data = np.zeros((mode, mode), dtype=int)

df_input = pd.DataFrame(st.session_state.grid_data)
edited_df = st.data_editor(df_input, use_container_width=True, hide_index=True)

if st.button("🚀 JALANKAN SOLVER", use_container_width=True):
    puzzle = edited_df.values.astype(int).tolist()
    solver = SudokuSolver(size=mode)
    
    start_t = time.time()
    success = False
    
    with st.spinner(f"Menyelesaikan dengan metode {method}..."):
        if method == "Backtracking Murni":
            success = solver.solve_backtracking(puzzle)
        elif method == "Greedy Saja":
            success = solver.solve_greedy(puzzle)
        elif method == "MRV Saja":
            success = solver.solve_mrv(puzzle)
        else:
            success = solver.solve_hybrid(puzzle)
    
    end_t = time.time()
    exec_time = round(end_t - start_t, 4)

    if success:
        st.success(f"Metode {method} berhasil dalam {exec_time} detik!")
        st.table(pd.DataFrame(puzzle).map(lambda v: solver.symbols[int(v)] if v != 0 else ""))
        
        # Dashboard Analisis
        c1, c2 = st.columns(2)
        c1.metric("Waktu Eksekusi", f"{exec_time}s")
        c2.metric("Metode", method)
    else:
        st.error(f"Metode {method} gagal menemukan solusi (mungkin terjebak atau input salah).")

# Tombol Tambahan untuk Perbandingan
if st.sidebar.button("📊 Bandingkan Semua Metode"):
    st.write("### ⏱️ Perbandingan Waktu Eksekusi")
    # Logika perbandingan bisa ditambahkan di sini untuk menjalankan 4 metode sekaligus
    st.info("Fitur ini akan menjalankan semua algoritma satu per satu pada input yang sama.")