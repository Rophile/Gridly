import streamlit as st
import time
import pandas as pd
import numpy as np
import random
from typing import List, Tuple, Optional, Set, Dict
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(page_title="Gridly - Puzzle Arcade", layout="wide", page_icon="🧩")

# --- CUSTOM NEON ARCADE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800;900&family=Outfit:wght@400;700;900&family=Bungee&display=swap');
    
    :root {
        --amethyst: #9956DE;
        --slate-blue: #7274ED;
        --summer-sky: #1FA7E1;
        --neon-pink: #FF71CE;
        --neon-blue: #01CDFE;
        --neon-green: #05FFA1;
        --neon-yellow: #B967FF;
        --neon-orange: #FFFB96;
    }

    * { font-family: 'Outfit', sans-serif; }
    
    /* Background Gradient */
    .stApp { 
        background: radial-gradient(circle at top left, #fdfaff 0%, #eef2ff 50%, #fdfaff 100%);
    }

    /* Bungee Font for Titles */
    .arcade-title {
        font-family: 'Bungee', cursive;
        color: var(--amethyst);
        text-shadow: 4px 4px 0px var(--neon-pink), 8px 8px 0px rgba(0,0,0,0.1);
        text-align: center;
        font-size: 5.5rem;
        margin-bottom: 0;
        animation: floating 3s ease-in-out infinite;
    }

    @keyframes floating {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    /* 3D Floating Arcade Buttons */
    .stButton>button {
        background: linear-gradient(135deg, var(--amethyst), var(--slate-blue));
        border: none;
        border-radius: 20px;
        color: white;
        padding: 25px;
        font-size: 1.4rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 10px 0 #4f46e5, 0 15px 30px rgba(114, 116, 237, 0.4);
        transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        margin-bottom: 10px;
    }
    
    .stButton>button:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 0 #4f46e5, 0 20px 40px rgba(114, 116, 237, 0.5);
        background: linear-gradient(135deg, var(--slate-blue), var(--amethyst));
        color: white;
    }

    .stButton>button:active {
        transform: translateY(5px);
        box-shadow: 0 5px 0 #4f46e5;
    }

    /* Glassmorphism Cards */
    .arcade-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 30px;
        padding: 40px;
        border: 4px solid white;
        box-shadow: 0 20px 50px rgba(0,0,0,0.05);
        margin-top: 20px;
    }

    /* Glowing Metric Cards */
    [data-testid="stMetric"] {
        background: white;
        border-radius: 20px;
        padding: 20px;
        border-bottom: 5px solid var(--neon-blue);
        box-shadow: 0 10px 20px rgba(0,0,0,0.02);
        transition: transform 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: scale(1.05);
        border-bottom: 5px solid var(--neon-pink);
    }

    /* Custom Data Editor Styling */
    div[data-testid="stDataFrame"] {
        border: 6px solid var(--slate-blue);
        border-radius: 25px;
        overflow: hidden;
        box-shadow: 0 25px 50px rgba(114, 116, 237, 0.2);
    }

    /* Animations */
    .fade-in { animation: fadeIn 1s ease-in; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    
    .pulse { animation: pulse 2s infinite; }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    </style>
""", unsafe_allow_html=True)

# --- SUDOKU STYLING HELPER ---
def get_styled_sudoku(grid, size):
    k = int(size**0.5)
    df = pd.DataFrame(grid)
    
    # Gridly Arcade Pastel Palette for Boxes
    # We use a pattern that makes adjacent blocks distinct
    colors = [
        '#fff1f2', # Rose
        '#f0f9ff', # Sky
        '#f0fdf4', # Emerald
        '#fffbeb', # Amber
        '#faf5ff', # Purple
    ]
    
    def apply_block_styles(data):
        styles = pd.DataFrame('', index=data.index, columns=data.columns)
        for r in range(size):
            for c in range(size):
                # Calculate block index for color rotation
                block_r, block_c = r // k, c // k
                # Checkerboard-like pattern for colors
                color_idx = (block_r + block_c) % len(colors)
                styles.iloc[r, c] = f'background-color: {colors[color_idx]}; color: #1e1b4b; font-weight: 800; border: 1px solid rgba(0,0,0,0.05);'
        return styles

    # Convert numbers to symbols for display
    symbols = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    display_df = df.applymap(lambda v: symbols[int(v)] if v > 0 else "")
    
    return display_df.style.apply(apply_block_styles, axis=None)

# --- SUDOKU LOGIC ENGINE ---
class SudokuEngine:
    def __init__(self, size: int = 16):
        self.n = size
        self.k = int(size**0.5)
        self.symbols = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.nodes_explored = 0
        self.backtracks = 0
        self.start_time = 0

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
    st.markdown("<h1 class='arcade-title'>Gridly</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:1.5rem; color:#7274ED; font-weight:800; margin-bottom:3rem; text-transform:uppercase; letter-spacing:4px;'>Logic Playground</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='arcade-card'>", unsafe_allow_html=True)
        if st.button("🎮 PLAY ARCADE", key="btn_play", use_container_width=True): nav_to("Play")
        if st.button("🤖 AI SOLVER", key="btn_solve", use_container_width=True): nav_to("Solve")
        if st.button("📊 ANALYTICS", key="btn_analysis", use_container_width=True): nav_to("Analysis")
        if st.button("⚙️ SETTINGS", key="btn_settings", use_container_width=True): nav_to("Settings")
        st.markdown("</div>", unsafe_allow_html=True)

def show_play():
    st.markdown("<h2 style='text-align:center; color:#9956DE; font-family:Bungee;'>🎮 Play Mode</h2>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.button("🏠 Menu", on_click=lambda: nav_to("Landing"))
        st.divider()
        size = st.selectbox("Grid Size", [9, 16, 25], index=1)
        diff = st.select_slider("Difficulty", ["Easy", "Medium", "Hard", "Extreme"], value="Medium")
        if st.button("🔄 Generate Puzzle", use_container_width=True):
            engine = SudokuEngine(size)
            st.session_state.current_grid = engine.generate_puzzle(diff)
            st.session_state.grid_size = size
            st.session_state.difficulty = diff

    if st.session_state.current_grid is None:
        st.info("Select your difficulty and hit 'Generate'!")
    else:
        col_board, col_edit = st.columns([2, 1])
        
        with col_board:
            st.markdown("<div class='arcade-card'>", unsafe_allow_html=True)
            st.write("### 🕹️ LIVE ARCADE BOARD")
            # Show the board with box colors
            st.dataframe(get_styled_sudoku(st.session_state.current_grid, st.session_state.grid_size), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_edit:
            st.write("### ✏️ INPUT PAD")
            st.write("Type numbers below. The board will update automatically!")
            edited_df = st.data_editor(pd.DataFrame(st.session_state.current_grid), 
                                      use_container_width=True, hide_index=True, key="play_editor")
            
            # Sync edited data back to session state for the live board
            st.session_state.current_grid = edited_df.values.astype(int).tolist()
            
            if st.button("🏆 CLAIM VICTORY", use_container_width=True):
                engine = SudokuEngine(st.session_state.grid_size)
                if engine.solve(st.session_state.current_grid):
                    st.balloons()
                    st.snow()
                    st.markdown("<h1 style='text-align:center; color:#05FFA1; font-family:Bungee;'>JACKPOT!</h1>", unsafe_allow_html=True)
                else:
                    st.error("Game Over! Check your logic.")

def show_solve():
    st.markdown("<h2 style='text-align:center; color:#1FA7E1; font-family:Bungee;'>🤖 AI Solver</h2>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.button("🏠 Menu", on_click=lambda: nav_to("Landing"))
        st.divider()
        size = st.selectbox("Grid Size", [9, 16, 25], index=1)
        mode = st.radio("Solving Style", ["Instant", "Step-by-Step", "Analyze"])

    col_board, col_edit = st.columns([2, 1])
    
    # Initialize empty grid for solver if needed
    if 'solve_grid' not in st.session_state or len(st.session_state.solve_grid) != size:
        st.session_state.solve_grid = [[0 for _ in range(size)] for _ in range(size)]

    with col_board:
        st.markdown("<div class='arcade-card'>", unsafe_allow_html=True)
        st.write("### 🧩 PUZZLE PREVIEW")
        st.dataframe(get_styled_sudoku(st.session_state.solve_grid, size), use_container_width=True)
        viz_placeholder = st.empty()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_edit:
        st.write("### 📝 EDIT PUZZLE")
        input_df = st.data_editor(pd.DataFrame(st.session_state.solve_grid), 
                                 use_container_width=True, hide_index=True, key="solve_editor")
        st.session_state.solve_grid = input_df.values.astype(int).tolist()
        
        if st.button("🚀 START SOLVING", use_container_width=True):
            engine = SudokuEngine(size)
            start = time.perf_counter()
            success = engine.solve(st.session_state.solve_grid, visualize=(mode != "Instant"), placeholder=viz_placeholder)
            end = time.perf_counter()
            
            if success:
                st.success(f"Solved in {end-start:.4f}s")
                # Metrics for analysis
                st.session_state.stats.append({
                    "time": end-start,
                    "nodes": engine.nodes_explored,
                    "backtracks": engine.backtracks,
                    "size": size,
                    "difficulty": "Manual Input",
                    "timestamp": time.time()
                })
            else:
                st.error("No solution found.")

def show_analysis():
    st.markdown("<h2 style='text-align:center; color:#75D06A; font-family:Bungee;'>📊 Analytics</h2>", unsafe_allow_html=True)
    st.button("🏠 Menu", on_click=lambda: nav_to("Landing"))
    
    if not st.session_state.stats:
        st.warning("Play some games first to see your logic stats!")
        return
    
    df_stats = pd.DataFrame(st.session_state.stats)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("AVG SPEED", f"{df_stats['time'].mean():.3f}s")
    m2.metric("WINS", len(df_stats))
    m3.metric("COMPLEXITY", df_stats['nodes'].max())
    m4.metric("ITERATIONS", int(df_stats['backtracks'].mean()))
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Speed Trend")
        fig_time = go.Figure()
        fig_time.add_trace(go.Scatter(y=df_stats['time'], mode='lines+markers', 
                                    line=dict(color='#FF71CE', width=4),
                                    marker=dict(size=10, color='#01CDFE')))
        fig_time.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_time, use_container_width=True)
        
    with col2:
        st.write("### Complexity Map")
        fig_nodes = go.Figure()
        fig_nodes.add_trace(go.Bar(x=df_stats['size'], y=df_stats['nodes'], marker_color='#B967FF'))
        fig_nodes.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_nodes, use_container_width=True)
    
    st.write("### Detailed Statistics")
    st.dataframe(df_stats, use_container_width=True)

def show_settings():
    st.markdown("<h2 style='text-align:center; color:#FFB356;'>⚙️ Settings</h2>", unsafe_allow_html=True)
    st.button("🏠 Back to Menu", on_click=lambda: nav_to("Landing"))
    
    st.markdown("<div class='intro-card'>", unsafe_allow_html=True)
    st.toggle("Enable Sound Effects", value=True)
    st.toggle("High Contrast Mode", value=False)
    st.toggle("Auto-save Progress", value=True)
    st.slider("Visualization Speed", 0.0, 1.0, 0.5)
    st.color_picker("Primary Theme Color", "#9956DE")
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

# --- FOOTER ---
st.divider()
st.markdown("""
<p style='text-align:center; color:#999;'>
Gridly Puzzle Arcade • Designed with ❤️ for Logic Enthusiasts<br>
<i>Combining colorful modern UI with advanced logic-based gameplay.</i>
</p>
""", unsafe_allow_html=True)
