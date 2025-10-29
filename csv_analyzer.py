import csv
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class LimitType(Enum):
    UPPER = "upper"
    LOWER = "lower"


@dataclass
class LimitData:
    upper_limit: Optional[float] = None
    lower_limit: Optional[float] = None


@dataclass
class ParametricData:
    name: str = ""
    limit: LimitData = None  # type: ignore

    def __post_init__(self):
        if self.limit is None:
            self.limit = LimitData()


@dataclass
class DataTool:
    parametric_index: int = -1
    total_params: int = 0
    data: List[ParametricData] = None  # type: ignore

    def __post_init__(self):
        if self.data is None:
            self.data = []


def extract_csv_data_preserve_format(file_path: str) -> DataTool:
    """Trích xuất dữ liệu CSV giữ nguyên format"""

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            # Đọc CSV với các tùy chọn để giữ nguyên cấu trúc
            reader = csv.reader(file)
            records = list(reader)

            if not records:
                raise ValueError("File CSV rỗng")

            data_tool = DataTool()
            map_parametric_data: Dict[int, ParametricData] = {}

            for i, record in enumerate(records):
                type_limit = None

                for j, value in enumerate(record):
                    if i == 0:  # Dòng header
                        if value.lower().strip() == "parametric":
                            data_tool.parametric_index = j

                    elif i == 1:  # Dòng name
                        if j >= data_tool.parametric_index:
                            data_tool.total_params += 1

                            # Lấy hoặc tạo ParametricData mới
                            if j not in map_parametric_data:
                                map_parametric_data[j] = ParametricData()

                            map_parametric_data[j].name = value

                    else:  # Các dòng khác
                        if j == 0:  # Cột đầu tiên - xác định loại limit
                            if "upper limit" in value.lower():
                                type_limit = LimitType.UPPER
                            elif "lower limit" in value.lower():
                                type_limit = LimitType.LOWER

                        if type_limit is None:
                            continue

                        if j >= data_tool.parametric_index:
                            # Lấy hoặc tạo ParametricData
                            if j not in map_parametric_data:
                                map_parametric_data[j] = ParametricData()

                            param_data = map_parametric_data[j]

                            # Chuyển đổi giá trị
                            limit_value = None
                            if value not in ["NA", ""]:
                                try:
                                    limit_value = float(value)
                                except ValueError:
                                    raise ValueError(
                                        f"Giá trị limit không hợp lệ tại dòng {i+1}, cột {j+1}: {value}"
                                    )

                            # Gán giá trị limit
                            if type_limit == LimitType.UPPER:
                                param_data.limit.upper_limit = limit_value
                            elif type_limit == LimitType.LOWER:
                                param_data.limit.lower_limit = limit_value

                            map_parametric_data[j] = param_data

            # Chuyển từ dict sang list
            data_tool.data = list(map_parametric_data.values())

            print(f"data_tool: {data_tool}")
            return data_tool

    except FileNotFoundError:
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")
    except Exception as e:
        raise Exception(f"Lỗi khi đọc file CSV: {e}")


def compare_data(
    old_data: DataTool, new_data: DataTool
) -> Tuple[List[ParametricData], List[ParametricData], List[ParametricData]]:
    """So sánh dữ liệu giữa 2 DataTool"""

    new_params: List[ParametricData] = []
    remove_params: List[ParametricData] = []
    remain_params: List[ParametricData] = []

    # Tạo set tên params cũ để tra cứu nhanh
    old_param_names = {param.name for param in old_data.data}
    new_param_names = {param.name for param in new_data.data}

    # Tìm params mới (có trong new nhưng không có trong old)
    for new_param in new_data.data:
        if new_param.name not in old_param_names:
            new_params.append(new_param)
        else:
            remain_params.append(new_param)

    # Tìm params bị xóa (có trong old nhưng không có trong new)
    for old_param in old_data.data:
        if old_param.name not in new_param_names:
            remove_params.append(old_param)

    return new_params, remove_params, remain_params


def print_comparison_results(
    new_params: List[ParametricData],
    remove_params: List[ParametricData],
    remain_params: List[ParametricData],
):
    """In kết quả so sánh"""

    print(f"\n📊 KẾT QUẢ SO SÁNH:")
    print("=" * 50)

    print(f"\n🆕 Params mới ({len(new_params)}):")
    for param in new_params:
        print(
            f"  - {param.name}: Upper={param.limit.upper_limit}, Lower={param.limit.lower_limit}"
        )

    print(f"\n❌ Params bị xóa ({len(remove_params)}):")
    for param in remove_params:
        print(
            f"  - {param.name}: Upper={param.limit.upper_limit}, Lower={param.limit.lower_limit}"
        )

    print(f"\n✅ Params giữ nguyên ({len(remain_params)}):")
    for param in remain_params:
        print(
            f"  - {param.name}: Upper={param.limit.upper_limit}, Lower={param.limit.lower_limit}"
        )


def create_sample_csv_files():
    """Tạo 2 file CSV mẫu để test"""

    # File dummy.csv
    dummy1_data = [
        ["header", "A", "B", "C", "Parametric"],
        ["name", "", "", "", "1", "2", "3", "4", "5", "6", "7"],
        ["priority", "", "", "", "", "", "", "", "", "", ""],
        ["upper limit", "", "", "", "NA", "NA", "NA", "NA", "20", "NA", "NA"],
        ["lower limit", "", "", "", "NA", "NA", "NA", "NA", "-20", "NA", "NA"],
        ["test", "", "", "", "", "", "", "", "", "", ""],
    ]

    # File dummy2.csv (có một số khác biệt)
    dummy2_data = [
        ["header", "A", "B", "C", "Parametric"],
        ["name", "", "", "", "1", "2", "3", "8", "9", "10"],  # Thay đổi params
        ["priority", "", "", "", "", "", "", "", "", ""],
        [
            "upper limit",
            "",
            "",
            "",
            "NA",
            "NA",
            "NA",
            "25",
            "30",
            "NA",
        ],  # Thay đổi limits
        ["lower limit", "", "", "", "NA", "NA", "NA", "-25", "-30", "NA"],
        ["test", "", "", "", "", "", "", "", "", ""],
    ]

    # Ghi file dummy.csv
    with open("dummy.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(dummy1_data)

    # Ghi file dummy2.csv
    with open("dummy2.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(dummy2_data)

    print("✅ Đã tạo file dummy.csv và dummy2.csv")


def main():
    """Hàm main"""
    print("🚀 ĐỌC VÀ SO SÁNH DỮ LIỆU CSV")
    print("=" * 60)

    # Tạo file CSV mẫu nếu chưa có
    try:
        with open("dummy.csv", "r") as f:
            pass
    except FileNotFoundError:
        create_sample_csv_files()

    # Files cần đọc
    csv_file1 = "dummy.csv"
    csv_file2 = "dummy2.csv"

    try:
        # Đọc dữ liệu từ file 1
        print(f"\n📖 Đọc file: {csv_file1}")
        old_data = extract_csv_data_preserve_format(csv_file1)

        # Đọc dữ liệu từ file 2
        print(f"\n📖 Đọc file: {csv_file2}")
        new_data = extract_csv_data_preserve_format(csv_file2)

        # So sánh dữ liệu
        print(f"\n🔍 So sánh dữ liệu giữa {csv_file1} và {csv_file2}")
        new_params, remove_params, remain_params = compare_data(old_data, new_data)

        # In kết quả
        print_comparison_results(new_params, remove_params, remain_params)

    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return

    print("\n✨ Hoàn thành!")


if __name__ == "__main__":
    main()
