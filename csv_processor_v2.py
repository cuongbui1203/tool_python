"""
CSV Processor V2 - Dựa trên csv_tool.py với đầy đủ Config options
"""

import csv
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class LimitData:
    """Lưu trữ các giá trị limit dưới dạng dictionary"""
    data: Dict[str, float] = field(default_factory=dict)
    
    @property
    def upper_limit(self) -> Optional[float]:
        """Compatibility với code cũ - lấy giá trị max hoặc upper"""
        return self.data.get('max') or self.data.get('upper')
    
    @property
    def lower_limit(self) -> Optional[float]:
        """Compatibility với code cũ - lấy giá trị min hoặc lower"""
        return self.data.get('min') or self.data.get('lower')
    
    def is_different(self, other: 'LimitData') -> bool:
        """Kiểm tra xem 2 LimitData có khác nhau không"""
        if len(self.data) != len(other.data):
            return True
        
        for key, value in self.data.items():
            if key not in other.data or other.data[key] != value:
                return True
        
        return False


@dataclass
class ParametricData:
    """Dữ liệu của một parametric"""
    limit: LimitData = field(default_factory=LimitData)
    name: str = ""


@dataclass
class RemainParametricData:
    """Dữ liệu của parametric vẫn còn nhưng có thay đổi"""
    old: ParametricData
    new: ParametricData


@dataclass
class DataTool:
    """Container chứa tất cả parametric data"""
    parametric_index: int = -1
    total_params: int = 0
    data: List[ParametricData] = field(default_factory=list)


@dataclass
class Config:
    """Cấu hình cho việc đọc và phân tích CSV"""
    parametric_name_column: str = "parametric"
    get_columns: List[str] = field(default_factory=lambda: ["min", "max"])
    begin_from_parametric: bool = False
    null_values: List[str] = field(default_factory=lambda: ["N/A", "NULL", "-", ""])
    key_column: str = "key"


@dataclass
class ComparisonResult:
    """Kết quả so sánh"""
    new_params: List[ParametricData] = field(default_factory=list)
    removed_params: List[ParametricData] = field(default_factory=list)
    changed_params: List[RemainParametricData] = field(default_factory=list)
    overlap_params: List[RemainParametricData] = field(default_factory=list)
    old_version: str = ""
    new_version: str = ""
    total_old_version: int = 0
    total_new_version: int = 0


def remove_element_at(lst: List, index: int) -> List:
    """
    Xóa phần tử tại vị trí index (swap với phần tử cuối rồi xóa)
    """
    if 0 <= index < len(lst):
        lst[index] = lst[-1]
        return lst[:-1]
    return lst


