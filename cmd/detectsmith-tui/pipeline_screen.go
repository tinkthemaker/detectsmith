package main

import "strings"

func renderPipelineScreen(m *Model) string {
	header := StyleTitle.Render("Detection Pipeline")

	// Step indicator
	steps := []string{"Scan", "Gap Analysis", "Backlog"}
	stepLine := ""
	for i, s := range steps {
		prefix := "[ ]"
		if m.pipelineState.step == strings.ToLower(s) || (m.pipelineState.step == "done" && i == 2) {
			prefix = "[✓]"
		}
		stepLine += " " + prefix + " " + s
	}
	stepDisplay := StyleDim.Render("\nSteps: ") + stepLine + "\n"

	// Progress bar
	progress := ""
	if m.pipelineState.progress > 0 {
		filled := int(m.pipelineState.progress * 20)
		bar := strings.Repeat("█", filled) + strings.Repeat("░", 20-filled)
		progress = StyleAccent.Render("\n" + bar + " " + string(rune(int(m.pipelineState.progress*100)+'0')) + "%")
	}

	// Output
	output := ""
	if m.pipelineState.gapOutput != "" {
		output = "\n" + m.pipelineState.gapOutput
	}

	err := ""
	if m.lastError != "" {
		err = StyleError.Render("\nError: " + m.lastError)
	}

	if m.commandRunning {
		return header + stepDisplay + "\n" + m.spinner.View() + " " + m.currentCmd + err
	}

	runBtn := StyleHeader.Render("[P] Run Pipeline")
	return header + stepDisplay + "\n" + runBtn + progress + output + err
}