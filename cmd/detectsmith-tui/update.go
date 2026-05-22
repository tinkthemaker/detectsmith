package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"time"

	"github.com/charmbracelet/bubbles/spinner"
	tea "github.com/charmbracelet/bubbletea"
)

// findDetectsmith searches common install paths for the detectsmith CLI.
func findDetectsmith() (string, bool) {
	paths := []string{
		"detectsmith",
		"detectsmith.exe",
		filepath.Join(os.Getenv("LOCALAPPDATA"), "Programs", "Python", "Python314", "Scripts", "detectsmith.exe"),
		filepath.Join(os.Getenv("APPDATA"), "Python", "Scripts", "detectsmith.exe"),
		filepath.Join(os.Getenv("USERPROFILE"), "AppData", "Roaming", "Python", "Python314", "Scripts", "detectsmith.exe"),
	}
	for _, p := range paths {
		if _, err := os.Stat(p); err == nil {
			return p, true
		}
	}
	if bin, err := exec.LookPath("detectsmith"); err == nil {
		return bin, true
	}
	return "", false
}

// NewModel builds the initial TUI model.
func NewModel() *Model {
	bin, ok := findDetectsmith()
	m := &Model{
		cliAvailable:   ok,
		detectsmithBin: bin,
	}
	m.spinner = spinner.New(spinner.WithSpinner(spinner.Dot))
	return m
}

// Msg types for command execution.
type cmdOutputMsg struct {
	cmd    string
	output []byte
}

type cmdErrorMsg struct {
	cmd string
	err string
}

// Init is tea.Model initialization.
func (m *Model) Init() tea.Cmd {
	bin, ok := findDetectsmith()
	m.detectsmithBin = bin
	m.cliAvailable = ok
	if !ok {
		m.loadError = "detectsmith CLI not found. Run 'pip install -e .' from the detectsmith project root, then restart the TUI."
	}
	return nil
}

// runDetectsmith shells out to detectsmith and returns stdout as a tea.Msg.
func runDetectsmith(cmdName string, args ...string) tea.Cmd {
	return func() tea.Msg {
		ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
		defer cancel()

		bin, ok := findDetectsmith()
		if !ok {
			return cmdErrorMsg{cmd: cmdName, err: "detectsmith binary not found"}
		}

		c := exec.CommandContext(ctx, bin, args...)
		out, err := c.Output()
		if err != nil {
			return cmdErrorMsg{cmd: cmdName, err: err.Error()}
		}
		return cmdOutputMsg{cmd: cmdName, output: out}
	}
}

func runLint() tea.Cmd {
	return runDetectsmith("lint", "lint", "rules/", "--format", "json", "--output", "reports/lint.json")
}

func runTest() tea.Cmd {
	return runDetectsmith("test", "test", "tests/expected.yml", "--format", "json", "--output", "reports/test_results.json")
}

func runCoverage() tea.Cmd {
	return runDetectsmith("coverage", "coverage", "rules/", "--format", "json", "--output", "reports/attack_coverage.json")
}

func runDocs() tea.Cmd {
	return runDetectsmith("docs", "docs", "rules/", "--out", "site/", "--format", "json", "--output", "reports/docs.json")
}

func runValidate() tea.Cmd {
	return runDetectsmith("validate", "run")
}

// Update is tea.Model update handler.
func (m *Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {

	case tea.KeyMsg:
		switch msg.String() {
		case "q", "ctrl+c":
			return m, tea.Quit

		case "1":
			m.currentScreen = screenDashboard
		case "2":
			m.currentScreen = screenRules
		case "3":
			m.currentScreen = screenTests
		case "4":
			m.currentScreen = screenCoverage
		case "5":
			m.currentScreen = screenDocs

		case "l":
			if !m.commandRunning && m.cliAvailable {
				m.commandRunning = true
				m.currentCmd = "lint"
				return m, runLint()
			}
		case "t":
			if !m.commandRunning && m.cliAvailable {
				m.commandRunning = true
				m.currentCmd = "test"
				return m, runTest()
			}
		case "c":
			if !m.commandRunning && m.cliAvailable {
				m.commandRunning = true
				m.currentCmd = "coverage"
				return m, runCoverage()
			}
		case "d":
			if !m.commandRunning && m.cliAvailable {
				m.commandRunning = true
				m.currentCmd = "docs"
				return m, runDocs()
			}
		case "a":
			if !m.commandRunning && m.cliAvailable {
				m.commandRunning = true
				m.currentCmd = "validate"
				return m, runValidate()
			}

		case "up", "k":
			switch m.currentScreen {
			case screenRules:
				if m.selectedRule > 0 {
					m.selectedRule--
				}
			case screenTests:
				if m.testsCursor > 0 {
					m.testsCursor--
				}
			}
		case "down", "j":
			switch m.currentScreen {
			case screenRules:
				if m.lintReport != nil && m.selectedRule < len(m.lintReport.Rules)-1 {
					m.selectedRule++
				}
			case screenTests:
				if m.testReport != nil && m.testsCursor < len(m.testReport.Tests)-1 {
					m.testsCursor++
				}
			}

		case "enter":
			if m.currentScreen == screenDashboard && m.lintReport != nil && len(m.lintReport.Rules) > 0 {
				m.currentScreen = screenRules
			}
		}

	case spinner.TickMsg:
		s, cmd := m.spinner.Update(msg)
		m.spinner = s
		return m, cmd

	case cmdOutputMsg:
		m.commandRunning = false
		m.lastCommand = msg.cmd
		m.lastError = ""
		switch msg.cmd {
		case "lint":
			var r LintReport
			if err := json.Unmarshal(msg.output, &r); err != nil {
				m.lastError = fmt.Sprintf("parse error: %v", err)
			} else {
				m.lintReport = &r
			}
		case "test":
			var r TestReport
			if err := json.Unmarshal(msg.output, &r); err != nil {
				m.lastError = fmt.Sprintf("parse error: %v", err)
			} else {
				m.testReport = &r
			}
		case "coverage":
			var r CoverageReport
			if err := json.Unmarshal(msg.output, &r); err != nil {
				m.lastError = fmt.Sprintf("parse error: %v", err)
			} else {
				m.coverageReport = &r
			}
		case "docs":
			var r DocsReport
			if err := json.Unmarshal(msg.output, &r); err != nil {
				m.lastError = fmt.Sprintf("parse error: %v", err)
			} else {
				m.docsResult = &r
			}
		}
		return m, nil

	case cmdErrorMsg:
		m.commandRunning = false
		m.lastCommand = msg.cmd
		m.lastError = msg.err
		return m, nil
	}

	return m, nil
}