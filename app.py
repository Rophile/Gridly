import streamlit as st
import time
import pandas as pd
import numpy as np
import random
from typing import List, Tuple, Optional, Set, Dict
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(page_title="Gridly - Puzzle Arcade", layout="wide", page_icon="🧩")

# --- CUSTOM ARCADE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800;900&family=Outfit:wght@400;700;900&display=swap');
    
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

    * { font-family: 'Outfit', sans-serif; }
    
    .stApp { background-color: #fdfaff; }

    /* Arcade Buttons */
    .arcade-btn {
        display: block;
        width: 100%;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        background: white;
        color: var(--slate-blue);
        border: 3px solid var(--slate-blue);
        border-radius: 15px;
        font-size: 1.5rem;
        font-weight: 900;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        text-decoration: none;
        box-shadow: 0 6px 0 var(--slate-blue);
    }
    .arcade-btn:hover {
        transform: translateY(-4px);
        background: var(--slate-blue);
        color: white;
        box-shadow: 0 10px 0 #4f46e5;
    }
    .arcade-btn:active {
        transform: translateY(2px);
        box-shadow: 0 2px 0 #4f46e5;
    }

    /* Grid Styling */
    .sudoku-cell {
        aspect-ratio: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.2rem;
        border: 1px solid #eee;
        transition: all 0.2s;
    }
    
    /* Glowing Effect for current cell */
    .glow-cell {
        box-shadow: inset 0 0 15px var(--summer-sky);
        background-color: #e0f2fe !important;
        border: 2px solid var(--summer-sky) !important;
    }
    
    .backtrack-cell {
        background-color: #fee2e2 !important;
        border: 2px solid var(--mona-lisa) !important;
    }

    .header-text { 
        color: var(--amethyst); 
        text-align: center; 
        font-weight: 900; 
        font-size: 4rem;
        margin-bottom: 0; 
        letter-spacing: -2px;
        text-shadow: 3px 3px 0px rgba(0,0,0,0.05);
    }
    
    .intro-card {
        background: white;
        padding: 30px;
        border-radius: 25px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05);
        border: 2px solid #f0f0f0;
    }
    
    /* Progress Bars */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, var(--amethyst), var(--summer-sky));
    }
    </style>
