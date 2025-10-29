import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import tkinter.font as tkfont
from typing import Optional
import threading
import os
from csv_processor import CSVProcessor, ComparisonResult


class MaterialColors:
    """Material Design color palette"""

    PRIMARY = "#1976D2"
    PRIMARY_DARK = "#1565C0"
    PRIMARY_LIGHT = "#42A5F5"
    SECONDARY = "#FF5722"
    BACKGROUND = "#FAFAFA"
    SURFACE = "#FFFFFF"
    ERROR = "#F44336"
    SUCCESS = "#4CAF50"
    WARNING = "#FF9800"
    TEXT_PRIMARY = "#212121"
    TEXT_SECONDARY = "#757575"
    DIVIDER = "#E0E0E0"


class MaterialButton(tk.Button):
    """Material Design styled button"""

    def __init__(self, parent, text="", command=None, style="primary", **kwargs):
        # Material button colors
        colors = {
            "primary": {
                "bg": MaterialColors.PRIMARY,
                "fg": "white",
                "active_bg": MaterialColors.PRIMARY_DARK,
            },
            "secondary": {
                "bg": MaterialColors.SECONDARY,
                "fg": "white",
                "active_bg": "#E64A19",
            },
            "success": {
                "bg": MaterialColors.SUCCESS,
                "fg": "white",
                "active_bg": "#388E3C",
            },
            "outline": {
                "bg": MaterialColors.SURFACE,
                "fg": MaterialColors.PRIMARY,
                "active_bg": MaterialColors.BACKGROUND,
            },
        }

        color_scheme = colors.get(style, colors["primary"])

        super().__init__(
            parent,
            text=text,
            command=command,  # type: ignore
            bg=color_scheme["bg"],
            fg=color_scheme["fg"],
            activebackground=color_scheme["active_bg"],
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=10,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            **kwargs,
        )

        # Hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.default_bg = color_scheme["bg"]
        self.hover_bg = color_scheme["active_bg"]

    def _on_enter(self, event):
        self.config(bg=self.hover_bg)

    def _on_leave(self, event):
        self.config(bg=self.default_bg)


class MaterialCard(tk.Frame):
    """Material Design card component"""

    def __init__(self, parent, title="", **kwargs):
        super().__init__(
            parent,
            bg=MaterialColors.SURFACE,
            relief="flat",
            borderwidth=1,
            highlightbackground=MaterialColors.DIVIDER,
            highlightthickness=1,
            **kwargs,
        )

        if title:
            title_label = tk.Label(
                self,
                text=title,
                bg=MaterialColors.SURFACE,
                fg=MaterialColors.TEXT_PRIMARY,
                font=("Segoe UI", 12, "bold"),
                anchor="w",
            )
            title_label.pack(fill="x", padx=16, pady=(16, 8))


