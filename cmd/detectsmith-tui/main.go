package main

import (
	"fmt"
	"os"

	tea "github.com/charmbracelet/bubbletea"
)

func main() {
	// Detectsmith TUI must be run from the project root.
	if err := os.Chdir("E:/AI backups/detectsmith"); err != nil {
		fmt.Fprintln(os.Stderr, "Failed to change to project directory:", err)
		os.Exit(1)
	}

	model := NewModel()
	if _, err := tea.NewProgram(model, tea.WithAltScreen()).Run(); err != nil {
		fmt.Fprintln(os.Stderr, "Error running TUI:", err)
		os.Exit(1)
	}
}