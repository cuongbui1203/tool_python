import tkinter as tk
from tkinter import ttk
from csv_gui import CSVComparatorGUI, MaterialColors


# Enhanced version với thêm features cho bảng
class EnhancedCSVComparatorGUI(CSVComparatorGUI):
    """Enhanced version với thêm tính năng cho bảng"""

    def setup_styles(self):
        """Thiết lập styles nâng cao cho ttk widgets"""
        super().setup_styles()
        style = ttk.Style()

        # Enhanced Treeview styles
        style.configure(
            "Material.Treeview",
            background="white",
            foreground=MaterialColors.TEXT_PRIMARY,
            fieldbackground="white",
            borderwidth=0,
            font=("Segoe UI", 10),
            rowheight=25,  # Tăng độ cao dòng
        )
        style.configure(
            "Material.Treeview.Heading",
            background=MaterialColors.PRIMARY,
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            borderwidth=1,
            relief="flat",
            anchor="center",
        )

        # Alternating row colors
        style.map(
            "Material.Treeview",
            background=[("selected", MaterialColors.PRIMARY_LIGHT)],
            foreground=[("selected", "white")],
        )

    def create_enhanced_table(self, parent, columns, column_widths=None):
        """Tạo bảng với các tính năng nâng cao"""
        frame = tk.Frame(parent, bg=MaterialColors.SURFACE)

        # Create treeview with scrollbars
        tree_frame = tk.Frame(frame, bg=MaterialColors.SURFACE)
        tree_frame.pack(fill="both", expand=True)

        # Treeview
        tree = ttk.Treeview(
            tree_frame,
            columns=list(columns.keys()),
            show="headings",
            style="Material.Treeview",
        )

        # Configure columns
        for col_id, col_name in columns.items():
            tree.heading(col_id, text=col_name)
            width = column_widths.get(col_id, 150) if column_widths else 150
            tree.column(
                col_id, width=width, anchor="center" if col_id != "name" else "w"
            )

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)

        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack widgets
        tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")

        # Add alternating row colors
        tree.tag_configure("oddrow", background="#F5F5F5")
        tree.tag_configure("evenrow", background="white")

        return frame, tree

    def add_export_button(self, parent, table, title):
        """Thêm nút export cho bảng"""
        export_frame = tk.Frame(parent, bg=MaterialColors.SURFACE)
        export_frame.pack(fill="x", padx=10, pady=5)

        from csv_gui import MaterialButton

        export_btn = MaterialButton(
            export_frame,
            text=f"📄 Export {title}",
            command=lambda: self.export_table_to_csv(table, title),
            style="outline",
        )
        export_btn.pack(side="right")

        # Add search functionality
        search_frame = tk.Frame(export_frame, bg=MaterialColors.SURFACE)
        search_frame.pack(side="left", fill="x", expand=True)

        tk.Label(
            search_frame,
            text="🔍 Search:",
            bg=MaterialColors.SURFACE,
            fg=MaterialColors.TEXT_SECONDARY,
            font=("Segoe UI", 9),
        ).pack(side="left", padx=(0, 5))

        search_entry = tk.Entry(
            search_frame,
            font=("Segoe UI", 9),
            bg="white",
            fg=MaterialColors.TEXT_PRIMARY,
            relief="solid",
            borderwidth=1,
            width=30,
        )
        search_entry.pack(side="left")
        search_entry.bind(
            "<KeyRelease>", lambda e: self.filter_table(table, search_entry.get())
        )

        return export_frame

    def filter_table(self, table, search_text):
        """Lọc bảng theo text tìm kiếm"""
        if not search_text:
            # Show all items
            for item in table.get_children():
                table.item(item, open=True)
            return

        search_text = search_text.lower()
        for item in table.get_children():
            values = table.item(item, "values")
            # Check if search text is in any column
            if any(search_text in str(val).lower() for val in values):
                table.item(item, open=True)
            else:
                table.item(item, open=False)

    def export_table_to_csv(self, table, title):
        """Export bảng ra file CSV"""
        from tkinter import filedialog
        import csv

        filename = filedialog.asksaveasfilename(
            title=f"Export {title}",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )

        if not filename:
            return

        try:
            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                # Write headers
                headers = [table.heading(col)["text"] for col in table["columns"]]
                writer.writerow(headers)

                # Write data
                for item in table.get_children():
                    values = table.item(item, "values")
                    writer.writerow(values)

            from tkinter import messagebox

            messagebox.showinfo("Success", f"Đã export thành công: {filename}")

        except Exception as e:
            from tkinter import messagebox

            messagebox.showerror("Error", f"Lỗi khi export: {e}")


def main():
    """Chạy enhanced GUI"""
    app = EnhancedCSVComparatorGUI()
    app.run()


if __name__ == "__main__":
    main()
