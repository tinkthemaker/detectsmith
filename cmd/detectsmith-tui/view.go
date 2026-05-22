package main

import (
	"fmt"
	"strings"

	"github.com/charmbracelet/lipgloss"
)

// View renders the current screen.
func (m *Model) View() string {
	if !m.cliAvailable {
		return renderErrorScreen(m.loadError)
	}

	var body string
	switch m.currentScreen {
	case screenDashboard:
		body = renderDashboard(m)
	case screenRules:
		body = renderRulesScreen(m)
	case screenTests:
		body = renderTestsScreen(m)
	case screenCoverage:
		body = renderCoverageScreen(m)
	case screenDocs:
		body = renderDocsScreen(m)
	default:
		body = renderDashboard(m)
	}

	return renderLayout(m, body)
}

// renderLayout wraps screen content with the shared chrome.
func renderLayout(m *Model, content string) string {
	nav := renderNav(m)
	header := renderHeader(m)
	footer := renderFooter(m)

	return lipgloss.JoinVertical(
		lipgloss.Top,
		header,
		nav,
		content,
		footer,
	)
}

func renderHeader(m *Model) string {
	icon := "⚔"
	title := lipgloss.NewStyle().
		Foreground(ColorHeader).
		Bold(true).
		Render("Detectsmith")

	subtitle := lipgloss.NewStyle().
		Foreground(ColorSubtle).
		Render("Detection Engineering Workbench")

	status := ""
	if m.commandRunning {
		status = lipgloss.NewStyle().
			Foreground(ColorInfo).
			Render("⟳ " + m.currentCmd)
	} else if m.lastError != "" {
		status = lipgloss.NewStyle().
			Foreground(ColorError).
			Render("✗ " + m.lastError)
	} else if m.lastCommand != "" {
		status = lipgloss.NewStyle().
			Foreground(ColorSuccess).
			Render("✓ " + m.lastCommand)
	}

	headerLine := fmt.Sprintf("  %s  %s   %s", icon, title, subtitle)
	if status != "" {
		headerLine += "   " + status
	}

	border := lipgloss.NewStyle().
		Foreground(ColorBorder).
		Render(strings.Repeat("─", 80))

	return lipgloss.JoinVertical(
		lipgloss.Top,
		border,
		headerLine,
	)
}

func renderNav(m *Model) string {
	screens := []struct {
		key      string
		label    string
		screen   screen
	}{
		{"1", "Dashboard", screenDashboard},
		{"2", "Rules", screenRules},
		{"3", "Tests", screenTests},
		{"4", "Coverage", screenCoverage},
		{"5", "Docs", screenDocs},
	}

	var parts []string
	for _, s := range screens {
		label := s.label
		if m.currentScreen == s.screen {
			label = lipgloss.NewStyle().
				Foreground(ColorInfo).
				Bold(true).
				Render("● " + label)
		} else {
			label = lipgloss.NewStyle().
				Foreground(ColorSubtle).
				Render("○ " + label)
		}
		parts = append(parts, label)
	}

	return lipgloss.JoinHorizontal(lipgloss.Top, parts...)
}

func renderFooter(m *Model) string {
	if m.commandRunning {
		spinnerView := lipgloss.NewStyle().
			Foreground(ColorInfo).
			Render(m.spinner.View())
		return lipgloss.JoinHorizontal(
			lipgloss.Bottom,
			spinnerView+" running "+m.currentCmd+"... (q to quit)",
		)
	}

	help := lipgloss.NewStyle().
		Foreground(ColorSubtle).
		Render("l:lint  t:test  c:coverage  d:docs  a:all  ↑↓:navigate  q:quit")

	return lipgloss.JoinVertical(
		lipgloss.Bottom,
		lipgloss.NewStyle().Foreground(ColorBorder).Render(strings.Repeat("─", 80)),
		help,
	)
}

func renderErrorScreen(msg string) string {
	border := lipgloss.NewStyle().
		Foreground(ColorError).
		Render("┌─────────────────────────────────────────────────┐")

	content := lipgloss.NewStyle().
		Foreground(ColorError).
		Bold(true).
		Render("✗ Detectsmith CLI Not Found")

	body := lipgloss.NewStyle().
		Foreground(ColorSubtle).
		Render(msg)

	return lipgloss.JoinVertical(
		lipgloss.Top,
		border,
		"",
		content,
		"",
		body,
		"",
		lipgloss.NewStyle().
			Foreground(ColorSubtle).
			Render("Install the detectsmith CLI: pip install -e E:/AI backups/detectsmith"),
		"",
		lipgloss.NewStyle().
			Foreground(ColorSubtle).
			Render("Then run: detectsmith-tui"),
		"",
		lipgloss.NewStyle().
			Foreground(ColorSubtle).
			Render("Press q to quit."),
		"",
	)
}