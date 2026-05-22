package main

func renderSepulchrynScreen(m *Model) string {
	header := StyleTitle.Render("SepulchrynScan — Network Vulnerability Scanner")
	targetLine := StyleDim.Render("\nTarget: ") + StyleHeader.Render(m.sepulchrynState.currentTarget)

	actions := StyleDim.Render("\n\nActions:")
	sBtn := "[S] Scan target"
	lBtn := "[L] List scans"
	rBtn := "[R] Report"

	output := ""
	if m.sepulchrynState.lastOutput != "" {
		output = "\n" + StyleDim.Render(m.sepulchrynState.lastOutput)
	}

	err := ""
	if m.lastError != "" {
		err = StyleError.Render("\nError: " + m.lastError)
	}

	if m.commandRunning && m.currentCmd == "sepulchrynscan scan" {
		return header + targetLine + "\n\n" + m.spinner.View() + " Scanning..." + err
	}

	return header + targetLine + "\n" + actions + "\n  " + sBtn + "  " + lBtn + "  " + rBtn + output + err
}