import streamlit as st
import time
import pandas as pd
import numpy as np
import random
from typing import List, Tuple, Optional, Set, Dict
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(page_title="Gridly - Premium Logic", layout="wide", page_icon="💎")

# --- PROFESSIONAL GRADIENT CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #2af598 0%, #009efd 100%);
        --surface-color: #ffffff;
        --background-color: #f4f7f6;
        --text-main: #2d3436;
        --text-muted: #636e72;
        --border-color: #dfe6e9;
    }

    * { font-family: 'Inter', sans-serif; }
    
    .stApp { 
        background-color: var(--background-color);
    }

    /* Mature Header */
    .main-header {
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }

    /* Clean Navigation Buttons */
    .stButton>button {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        color: var(--text-main);
        padding: 1rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    .stButton>button:hover {
        border-color: #667eea;
        color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.05);
    }

    /* Sophisticated Cards */
    .premium-card {
        background: var(--surface-color);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.03);
        margin-bottom: 2rem;
    }

    /* Metric Styling */
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 15px;
        padding: 1.5rem;
    }
    [data-testid="stMetric"] label { color: var(--text-muted) !important; font-weight: 600 !important; }
    [data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #667eea !important; font-weight: 800 !important; }

    /* Grid Customization */
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border-color);
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SUDOKU STYLING HELPER ---
def get_styled_sudoku(grid, size):
    k = int(size**0.5)
    df = pd.DataFrame(grid)
    
    # Mature Palette
    colors = ['#f8f9fa', '#e9ecef', '#dee2e6', '#ced4da']
    
    def apply_block_styles(data):
        styles = pd.DataFrame('', index=data.index, columns=data.columns)
        for r in range(size):
            for c in range(size):
                block_r, block_c = r // k, c // k
                color_idx = (block_r + block_c) % 2
                bg = '#ffffff' if color_idx == 0 else '#f8f9fa'
                styles.iloc[r, c] = f'background-color: {bg}; color: #2d3436; font-weight: 600; border: 1px solid #edf2f7;'
        return styles

    symbols = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    display_df = df.map(lambda v: symbols[int(v)] if v > 0 else "")
    df_styled = display_df.style.pipe(lambda s: s.apply(apply_block_styles, axis=None))
    return df_styled

