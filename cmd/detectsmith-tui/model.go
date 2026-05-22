package main

import (
	"github.com/charmbracelet/bubbles/spinner"
	tea "github.com/charmbracelet/bubbletea"
)

type screen int

const (
	screenDashboard screen = iota
	screenSepulchrynScan
	screenDetectsmith
	screenPipeline
	screenSettings
)

func (s screen) String() string {
	switch s {
	case screenDashboard: return "Dashboard"
	case screenSepulchrynScan: return "SepulchrynScan"
	case screenDetectsmith: return "Detectsmith"
	case screenPipeline: return "Pipeline"
	case screenSettings: return "Settings"
	default: return "DetectSmith"
	}
}

func (s screen) label() string {
	return "[" + s.String() + "]"
}

type Model struct {
	currentScreen    screen
	sepulchrynState  SepulchrynState
	detectsmithState DetectsmithState
	pipelineState    PipelineState
	spinner          spinner.Model
	commandRunning   bool
	currentCmd       string
	lastError        string
	outputBuffer     string
	navCursor        int
}

type SepulchrynState struct {
	scans          []ScanEntry
	currentTarget  string
	latestScanID   string
	lastOutput     string
}

type DetectsmithState struct {
	lintOutput     string
	testOutput     string
	coverageOutput string
	gapOutput      string
}

type PipelineState struct {
	step         string
	scanDBPath   string
	gapOutput    string
	backlogJSON  string
	progress     float64
}

type ScanEntry struct {
	ID       string
	Target   string
	Status   string
	Started  string
}

func NewModel() *Model {
	sp := spinner.New()
	sp.Spinner = spinner.Dot
	return &Model{
		currentScreen:    screenDashboard,
		sepulchrynState:   SepulchrynState{},
		detectsmithState:  DetectsmithState{},
		pipelineState:     PipelineState{step: "idle"},
		spinner:           sp,
	}
}

func (m *Model) Init() tea.Cmd {
	return nil
}
