package main

func renderDashboard(m *Model) string {
	title := StyleTitle.Render("DetectSmith — Security Detection Workbench")
	desc := StyleDim.Render("Unified vulnerability scanning and detection gap analysis.")

	stats := StyleDim.Render(
		"\n  SepulchrynScan: network vulnerability scanner\n" +
		"  Detectsmith: detection rule linting and regression\n" +
		"  Pipeline: scan → gap analysis → prioritized backlog\n")

	section1 := StyleHeader.Render("\n[SepulchrynScan]")
	section1Desc := StyleDim.Render("\n  [S] Scan target    [L] List scans    [R] Report")

	section2 := StyleHeader.Render("\n[Detectsmith]")
	section2Desc := StyleDim.Render("\n  [L] Lint rules    [T] Run tests    [C] Coverage    [G] Gap analysis")

	section3 := StyleHeader.Render("\n[Pipeline]")
	section3Desc := StyleDim.Render("\n  [P] Run full pipeline: scan → gap → backlog")

	if m.lastError != "" {
		errLine := StyleError.Render("\nError: " + m.lastError)
		return title + "\n" + desc + stats + section1 + section1Desc + section2 + section2Desc + section3 + section3Desc + errLine
	}

	return title + "\n" + desc + stats + section1 + section1Desc + section2 + section2Desc + section3 + section3Desc
}