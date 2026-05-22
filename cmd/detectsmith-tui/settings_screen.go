package main

func renderSettingsScreen(m *Model) string {
	header := StyleTitle.Render("Settings")
	sepulchrynPath := StyleDim.Render("\nSepulchrynScan: ") + "tools/sepulchrynscan/"
	detectsmithPath := StyleDim.Render("\nDetectsmith: ") + "detectsmith/"
	repoPath := StyleDim.Render("\nRepo root: ") + repoRoot()
	about := StyleDim.Render("\n\nDetectSmith v0.4 — Unified detection workbench\nCharm Bubble Tea TUI + Python CLI")

	return header + sepulchrynPath + detectsmithPath + repoPath + about
}