package main

import (
	"bytes"
	"context"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/spinner"
	tea "github.com/charmbracelet/bubbletea"
)

// msg types
type tickMsg struct{}

type runCmdMsg struct {
	tool string
	args []string
	desc string
}

type cmdResultMsg struct {
	tool   string
	stdout string
	stderr string
	err    error
}

type setScreenMsg struct {
	s screen
}

// Update is the tea.Model Update function.
func (m *Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		return m.handleKey(msg)
	case spinner.TickMsg:
		newSpinner, cmd := m.spinner.Update(msg)
		m.spinner = newSpinner
		return m, cmd
	case setScreenMsg:
		m.currentScreen = msg.s
		return m, nil
	case runCmdMsg:
		return m, m.runCommand(msg.tool, msg.args, msg.desc)
	case cmdResultMsg:
		return m.handleCmdResult(msg)
	}
	return m, nil
}

func (m *Model) handleKey(msg tea.KeyMsg) (tea.Model, tea.Cmd) {
	key := msg.String()
	switch key {
	case "q", "Q":
		return m, tea.Quit
	case "1": m.currentScreen = screenDashboard
	case "2": m.currentScreen = screenSepulchrynScan
	case "3": m.currentScreen = screenDetectsmith
	case "4": m.currentScreen = screenPipeline
	case "5": m.currentScreen = screenSettings
	case "s", "S":
		if m.currentScreen == screenSepulchrynScan && m.sepulchrynState.currentTarget != "" {
			return m, m.runCommand("sepulchrynscan", []string{"scan", m.sepulchrynState.currentTarget}, "sepulchrynscan scan")
		}
	case "l", "L":
		if m.currentScreen == screenDetectsmith {
			return m, m.runCommand("detectsmith", []string{"lint", "rules/"}, "detectsmith lint")
		}
	case "t", "T":
		if m.currentScreen == screenDetectsmith {
			return m, m.runCommand("detectsmith", []string{"test", "tests/expected.yml"}, "detectsmith test")
		}
	case "c", "C":
		if m.currentScreen == screenDetectsmith {
			return m, m.runCommand("detectsmith", []string{"coverage", "rules/", "--format", "json", "--output", "reports/attack_coverage.json"}, "detectsmith coverage")
		}
	case "g", "G":
		if m.currentScreen == screenDetectsmith {
			return m, m.runCommand("detectsmith", []string{"gap", "tools/sepulchrynscan/data/sepulchryn.db", "--coverage", "reports/attack_coverage.json"}, "detectsmith gap")
		}
	case "p", "P":
		if m.currentScreen == screenPipeline {
			return m, m.runCommand("detectsmith", []string{"gap", "tools/sepulchrynscan/data/sepulchryn.db", "--coverage", "reports/attack_coverage.json"}, "pipeline: gap analysis")
		}
	}
	return m, nil
}

func (m *Model) handleCmdResult(msg cmdResultMsg) (tea.Model, tea.Cmd) {
	m.commandRunning = false
	if msg.err != nil {
		m.lastError = msg.err.Error()
		m.outputBuffer = msg.stderr
	} else {
		m.lastError = ""
		m.outputBuffer = msg.stdout
		switch msg.tool {
		case "sepulchrynscan":
			m.sepulchrynState.lastOutput = msg.stdout
		case "detectsmith":
			m.detectsmithState.gapOutput = msg.stdout
		}
	}
	return m, nil
}

func (m *Model) runCommand(tool string, args []string, desc string) tea.Cmd {
	m.commandRunning = true
	m.currentCmd = desc
	m.lastError = ""

	return func() tea.Msg {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
		defer cancel()

		python, _ := os.Executable()
		if python == "" || strings.Contains(python, "hermes") {
			python = "python"
		}

		var cmd *exec.Cmd
		if tool == "sepulchrynscan" {
			cmd = exec.CommandContext(ctx, python, append([]string{"-m", "sepulchrynscan.cli"}, args...)...)
			cmd.Dir = filepath.Join(repoRoot(), "tools", "sepulchrynscan")
		} else {
			cmd = exec.CommandContext(ctx, python, append([]string{"-m", "detectsmith.cli"}, args...)...)
			cmd.Dir = repoRoot()
		}

		var stdout, stderr bytes.Buffer
		cmd.Stdout = &stdout
		cmd.Stderr = &stderr
		err := cmd.Run()

		return cmdResultMsg{tool: tool, stdout: stdout.String(), stderr: stderr.String(), err: err}
	}
}

func repoRoot() string {
	cwd, _ := os.Getwd()
	return cwd
}