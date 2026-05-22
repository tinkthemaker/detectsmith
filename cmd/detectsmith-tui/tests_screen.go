package main

import (
	"fmt"

	"github.com/charmbracelet/bubbles/table"
	"github.com/charmbracelet/lipgloss"
)

func renderTestsScreen(m *Model) string {
	if m.commandRunning && m.currentCmd == "test" {
		return lipgloss.NewStyle().Foreground(ColorInfo).Render(m.spinner.View()) + " Running tests..."
	}

	if m.testReport == nil {
		return lipgloss.NewStyle().
			Foreground(ColorSubtle).
			Render("  Press [T] to run regression tests.")
	}

	r := m.testReport

	cols := []table.Column{
		{Title: "", Width: 3},
		{Title: "Test Name", Width: 35},
		{Title: "Status", Width: 10},
		{Title: "Matched", Width: 8},
		{Title: "Failure Reason", Width: 30},
	}

	var rows []table.Row
	for i, test := range r.Tests {
		statusStr := test.Status
		status := statusStr
		if status == "passed" {
			status = lipgloss.NewStyle().Foreground(ColorSuccess).Render("✓ passed")
		} else {
			status = lipgloss.NewStyle().Foreground(ColorError).Render("✗ failed")
		}
		row := table.Row{"", test.Name, status, fmt.Sprintf("%d", test.MatchedEvents), test.FailureReason}
		if i == m.testsCursor {
			row[0] = "→"
		}
		rows = append(rows, row)
	}

	t := table.New(
		table.WithColumns(cols),
		table.WithRows(rows),
	)

	s := table.DefaultStyles()
	s.Header = s.Header.Foreground(lipgloss.Color("#8B949E")).Bold(true)
	s.Cell = s.Cell.Foreground(lipgloss.Color("#E8E6E3"))
	t.SetStyles(s)

	return t.View()
}