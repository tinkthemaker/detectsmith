package main

import (
	"fmt"

	"github.com/charmbracelet/lipgloss"
)

func renderDashboard(m *Model) string {
	if m.commandRunning && (m.currentCmd == "lint" || m.currentCmd == "test" || m.currentCmd == "coverage" || m.currentCmd == "docs" || m.currentCmd == "validate") {
		spinnerView := lipgloss.NewStyle().Foreground(ColorInfo).Render(m.spinner.View())
		msg := lipgloss.NewStyle().Foreground(ColorSubtle).Render("Running " + m.currentCmd + "... press q to cancel")
		return fmt.Sprintf("\n\n%s  %s\n\n", spinnerView, msg)
	}

	var lines []string

	// Lint summary
	if m.lintReport != nil {
		r := m.lintReport
		scoreStr := fmt.Sprintf("%.0f", r.Summary.AverageScore)
		errorsStr := lipgloss.NewStyle().Foreground(ColorError).Render(fmt.Sprintf("%d", r.Summary.FindingsError))
		warnsStr := lipgloss.NewStyle().Foreground(ColorWarning).Render(fmt.Sprintf("%d", r.Summary.FindingsWarn))
		scoreStyle := lipgloss.NewStyle().Foreground(ColorSuccess)
		if r.Summary.AverageScore < 80 {
			scoreStyle = lipgloss.NewStyle().Foreground(ColorError)
		} else if r.Summary.AverageScore < 100 {
			scoreStyle = lipgloss.NewStyle().Foreground(ColorWarning)
		}
		lines = append(lines,
			lipgloss.NewStyle().Foreground(ColorHeader).Bold(true).Render("  LINT RESULTS")+"  ("+lipgloss.NewStyle().Foreground(ColorSubtle).Render("press l to re-run")+")",
			fmt.Sprintf("    Rules: %d   Errors: %s   Warnings: %s   Avg Score: %s",
				r.Summary.RulesTotal, errorsStr, warnsStr, scoreStyle.Render(scoreStr)),
		)
	} else {
		lines = append(lines,
			lipgloss.NewStyle().Foreground(ColorHeader).Bold(true).Render("  LINT RESULTS"),
			lipgloss.NewStyle().Foreground(ColorSubtle).Render("    Press [L] to lint detection rules"),
		)
	}

	// Test summary
	if m.testReport != nil {
		r := m.testReport
		passedStr := lipgloss.NewStyle().Foreground(ColorSuccess).Render(fmt.Sprintf("%d", r.Summary.TestsPassed))
		failedStr := lipgloss.NewStyle().Foreground(ColorError).Render(fmt.Sprintf("%d", r.Summary.TestsFailed))
		lines = append(lines,
			"",
			lipgloss.NewStyle().Foreground(ColorHeader).Bold(true).Render("  TEST RESULTS")+"  ("+lipgloss.NewStyle().Foreground(ColorSubtle).Render("press t to re-run")+")",
			fmt.Sprintf("    Tests: %d total   Passed: %s   Failed: %s   Rules Tested: %d",
				r.Summary.TestsTotal, passedStr, failedStr, r.Summary.RulesTested),
		)
	} else {
		lines = append(lines,
			"",
			lipgloss.NewStyle().Foreground(ColorHeader).Bold(true).Render("  TEST RESULTS"),
			lipgloss.NewStyle().Foreground(ColorSubtle).Render("    Press [T] to run regression tests"),
		)
	}

	// Coverage summary
	if m.coverageReport != nil {
		r := m.coverageReport
		lines = append(lines,
			"",
			lipgloss.NewStyle().Foreground(ColorHeader).Bold(true).Render("  ATT&CK COVERAGE")+"  ("+lipgloss.NewStyle().Foreground(ColorSubtle).Render("press c to re-run")+")",
			fmt.Sprintf("    Tactics: %d   Techniques: %d   Untagged rules: %d",
				r.Summary.TacticsCovered, r.Summary.TechniquesCovered, r.Summary.RulesMissingATTACKTags),
		)
	} else {
		lines = append(lines,
			"",
			lipgloss.NewStyle().Foreground(ColorHeader).Bold(true).Render("  ATT&CK COVERAGE"),
			lipgloss.NewStyle().Foreground(ColorSubtle).Render("    Press [C] to generate coverage report"),
		)
	}

	// Docs summary
	if m.docsResult != nil {
		r := m.docsResult
		lines = append(lines,
			"",
			lipgloss.NewStyle().Foreground(ColorHeader).Bold(true).Render("  DOCUMENTATION")+"  ("+lipgloss.NewStyle().Foreground(ColorSubtle).Render("press d to re-run")+")",
			fmt.Sprintf("    Rule pages: %d   Index pages: %d   Output: %s",
				r.RulePagesWritten, r.IndexPagesWritten, r.OutputDirectory),
		)
	} else {
		lines = append(lines,
			"",
			lipgloss.NewStyle().Foreground(ColorHeader).Bold(true).Render("  DOCUMENTATION"),
			lipgloss.NewStyle().Foreground(ColorSubtle).Render("    Press [D] to generate docs"),
		)
	}

	// Quick commands
	lines = append(lines,
		"",
		lipgloss.NewStyle().Foreground(ColorHeader).Bold(true).Render("  QUICK COMMANDS"),
	)

	cmdStyle := lipgloss.NewStyle().
		Border(lipgloss.RoundedBorder()).
		BorderForeground(ColorBorder).
		Padding(0, 1).
		Foreground(ColorForeground)

	keys := []string{"L", "T", "C", "D", "A"}
	cmds := []string{"lint", "test", "coverage", "docs", "all (validate)"}
	var cards []string
	for i := range keys {
		keyStyle := lipgloss.NewStyle().Foreground(ColorInfo).Bold(true)
		cards = append(cards, cmdStyle.Render(
			keyStyle.Render("["+keys[i]+"]")+" "+cmds[i],
		))
	}
	lines = append(lines, lipgloss.JoinHorizontal(lipgloss.Top, cards...))

	return lipgloss.JoinVertical(lipgloss.Top, lines...)
}