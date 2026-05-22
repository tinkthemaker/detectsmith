package main

import (
	"fmt"

	"github.com/charmbracelet/bubbles/table"
	"github.com/charmbracelet/lipgloss"
)

func renderRulesScreen(m *Model) string {
	if m.commandRunning && m.currentCmd == "lint" {
		return lipgloss.NewStyle().Foreground(ColorInfo).Render(m.spinner.View()) + " Running lint..."
	}

	if m.lintReport == nil {
		return lipgloss.NewStyle().
			Foreground(ColorSubtle).
			Render("  Press [L] to run lint on detection rules.")
	}

	r := m.lintReport

	cols := []table.Column{
		{Title: "", Width: 3},
		{Title: "Rule File", Width: 55},
		{Title: "Score", Width: 6},
		{Title: "Findings", Width: 10},
	}

	var rows []table.Row
	for i, rule := range r.Rules {
		status := "✓"
		if rule.Score < 80 {
			status = "✗"
		} else if rule.Score < 100 {
			status = "⚠"
		}
		findings := ""
		if len(rule.Findings) > 0 {
			findings = fmt.Sprintf("%d", len(rule.Findings))
		}
		row := table.Row{status, rule.Path, fmt.Sprintf("%.0f", rule.Score), findings}
		if i == m.selectedRule {
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
