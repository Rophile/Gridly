import tkinter as tk
from tkinter import ttk, messagebox
import time
from typing import List, Tuple, Optional

class SudokuSolver:
    def __init__(self, size: int):
        self.size = size
        self.block_size = int(size ** 0.5)
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.backtrack_count = 0
        
    def is_valid(self, row: int, col: int, num: int) -> bool:
        """Check if placing num at grid[row][col] is valid"""
        # Check row
        if num in self.grid[row]:
            return False
        
        # Check column
        if num in [self.grid[i][col] for i in range(self.size)]:
            return False
        
        # Check block
        start_row = (row // self.block_size) * self.block_size
        start_col = (col // self.block_size) * self.block_size
        
        for i in range(start_row, start_row + self.block_size):
            for j in range(start_col, start_col + self.block_size):
                if self.grid[i][j] == num:
                    return False
        
        return True
    
    def find_empty(self) -> Optional[Tuple[int, int]]:
        """Find empty cell in grid"""
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    return (i, j)
        return None
    
    def solve(self) -> bool:
        """Solve sudoku using backtracking"""
        empty = self.find_empty()
        if not empty:
            return True
        
        row, col = empty
        self.backtrack_count += 1
        
        for num in range(1, self.size + 1):
            if self.is_valid(row, col, num):
                self.grid[row][col] = num
                
                if self.solve():
                    return True
                
                self.grid[row][col] = 0
        
        return False
    
    def set_grid(self, grid: List[List[int]]):
        """Set the initial grid"""
        self.grid = [row[:] for row in grid]
        self.backtrack_count = 0
    
    def get_grid(self) -> List[List[int]]:
        """Get current grid"""
        return [row[:] for row in self.grid]


class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 Sudoku Solver Advanced - Python Edition")
        self.root.geometry("1200x900")
        self.root.configure(bg='#f0f0f0')
        
        self.current_mode = 16
        self.cells = []
        self.original_values = []
        self.solver = None
        
        # Colors for regions (16x16)
        self.colors_16 = [
            '#ffe6e6', '#e6f3ff', '#fff0e6', '#e6ffe6',
            '#f0e6ff', '#ffffe6', '#ffe6f0', '#e6ffff',
            '#fff0f0', '#f0f0ff', '#f0fff0', '#fffef0',
            '#ffe6fa', '#e6fff5', '#ffeee6', '#f5e6ff'
        ]
        
        # Colors for regions (25x25)
        self.colors_25 = [
            '#ffe6e6', '#e6f3ff', '#fff0e6', '#e6ffe6', '#f0e6ff',
            '#ffffe6', '#ffe6f0', '#e6ffff', '#fff0f0', '#f0f0ff',
            '#f0fff0', '#fffef0', '#ffe6fa', '#e6fff5', '#ffeee6',
            '#f5e6ff', '#ffe6eb', '#e6f0ff', '#fff5e6', '#ebffe6',
            '#f5e6ff', '#fffbe6', '#ffe6ed', '#e6fffb', '#fff8f0'
        ]
        
        self.create_widgets()
        self.create_grid(16)
        
    def create_widgets(self):
        """Create main UI widgets"""
        # Header
        header_frame = tk.Frame(self.root, bg='#667eea', height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="🎯 Sudoku Solver Advanced", 
                        font=('Arial', 24, 'bold'), bg='#667eea', fg='white')
        title.pack(pady=10)
        
        subtitle = tk.Label(header_frame, text="Solver untuk Sudoku 16x16 dan 25x25 dengan analisis hasil", 
                           font=('Arial', 11), bg='#667eea', fg='white')
        subtitle.pack()
        
        # Mode selector
        mode_frame = tk.Frame(self.root, bg='#f0f0f0')
        mode_frame.pack(pady=10)
        
        self.mode_16_btn = tk.Button(mode_frame, text="16x16 Sudoku", 
                                     font=('Arial', 12, 'bold'),
                                     bg='#667eea', fg='white', 
                                     padx=30, pady=10, 
                                     relief=tk.RAISED, bd=3,
                                     command=lambda: self.switch_mode(16))
        self.mode_16_btn.pack(side=tk.LEFT, padx=5)
        
        self.mode_25_btn = tk.Button(mode_frame, text="25x25 Sudoku", 
                                     font=('Arial', 12, 'bold'),
                                     bg='white', fg='#667eea', 
                                     padx=30, pady=10,
                                     relief=tk.RAISED, bd=3,
                                     command=lambda: self.switch_mode(25))
        self.mode_25_btn.pack(side=tk.LEFT, padx=5)
        
        # Grid container
        self.grid_container = tk.Frame(self.root, bg='#f0f0f0')
        self.grid_container.pack(pady=10)
        
        # Control buttons
        control_frame = tk.Frame(self.root, bg='#f0f0f0')
        control_frame.pack(pady=15)
        
        tk.Button(control_frame, text="📝 Muat Contoh", 
                 font=('Arial', 11, 'bold'), bg='#ffc107', 
                 fg='#333', padx=20, pady=10,
                 command=self.load_example).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="✨ Selesaikan", 
                 font=('Arial', 11, 'bold'), bg='#28a745', 
                 fg='white', padx=20, pady=10,
                 command=self.solve_sudoku).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="🗑️ Hapus Semua", 
                 font=('Arial', 11, 'bold'), bg='#dc3545', 
                 fg='white', padx=20, pady=10,
                 command=self.clear_grid).pack(side=tk.LEFT, padx=5)
        
        # Result panel
        self.result_frame = tk.Frame(self.root, bg='#f8f9fa', relief=tk.RAISED, bd=2)
        self.result_frame.pack(fill=tk.X, padx=20, pady=10)
        self.result_frame.pack_forget()
        
    def create_grid(self, size: int):
        """Create sudoku grid"""
        # Clear existing grid
        for widget in self.grid_container.winfo_children():
            widget.destroy()
        
        self.cells = []
        self.current_mode = size
        block_size = int(size ** 0.5)
        
        # Grid frame with border
        grid_frame = tk.Frame(self.grid_container, bg='#333', bd=4, relief=tk.RAISED)
        grid_frame.pack()
        
        # Determine cell size
        cell_size = 35 if size == 16 else 28
        font_size = 10 if size == 16 else 8
        
        colors = self.colors_16 if size == 16 else self.colors_25
        
        for row in range(size):
            row_cells = []
            for col in range(size):
                # Determine region for coloring
                region_row = row // block_size
                region_col = col // block_size
                region_index = region_row * block_size + region_col
                bg_color = colors[region_index]
                
                # Create cell frame
                cell_frame = tk.Frame(grid_frame, bg=bg_color, 
                                     width=cell_size, height=cell_size,
                                     highlightbackground='#ccc', 
                                     highlightthickness=1)
                cell_frame.grid(row=row, column=col, sticky='nsew')
                cell_frame.grid_propagate(False)
                
                # Create entry
                entry = tk.Entry(cell_frame, width=2 if size == 16 else 3, 
                                font=('Arial', font_size, 'bold'),
                                justify='center', bg=bg_color,
                                relief=tk.FLAT, bd=0)
                entry.pack(fill=tk.BOTH, expand=True)
                
                # Bind validation
                entry.bind('<KeyRelease>', lambda e, s=size: self.validate_input(e, s))
                
                row_cells.append({
                    'entry': entry,
                    'frame': cell_frame,
                    'bg_color': bg_color
                })
            
            self.cells.append(row_cells)
        
        self.solver = SudokuSolver(size)
        
    def validate_input(self, event, size):
        """Validate user input"""
        entry = event.widget
        value = entry.get().upper()
        
        if size == 16:
            # Allow 1-9 and A-G
            if value and not (value.isdigit() or value in 'ABCDEFG'):
                entry.delete(0, tk.END)
            elif value and value.isdigit() and value == '0':
                entry.delete(0, tk.END)
        else:
            # Allow 1-25
            if value:
                try:
                    num = int(value)
                    if num < 1 or num > 25:
                        entry.delete(0, tk.END)
                except ValueError:
                    entry.delete(0, tk.END)
    
    def switch_mode(self, mode):
        """Switch between 16x16 and 25x25"""
        if mode == 16:
            self.mode_16_btn.config(bg='#667eea', fg='white')
            self.mode_25_btn.config(bg='white', fg='#667eea')
        else:
            self.mode_16_btn.config(bg='white', fg='#667eea')
            self.mode_25_btn.config(bg='#667eea', fg='white')
        
        self.create_grid(mode)
        self.result_frame.pack_forget()
    
    def convert_to_number(self, value: str) -> int:
        """Convert cell value to number"""
        if not value:
            return 0
        value = value.upper()
        if value.isdigit():
            return int(value)
        # A=10, B=11, ..., G=16
        return ord(value) - ord('A') + 10
    
    def convert_to_char(self, num: int) -> str:
        """Convert number to display character"""
        if num == 0:
            return ''
        if self.current_mode == 16 and num > 9:
            return chr(num - 10 + ord('A'))
        return str(num)
    
    def get_grid_data(self) -> List[List[int]]:
        """Get current grid data"""
        grid = []
        for row in self.cells:
            grid_row = []
            for cell in row:
                value = cell['entry'].get()
                grid_row.append(self.convert_to_number(value))
            grid.append(grid_row)
        return grid
    
    def count_filled_cells(self, grid: List[List[int]]) -> int:
        """Count filled cells in grid"""
        return sum(1 for row in grid for cell in row if cell != 0)
    
    def solve_sudoku(self):
        """Solve the sudoku puzzle"""
        grid = self.get_grid_data()
        filled_count = self.count_filled_cells(grid)
        min_required = 16 if self.current_mode == 16 else 25
        
        if filled_count < min_required:
            messagebox.showerror("Input Tidak Cukup", 
                               f"Minimal {min_required} sel harus diisi untuk Sudoku {self.current_mode}x{self.current_mode}.\n"
                               f"Saat ini terisi: {filled_count} sel.")
            return
        
        # Save original values
        self.original_values = [row[:] for row in grid]
        
        # Show loading message
        loading = tk.Toplevel(self.root)
        loading.title("Processing")
        loading.geometry("300x100")
        loading.transient(self.root)
        loading.grab_set()
        
        tk.Label(loading, text="Memproses...", 
                font=('Arial', 14, 'bold')).pack(pady=20)
        progress = ttk.Progressbar(loading, mode='indeterminate', length=250)
        progress.pack(pady=10)
        progress.start()
        
        self.root.update()
        
        # Solve
        start_time = time.time()
        self.solver.set_grid(grid)
        solved = self.solver.solve()
        solve_time = time.time() - start_time
        
        loading.destroy()
        
        if solved:
            # Update grid with solution
            solution = self.solver.get_grid()
            for i, row in enumerate(self.cells):
                for j, cell in enumerate(row):
                    cell['entry'].delete(0, tk.END)
                    cell['entry'].insert(0, self.convert_to_char(solution[i][j]))
                    
                    # Color code cells
                    if self.original_values[i][j] == 0:
                        # Solved cell
                        cell['frame'].config(bg='#d4edda')
                        cell['entry'].config(bg='#d4edda', fg='#155724')
                    else:
                        # Original cell
                        cell['frame'].config(bg='#e8f4f8')
                        cell['entry'].config(bg='#e8f4f8', fg='#000')
            
            # Show results
            solved_cells = self.count_filled_cells(solution) - filled_count
            self.show_results(True, solve_time, filled_count, solved_cells)
        else:
            messagebox.showerror("Tidak Dapat Diselesaikan", 
                               "Tidak dapat menemukan solusi.\n"
                               "Pastikan input sudoku valid dan dapat diselesaikan.")
    
    def calculate_difficulty(self, filled_cells: int) -> str:
        """Calculate difficulty level"""
        total_cells = self.current_mode * self.current_mode
        fill_percentage = (filled_cells / total_cells) * 100
        
        if fill_percentage >= 50:
            return 'Mudah'
        elif fill_percentage >= 35:
            return 'Sedang'
        elif fill_percentage >= 25:
            return 'Sulit'
        else:
            return 'Sangat Sulit'
    
    def show_results(self, success: bool, solve_time: float, 
                    original_filled: int, solved_cells: int):
        """Show analysis results"""
        # Clear previous results
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        
        self.result_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Title
        title = tk.Label(self.result_frame, text="📊 Hasil Analisis", 
                        font=('Arial', 16, 'bold'), bg='#f8f9fa', fg='#667eea')
        title.pack(pady=(10, 5))
        
        # Success message
        msg_frame = tk.Frame(self.result_frame, bg='#d4edda', 
                            relief=tk.RAISED, bd=2)
        msg_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(msg_frame, text="✅ Sudoku berhasil diselesaikan!", 
                font=('Arial', 12, 'bold'), bg='#d4edda', 
                fg='#155724').pack(pady=10)
        
        # Stats grid
        stats_frame = tk.Frame(self.result_frame, bg='#f8f9fa')
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        total_cells = self.current_mode * self.current_mode
        difficulty = self.calculate_difficulty(original_filled)
        fill_percentage = (original_filled / total_cells) * 100
        
        stats = [
            ("Waktu Penyelesaian", f"{solve_time:.3f}s"),
            ("Sel Awal Terisi", str(original_filled)),
            ("Sel yang Diselesaikan", str(solved_cells)),
            ("Total Sel", str(total_cells)),
            ("Tingkat Kesulitan", difficulty),
            ("Persentase Terisi Awal", f"{fill_percentage:.1f}%"),
            ("Backtrack Count", f"{self.solver.backtrack_count:,}")
        ]
        
        for idx, (label, value) in enumerate(stats):
            row = idx // 3
            col = idx % 3
            
            stat_frame = tk.Frame(stats_frame, bg='white', 
                                 relief=tk.RAISED, bd=2)
            stat_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            tk.Label(stat_frame, text=label, font=('Arial', 9), 
                    bg='white', fg='#666').pack(pady=(5, 0))
            tk.Label(stat_frame, text=value, font=('Arial', 14, 'bold'), 
                    bg='white', fg='#333').pack(pady=(0, 5))
        
        for i in range(3):
            stats_frame.grid_columnconfigure(i, weight=1, uniform='col')
    
    def clear_grid(self):
        """Clear all cells"""
        for row in self.cells:
            for cell in row:
                cell['entry'].delete(0, tk.END)
                cell['frame'].config(bg=cell['bg_color'])
                cell['entry'].config(bg=cell['bg_color'], fg='#000')
        
        self.result_frame.pack_forget()
    
    def load_example(self):
        """Load example puzzle"""
        self.clear_grid()
        
        if self.current_mode == 16:
            # Example 16x16 with 20 clues
            example = [
                [1, 0, 0, 0, 5, 0, 0, 0, 9, 0, 0, 0, 13, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16],
                [0, 0, 0, 0, 0, 0, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0]
            ]
            
            for i, row in enumerate(self.cells):
                for j, cell in enumerate(row):
                    if example[i][j] != 0:
                        cell['entry'].insert(0, self.convert_to_char(example[i][j]))
                        cell['frame'].config(bg='#e8f4f8')
                        cell['entry'].config(bg='#e8f4f8')
        else:
            # Example 25x25 with 30 clues (diagonal pattern + extras)
            for i in range(25):
                self.cells[i][i]['entry'].insert(0, str(i + 1))
                self.cells[i][i]['frame'].config(bg='#e8f4f8')
                self.cells[i][i]['entry'].config(bg='#e8f4f8')
            
            # Add 5 more random clues
            extras = [(0, 5), (5, 0), (10, 15), (15, 10), (20, 24)]
            for row, col in extras:
                self.cells[row][col]['entry'].insert(0, '1')
                self.cells[row][col]['frame'].config(bg='#e8f4f8')
                self.cells[row][col]['entry'].config(bg='#e8f4f8')


def main():
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()