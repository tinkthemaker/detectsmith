package main

import (
	"fmt"

	"github.com/charmbracelet/bubbles/table"
	"github.com/charmbracelet/lipgloss"
)

func renderCoverageScreen(m *Model) string {
	if m.commandRunning && m.currentCmd == "coverage" {
		return lipgloss.NewStyle().Foreground(ColorInfo).Render(m.spinner.View()) + " Running coverage..."
	}

	if m.coverageReport == nil {
		return lipgloss.NewStyle().
			Foreground(ColorSubtle).
			Render("  Press [C] to generate ATT&CK coverage report.")
	}

	r := m.coverageReport

	// Tactics summary table
	tacticCols := []table.Column{
		{Title: "Tactic ID", Width: 22},
		{Title: "Name", Width: 25},
		{Title: "Techniques", Width: 12},
		{Title: "Rules", Width: 20},
	}

	var tacticRows []table.Row
	for _, t := range r.Tactics {
		tacticRows = append(tacticRows, table.Row{
			t.ID, t.Name,
			fmt.Sprintf("%d", t.Techniques),
			fmt.Sprintf("%d rules", len(t.Rules)),
		})
	}

	t := table.New(table.WithColumns(tacticCols), table.WithRows(tacticRows))
	s := table.DefaultStyles()
	s.Header = s.Header.Foreground(lipgloss.Color("#8B949E")).Bold(true)
	s.Cell = s.Cell.Foreground(lipgloss.Color("#E8E6E3"))
	t.SetStyles(s)

	// Missing tags section
	var missingStr string
	if len(r.RulesMissing) > 0 {
		missingStr = lipgloss.NewStyle().Foreground(ColorWarning).Render(
			fmt.Sprintf("  %d rules missing ATT&CK tags", len(r.RulesMissing)))
	} else {
		missingStr = lipgloss.NewStyle().Foreground(ColorSuccess).Render("  All rules have ATT&CK tags ✓")
	}

	header := lipgloss.NewStyle().Foreground(ColorHeader).Bold(true)
	summary := fmt.Sprintf("  Rules: %d   Tactics: %d   Techniques: %d",
		r.Summary.RulesTotal, r.Summary.TacticsCovered, r.Summary.TechniquesCovered)

	return lipgloss.JoinVertical(
		lipgloss.Top,
		header.Render("  ATT&CK COVERAGE"),
		summary,
		"",
		t.View(),
		missingStr,
	)
}