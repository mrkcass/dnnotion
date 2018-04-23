// Copyright 2017 Zack Guo <zack.y.guo@gmail.com>. All rights reserved.
// Use of this source code is governed by a MIT license that can
// be found in the LICENSE file.

package main

import (
	"fmt"
	"io/ioutil"
	"math"
	"regexp"
	"strings"

	"github.com/gizak/termui"
)

func main() {
	err := termui.Init()
	if err != nil {
		panic(err)
	}
	defer termui.Close()

	rows1 := [][]string{
		[]string{"runlog", "loss", "accuracy", "f1"},
	}

	sweepLogData := readFile("data/run.0407.sweep")
	runLogFiles := getRunFilenamesFromSweepLog(sweepLogData)
	for _, name := range runLogFiles {
		fmt.Printf("run log name: %s\n", name)
		rowdata := []string{name, ".34", "0.8911", "0.7777"}
		rows1 = append(rows1, rowdata)
	}

	table1 := termui.NewTable()
	table1.Rows = rows1
	table1.FgColor = termui.ColorWhite
	table1.BgColor = termui.ColorDefault
	table1.Y = 0
	table1.X = 0
	table1.Width = 51
	table1.Height = 35

	termui.Render(table1)

	// createAccPlot()

	termui.Handle("/sys/kbd/q", func(termui.Event) {
		termui.StopLoop()
	})
	termui.Loop()
}

func createAccPlot() {

	sinps := (func() []float64 {
		n := 220
		ps := make([]float64, n)
		for i := range ps {
			ps[i] = 1 + math.Sin(float64(i)/5)
		}
		return ps
	})()

	lc0 := termui.NewLineChart()
	lc0.BorderLabel = "braille-mode Line Chart"
	lc0.Data = sinps
	lc0.Width = 50
	lc0.Height = 12
	lc0.X = 0
	lc0.Y = 30
	lc0.AxesColor = termui.ColorWhite
	lc0.LineColor = termui.ColorGreen | termui.AttrBold

	lc1 := termui.NewLineChart()
	lc1.BorderLabel = "dot-mode Line Chart"
	lc1.Mode = "dot"
	lc1.Data = sinps
	lc1.Width = 26
	lc1.Height = 12
	lc1.X = 51
	lc1.DotStyle = '+'
	lc1.AxesColor = termui.ColorWhite
	lc1.LineColor = termui.ColorYellow | termui.AttrBold

	lc2 := termui.NewLineChart()
	lc2.BorderLabel = "dot-mode Line Chart"
	lc2.Mode = "dot"
	lc2.Data = sinps[4:]
	lc2.Width = 77
	lc2.Height = 16
	lc2.X = 0
	lc2.Y = 40
	lc2.AxesColor = termui.ColorWhite
	lc2.LineColor = termui.ColorCyan | termui.AttrBold

	termui.Render(lc0, lc1, lc2)
}

func readFile(fname string) string {
	fileBytes, _ := ioutil.ReadFile(fname)
	var fileString = string(fileBytes)
	return fileString
}

func getRunFilenamesFromSweepLog(sweepLog string) []string {
	lines := strings.Split(sweepLog, "\n")
	var runLogFnames []string
	reRunIdAll := regexp.MustCompile("RUNID: [0-9]+")
	reRunIdNum := regexp.MustCompile("[0-9]+")
	for _, element := range lines {
		if strings.Contains(element, "TRAINID") {
			runid := reRunIdAll.FindString(element)
			runid = reRunIdNum.FindString(runid)
			fname := "data/run." + runid + ".log"
			runLogFnames = append(runLogFnames, fname)
		}
	}

	return runLogFnames
}