def read_csv_file(file_path: str) -> List[List[str]]:
    """
    Đọc file CSV và trả về records
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, skipinitialspace=False)
            records = list(reader)
            
            if len(records) == 0:
                raise ValueError("file CSV empty")
            
            return records
    except FileNotFoundError:
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")
    except Exception as e:
        raise Exception(f"Lỗi khi đọc file CSV: {e}")


def convert_data(records: List[List[str]], config: Config) -> DataTool:
    """
    Chuyển đổi CSV records thành DataTool
    """
    data_tool = DataTool()
    map_parametric_data: Dict[int, ParametricData] = {}
    check_column_start = 0
    
    for row_index, record in enumerate(records):
        parameter_type = ""
        is_key_row = -1
        
        for column_index, value in enumerate(record):
            # Tìm cột parametric
            if config.parametric_name_column.lower() in value.lower():
                data_tool.parametric_index = column_index
                if config.begin_from_parametric:
                    check_column_start = column_index
                else:
                    check_column_start = column_index + 1
            
            if data_tool.parametric_index < 0:
                continue
            
            # Cột đầu tiên - xác định loại row
            if column_index == 0:
                parameter_type = ""
                if config.key_column.lower() in value.lower():
                    is_key_row = row_index
                    parameter_type = ""
                else:
                    if row_index != is_key_row and is_key_row != -1:
                        is_key_row = -1
                    
                    # Tìm loại column (min/max/avg/etc)
                    for i, col in enumerate(config.get_columns):
                        if col.lower() in value.lower():
                            parameter_type = col
                            config.get_columns = [col for j, col in enumerate(config.get_columns) if j != i]
                            break
                
                continue
            
            # Xử lý key row (tên của các parametric)
            if is_key_row >= 0:
                if column_index >= check_column_start:
                    e = ParametricData(
                        name=value,
                        limit=LimitData()
                    )
                    map_parametric_data[column_index] = e
                    data_tool.total_params += 1
            
            # Xử lý data rows
            else:
                if parameter_type == "":
                    continue
                
                if column_index >= check_column_start:
                    e = map_parametric_data.get(column_index)
                    if e is None:
                        continue
                    
                    v = None
                    if value not in config.null_values:
                        try:
                            v = float(value)
                        except ValueError:
                            raise ValueError(
                                f"invalid {parameter_type} at row {row_index + 1}, "
                                f"column {column_index + 1}: {value}"
                            )
                    
                    if v is not None:
                        e.limit.data[parameter_type] = v
                    
                    map_parametric_data[column_index] = e
    
    # Chuyển dict sang list
    data_tool.data = list(map_parametric_data.values())
    
    return data_tool


def compare(old_data: DataTool, new_data: DataTool) -> tuple:
    """
    So sánh 2 DataTool một cách tối ưu
    Trả về: (new_params, removed_params, changed_params, overlap_params)
    - new_params: Các parametric keys mới được thêm
    - removed_params: Các parametric keys bị xóa
    - changed_params: Các parametric keys có thay đổi giá trị limit
    - overlap_params: Các parametric keys không thay đổi (giữ nguyên)
    
    Time Complexity: O(n + m) where n = len(old_data), m = len(new_data)
    Space Complexity: O(n)
    """
    new_params: List[ParametricData] = []
    removed_params: List[ParametricData] = []
    changed_params: List[RemainParametricData] = []
    overlap_params: List[RemainParametricData] = []
    
    # Tạo map của old_data để lookup O(1)
    old_map: Dict[str, ParametricData] = {old.name: old for old in old_data.data}
    
    # Duyệt qua new_data một lần - O(m)
    for new_param in new_data.data:
        old_param = old_map.get(new_param.name)
        
        if old_param is None:
            # Key mới - không có trong old_data
            new_params.append(new_param)
        else:
            # Key tồn tại trong cả old và new
            if old_param.limit.is_different(new_param.limit):
                # Có thay đổi giá trị
                changed_params.append(RemainParametricData(old=old_param, new=new_param))
            else:
                # Không thay đổi
                overlap_params.append(RemainParametricData(old=old_param, new=new_param))
            
            # Đánh dấu đã xử lý
            del old_map[new_param.name]
    
    # Những key còn lại trong old_map là các key bị xóa - O(remaining)
    removed_params = list(old_map.values())
    
    return new_params, removed_params, changed_params, overlap_params


class CSVProcessorV2:
    """CSV Processor với đầy đủ Config options"""
    
    @staticmethod
    def process_files(file1: str, file2: str, config: Optional[Config] = None) -> ComparisonResult:
        """
        Xử lý và so sánh 2 files với config
        """
        if config is None:
            config = Config()
        
        # Đọc file 1
        records1 = read_csv_file(file1)
        config1 = Config(
            parametric_name_column=config.parametric_name_column,
            get_columns=config.get_columns,
            begin_from_parametric=config.begin_from_parametric,
            null_values=config.null_values,
            key_column=config.key_column
        )
        old_data = convert_data(records1, config1)
        
        # Đọc file 2
        records2 = read_csv_file(file2)
        config2 = Config(
            parametric_name_column=config.parametric_name_column,
            get_columns=config.get_columns,
            begin_from_parametric=config.begin_from_parametric,
            null_values=config.null_values,
            key_column=config.key_column
        )
        new_data = convert_data(records2, config2)
        
        # So sánh
        new_params, removed_params, changed_params, overlap_params = compare(old_data, new_data)
        print(f"Debug: Overlap params count: {len(overlap_params)}")
        # Tạo kết quả
        result = ComparisonResult(
            new_params=new_params,
            removed_params=removed_params,
            changed_params=changed_params,
            overlap_params=overlap_params,
            old_version=file1.split('/')[-1],
            new_version=file2.split('/')[-1],
            total_old_version=old_data.total_params,
            total_new_version=new_data.total_params
        )
        
        return result
