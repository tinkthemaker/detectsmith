package main

import "github.com/charmbracelet/bubbles/spinner"

type screen int

const (
	screenDashboard screen = iota
	screenRules
	screenTests
	screenCoverage
	screenDocs
)

func (s screen) title() string {
	switch s {
	case screenDashboard:
		return "Dashboard"
	case screenRules:
		return "Rules"
	case screenTests:
		return "Test Results"
	case screenCoverage:
		return "ATT&CK Coverage"
	case screenDocs:
		return "Documentation"
	default:
		return "Detectsmith"
	}
}

// Model is the root tea.Model for the Detectsmith TUI.
type Model struct {
	currentScreen screen

	// CLI state
	projectRoot   string
	detectsmithBin string
	cliAvailable  bool
	loadError      string

	// Command results (populated after a command runs)
	lintReport      *LintReport
	testReport      *TestReport
	coverageReport  *CoverageReport
	docsResult      *DocsReport
	lastCommand     string
	lastError       string

	// Spinner state for running commands
	spinner       spinner.Model
	commandRunning bool
	currentCmd     string

	// Screen-specific state
	rulesCursor   int
	testsCursor   int
	selectedRule  int
}

// LintReport mirrors the detectsmith CLI JSON output schema.
type LintReport struct {
	SchemaVersion string       `json:"schema_version"`
	Command       string       `json:"command"`
	Status        string       `json:"status"`
	Summary       LintSummary  `json:"summary"`
	Rules         []RuleResult `json:"rules"`
}

// LintSummary holds aggregate lint metrics.
type LintSummary struct {
	RulesTotal     int     `json:"rules_total"`
	FindingsError  int     `json:"findings_error"`
	FindingsWarn   int     `json:"findings_warn"`
	AverageScore   float64 `json:"average_score"`
}

// RuleResult is a per-rule lint result.
type RuleResult struct {
	Path       string        `json:"path"`
	Score      float64       `json:"score"`
	Findings   []LintFinding `json:"findings"`
}

// LintFinding is a single lint issue.
type LintFinding struct {
	Severity     string `json:"severity"`
	CheckID      string `json:"check_id"`
	Message      string `json:"message"`
	Recommendation string `json:"recommendation"`
}

// TestReport mirrors the detectsmith test JSON output.
type TestReport struct {
	SchemaVersion string       `json:"schema_version"`
	Command       string       `json:"command"`
	Status        string       `json:"status"`
	Summary       TestSummary  `json:"summary"`
	Tests         []TestResult `json:"tests"`
}

// TestSummary holds aggregate test metrics.
type TestSummary struct {
	TestsTotal   int `json:"tests_total"`
	TestsPassed  int `json:"tests_passed"`
	TestsFailed  int `json:"tests_failed"`
	RulesTested  int `json:"rules_tested"`
}

// TestResult is a single test case result.
type TestResult struct {
	Name            string `json:"name"`
	Status          string `json:"status"`
	MatchedEvents   int    `json:"matched_events"`
	FailureReason   string `json:"failure_reason,omitempty"`
}

// CoverageReport mirrors the detectsmith coverage JSON output.
type CoverageReport struct {
	SchemaVersion string           `json:"schema_version"`
	Command       string           `json:"command"`
	Status        string           `json:"status"`
	Summary       CoverageSummary  `json:"summary"`
	Tactics       []TacticCoverage `json:"tactics"`
	Techniques    []TechCoverage   `json:"techniques"`
	RulesMissing  []string        `json:"rules_missing_attack_tags"`
}

// CoverageSummary holds aggregate coverage metrics.
type CoverageSummary struct {
	RulesTotal            int `json:"rules_total"`
	TacticsCovered        int `json:"tactics_covered"`
	TechniquesCovered     int `json:"techniques_covered"`
	RulesMissingATTACKTags int `json:"rules_missing_attack_tags"`
}

// TacticCoverage is ATT&CK tactic-level coverage.
type TacticCoverage struct {
	ID        string `json:"id"`
	Name      string `json:"name"`
	Techniques int   `json:"techniques"`
	Rules      []string `json:"rules"`
}

// TechCoverage is ATT&CK technique-level coverage.
type TechCoverage struct {
	ID        string `json:"id"`
	Name      string `json:"name"`
	Tactic    string `json:"tactic"`
	Rules      []string `json:"rules"`
}

// DocsReport mirrors the detectsmith docs JSON output.
type DocsReport struct {
	SchemaVersion      string `json:"schema_version"`
	Command            string `json:"command"`
	Status             string `json:"status"`
	RulePagesWritten   int    `json:"rule_pages_written"`
	IndexPagesWritten  int    `json:"index_pages_written"`
	OutputDirectory    string `json:"output_directory"`
}