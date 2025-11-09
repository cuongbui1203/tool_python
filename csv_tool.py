#!/usr/bin/env python3
"""
CSV Tool - Python implementation tương đương với main.go
Chức năng: Đọc và so sánh dữ liệu CSV với các tham số có thể cấu hình
"""

import csv
import argparse
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class LimitData:
    """Lưu trữ các giá trị limit dưới dạng dictionary"""
    data: Dict[str, float] = field(default_factory=dict)
    
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
    get_columns: List[str] = field(default_factory=lambda: ["min", "max", "avg"])
    begin_from_parametric: bool = False
    null_values: List[str] = field(default_factory=lambda: ["N/A", "NULL", "-"])
    key_column: str = "key"


def read_csv_file(file_path: str) -> List[List[str]]:
    """
    Đọc file CSV và trả về records
    Tương đương với readCSVFile() trong Go
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Cấu hình CSV reader giống Go:
            # - FieldsPerRecord = -1: cho phép số field khác nhau mỗi dòng
            # - TrimLeadingSpace = False: không trim space
            reader = csv.reader(file, skipinitialspace=False)
            records = list(reader)
            
            if len(records) == 0:
                raise ValueError("file CSV empty")
            
            return records
    except FileNotFoundError:
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")
    except Exception as e:
        raise Exception(f"Lỗi khi đọc file CSV: {e}")


def remove_element_at(lst: List, index: int) -> List:
    """
    Xóa phần tử tại vị trí index (swap với phần tử cuối rồi xóa)
    Tương đương với removeElementAt() trong Go
    """
    if 0 <= index < len(lst):
        lst[index] = lst[-1]
        return lst[:-1]
    return lst


def convert_data(records: List[List[str]], config: Config) -> DataTool:
    """
    Chuyển đổi CSV records thành DataTool
    Tương đương với convertData() trong Go
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
                            config.get_columns = remove_element_at(config.get_columns, i)
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
    So sánh 2 DataTool
    Tương đương với compare() trong Go
    Trả về: (new_params, remove_params, remain_res)
    """
    new_params: List[ParametricData] = []
    remove_params: List[ParametricData] = []
    remain_params: Dict[str, ParametricData] = {}
    remain_res: List[RemainParametricData] = []
    exist_params: Dict[str, bool] = {}
    
    # Đánh dấu tất cả params cũ
    for old in old_data.data:
        exist_params[old.name] = True
    
    # Tìm new params và remain params
    for new_param in new_data.data:
        if new_param.name not in exist_params:
            new_params.append(new_param)
        else:
            remain_params[new_param.name] = new_param
            exist_params[new_param.name] = False
    
    # Tìm removed params và changed params
    for old in old_data.data:
        if exist_params.get(old.name, False):
            remove_params.append(old)
        
        if old.name in remain_params:
            e = remain_params[old.name]
            if old.limit.is_different(e.limit):
                remain_res.append(RemainParametricData(old=old, new=e))
    
    return new_params, remove_params, remain_res


def print_results(new_params: List[ParametricData], 
                 remove_params: List[ParametricData], 
                 remain_res: List[RemainParametricData]):
    """In kết quả so sánh"""
    print(f"\nNew Params: {[{'name': p.name, 'limit': p.limit.data} for p in new_params]}")
    print(f"Remove Params: {[{'name': p.name, 'limit': p.limit.data} for p in remove_params]}")
    print(f"Remain Res: {[{'old': {'name': r.old.name, 'limit': r.old.limit.data}, 'new': {'name': r.new.name, 'limit': r.new.limit.data}} for r in remain_res]}")


def main():
    """Hàm main - tương đương với main() trong Go"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='CSV Tool - So sánh dữ liệu CSV')
    parser.add_argument('--parametric', type=str, default='parametric',
                       help='Tên cột parametric (default: parametric)')
    parser.add_argument('--get-columns', type=str, default='min,max,avg',
                       help='Các cột cần lấy, phân cách bởi dấu phẩy (default: min,max,avg)')
    parser.add_argument('--begin-from-parametric', action='store_true',
                       help='Bắt đầu từ cột parametric (default: False)')
    parser.add_argument('--null-values', type=str, default='N/A,NULL,-',
                       help='Các giá trị null, phân cách bởi dấu phẩy (default: N/A,NULL,-)')
    parser.add_argument('--key', type=str, default='key',
                       help='Tên cột key (default: key)')
    parser.add_argument('--file1', type=str, default='dummy.csv',
                       help='File CSV đầu tiên (default: dummy.csv)')
    parser.add_argument('--file2', type=str, default='dummy2.csv',
                       help='File CSV thứ hai (default: dummy2.csv)')
    
    args = parser.parse_args()
    
    # Tạo config
    config = Config(
        parametric_name_column=args.parametric,
        get_columns=args.get_columns.split(','),
        begin_from_parametric=args.begin_from_parametric,
        null_values=args.null_values.split(','),
        key_column=args.key
    )
    
    print(f"Config: {config}")
    print("Read CSV")
    print("=" * 60)
    
    try:
        # Đọc file 1
        print(f"\nĐọc file: {args.file1}")
        records = read_csv_file(args.file1)
        old = convert_data(records, config)
        print(f"Old Data: parametric_index={old.parametric_index}, total_params={old.total_params}")
        print(f"  Data: {[{'name': p.name, 'limit': p.limit.data} for p in old.data]}")
        
        # Đọc file 2
        print(f"\nĐọc file: {args.file2}")
        records = read_csv_file(args.file2)
        
        # Tạo config mới cho file 2 (vì get_columns đã bị thay đổi)
        config2 = Config(
            parametric_name_column=args.parametric,
            get_columns=args.get_columns.split(','),
            begin_from_parametric=args.begin_from_parametric,
            null_values=args.null_values.split(','),
            key_column=args.key
        )
        
        new = convert_data(records, config2)
        print(f"New Data: parametric_index={new.parametric_index}, total_params={new.total_params}")
        print(f"  Data: {[{'name': p.name, 'limit': p.limit.data} for p in new.data]}")
        
        # So sánh
        print("\nSo sánh dữ liệu...")
        new_params, remove_params, remain_res = compare(old, new)
        print_results(new_params, remove_params, remain_res)
        
    except Exception as e:
        print(f"Err: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\nDone")


if __name__ == "__main__":
    main()
