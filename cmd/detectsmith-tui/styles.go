package main

import (
	"github.com/charmbracelet/lipgloss"
)

// Detectsmith color palette — dark theme
var (
	// Brand / header
	ColorForeground = lipgloss.Color("#E8E6E3")
	ColorBackground  = lipgloss.Color("#1A1A1D")

	// Status
	ColorSuccess  = lipgloss.Color("#3FB950")
	ColorWarning  = lipgloss.Color("#D29922")
	ColorError    = lipgloss.Color("#F85149")
	ColorInfo     = lipgloss.Color("#58A6FF")

	// TUI chrome
	ColorHeader    = lipgloss.Color("#79C0FF")
	ColorSubtle    = lipgloss.Color("#8B949E")
	ColorBorder    = lipgloss.Color("#30363D")
	ColorSelection = lipgloss.Color("#264F78")
	ColorHighlight = lipgloss.Color("#388BFD26")

	// ATT&CK tactic colors
	ColorRecon    = lipgloss.Color("#FF7B72")
	ColorResource  = lipgloss.Color("#FFA657")
	ColorInitial  = lipgloss.Color("#FF7B72")
	ColorExec     = lipgloss.Color("#FFC657")
	ColorPersist  = lipgloss.Color("#D2A8FF")
	ColorPrivEsc   = lipgloss.Color("#79C0FF")
	ColorDefense    = lipgloss.Color("#FFA657")
	ColorC2       = lipgloss.Color("#79C0FF")
	ColorExfil    = lipgloss.Color("#56D364")
	ColorImpact   = lipgloss.Color("#F85149")
)

// Style definitions
var (
	WindowStyle = lipgloss.NewStyle().
		Foreground(ColorForeground).
		Background(ColorBackground).
		Padding(1, 2)

	TitleStyle = lipgloss.NewStyle().
		Foreground(ColorHeader).
		Bold(true).
		Padding(0, 1)

	SubtitleStyle = lipgloss.NewStyle().
		Foreground(ColorSubtle).
		Padding(0, 1)

	StatusSuccessStyle = lipgloss.NewStyle().
			Foreground(ColorSuccess)

	StatusWarningStyle = lipgloss.NewStyle().
			Foreground(ColorWarning)

	StatusErrorStyle = lipgloss.NewStyle().
		  Foreground(ColorError)

	LabelStyle = lipgloss.NewStyle().
	    Foreground(ColorSubtle)

	ValueStyle = lipgloss.NewStyle().
	    Foreground(ColorForeground)

	CardStyle = lipgloss.NewStyle().
	    Foreground(ColorForeground).
	    Background(lipgloss.Color("#21222C")).
	    BorderStyle(lipgloss.Border{
		Left: "│",
		Right: "│",
		Top: " ",
		Bottom: " ",
	}).
	BorderForeground(ColorBorder).
	Padding(1, 2).
	MarginRight(1)

	CardActiveStyle = lipgloss.NewStyle().
		  Foreground(ColorHeader).
		  Background(lipgloss.Color("#1F3054")).
		  BorderStyle(lipgloss.Border{
		 	Left: "│",
		 	Right: "│",
		 	Top: " ",
		 	Bottom: " ",
		  }).
		  BorderForeground(ColorInfo).
		  Padding(1, 2).
		  MarginRight(1)

	TableHeaderStyle = lipgloss.NewStyle().
			   Foreground(ColorSubtle).
			   Bold(true)

	TableRowStyle = lipgloss.NewStyle().
			Foreground(ColorForeground)

	TableRowAltStyle = lipgloss.NewStyle().
			   Background(lipgloss.Color("#161B22")).
			   Foreground(ColorForeground)

	// Common style aliases for TUI screens
	StyleHeader = lipgloss.NewStyle().
		      Foreground(ColorHeader).
		      Bold(true)

	StyleTitle = TitleStyle

	StyleDim = lipgloss.NewStyle().
		   Foreground(ColorSubtle)

	StyleGood = lipgloss.NewStyle().
		    Foreground(ColorSuccess)

	StyleWarn = lipgloss.NewStyle().
		    Foreground(ColorWarning)

	StyleError = lipgloss.NewStyle().
		     Foreground(ColorError)

	StyleAccent = lipgloss.NewStyle().
		      Foreground(ColorInfo)
)