class CSVComparatorGUI:
    """GUI chính cho CSV Comparator với Material Design"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CSV Parametric Comparator")
        self.root.geometry("1200x800")
        self.root.configure(bg=MaterialColors.BACKGROUND)

        # Variables
        self.file1_path = tk.StringVar()
        self.file2_path = tk.StringVar()
        self.comparison_result: Optional[ComparisonResult] = None

        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        """Thiết lập styles cho ttk widgets"""
        style = ttk.Style()

        # Configure Notebook style
        style.configure(
            "Material.TNotebook", background=MaterialColors.BACKGROUND, borderwidth=0
        )
        style.configure(
            "Material.TNotebook.Tab",
            background=MaterialColors.SURFACE,
            foreground=MaterialColors.TEXT_PRIMARY,
            padding=[20, 10],
            font=("Segoe UI", 10),
        )
        style.map(
            "Material.TNotebook.Tab",
            background=[("selected", MaterialColors.PRIMARY)],
            foreground=[("selected", "white")],
        )

        # Configure Treeview style for tables
        style.configure(
            "Material.Treeview",
            background="white",
            foreground=MaterialColors.TEXT_PRIMARY,
            fieldbackground="white",
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Material.Treeview.Heading",
            background=MaterialColors.PRIMARY,
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            borderwidth=1,
            relief="flat",
        )
        style.map(
            "Material.Treeview",
            background=[("selected", MaterialColors.PRIMARY_LIGHT)],
            foreground=[("selected", "white")],
        )
        style.map(
            "Material.Treeview.Heading",
            background=[("active", MaterialColors.PRIMARY_DARK)],
        )

    def create_widgets(self):
        """Tạo giao diện chính"""
        # Header
        self.create_header()

        # Main content
        main_frame = tk.Frame(self.root, bg=MaterialColors.BACKGROUND)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # File selection section
        self.create_file_selection(main_frame)

        # Results section
        self.create_results_section(main_frame)

    def create_header(self):
        """Tạo header của ứng dụng"""
        header_frame = tk.Frame(self.root, bg=MaterialColors.PRIMARY, height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="CSV Parametric Comparator",
            bg=MaterialColors.PRIMARY,
            fg="white",
            font=("Segoe UI", 20, "bold"),
        )
        title_label.pack(expand=True)

        subtitle_label = tk.Label(
            header_frame,
            text="So sánh dữ liệu parametric giữa 2 file CSV",
            bg=MaterialColors.PRIMARY,
            fg="white",
            font=("Segoe UI", 10),
        )
        subtitle_label.pack()

    def create_file_selection(self, parent):
        """Tạo phần chọn file"""
        file_card = MaterialCard(parent, title="Chọn Files để So Sánh")
        file_card.pack(fill="x", pady=(0, 20))

        # File 1
        file1_frame = tk.Frame(file_card, bg=MaterialColors.SURFACE)
        file1_frame.pack(fill="x", padx=16, pady=8)

        tk.Label(
            file1_frame,
            text="File 1 (Old):",
            bg=MaterialColors.SURFACE,
            fg=MaterialColors.TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")

        file1_input_frame = tk.Frame(file1_frame, bg=MaterialColors.SURFACE)
        file1_input_frame.pack(fill="x", pady=(5, 0))

        self.file1_entry = tk.Entry(
            file1_input_frame,
            textvariable=self.file1_path,
            font=("Segoe UI", 10),
            bg="white",
            fg=MaterialColors.TEXT_PRIMARY,
            relief="solid",
            borderwidth=1,
        )
        self.file1_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        MaterialButton(
            file1_input_frame,
            text="Browse",
            command=lambda: self.browse_file(self.file1_path),
            style="outline",
        ).pack(side="right")

        # File 2
        file2_frame = tk.Frame(file_card, bg=MaterialColors.SURFACE)
        file2_frame.pack(fill="x", padx=16, pady=8)

        tk.Label(
            file2_frame,
            text="File 2 (New):",
            bg=MaterialColors.SURFACE,
            fg=MaterialColors.TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")

        file2_input_frame = tk.Frame(file2_frame, bg=MaterialColors.SURFACE)
        file2_input_frame.pack(fill="x", pady=(5, 0))

        self.file2_entry = tk.Entry(
            file2_input_frame,
            textvariable=self.file2_path,
            font=("Segoe UI", 10),
            bg="white",
            fg=MaterialColors.TEXT_PRIMARY,
            relief="solid",
            borderwidth=1,
        )
        self.file2_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        MaterialButton(
            file2_input_frame,
            text="Browse",
            command=lambda: self.browse_file(self.file2_path),
            style="outline",
        ).pack(side="right")

        # Compare button
        button_frame = tk.Frame(file_card, bg=MaterialColors.SURFACE)
        button_frame.pack(fill="x", padx=16, pady=(8, 16))

        self.compare_button = MaterialButton(
            button_frame,
            text="Compare Files",
            command=self.compare_files,
            style="primary",
        )
        self.compare_button.pack(pady=10)

        # Status label
        self.status_label = tk.Label(
            button_frame,
            text="Chọn 2 file CSV để bắt đầu so sánh",
            bg=MaterialColors.SURFACE,
            fg=MaterialColors.TEXT_SECONDARY,
            font=("Segoe UI", 9),
        )
        self.status_label.pack()

    def create_results_section(self, parent):
        """Tạo phần hiển thị kết quả"""
        results_card = MaterialCard(parent, title="📊 Kết Quả So Sánh")
        results_card.pack(fill="both", expand=True)

        # Notebook for tabs
        self.notebook = ttk.Notebook(results_card, style="Material.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=16, pady=(8, 16))

        # Create tabs
        self.create_summary_tab()
        self.create_new_params_tab()
        self.create_removed_params_tab()
        self.create_changed_params_tab()

    def create_summary_tab(self):
        """Tạo tab tổng quan với thống kê dạng bảng"""
        frame = tk.Frame(self.notebook, bg=MaterialColors.SURFACE)
        self.notebook.add(frame, text="📈 Tổng Quan")

        # Stats summary frame
        stats_frame = tk.Frame(frame, bg=MaterialColors.SURFACE)
        stats_frame.pack(fill="x", padx=10, pady=(10, 5))

        # Files info
        files_label = tk.Label(
            stats_frame,
            text="📁 Files đã so sánh:",
            bg=MaterialColors.SURFACE,
            fg=MaterialColors.TEXT_PRIMARY,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        files_label.pack(fill="x")

        self.files_info_label = tk.Label(
            stats_frame,
            text="",
            bg=MaterialColors.SURFACE,
            fg=MaterialColors.TEXT_SECONDARY,
            font=("Segoe UI", 9),
            anchor="w",
            wraplength=1000,
        )
        self.files_info_label.pack(fill="x", padx=20)

        # Stats table
        stats_table_frame = tk.Frame(frame, bg=MaterialColors.SURFACE)
        stats_table_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(
            stats_table_frame,
            text="📊 Thống kê tổng quan:",
            bg=MaterialColors.SURFACE,
            fg=MaterialColors.TEXT_PRIMARY,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        ).pack(fill="x")

        # Create stats table
        self.stats_table = ttk.Treeview(
            stats_table_frame,
            columns=("category", "count", "percentage"),
            show="headings",
            height=4,
            style="Material.Treeview",
        )

        # Configure columns
        self.stats_table.heading("category", text="Loại thay đổi")
        self.stats_table.heading("count", text="Số lượng")
        self.stats_table.heading("percentage", text="Tỷ lệ (%)")

        self.stats_table.column("category", width=200, anchor="w")
        self.stats_table.column("count", width=100, anchor="center")
        self.stats_table.column("percentage", width=100, anchor="center")

        self.stats_table.pack(fill="x", pady=5)

        # Summary text for additional details
        detail_frame = tk.Frame(frame, bg=MaterialColors.SURFACE)
        detail_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # tk.Label(
        #     detail_frame,
        #     text="🔍 Chi tiết nhanh:",
        #     bg=MaterialColors.SURFACE,
        #     fg=MaterialColors.TEXT_PRIMARY,
        #     font=("Segoe UI", 12, "bold"),
        #     anchor="w"
        # ).pack(fill="x")

        # self.summary_text = scrolledtext.ScrolledText(
        #     detail_frame,
        #     wrap=tk.WORD,
        #     bg="white",
        #     fg=MaterialColors.TEXT_PRIMARY,
        #     font=("Segoe UI", 9),
        #     relief="flat",
        #     borderwidth=1,
        #     height=8
        # )
        # self.summary_text.pack(fill="both", expand=True, pady=5)

    def create_new_params_tab(self):
        """Tạo tab parameters mới với bảng"""
        frame = tk.Frame(self.notebook, bg=MaterialColors.SURFACE)
        self.notebook.add(frame, text="🆕 Params Mới")

        # Header
        header_frame = tk.Frame(frame, bg=MaterialColors.SURFACE)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        self.new_params_count_label = tk.Label(
            header_frame,
            text="🆕 PARAMETERS MỚI",
            bg=MaterialColors.SURFACE,
            fg=MaterialColors.TEXT_PRIMARY,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        self.new_params_count_label.pack(fill="x")

        # Create table
        table_frame = tk.Frame(frame, bg=MaterialColors.SURFACE)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Treeview with scrollbar
        tree_frame = tk.Frame(table_frame, bg=MaterialColors.SURFACE)
        tree_frame.pack(fill="both", expand=True)

        self.new_params_table = ttk.Treeview(
            tree_frame,
            columns=("name", "upper_limit", "lower_limit", "status"),
            show="headings",
            style="Material.Treeview",
        )

        # Configure columns
        self.new_params_table.heading("name", text="Parameter Name")
        self.new_params_table.heading("upper_limit", text="Upper Limit")
        self.new_params_table.heading("lower_limit", text="Lower Limit")
        self.new_params_table.heading("status", text="Status")

        self.new_params_table.column("name", width=250, anchor="w")
        self.new_params_table.column("upper_limit", width=120, anchor="center")
        self.new_params_table.column("lower_limit", width=120, anchor="center")
        self.new_params_table.column("status", width=100, anchor="center")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.new_params_table.yview
        )
        h_scrollbar = ttk.Scrollbar(
            tree_frame, orient="horizontal", command=self.new_params_table.xview
        )

        self.new_params_table.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        # Pack table and scrollbars
        self.new_params_table.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")

    def create_removed_params_tab(self):
        """Tạo tab parameters bị xóa với bảng"""
        frame = tk.Frame(self.notebook, bg=MaterialColors.SURFACE)
        self.notebook.add(frame, text="❌ Params Bị Xóa")

        # Header
        header_frame = tk.Frame(frame, bg=MaterialColors.SURFACE)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        self.removed_params_count_label = tk.Label(
            header_frame,
            text="❌ PARAMETERS BỊ XÓA",
            bg=MaterialColors.SURFACE,
            fg=MaterialColors.TEXT_PRIMARY,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        self.removed_params_count_label.pack(fill="x")

        # Create table
        table_frame = tk.Frame(frame, bg=MaterialColors.SURFACE)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        tree_frame = tk.Frame(table_frame, bg=MaterialColors.SURFACE)
        tree_frame.pack(fill="both", expand=True)

        self.removed_params_table = ttk.Treeview(
            tree_frame,
            columns=("name", "upper_limit", "lower_limit", "status"),
            show="headings",
            style="Material.Treeview",
        )

        # Configure columns
        self.removed_params_table.heading("name", text="Parameter Name")
        self.removed_params_table.heading("upper_limit", text="Upper Limit")
        self.removed_params_table.heading("lower_limit", text="Lower Limit")
        self.removed_params_table.heading("status", text="Status")

        self.removed_params_table.column("name", width=250, anchor="w")
        self.removed_params_table.column("upper_limit", width=120, anchor="center")
        self.removed_params_table.column("lower_limit", width=120, anchor="center")
        self.removed_params_table.column("status", width=100, anchor="center")

        # Scrollbars
        v_scrollbar2 = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.removed_params_table.yview
        )
        self.removed_params_table.configure(yscrollcommand=v_scrollbar2.set)

        self.removed_params_table.pack(side="left", fill="both", expand=True)
        v_scrollbar2.pack(side="right", fill="y")

    def create_changed_params_tab(self):
        """Tạo tab parameters thay đổi với bảng so sánh"""
        frame = tk.Frame(self.notebook, bg=MaterialColors.SURFACE)
        self.notebook.add(frame, text="🔄 Params Thay Đổi")

        # Header
        header_frame = tk.Frame(frame, bg=MaterialColors.SURFACE)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        self.changed_params_count_label = tk.Label(
            header_frame,
            text="🔄 PARAMETERS THAY ĐỔI",
            bg=MaterialColors.SURFACE,
            fg=MaterialColors.TEXT_PRIMARY,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        self.changed_params_count_label.pack(fill="x")

        # Create table
        table_frame = tk.Frame(frame, bg=MaterialColors.SURFACE)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        tree_frame = tk.Frame(table_frame, bg=MaterialColors.SURFACE)
        tree_frame.pack(fill="both", expand=True)

        self.changed_params_table = ttk.Treeview(
            tree_frame,
            columns=(
                "name",
                "old_upper",
                "old_lower",
                "new_upper",
                "new_lower",
                "change_type",
            ),
            show="headings",
            style="Material.Treeview",
        )

        # Configure columns
        self.changed_params_table.heading("name", text="Parameter Name")
        self.changed_params_table.heading("old_upper", text="Old Upper")
        self.changed_params_table.heading("old_lower", text="Old Lower")
        self.changed_params_table.heading("new_upper", text="New Upper")
        self.changed_params_table.heading("new_lower", text="New Lower")
        self.changed_params_table.heading("change_type", text="Change Type")

        self.changed_params_table.column("name", width=200, anchor="w")
        self.changed_params_table.column("old_upper", width=100, anchor="center")
        self.changed_params_table.column("old_lower", width=100, anchor="center")
        self.changed_params_table.column("new_upper", width=100, anchor="center")
        self.changed_params_table.column("new_lower", width=100, anchor="center")
        self.changed_params_table.column("change_type", width=120, anchor="center")

        # Scrollbars
        v_scrollbar3 = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.changed_params_table.yview
        )
        h_scrollbar3 = ttk.Scrollbar(
            tree_frame, orient="horizontal", command=self.changed_params_table.xview
        )

        self.changed_params_table.configure(
            yscrollcommand=v_scrollbar3.set, xscrollcommand=h_scrollbar3.set
        )

        self.changed_params_table.pack(side="left", fill="both", expand=True)
        v_scrollbar3.pack(side="right", fill="y")

    def browse_file(self, var: tk.StringVar):
        """Mở dialog chọn file"""
        filename = filedialog.askopenfilename(
            title="Chọn CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if filename:
            var.set(filename)

    def compare_files(self):
        """So sánh 2 files"""
        file1 = self.file1_path.get().strip()
        file2 = self.file2_path.get().strip()

        if not file1 or not file2:
            messagebox.showerror("Lỗi", "Vui lòng chọn 2 file CSV")
            return

        if not os.path.exists(file1):
            messagebox.showerror("Lỗi", f"File không tồn tại: {file1}")
            return

        if not os.path.exists(file2):
            messagebox.showerror("Lỗi", f"File không tồn tại: {file2}")
            return

        # Disable button và hiển thị loading
        self.compare_button.config(state="disabled", text="⏳ Đang so sánh...")
        self.status_label.config(
            text="Đang xử lý dữ liệu...", fg=MaterialColors.WARNING
        )

        # Chạy so sánh trong thread riêng
        thread = threading.Thread(target=self.perform_comparison, args=(file1, file2))
        thread.daemon = True
        thread.start()

    def perform_comparison(self, file1: str, file2: str):
        """Thực hiện so sánh trong background thread"""
        try:
            # So sánh files
            result = CSVProcessor.process_files(file1, file2)

            # Cập nhật UI trong main thread
            self.root.after(0, self.update_results, result, None)

        except Exception as e:
            # Cập nhật UI với lỗi
            self.root.after(0, self.update_results, None, str(e))

    def update_results(self, result: Optional[ComparisonResult], error: Optional[str]):
        """Cập nhật kết quả lên UI"""
        # Enable button
        self.compare_button.config(state="normal", text="🔍 Compare Files")

        if error:
            self.status_label.config(text=f"Lỗi: {error}", fg=MaterialColors.ERROR)
            messagebox.showerror("Lỗi", error)
            return

        if not result:
            return

        self.comparison_result = result
        self.status_label.config(text="So sánh hoàn thành!", fg=MaterialColors.SUCCESS)

        # Clear previous results
        self.clear_results()

        # Update summary
        self.update_summary_tab(result)

        # Update other tabs
        self.update_new_params_tab(result.new_params)
        self.update_removed_params_tab(result.removed_params)
        self.update_changed_params_tab(result.changed_params)

        # Switch to summary tab
        self.notebook.select(0)

    def clear_results(self):
        """Xóa kết quả cũ"""
        # self.summary_text.delete(1.0, tk.END)

        # Clear tables
        for item in self.new_params_table.get_children():
            self.new_params_table.delete(item)
        for item in self.removed_params_table.get_children():
            self.removed_params_table.delete(item)
        for item in self.changed_params_table.get_children():
            self.changed_params_table.delete(item)
        for item in self.stats_table.get_children():
            self.stats_table.delete(item)

    def update_summary_tab(self, result: ComparisonResult):
        """Cập nhật tab tổng quan với bảng thống kê"""
        # Update files info
        files_info = f"• File 1 (Old): {self.file1_path.get()}\n• File 2 (New): {self.file2_path.get()}"
        self.files_info_label.config(text=files_info)

        # Calculate totals
        total_changes = (
            len(result.new_params)
            + len(result.removed_params)
            + len(result.changed_params)
        )

        # Update stats table
        stats_data = [
            (
                "🆕 Parameters mới",
                len(result.new_params),
                (
                    f"{len(result.new_params)/max(total_changes,1)*100:.1f}%"
                    if total_changes > 0
                    else "0%"
                ),
            ),
            (
                "❌ Parameters bị xóa",
                len(result.removed_params),
                (
                    f"{len(result.removed_params)/max(total_changes,1)*100:.1f}%"
                    if total_changes > 0
                    else "0%"
                ),
            ),
            (
                "🔄 Parameters thay đổi",
                len(result.changed_params),
                (
                    f"{len(result.changed_params)/max(total_changes,1)*100:.1f}%"
                    if total_changes > 0
                    else "0%"
                ),
            ),
            ("� Tổng thay đổi", total_changes, "100%" if total_changes > 0 else "0%"),
        ]

        for category, count, percentage in stats_data:
            self.stats_table.insert("", "end", values=(category, count, percentage))

        # Update summary text with quick details
        summary = "🔍 CHI TIẾT NHANH:\n\n"

        if result.new_params:
            summary += f"🆕 TOP PARAMETERS MỚI:\n"
            for i, param in enumerate(result.new_params[:5], 1):  # Show first 5
                summary += f"   {i}. {param.name}\n"
            if len(result.new_params) > 5:
                summary += f"   ... và {len(result.new_params) - 5} parameters khác\n"

        if result.removed_params:
            summary += f"\n❌ TOP PARAMETERS BỊ XÓA:\n"
            for i, param in enumerate(result.removed_params[:5], 1):  # Show first 5
                summary += f"   {i}. {param.name}\n"
            if len(result.removed_params) > 5:
                summary += (
                    f"   ... và {len(result.removed_params) - 5} parameters khác\n"
                )

        if result.changed_params:
            summary += f"\n🔄 TOP PARAMETERS THAY ĐỔI:\n"
            for i, change in enumerate(result.changed_params[:5], 1):  # Show first 5
                summary += f"   {i}. {change.old.name}\n"
            if len(result.changed_params) > 5:
                summary += (
                    f"   ... và {len(result.changed_params) - 5} parameters khác\n"
                )

        if total_changes == 0:
            summary += "✅ Không có thay đổi nào giữa 2 files!"

        # self.summary_text.insert(1.0, summary)

    def update_new_params_tab(self, new_params):
        """Cập nhật tab parameters mới với bảng"""
        # Update header
        count_text = f"🆕 PARAMETERS MỚI ({len(new_params)} items)"
        self.new_params_count_label.config(text=count_text)

        if not new_params:
            # Insert empty message
            self.new_params_table.insert(
                "",
                "end",
                values=("Không có parameters mới nào", "-", "-", "No changes"),
            )
            return

        # Populate table
        for i, param in enumerate(new_params, 1):
            upper_val = (
                param.limit.upper_limit
                if param.limit.upper_limit is not None
                else "N/A"
            )
            lower_val = (
                param.limit.lower_limit
                if param.limit.lower_limit is not None
                else "N/A"
            )

            self.new_params_table.insert(
                "",
                "end",
                values=(param.name, upper_val, lower_val, "NEW"),
                tags=("new",),
            )

        # Configure tag colors
        self.new_params_table.tag_configure(
            "new", background="#E8F5E8", foreground="#2E7D32"
        )

    def update_removed_params_tab(self, removed_params):
        """Cập nhật tab parameters bị xóa với bảng"""
        # Update header
        count_text = f"❌ PARAMETERS BỊ XÓA ({len(removed_params)} items)"
        self.removed_params_count_label.config(text=count_text)

        if not removed_params:
            self.removed_params_table.insert(
                "",
                "end",
                values=("Không có parameters nào bị xóa", "-", "-", "No changes"),
            )
            return

        # Populate table
        for i, param in enumerate(removed_params, 1):
            upper_val = (
                param.limit.upper_limit
                if param.limit.upper_limit is not None
                else "N/A"
            )
            lower_val = (
                param.limit.lower_limit
                if param.limit.lower_limit is not None
                else "N/A"
            )

            self.removed_params_table.insert(
                "",
                "end",
                values=(param.name, upper_val, lower_val, "REMOVED"),
                tags=("removed",),
            )

        # Configure tag colors
        self.removed_params_table.tag_configure(
            "removed", background="#FFEBEE", foreground="#C62828"
        )

    def update_changed_params_tab(self, changed_params):
        """Cập nhật tab parameters thay đổi với bảng so sánh"""
        # Update header
        count_text = f"🔄 PARAMETERS THAY ĐỔI ({len(changed_params)} items)"
        self.changed_params_count_label.config(text=count_text)

        if not changed_params:
            self.changed_params_table.insert(
                "",
                "end",
                values=(
                    "Không có parameters nào thay đổi",
                    "-",
                    "-",
                    "-",
                    "-",
                    "No changes",
                ),
            )
            return

        # Populate table
        for i, change in enumerate(changed_params, 1):
            old_upper = (
                change.old.limit.upper_limit
                if change.old.limit.upper_limit is not None
                else "N/A"
            )
            old_lower = (
                change.old.limit.lower_limit
                if change.old.limit.lower_limit is not None
                else "N/A"
            )
            new_upper = (
                change.new.limit.upper_limit
                if change.new.limit.upper_limit is not None
                else "N/A"
            )
            new_lower = (
                change.new.limit.lower_limit
                if change.new.limit.lower_limit is not None
                else "N/A"
            )

            # Determine change type
            change_type = []
            if old_upper != new_upper:
                change_type.append("Upper")
            if old_lower != new_lower:
                change_type.append("Lower")
            change_type_str = " + ".join(change_type) if change_type else "Other"

            self.changed_params_table.insert(
                "",
                "end",
                values=(
                    change.old.name,
                    old_upper,
                    old_lower,
                    new_upper,
                    new_lower,
                    change_type_str,
                ),
                tags=("changed",),
            )

        # Configure tag colors
        self.changed_params_table.tag_configure(
            "changed", background="#FFF3E0", foreground="#E65100"
        )

    def run(self):
        """Chạy ứng dụng"""
        # Set default files nếu có
        if os.path.exists("dummy.csv"):
            self.file1_path.set("dummy.csv")
        if os.path.exists("dummy2.csv"):
            self.file2_path.set("dummy2.csv")

        self.root.mainloop()


def main():
    """Chạy GUI"""
    app = CSVComparatorGUI()
    app.run()


if __name__ == "__main__":
    main()
