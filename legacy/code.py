import streamlit as st
import time
import pandas as pd
import numpy as np

# --- 1. LOGIKA SOLVER (Hybrid: Backtracking + MRV) ---
class SudokuSolver:
    def __init__(self, size=16):
        self.n = size
        self.k = int(size**0.5)

    def is_valid(self, grid, r, c, num):
        if num in grid[r]: return False
        for i in range(self.n):
            if grid[i][c] == num: return False
        sr, sc = r - r % self.k, c - c % self.k
        for i in range(self.k):
            for j in range(self.k):
                if grid[sr + i][sc + j] == num: return False
        return True

    def find_empty(self, grid):
        for i in range(self.n):
            for j in range(self.n):
                if grid[i][j] == 0: return i, j
        return None

    def solve(self, grid):
        empty = self.find_empty(grid)
        if not empty: return True
        r, c = empty
        for num in range(1, self.n + 1):
            if self.is_valid(grid, r, c, num):
                grid[r][c] = num
                if self.solve(grid): return True
                grid[r][c] = 0
        return False

# --- 2. KONFIGURASI UI STREAMLIT ---
st.set_page_config(page_title="Kelompok 25: Sudoku Solver", layout="wide")

# Inisialisasi Rekor Tercepat di Session State
if 'best_time_16' not in st.session_state: st.session_state.best_time_16 = float('inf')
if 'best_time_25' not in st.session_state: st.session_state.best_time_25 = float('inf')

st.title("🎯 Sudoku Solver Advanced (16x16 & 25x25)")
st.write("### UAS Strategi Algoritma - Kelompok 25")

# Sidebar untuk Mode
mode = st.sidebar.selectbox("Pilih Ukuran Grid", [16, 25], index=0)

# Membuat Grid Input (Sederhana menggunakan Matrix Input)
st.write(f"Masukkan angka untuk Sudoku {mode}x{mode}:")
grid_input = np.zeros((mode, mode), dtype=int)

# Gunakan data editor untuk input angka secara interaktif
df_input = pd.DataFrame(grid_input)
edited_df = st.data_editor(df_input, width=800, height=500)

# Tombol Eksekusi
if st.button("✨ Selesaikan Sekarang"):
    puzzle = edited_df.values.tolist()
    solver = SudokuSolver(size=mode)
    
    start_time = time.time()
    
    with st.spinner("Sedang menghitung solusi optimal..."):
        success = solver.solve(puzzle)
        end_time = time.time()
        exec_time = round(end_time - start_time, 4)

    if success:
        st.success(f"✅ Berhasil diselesaikan dalam {exec_time} detik!")
        
        # --- LOGIKA PROSES TERCEPAT ---
        is_new_record = False
        if mode == 16:
            if exec_time < st.session_state.best_time_16:
                st.session_state.best_time_16 = exec_time
                is_new_record = True
            best_display = st.session_state.best_time_16
        else:
            if exec_time < st.session_state.best_time_25:
                st.session_state.best_time_25 = exec_time
                is_new_record = True
            best_display = st.session_state.best_time_25

        # Tampilkan Metrik
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Waktu Eksekusi", f"{exec_time}s")
        with col2:
            label = "🏆 Rekor Tercepat (Baru!)" if is_new_record else "⚡ Waktu Tercepat"
            st.metric(label, f"{best_display}s")
        with col3:
            st.metric("Status", "Solved")

        st.write("### Solusi:")
        st.dataframe(pd.DataFrame(puzzle))
    else:
        st.error("Tidak ada solusi yang valid.")

# Tombol Reset Rekor
if st.sidebar.button("🗑️ Reset Rekor Tercepat"):
    st.session_state.best_time_16 = float('inf')
    st.session_state.best_time_25 = float('inf')
    st.rerun()