""", unsafe_allow_html=True)

# --- SUDOKU LOGIC ENGINE ---
class SudokuEngine:
    def __init__(self, size: int = 16):
        self.n = size
        self.k = int(size**0.5)
        self.symbols = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.nodes_explored = 0
        self.backtracks = 0
        self.start_time = 0
        self.history = [] # For step-by-step visualization

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
        df = pd.DataFrame(grid)
        def style_cells(val):
            return 'background-color: #f8fafc'
        
        with placeholder.container():
            st.write(f"🔍 Exploring: **({r},{c})** | Nodes: **{self.nodes_explored}**")
            # In a real arcade app, we'd use a more complex component, but for Streamlit:
            st.dataframe(df.style.applymap(lambda x: 'background-color: #fee2e2' if is_backtrack else 'background-color: #e0f2fe'))
            time.sleep(0.01)

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
    st.markdown("<h1 class='header-text'>Gridly</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:1.5rem; color:#7274ED; margin-bottom:3rem;'>Modern Logic Arcade</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='intro-card'>", unsafe_allow_html=True)
        if st.button("🎮 PLAY GAME", key="btn_play", use_container_width=True): nav_to("Play")
        if st.button("🤖 SOLVE PUZZLE", key="btn_solve", use_container_width=True): nav_to("Solve")
        if st.button("📊 ANALYSIS", key="btn_analysis", use_container_width=True): nav_to("Analysis")
        if st.button("⚙️ SETTINGS", key="btn_settings", use_container_width=True): nav_to("Settings")
        if st.button("🚪 EXIT", key="btn_exit", use_container_width=True): st.info("Thank you for playing Gridly!")
        st.markdown("</div>", unsafe_allow_html=True)

def show_play():
    st.markdown("<h2 style='text-align:center; color:#9956DE;'>🎮 Play Mode</h2>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.button("🏠 Back to Menu", on_click=lambda: nav_to("Landing"))
        st.divider()
        size = st.selectbox("Grid Size", [9, 16, 25], index=1)
        diff = st.select_slider("Difficulty", ["Easy", "Medium", "Hard", "Extreme"], value="Medium")
        if st.button("🔄 Generate New Puzzle", use_container_width=True):
            engine = SudokuEngine(size)
            st.session_state.current_grid = engine.generate_puzzle(diff)
            st.session_state.grid_size = size
            st.session_state.difficulty = diff

    if st.session_state.current_grid is None:
        st.info("Choose settings and click 'Generate' to start!")
    else:
        # Display Grid
        df = pd.DataFrame(st.session_state.current_grid)
        st.write(f"Mode: **{st.session_state.grid_size}x{st.session_state.grid_size}** | Difficulty: **{st.session_state.difficulty}**")
        
        edited_df = st.data_editor(df, use_container_width=True, hide_index=True, key="play_editor")
        
        col1, col2 = st.columns(2)
        if col1.button("✨ Check Solution", use_container_width=True):
            engine = SudokuEngine(st.session_state.grid_size)
            grid_copy = edited_df.values.astype(int).tolist()
            if engine.solve(grid_copy):
                st.balloons()
                st.success("Perfect! You solved it!")
            else:
                st.error("Something's not right. Keep trying!")
        
        if col2.button("💡 Hint", use_container_width=True):
            st.warning("Hint system coming soon in the next update!")

def show_solve():
    st.markdown("<h2 style='text-align:center; color:#1FA7E1;'>🤖 Solver Mode</h2>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.button("🏠 Back to Menu", on_click=lambda: nav_to("Landing"))
        st.divider()
        size = st.selectbox("Grid Size", [9, 16, 25], index=1)
        mode = st.radio("Solving Style", ["Instant", "Step-by-Step", "Analyze"])

    st.write("Input your puzzle below:")
    empty_grid = np.zeros((size, size), dtype=int)
    input_df = st.data_editor(pd.DataFrame(empty_grid), use_container_width=True, hide_index=True)
    
    viz_placeholder = st.empty()
    
    if st.button("🚀 START SOLVING", use_container_width=True):
        grid = input_df.values.astype(int).tolist()
        engine = SudokuEngine(size)
        
        start = time.perf_counter()
        success = engine.solve(grid, visualize=(mode != "Instant"), placeholder=viz_placeholder)
        end = time.perf_counter()
        
        if success:
            st.success(f"Solved in {end-start:.4f}s")
            st.table(pd.DataFrame(grid).applymap(lambda v: engine.symbols[v] if v > 0 else ""))
            
            # Save for analysis
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
    st.markdown("<h2 style='text-align:center; color:#75D06A;'>📊 Performance Analysis</h2>", unsafe_allow_html=True)
    st.button("🏠 Back to Menu", on_click=lambda: nav_to("Landing"))
    
    if not st.session_state.stats:
        st.warning("No data yet. Solve some puzzles to see analysis!")
        return
    
    df_stats = pd.DataFrame(st.session_state.stats)
    
    # Summary Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Avg Time", f"{df_stats['time'].mean():.3f}s")
    m2.metric("Total Solved", len(df_stats))
    m3.metric("Max Nodes", df_stats['nodes'].max())
    m4.metric("Avg Backtracks", int(df_stats['backtracks'].mean()))
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Solving Time Trend")
        fig_time = go.Figure()
        fig_time.add_trace(go.Scatter(y=df_stats['time'], mode='lines+markers', line=dict(color='#7274ED')))
        st.plotly_chart(fig_time, use_container_width=True)
        
    with col2:
        st.write("### Nodes Explored vs Size")
        fig_nodes = go.Figure()
        fig_nodes.add_trace(go.Bar(x=df_stats['size'], y=df_stats['nodes'], marker_color='#9956DE'))
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
