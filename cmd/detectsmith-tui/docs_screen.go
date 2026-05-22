package main

import (
	"fmt"

	"github.com/charmbracelet/lipgloss"
)

func renderDocsScreen(m *Model) string {
	if m.commandRunning && m.currentCmd == "docs" {
		return lipgloss.NewStyle().Foreground(ColorInfo).Render(m.spinner.View()) + " Generating docs..."
	}

	if m.docsResult == nil {
		return lipgloss.NewStyle().
			Foreground(ColorSubtle).
			Render("  Press [D] to generate documentation.")
	}

	r := m.docsResult

	label := lipgloss.NewStyle().Foreground(ColorHeader).Bold(true).Render

	rulePages := fmt.Sprintf("%d", r.RulePagesWritten)
	indexPages := fmt.Sprintf("%d", r.IndexPagesWritten)
	outputDir := r.OutputDirectory

	return lipgloss.JoinVertical(
		lipgloss.Top,
		label("  DOCUMENTATION"),
		"",
		fmt.Sprintf("  %s  Rule pages written", label("Pages:")+" "+rulePages),
		fmt.Sprintf("  %s  Index pages written", label("Indexes:")+" "+indexPages),
		fmt.Sprintf("  %s  %s", label("Output:"), lipgloss.NewStyle().Foreground(ColorForeground).Render(outputDir)),
		"",
		label("  Run [D] to regenerate docs"),
	)
}