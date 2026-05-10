import streamlit as st
import time
import pandas as pd
import numpy as np
from typing import List, Tuple, Optional, Set, Dict

# --- SUDOKU HYBRID SOLVER CORE ---
class SudokuHybridSolver:
    def __init__(self, size: int = 16):
        self.n = size
        self.k = int(size**0.5)
        self.symbols = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.nodes_explored = 0
        self.backtracks = 0
        
    def get_neighbors(self, r: int, c: int) -> Set[Tuple[int, int]]:
        neighbors = set()
        # Row and column
        for i in range(self.n):
            if i != c: neighbors.add((r, i))
            if i != r: neighbors.add((i, c))
        # Box
        sr, sc = (r // self.k) * self.k, (c // self.k) * self.k
        for i in range(sr, sr + self.k):
            for j in range(sc, sc + self.k):
                if i != r or j != c:
                    neighbors.add((i, j))
        return neighbors

    def get_possibilities(self, grid: List[List[int]], r: int, c: int) -> Set[int]:
        if grid[r][c] != 0:
            return set()
        
        used = set()
        # Row
        for i in range(self.n):
            if grid[r][i] != 0: used.add(grid[r][i])
        # Column
        for i in range(self.n):
            if grid[i][c] != 0: used.add(grid[i][c])
        # Box
        sr, sc = (r // self.k) * self.k, (c // self.k) * self.k
        for i in range(sr, sr + self.k):
            for j in range(sc, sc + self.k):
                if grid[i][j] != 0: used.add(grid[i][j])
        
        return {n for n in range(1, self.n + 1) if n not in used}

    def find_best_cell(self, grid: List[List[int]]) -> Optional[Tuple[int, int]]:
        """MRV (Minimum Remaining Values) + Degree Heuristic tie-breaker"""
        best_cell = None
        min_remaining = self.n + 1
        max_degree = -1
        
        for r in range(self.n):
            for c in range(self.n):
                if grid[r][c] == 0:
                    possibilities = self.get_possibilities(grid, r, c)
                    num_remaining = len(possibilities)
                    
                    if num_remaining == 0:
                        return None # Fail early
                    
                    if num_remaining < min_remaining:
                        min_remaining = num_remaining
                        best_cell = (r, c)
                        # Re-calculate degree for tie-breaker
                        max_degree = self.get_degree(grid, r, c)
                    elif num_remaining == min_remaining:
                        degree = self.get_degree(grid, r, c)
                        if degree > max_degree:
                            max_degree = degree
                            best_cell = (r, c)
                            
                    if min_remaining == 1:
                        return (r, c) # Heuristic: Singleton choice
        return best_cell

    def get_degree(self, grid: List[List[int]], r: int, c: int) -> int:
        """Count unassigned neighbors"""
        count = 0
        for nr, nc in self.get_neighbors(r, c):
            if grid[nr][nc] == 0:
                count += 1
        return count

    def get_lcv_ordered_values(self, grid: List[List[int]], r: int, c: int, possibilities: Set[int]) -> List[int]:
        """LCV (Least Constraining Value) Heuristic"""
        if len(possibilities) <= 1:
            return list(possibilities)
            
        neighbors = self.get_neighbors(r, c)
        value_impacts = []
        
        for val in possibilities:
            impact = 0
            for nr, nc in neighbors:
                if grid[nr][nc] == 0:
                    # If placing val at (r,c) removes val from neighbor's possibilities
                    # We check if val is valid for neighbor currently
                    if self.is_valid(grid, nr, nc, val):
                        impact += 1
            value_impacts.append((impact, val))
        
        # Sort by least impact (ascending)
        value_impacts.sort()
        return [v for _, v in value_impacts]

    def is_valid(self, grid: List[List[int]], r: int, c: int, num: int) -> bool:
        # Row
        for i in range(self.n):
            if grid[r][i] == num: return False
        # Column
        for i in range(self.n):
            if grid[i][c] == num: return False
        # Box
        sr, sc = (r // self.k) * self.k, (c // self.k) * self.k
        for i in range(sr, sr + self.k):
            for j in range(sc, sc + self.k):
                if grid[i][j] == num: return False
        return True

    def solve(self, grid: List[List[int]]) -> bool:
        self.nodes_explored += 1
        
        cell = self.find_best_cell(grid)
        if not cell:
            # If no empty cell, solved. 
            # If find_best_cell returned None but there are empty cells, it means a cell has 0 possibilities.
            for r in range(self.n):
                for c in range(self.n):
                    if grid[r][c] == 0: return False
            return True
        
        r, c = cell
        possibilities = self.get_possibilities(grid, r, c)
        ordered_values = self.get_lcv_ordered_values(grid, r, c, possibilities)
        
        for num in ordered_values:
            grid[r][c] = num
            if self.solve(grid):
                return True
            grid[r][c] = 0
            self.backtracks += 1
            
        return False

# --- STREAMLIT UI ---
def main():
    st.set_page_config(page_title="Gridly - Modern Sudoku", layout="wide", page_icon="🧩")
    
    # Custom CSS for Gridly's unique visual identity
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800;900&display=swap');
        
        * { font-family: 'Nunito', sans-serif; }
        
        .main { background-color: #fdfaff; }
        
        /* Pastel Color Palette */
        :root {
            --amethyst: #9956DE;
            --slate-blue: #7274ED;
            --summer-sky: #1FA7E1;
            --downy: #6ED1CF;
            --pastel-green: #75D06A;
            --texas-rose: #FFB356;
            --mona-lisa: #FF8B8B;
            --illusion: #FB96BB;
        }

        .stButton>button { 
            width: 100%; 
            border-radius: 12px; 
            height: 3.5em; 
            background: linear-gradient(135deg, #9956DE, #7274ED); 
            color: white; 
            font-weight: 800; 
            border: none;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(114, 116, 237, 0.3);
        }
        .stButton>button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(114, 116, 237, 0.4);
            color: white;
        }
        
        .header-text { 
            color: #9956DE; 
            text-align: center; 
            font-weight: 900; 
            font-size: 3.5rem;
            margin-bottom: 0; 
            letter-spacing: -1px;
        }
        .sub-text { 
            color: #7274ED; 
            text-align: center; 
            font-weight: 600; 
            margin-top: 0; 
            margin-bottom: 2.5rem;
            font-size: 1.2rem;
        }
        
        .intro-card { 
            background: white; 
            padding: 25px; 
            border-radius: 20px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            margin-bottom: 20px; 
            border: 1px solid #f0f0f0;
        }
        
        .highlight-box {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 8px;
            font-weight: 800;
            color: white;
            margin: 5px;
        }
        
        /* Custom styles for metrics and inputs */
        .stMetric { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); border: 1px solid #eee; }
        div[data-testid="stExpander"] { border-radius: 15px; border: 1px solid #eee; background: white; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='header-text'>Gridly</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-text'>Fresh • Engaging • Analytical</p>", unsafe_allow_html=True)

    with st.expander("✨ Discover Gridly", expanded=True):
        st.markdown(f"""
        <div class='intro-card'>
            <p><strong>Gridly</strong> is a modern Sudoku puzzle application designed to provide a fresh and engaging brain-training experience through advanced grid sizes such as <strong>16x16 and 25x25</strong>. Unlike traditional Sudoku games, Gridly combines challenging logic-based gameplay with a colorful and minimalist interface, making complex puzzles feel more interactive and enjoyable for users.</p>
            <p>The application helps improve concentration, analytical thinking, and problem-solving skills while maintaining a relaxing and visually appealing atmosphere. Featuring multiple Sudoku modes with automatically generated boards, Gridly includes real-time answer validation, advanced heuristics, and gameplay statistics to enhance your experience.</p>
            <div style='text-align: center; margin-top: 20px;'>
                <span class='highlight-box' style='background-color: #9956DE;'>9x9 Standard</span>
                <span class='highlight-box' style='background-color: #7274ED;'>16x16 Pro</span>
                <span class='highlight-box' style='background-color: #1FA7E1;'>25x25 Elite</span>
                <span class='highlight-box' style='background-color: #75D06A;'>Hybrid AI</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("⚙️ Konfigurasi")
    size_option = st.sidebar.selectbox("Ukuran Grid", [9, 16, 25], index=1)
    
    if 'grid' not in st.session_state or st.session_state.get('last_size') != size_option:
        st.session_state.grid = np.zeros((size_option, size_option), dtype=int)
        st.session_state.last_size = size_option

    # Control Buttons in Sidebar
    if st.sidebar.button("🧹 Reset Grid"):
        st.session_state.grid = np.zeros((size_option, size_option), dtype=int)
        st.rerun()

    if st.sidebar.button("📝 Muat Contoh (16x16)"):
        if size_option == 16:
            example = np.zeros((16, 16), dtype=int)
            # Some clues for 16x16
            clues = [(0,0,1), (0,4,5), (0,8,9), (0,12,13), (4,1,6), (8,2,11), (12,3,16)]
            for r, c, v in clues: example[r][c] = v
            st.session_state.grid = example
            st.rerun()
        else:
            st.sidebar.warning("Contoh hanya tersedia untuk ukuran 16x16")

    # Layout using Tabs for better mobile experience
    tab1, tab2 = st.tabs(["📝 Input Puzzle", "🚀 Hasil & Analisis"])
    
    with tab1:
        st.write("Isi sel kosong dengan 0 atau biarkan kosong.")
        
        # Display as data editor
        df_input = pd.DataFrame(st.session_state.grid)
        edited_df = st.data_editor(df_input, use_container_width=True, hide_index=True)
        
    with tab2:
        if st.button("Selesaikan Sudoku", use_container_width=True):
            grid_to_solve = edited_df.values.astype(int).tolist()
            solver = SudokuHybridSolver(size_option)
            
            start_time = time.perf_counter()
            with st.spinner("Sedang mencari solusi optimal..."):
                success = solver.solve(grid_to_solve)
            end_time = time.perf_counter()
            
            duration = end_time - start_time
            
            if success:
                st.success(f"Solusi ditemukan dalam {duration:.4f} detik!")
                
                # Show results
                result_df = pd.DataFrame(grid_to_solve)
                symbols = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                
                # Format for display
                def format_val(v):
                    if v == 0: return ""
                    if size_option == 16 and v > 9: return symbols[v]
                    return str(v)
                
                st.table(result_df.applymap(format_val))
                
                # Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Waktu", f"{duration:.4f}s")
                m2.metric("Nodes", f"{solver.nodes_explored:,}")
                m3.metric("Backtracks", f"{solver.backtracks:,}")
            else:
                st.error("Tidak ditemukan solusi untuk puzzle ini.")
                st.info("Pastikan input awal valid (tidak ada angka yang bertabrakan di baris, kolom, atau box).")

    st.divider()
    with st.expander("ℹ️ Tentang Algoritma"):
        st.write("""
        Aplikasi ini menggunakan pendekatan **Constraint Satisfaction Problem (CSP)** dengan kombinasi beberapa teknik:
        1.  **MRV (Minimum Remaining Values):** Memilih sel dengan jumlah kemungkinan angka paling sedikit untuk dikerjakan terlebih dahulu.
        2.  **Degree Heuristic:** Jika ada beberapa sel dengan jumlah kemungkinan yang sama, pilih sel yang paling banyak membatasi sel tetangganya.
        3.  **LCV (Least Constraining Value):** Memilih angka yang paling sedikit membatasi pilihan angka untuk sel-sel tetangga yang belum terisi.
        4.  **Backtracking:** Proses pencarian solusi secara rekursif dengan kemampuan membatalkan langkah jika menemui jalan buntu.
        """)

if __name__ == "__main__":
    main()
