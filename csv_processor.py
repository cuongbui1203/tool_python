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

    def is_different(self, other: "LimitData") -> bool:
        """Kiểm tra xem 2 limit có khác nhau không"""
        # Kiểm tra upper limit
        if (self.upper_limit is None) != (other.upper_limit is None):
            return True
        if (
            self.upper_limit is not None
            and other.upper_limit is not None
            and self.upper_limit != other.upper_limit
        ):
            return True

        # Kiểm tra lower limit
        if (self.lower_limit is None) != (other.lower_limit is None):
            return True
        if (
            self.lower_limit is not None
            and other.lower_limit is not None
            and self.lower_limit != other.lower_limit
        ):
            return True

        return False


@dataclass
class ParametricData:
    name: str = ""

    def __init__(self, name: str = ""):
        self.name = name
        self.limit = LimitData()


@dataclass
class RemainParametricData:
    old: ParametricData
    new: ParametricData


@dataclass
class DataTool:
    parametric_index: int = -1
    total_params: int = 0

    def __init__(self):
        self.parametric_index = -1
        self.total_params = 0
        self.data: List[ParametricData] = []


@dataclass
class ComparisonResult:
    def __init__(self):
        self.new_params: List[ParametricData] = []
        self.removed_params: List[ParametricData] = []
        self.changed_params: List[RemainParametricData] = []


class CSVProcessor:
    """Class chính để xử lý CSV"""

    @staticmethod
    def read_csv_file(file_path: str) -> List[List[str]]:
        """Đọc file CSV và trả về records"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                records = list(reader)

                if not records:
                    raise ValueError("File CSV rỗng")

                return records

        except FileNotFoundError:
            raise FileNotFoundError(f"Không tìm thấy file: {file_path}")
        except Exception as e:
            raise Exception(f"Lỗi khi đọc file CSV: {e}")

    @staticmethod
    def convert_data(records: List[List[str]]) -> DataTool:
        """Chuyển đổi records thành DataTool"""
        data_tool = DataTool()
        map_parametric_data: Dict[int, ParametricData] = {}

        for i, record in enumerate(records):
            type_limit = None

            for j, value in enumerate(record):
                # Xử lý break condition
                is_break = False

                if i == 0:  # Dòng header
                    if value.lower().strip() == "parametric":
                        data_tool.parametric_index = j
                    is_break = True

                elif i == 1:  # Dòng name
                    if j >= data_tool.parametric_index:
                        data_tool.total_params += 1

                        if j not in map_parametric_data:
                            map_parametric_data[j] = ParametricData()

                        map_parametric_data[j].name = value

                else:  # Các dòng khác
                    if j == 0:  # Cột đầu tiên - xác định loại limit
                        if "upper limit" in value.lower():
                            type_limit = LimitType.UPPER
                        elif "lower limit" in value.lower():
                            type_limit = LimitType.LOWER
                        continue

                    if type_limit is None:
                        continue

                    if j >= data_tool.parametric_index:
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

                if is_break:
                    break

        # Chuyển từ dict sang list
        data_tool.data = list(map_parametric_data.values())
        return data_tool

    @staticmethod
    def compare_data(old_data: DataTool, new_data: DataTool) -> ComparisonResult:
        """So sánh dữ liệu giữa 2 DataTool"""
        result = ComparisonResult()

        # Tạo map để tra cứu nhanh
        exist_params: Dict[str, bool] = {}
        remain_params: Dict[str, ParametricData] = {}

        # Đánh dấu tất cả params cũ
        for old_param in old_data.data:
            exist_params[old_param.name] = True

        # Kiểm tra params mới
        for new_param in new_data.data:
            if new_param.name not in exist_params:
                result.new_params.append(new_param)
            else:
                remain_params[new_param.name] = new_param
                exist_params[new_param.name] = False

        # Kiểm tra params bị xóa và thay đổi
        for old_param in old_data.data:
            # Params bị xóa
            if exist_params.get(old_param.name, False):
                result.removed_params.append(old_param)

            # Params có thay đổi limit
            if old_param.name in remain_params:
                new_param = remain_params[old_param.name]
                if old_param.limit.is_different(new_param.limit):
                    result.changed_params.append(
                        RemainParametricData(old=old_param, new=new_param)
                    )

        return result

    @staticmethod
    def process_files(file1: str, file2: str) -> ComparisonResult:
        """Xử lý và so sánh 2 files"""
        # Đọc file 1
        records1 = CSVProcessor.read_csv_file(file1)
        old_data = CSVProcessor.convert_data(records1)

        # Đọc file 2
        records2 = CSVProcessor.read_csv_file(file2)
        new_data = CSVProcessor.convert_data(records2)

        # So sánh
        return CSVProcessor.compare_data(old_data, new_data)


def main():
    """Hàm main để test"""
    print("🚀 CSV PROCESSOR")
    print("=" * 60)

    try:
        result = CSVProcessor.process_files("dummy.csv", "dummy2.csv")

        print(f"\n📊 KẾT QUẢ SO SÁNH:")
        print("=" * 50)

        print(f"\n🆕 New Params ({len(result.new_params)}):")
        for param in result.new_params:
            print(
                f"  - {param.name}: Upper={param.limit.upper_limit}, Lower={param.limit.lower_limit}"
            )

        print(f"\n❌ Removed Params ({len(result.removed_params)}):")
        for param in result.removed_params:
            print(
                f"  - {param.name}: Upper={param.limit.upper_limit}, Lower={param.limit.lower_limit}"
            )

        print(f"\n🔄 Changed Params ({len(result.changed_params)}):")
        for change in result.changed_params:
            print(f"  - {change.old.name}:")
            print(
                f"    Old: Upper={change.old.limit.upper_limit}, Lower={change.old.limit.lower_limit}"
            )
            print(
                f"    New: Upper={change.new.limit.upper_limit}, Lower={change.new.limit.lower_limit}"
            )

    except Exception as e:
        print(f"❌ Lỗi: {e}")

    print("\n✨ Hoàn thành!")


if __name__ == "__main__":
    main()