# --- SUDOKU LOGIC ENGINE ---
class SudokuEngine:
    def __init__(self, size: int = 16):
        self.n = size
        self.k = int(size**0.5)
        self.symbols = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.nodes_explored = 0
        self.backtracks = 0
        self.start_time = 0

    def is_valid_grid(self, grid: List[List[int]]) -> bool:
        """Check if the entire grid is valid and complete"""
        for r in range(self.n):
            for c in range(self.n):
                val = grid[r][c]
                if val == 0: return False
                # Temporary clear to check validity
                grid[r][c] = 0
                if not self.is_valid(grid, r, c, val):
                    grid[r][c] = val
                    return False
                grid[r][c] = val
        return True

    def is_valid(self, grid: List[List[int]], r: int, c: int, num: int) -> bool:
        for i in range(self.n):
            if grid[r][i] == num or grid[i][c] == num: return False
        sr, sc = (r // self.k) * self.k, (c // self.k) * self.k
        for i in range(sr, sr + self.k):
            for j in range(sc, sc + self.k):
                if grid[i][j] == num: return False
        return True

    def get_possibilities(self, grid: List[List[int]], r: int, c: int) -> Set[int]:
        used = set()
        for i in range(self.n):
            used.add(grid[r][i]); used.add(grid[i][c])
        sr, sc = (r // self.k) * self.k, (c // self.k) * self.k
        for i in range(sr, sr + self.k):
            for j in range(sc, sc + self.k): used.add(grid[i][j])
        return {n for n in range(1, self.n + 1) if n not in used}

    def solve(self, grid: List[List[int]], visualize: bool = False, placeholder = None) -> bool:
        self.nodes_explored += 1
        
        # MRV Heuristic
        best_cell = None
        min_p = self.n + 1
        for r in range(self.n):
            for c in range(self.n):
                if grid[r][c] == 0:
                    p = self.get_possibilities(grid, r, c)
                    if len(p) == 0: return False
                    if len(p) < min_p:
                        min_p, best_cell, best_p = len(p), (r, c), p
                    if min_p == 1: break
            if min_p == 1: break
            
        if not best_cell: return True
        
        r, c = best_cell
        for num in best_p:
            grid[r][c] = num
            if visualize and placeholder:
                self.update_visual(grid, r, c, placeholder)
            
            if self.solve(grid, visualize, placeholder): return True
            
            grid[r][c] = 0
            self.backtracks += 1
            if visualize and placeholder:
                self.update_visual(grid, r, c, placeholder, is_backtrack=True)
                
        return False

    def update_visual(self, grid, r, c, placeholder, is_backtrack=False):
        styled_df = get_styled_sudoku(grid, self.n)
        
        with placeholder.container():
            st.markdown(f"""
                <div style='padding: 10px; border-radius: 10px; background: {"#fee2e2" if is_backtrack else "#e0f2fe"}; border-left: 5px solid {"#FF8B8B" if is_backtrack else "#1FA7E1"}'>
                    <b>{'🛑 BACKTRACKING' if is_backtrack else '🔍 EXPLORING'}</b> at ({r},{c})<br>
                    Nodes: {self.nodes_explored} | Backtracks: {self.backtracks}
                </div>
            """, unsafe_allow_html=True)
            st.dataframe(styled_df, use_container_width=True)
            time.sleep(0.02)

    def generate_puzzle(self, difficulty: str) -> List[List[int]]:
        # Start with empty grid
        grid = [[0 for _ in range(self.n)] for _ in range(self.n)]
        # Fill diagonal blocks (independent)
        for i in range(0, self.n, self.k):
            nums = list(range(1, self.n + 1))
            random.shuffle(nums)
            for r in range(self.k):
                for c in range(self.k):
                    grid[i+r][i+c] = nums.pop()
        
        # Solve the rest to get a complete board
        self.solve(grid)
        
        # Remove cells based on difficulty
        cells_to_remove = {
            "Easy": self.n * self.n * 0.4,
            "Medium": self.n * self.n * 0.6,
            "Hard": self.n * self.n * 0.75,
            "Extreme": self.n * self.n * 0.85
        }.get(difficulty, self.n * self.n * 0.5)
        
        puzzle = [row[:] for row in grid]
        coords = [(r, c) for r in range(self.n) for c in range(self.n)]
        random.shuffle(coords)
        
        for i in range(int(cells_to_remove)):
            r, c = coords[i]
            puzzle[r][c] = 0
            
        return puzzle

# --- SESSION STATE MANAGEMENT ---
if 'page' not in st.session_state: st.session_state.page = "Landing"
if 'grid_size' not in st.session_state: st.session_state.grid_size = 16
if 'difficulty' not in st.session_state: st.session_state.difficulty = "Medium"
if 'current_grid' not in st.session_state: st.session_state.current_grid = None
if 'stats' not in st.session_state: st.session_state.stats = []

def nav_to(page):
    st.session_state.page = page
    st.rerun()

# --- PAGES ---

def show_landing():
    st.markdown("<h1 class='main-header'>Gridly</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:var(--text-muted); font-size:1.1rem; margin-bottom:3rem;'>PREMIUM LOGIC EXPERIENCE</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        if st.button("🎮 PLAY SESSION", key="btn_play", use_container_width=True): nav_to("Play")
        if st.button("🤖 AI ASSISTANT", key="btn_solve", use_container_width=True): nav_to("Solve")
        if st.button("📊 ANALYTICS", key="btn_analysis", use_container_width=True): nav_to("Analysis")
        if st.button("⚙️ PREFERENCES", key="btn_settings", use_container_width=True): nav_to("Settings")
        if st.button("ℹ️ ABOUT & HELP", key="btn_about", use_container_width=True): nav_to("About")
        st.markdown("</div>", unsafe_allow_html=True)

# --- UNIFIED ARCADE GRID COMPONENT ---
def unified_arcade_grid(grid, size, key):
    df = pd.DataFrame(grid)
    col_cfg = {str(i): st.column_config.NumberColumn(label="", width="small") for i in range(size)}
    df.columns = [str(i) for i in range(size)]
    
    st.markdown(f"<div class='premium-card' style='padding:1.5rem;'>", unsafe_allow_html=True)
    edited_df = st.data_editor(df, column_config=col_cfg, use_container_width=True, hide_index=True, key=key)
    st.markdown("</div>", unsafe_allow_html=True)
    return edited_df.values.astype(int).tolist()

def show_play():
    st.markdown("<h1 class='main-header' style='font-size:2.5rem;'>Logic Session</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        if st.button("🏠 RETURN TO HUB", use_container_width=True):
            nav_to("Landing")
        st.divider()
        size = st.selectbox("Grid Dimensions", [9, 16, 25], index=1)
        diff = st.select_slider("Complexity Level", ["Easy", "Medium", "Hard", "Extreme"], value="Medium")
        if st.button("🔄 GENERATE NEW PUZZLE", use_container_width=True):
            engine = SudokuEngine(size)
            st.session_state.current_grid = engine.generate_puzzle(diff)
            st.session_state.grid_size = size
            st.session_state.difficulty = diff

    if st.session_state.current_grid is None:
        st.info("Select parameters and generate a puzzle to begin.")
    else:
        with st.expander("ℹ️ ATURAN & PETUNJUK", expanded=False):
            st.markdown("""
            **Aturan Dasar Sudoku:**
            - **Baris:** Tidak boleh ada angka yang sama dalam satu baris horizontal.
            - **Kolom:** Tidak boleh ada angka yang sama dalam satu kolom vertikal.
            - **Blok (Sub-grid):** Tidak boleh ada angka yang sama dalam satu kotak blok (misal 3x3 atau 4x4).
            
            **Cara Bermain:**
            - Klik pada kotak untuk memasukkan angka (1 hingga dimensi grid).
            - Angka **0** berarti kotak kosong.
            - Gunakan tombol **Verify Solution** di bawah untuk mengecek hasil akhir Anda.
            """)
        
        st.write(f"**Session:** {st.session_state.difficulty} | **Grid:** {st.session_state.grid_size}x{st.session_state.grid_size}")
        
        # Simplified Input System
        if st.session_state.grid_size <= 16:
            st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
            new_grid = []
            k = int(st.session_state.grid_size**0.5)
            
            for r in range(st.session_state.grid_size):
                cols = st.columns(st.session_state.grid_size)
                row_vals = []
                for c in range(st.session_state.grid_size):
                    val = cols[c].number_input(
                        label=f"r{r}c{c}",
                        min_value=0,
                        max_value=st.session_state.grid_size,
                        value=int(st.session_state.current_grid[r][c]),
                        key=f"play_{r}_{c}",
                        label_visibility="collapsed"
                    )
                    row_vals.append(val)
                new_grid.append(row_vals)
            st.session_state.current_grid = new_grid
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.session_state.current_grid = unified_arcade_grid(st.session_state.current_grid, 25, "play_elite")

        if st.button("✨ VERIFY SOLUTION", use_container_width=True):
            engine = SudokuEngine(st.session_state.grid_size)
            if engine.is_valid_grid(st.session_state.current_grid):
                st.balloons()
                st.success("Verification Successful. Logic is sound.")
            else:
                st.error("Inconsistencies detected. Please review your entries.")

def show_solve():
    st.markdown("<h1 class='main-header' style='font-size:2.5rem;'>AI Diagnostics</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        if st.button("🏠 RETURN TO HUB", key="btn_solve_back", use_container_width=True):
            nav_to("Landing")
        st.divider()
        size = st.selectbox("Grid Dimensions", [9, 16, 25], index=1)
        mode = st.radio("Processing Mode", ["Instant", "Step-by-Step"])

    with st.expander("ℹ️ PETUNJUK INPUT AI", expanded=False):
        st.markdown("""
        **Cara Menggunakan AI Solver:**
        1. **Input Grid:** Masukkan angka-angka yang sudah diketahui pada grid di bawah.
        2. **Validasi Aturan:** Pastikan tidak ada angka yang sama dalam satu baris, kolom, atau blok sebelum memulai.
        3. **Mode Instant:** AI akan langsung memberikan solusi akhir.
        4. **Mode Step-by-Step:** Lihat bagaimana AI bekerja dan melakukan *backtracking* secara visual.
        
        *Catatan: Gunakan angka **0** atau kosongkan sel untuk kotak yang belum terisi.*
        """)

    st.write("### Input Matrix")
    st.session_state.solve_grid = unified_arcade_grid(st.session_state.solve_grid if 'solve_grid' in st.session_state and len(st.session_state.solve_grid) == size else [[0]*size for _ in range(size)], size, "solve_input")
    
    viz_placeholder = st.empty()
    
    if st.button("🚀 INITIATE SOLVER", use_container_width=True):
        engine = SudokuEngine(size)
        start = time.perf_counter()
        solve_copy = [row[:] for row in st.session_state.solve_grid]
        success = engine.solve(solve_copy, visualize=(mode == "Step-by-Step"), placeholder=viz_placeholder)
        end = time.perf_counter()
        
        if success:
            st.session_state.solve_grid = solve_copy
            st.session_state.stats.append({
                "time": end-start, "nodes": engine.nodes_explored, 
                "backtracks": engine.backtracks, "size": size, 
                "difficulty": "AI Assisted", "timestamp": time.time()
            })
            st.success(f"Diagnostics complete in {end-start:.4f}s.")
            st.rerun()
        else:
            st.error("No valid solution exists for the provided matrix.")

def show_analysis():
    st.markdown("<h1 class='main-header' style='font-size:2.5rem;'>Performance Analytics</h1>", unsafe_allow_html=True)
    if st.button("🏠 HUB", key="btn_analysis_back"):
        nav_to("Landing")
    
    if not st.session_state.stats:
        st.info("Insufficient data. Complete a session to generate analytics.")
        return
    
    df_stats = pd.DataFrame(st.session_state.stats)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("AVG LATENCY", f"{df_stats['time'].mean():.3f}s")
    m2.metric("SESSIONS", len(df_stats))
    m3.metric("MAX NODES", df_stats['nodes'].max())
    m4.metric("ITERATIONS", int(df_stats['backtracks'].mean()))
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.write("### Latency Trend")
        fig_time = go.Figure()
        fig_time.add_trace(go.Scatter(y=df_stats['time'], mode='lines+markers', line=dict(color='#667eea', width=3)))
        fig_time.update_layout(margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_time, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.write("### Complexity Distribution")
        fig_nodes = go.Figure()
        fig_nodes.add_trace(go.Bar(x=df_stats['size'], y=df_stats['nodes'], marker_color='#764ba2'))
        fig_nodes.update_layout(margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_nodes, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

def show_settings():
    st.markdown("<h1 class='main-header' style='font-size:2.5rem;'>Preferences</h1>", unsafe_allow_html=True)
    if st.button("🏠 HUB", key="btn_settings_back"):
        nav_to("Landing")
    
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.toggle("Audio Feedback", value=False)
    st.toggle("High Contrast Interface", value=False)
    st.toggle("Persistent State", value=True)
    st.slider("Visualization Speed", 0.0, 1.0, 0.5)
    st.color_picker("Accent Color", "#667eea")
    st.markdown("</div>", unsafe_allow_html=True)

def show_about():
    st.markdown("<h1 class='main-header' style='font-size:2.5rem;'>About & Help</h1>", unsafe_allow_html=True)
    if st.button("🏠 HUB", key="btn_about_back"):
        nav_to("Landing")
    
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("""
    ### 🧩 Apa itu Gridly?
    Gridly adalah platform logika premium yang dirancang untuk menyelesaikan teka-teki Sudoku kompleks. 
    Mendukung berbagai ukuran grid mulai dari standar 9x9 hingga 25x25 yang menantang.

    ### 🧠 Teknologi Solver Hybrid
    Aplikasi ini menggunakan pendekatan **Hybrid Algorithm** yang menggabungkan:
    1.  **Backtracking Search**: Menjamin penemuan solusi jika solusi tersebut ada.
    2.  **MRV (Minimum Remaining Values) Heuristic**: Mempercepat pencarian dengan memilih sel yang memiliki kemungkinan angka paling sedikit terlebih dahulu.

    #### Perbandingan Algoritma:
    | Algoritma | Kecepatan | Efisiensi Memori | Kompleksitas Grid |
    | :--- | :--- | :--- | :--- |
    | Brute Force | Sangat Lambat | Tinggi | Rendah (9x9 saja) |
    | Standard Backtracking | Sedang | Rendah | Menengah (16x16) |
    | **Hybrid (MRV + Backtracking)** | **Sangat Cepat** | **Sangat Rendah** | **Tinggi (Hingga 25x25+)** |

    #### Keunggulan Solver Ini:
    - **Pruning Efisien**: Mengurangi jutaan langkah pencarian yang tidak perlu.
    - **Adaptif**: Performa tetap stabil meskipun pada tingkat kesulitan "Extreme".
    - **Visualisasi Real-time**: Anda dapat melihat bagaimana algoritma membuat keputusan dan melakukan *backtracking* saat terjadi kebuntuan.

    ### 📖 Cara Penggunaan
    1. **Play Session**: 
       - Pilih dimensi grid dan tingkat kesulitan.
       - Isi angka pada kotak yang kosong.
       - Gunakan tombol **Verify Solution** untuk mengecek kebenaran jawabanmu.
    2. **AI Assistant**: 
       - Masukkan angka pada grid yang ingin diselesaikan.
       - Pilih mode **Instant** untuk hasil cepat atau **Step-by-Step** untuk melihat proses berpikir AI.
       - Klik **Initiate Solver** untuk memulai.
    3. **Analytics**: 
       - Pantau performa AI dan kompleksitas grid yang telah diselesaikan.
    4. **Settings**: 
       - Sesuaikan preferensi visual dan interaksi aplikasi.

    ### 🛠️ Teknologi Internal
    Dibangun dengan **Python** menggunakan framework **Streamlit** untuk antarmuka yang responsif dan **Plotly** untuk visualisasi data analitik.
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- APP ROUTER ---
if st.session_state.page == "Landing":
    show_landing()
elif st.session_state.page == "Play":
    show_play()
elif st.session_state.page == "Solve":
    show_solve()
elif st.session_state.page == "Analysis":
    show_analysis()
elif st.session_state.page == "Settings":
    show_settings()
elif st.session_state.page == "About":
    show_about()

# --- FOOTER ---
st.divider()
st.markdown("""
<p style='text-align:center; color:var(--text-muted); font-size:0.9rem;'>
Gridly Premium Logic • Engineered for Cognitive Performance<br>
<i>A sophisticated environment for complex logic solving and analysis.</i>
</p>
""", unsafe_allow_html=True)
