import csv
from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class Limit:
    """Class để lưu upper và lower limit"""

    upper: Optional[float] = None
    lower: Optional[float] = None


@dataclass
class Parameter:
    """Class để lưu thông tin một parameter"""

    name: str = ""

    def __init__(self, name: str = ""):
        self.name = name
        self.limit = Limit()


class CSVAnalyzer:
    """Class chính để phân tích CSV"""

    def __init__(self):
        self.parametric_start_col = -1
        self.parameters: List[Parameter] = []

    def read_csv(self, file_path: str) -> List[Parameter]:
        """Đọc file CSV và trích xuất parameters"""

        print(f"📖 Đọc file: {file_path}")

        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            rows = list(reader)

        if not rows:
            raise ValueError("File CSV rỗng")

        # Reset
        self.parametric_start_col = -1
        self.parameters = []
        param_map: Dict[int, Parameter] = {}

        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):

                # Dòng 0: Tìm cột "Parametric"
                if row_idx == 0:
                    if value.lower().strip() == "parametric":
                        self.parametric_start_col = col_idx
                        print(f"✅ Tìm thấy cột Parametric tại vị trí {col_idx}")

                # Dòng 1: Tên parameters
                elif row_idx == 1:
                    if col_idx >= self.parametric_start_col and value.strip():
                        if col_idx not in param_map:
                            param_map[col_idx] = Parameter()
                        param_map[col_idx].name = value.strip()

                # Các dòng khác: Upper/Lower limits
                else:
                    # Kiểm tra loại limit từ cột đầu tiên
                    if col_idx == 0:
                        row_type = value.lower().strip()

                        # Xử lý upper limit
                        if "upper limit" in row_type:
                            self._process_limit_row(row, param_map, "upper")

                        # Xử lý lower limit
                        elif "lower limit" in row_type:
                            self._process_limit_row(row, param_map, "lower")

        # Chuyển dict thành list
        self.parameters = [param for param in param_map.values() if param.name]

        return self.parameters

    def _process_limit_row(
        self, row: List[str], param_map: Dict[int, Parameter], limit_type: str
    ):
        """Xử lý dòng chứa limit values"""

        for col_idx, value in enumerate(row):
            if col_idx >= self.parametric_start_col and value.strip():
                if value.strip().upper() not in ["NA", ""]:
                    try:
                        limit_value = float(value.strip())

                        # Tạo parameter nếu chưa có
                        if col_idx not in param_map:
                            param_map[col_idx] = Parameter()

                        # Gán giá trị limit
                        if limit_type == "upper":
                            param_map[col_idx].limit.upper = limit_value
                        elif limit_type == "lower":
                            param_map[col_idx].limit.lower = limit_value

                    except ValueError:
                        print(f"⚠️ Không thể chuyển đổi '{value}' thành số")

    def compare_with(self, other_file: str) -> Dict[str, List[Parameter]]:
        """So sánh với file khác"""

        print(f"\n🔍 So sánh với file: {other_file}")

        # Đọc file thứ 2
        analyzer2 = CSVAnalyzer()
        other_params = analyzer2.read_csv(other_file)

        # Tạo dict để tra cứu nhanh
        current_names = {p.name for p in self.parameters}
        other_names = {p.name for p in other_params}

        # Phân loại
        new_params = [p for p in other_params if p.name not in current_names]
        removed_params = [p for p in self.parameters if p.name not in other_names]
        common_params = [p for p in other_params if p.name in current_names]

        return {"new": new_params, "removed": removed_params, "common": common_params}

    def print_comparison(self, comparison: Dict[str, List[Parameter]]):
        """In kết quả so sánh"""

        print(f"\n📊 KẾT QUẢ SO SÁNH:")
        print("=" * 50)

        print(f"\n🆕 Parameters mới ({len(comparison['new'])}):")
        for param in comparison["new"]:
            print(
                f"  - {param.name}: Upper={param.limit.upper}, Lower={param.limit.lower}"
            )

        print(f"\n❌ Parameters bị xóa ({len(comparison['removed'])}):")
        for param in comparison["removed"]:
            print(
                f"  - {param.name}: Upper={param.limit.upper}, Lower={param.limit.lower}"
            )

        print(f"\n✅ Parameters giữ nguyên ({len(comparison['common'])}):")
        for param in comparison["common"]:
            print(
                f"  - {param.name}: Upper={param.limit.upper}, Lower={param.limit.lower}"
            )


def main():
    """Hàm main - tương đương với Go code"""

    print("🚀 PHÂN TÍCH VÀ SO SÁNH CSV FILES")
    print("=" * 60)

    # Files cần so sánh
    file1 = "dummy.csv"
    file2 = "dummy2.csv"

    try:
        # Tạo analyzer và đọc file đầu tiên
        analyzer = CSVAnalyzer()
        analyzer.read_csv(file1)

        # So sánh với file thứ 2
        comparison = analyzer.compare_with(file2)

        # In kết quả
        analyzer.print_comparison(comparison)

    except FileNotFoundError as e:
        print(f"❌ Không tìm thấy file: {e}")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

    print("\n✨ Hoàn thành!")


if __name__ == "__main__":
    main()
