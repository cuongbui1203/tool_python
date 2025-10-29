package main

import (
	"encoding/csv"
	"fmt"
	"os"
	"strconv"
	"strings"
)

type DataTool struct {
	ParametricIndex int
	TotalParams     int
	Data            []ParametricData
}

type LimitData struct {
	UpperLimit *float64
	LowerLimit *float64
}

func (l LimitData) IsDifferent(other LimitData) bool {
	if (l.UpperLimit == nil) != (other.UpperLimit == nil) {
		return true
	}
	if l.UpperLimit != nil && other.UpperLimit != nil && *l.UpperLimit != *other.UpperLimit {
		return true
	}

	if (l.LowerLimit == nil) != (other.LowerLimit == nil) {
		return true
	}

	if l.LowerLimit != nil && other.LowerLimit != nil && *l.LowerLimit != *other.LowerLimit {
		return true
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

type LimitType string

const (
	UpperLimit LimitType = "upper"
	LowerLimit LimitType = "lower"
)

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

func convertData(records [][]string) (*DataTool, error) {
	dataTool := &DataTool{
		ParametricIndex: -1,
		TotalParams:     0,
		Data:            make([]ParametricData, 0),
	}

	mapParametricData := make(map[int]ParametricData)
	for i, record := range records {
		typeLimit := LimitType("")
		for j, value := range record {
			isBreak := false
			switch i {
			case 0:
				if strings.EqualFold(value, "Parametric") {
					dataTool.ParametricIndex = j
				}

				isBreak = true

			case 1:
				if j >= dataTool.ParametricIndex {
					dataTool.TotalParams++
					e, ok := mapParametricData[j]
					if !ok {
						e = ParametricData{}
					}
					e.Name = value
					mapParametricData[j] = e
				}

			default:
				if j == 0 {
					if strings.Contains(strings.ToLower(value), "upper limit") {
						typeLimit = UpperLimit
					}

					if strings.Contains(strings.ToLower(value), "lower limit") {
						typeLimit = LowerLimit
					}

					continue
				}

				if typeLimit == "" {
					continue
				}

				if j >= dataTool.ParametricIndex {
					e := mapParametricData[j]
					var v *float64
					if value != "NA" && value != "" {
						vP, err := strconv.ParseFloat(value, 64)
						if err != nil {
							return nil, fmt.Errorf("invalid limit value at row %d, column %d: %v", i+1, j+1, err)
						}

						v = &vP
					}

					if typeLimit == UpperLimit {
						e.Limit.UpperLimit = v
					}

					if typeLimit == LowerLimit {
						e.Limit.LowerLimit = v
					}

					mapParametricData[j] = e
				}
			}
			if isBreak {
				break
			}
		}
	}

	for _, v := range mapParametricData {
		dataTool.Data = append(dataTool.Data, v)
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

	old, err := convertData(records)
	if err != nil {
		fmt.Printf("Err: %v\n", err)
		return
	}

	records, err = readCSVFile(csvFile2)
	if err != nil {
		fmt.Printf("Err: %v\n", err)
		return
	}

	new, err := convertData(records)
	if err != nil {
		fmt.Printf("Err: %v\n", err)
		return
	}

	compare(old, new)

	fmt.Println("\nDone")
}
