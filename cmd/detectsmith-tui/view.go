package main

func (m *Model) View() string {
	header := renderHeader(m)
	footer := renderFooter(m)
	body := renderScreen(m)

	return header + body + footer
}

func renderHeader(m *Model) string {
	tabs := ""
	for i := screenDashboard; i <= screenSettings; i++ {
		prefix := " "
		if m.currentScreen == i {
			prefix = ">"
		}
		tabs += prefix + i.String() + " "
	}
	return StyleHeader.Render("DetectSmith  ") + StyleDim.Render(tabs) + "\n"
}

func renderFooter(m *Model) string {
	keys := "[1-5] nav  [S] scan  [L] lint  [P] pipeline  [q] quit"
	if m.commandRunning {
		return StyleDim.Render(keys+"  ") + m.spinner.View() + " " + m.currentCmd
	}
	return StyleDim.Render(keys)
}

func renderScreen(m *Model) string {
	switch m.currentScreen {
	case screenDashboard:
		return renderDashboard(m)
	case screenSepulchrynScan:
		return renderSepulchrynScreen(m)
	case screenDetectsmith:
		return renderDetectsmithScreen(m)
	case screenPipeline:
		return renderPipelineScreen(m)
	case screenSettings:
		return renderSettingsScreen(m)
	}
	return StyleError.Render("Unknown screen")
}