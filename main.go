package main

import (
	"encoding/csv"
	"flag"
	"fmt"
	"os"
	"slices"
	"strconv"
	"strings"
)

type DataTool struct {
	ParametricIndex int
	TotalParams     int
	Data            []ParametricData
}

type LimitData struct {
	data map[string]float64
}

func (l LimitData) IsDifferent(other LimitData) bool {
	if len(l.data) != len(other.data) {
		return true
	}

	for k, v := range l.data {
		if ov, ok := other.data[k]; !ok || ov != v {
			return true
		}
	}

	return false
}

type RemainParametricData struct {
	Old ParametricData
	New ParametricData
}

type ParametricData struct {
	Limit LimitData
	Name  string
}

type Config struct {
	parametricNameColumn string
	getColumns           []string
	beginFromParametric  bool
	nullValues           []string
	keyColumn            string
}

func readCSVFile(filePath string) ([][]string, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	// Tạo CSV reader
	reader := csv.NewReader(file)
	reader.FieldsPerRecord = -1     // Cho phép số field khác nhau mỗi dòng
	reader.TrimLeadingSpace = false // Không trim space để giữ nguyên cấu trúc

	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	if len(records) == 0 {
		return nil, fmt.Errorf("file CSV empty")
	}

	return records, nil
}

func removeElementAt[T any](s []T, i int) []T {
	s[i] = s[len(s)-1]
	return s[:len(s)-1]
}

func convertData(records [][]string, config Config) (*DataTool, error) {
	dataTool := &DataTool{
		ParametricIndex: -1,
		TotalParams:     0,
		Data:            make([]ParametricData, 0),
	}

	mapParametricData := make(map[int]*ParametricData)
	checkColumnStart := 0
	for rowIndex, record := range records {
		var parameterType string
		isKeyRow := -1
		for columnIndex, value := range record {
			// isBreak := false

			if strings.Contains(strings.ToLower(value), config.parametricNameColumn) {
				dataTool.ParametricIndex = columnIndex
				if config.beginFromParametric {
					checkColumnStart = columnIndex
				} else {
					checkColumnStart = columnIndex + 1
				}
			}

			if dataTool.ParametricIndex < 0 {
				continue
			}

			if columnIndex == 0 {
				parameterType = ""
				if strings.Contains(strings.ToLower(value), strings.ToLower(config.keyColumn)) {
					isKeyRow = rowIndex
					parameterType = ""
				} else {
					if rowIndex != isKeyRow && isKeyRow != -1 {
						isKeyRow = -1
					}
					for i, col := range config.getColumns {
						if strings.Contains(strings.ToLower(value), strings.ToLower(col)) {
							parameterType = col
							config.getColumns = removeElementAt(config.getColumns, i)
							break
						}
					}
				}

				continue
			}

			if isKeyRow >= 0 {
				if columnIndex >= checkColumnStart {
					e := &ParametricData{
						Name:  value,
						Limit: LimitData{data: make(map[string]float64)},
					}

					mapParametricData[columnIndex] = e
					dataTool.TotalParams++
				}
			} else {
				if parameterType == "" {
					continue
				}

				if columnIndex >= checkColumnStart {
					e := mapParametricData[columnIndex]
					var v *float64
					if !slices.Contains(config.nullValues, value) {
						vP, err := strconv.ParseFloat(value, 64)
						if err != nil {
							return nil, fmt.Errorf("invalid %s at row %d, column %d: %v", parameterType, rowIndex+1, columnIndex+1, err)
						}

						v = &vP
					}

					if v != nil {
						e.Limit.data[parameterType] = *v
					}
					mapParametricData[columnIndex] = e
				}
			}
			// if isBreak {
			// 	break
			// }
		}
	}

	for _, v := range mapParametricData {
		dataTool.Data = append(dataTool.Data, *v)
	}

	return dataTool, nil
}

func compare(oldData, newData *DataTool) {
	newParams := make([]ParametricData, 0)
	removeParams := make([]ParametricData, 0)
	remainParams := make(map[string]ParametricData, 0)
	remainRes := make([]RemainParametricData, 0)
	existParams := make(map[string]bool)

	for _, old := range oldData.Data {
		existParams[old.Name] = true
	}
	for _, newParam := range newData.Data {
		if _, exists := existParams[newParam.Name]; !exists {
			newParams = append(newParams, newParam)
		} else {
			remainParams[newParam.Name] = newParam
			existParams[newParam.Name] = false
		}
	}

	for _, old := range oldData.Data {
		if exists, found := existParams[old.Name]; found && exists {
			removeParams = append(removeParams, old)
		}
		if e, found := remainParams[old.Name]; found {
			if old.Limit.IsDifferent(e.Limit) {
				remainRes = append(remainRes, RemainParametricData{
					Old: old,
					New: e,
				})
			}
		}
	}
	// for _, new := range newData.Data {
	// 	if exists, found := existParams[new.Name]; found && exists {

	// 	}
	// }

	fmt.Printf("New Params: %+v\n", newParams)
	fmt.Printf("Remove Params: %+v\n", removeParams)
	fmt.Printf("Remain Res: %+v\n", remainRes)
}

func main() {
	parametric := flag.String("parametric", "parametric", "a string")
	getColumns := flag.String("get-columns", "min,max,avg", "a comma separated string")
	beginFromParametric := flag.Bool("begin-from-parametric", false, "a bool")
	nullValues := flag.String("null-values", "N/A,NULL,-", "a comma separated string")
	keyColumn := flag.String("key", "key", "a string")

	flag.Parse()

	config := Config{
		parametricNameColumn: *parametric,
		getColumns:           strings.Split(*getColumns, ","),
		beginFromParametric:  *beginFromParametric,
		nullValues:           strings.Split(*nullValues, ","),
		keyColumn:            *keyColumn,
	}
	fmt.Println(config)
	fmt.Println("Read CSV")
	fmt.Println(strings.Repeat("=", 60))

	// File cần đọc
	csvFile := "dummy.csv"
	csvFile2 := "dummy2.csv"

	records, err := readCSVFile(csvFile)
	if err != nil {
		fmt.Printf("Err: %v\n", err)
		return
	}

	old, err := convertData(records, config)
	if err != nil {
		fmt.Printf("Err: %v\n", err)
		return
	}
	fmt.Printf("Old Data: %+v\n", old)

	records, err = readCSVFile(csvFile2)
	if err != nil {
		fmt.Printf("Err: %v\n", err)
		return
	}

	new, err := convertData(records, config)
	if err != nil {
		fmt.Printf("Err: %v\n", err)
		return
	}

	compare(old, new)

	fmt.Println("\nDone")
}
