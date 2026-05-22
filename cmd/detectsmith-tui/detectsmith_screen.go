package main

func renderDetectsmithScreen(m *Model) string {
	header := StyleTitle.Render("Detectsmith — Detection Rule Engine")
	actions := StyleDim.Render("\nActions:")
	lBtn := "[L] Lint"
	tBtn := "[T] Tests"
	cBtn := "[C] Coverage"
	gBtn := "[G] Gap"

	output := ""
	if m.detectsmithState.gapOutput != "" {
		output = "\n" + m.detectsmithState.gapOutput
	} else if m.outputBuffer != "" && m.currentScreen == screenDetectsmith {
		output = "\n" + m.outputBuffer
	}

	err := ""
	if m.lastError != "" && m.currentScreen == screenDetectsmith {
		err = StyleError.Render("\nError: " + m.lastError)
	}

	if m.commandRunning {
		return header + "\n" + actions + "\n  " + lBtn + "  " + tBtn + "  " + cBtn + "  " + gBtn + "\n\n" + m.spinner.View() + " " + m.currentCmd
	}

	return header + "\n" + actions + "\n  " + lBtn + "  " + tBtn + "  " + cBtn + "  " + gBtn + output + err
}