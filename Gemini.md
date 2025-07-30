# Gemini Agent Workspace

This document is a workspace for the Gemini agent to track tasks, understand the project, and collaborate with you.

## Project Overview

This project is a retirement planner that models financial scenarios based on user-provided data. It calculates savings, expenses, taxes, and other financial metrics over time and generates reports.

## Key Files

*   `retirement_model_v9.py`: The main Python script containing the retirement planning model.
*   `input_files/`: Directory for input data files (e.g., `accounts.csv`, `config.csv`).
*   `reports/`: Directory where the output reports and plots are generated.
*   `documentation/`: Contains documentation for the project.
*   `Gemini.md`: This file, used for tracking tasks and project context.

## Development Workflow

*   **Running the model:** (to be determined)
*   **Running tests:** (to be determined)
*   **Linting:** (to be determined)

## Programming Rules

*   Any currency should be rounded to the nearest whole dollar for the output reports.
*   **IMPORTANT:** Do not use the `input_files - sample` directory for any reason. Always use the `input_files` directory.

## Future Enhancements

### High Priority
- [] In "Max SS + Fill 22% Bracket_yearly.csv" report, IRMAA  values in reports seem much too high.  Please review for logic errors.
- [] In "Max SS + Fill 22% Bracket_yearly.csv" report, RMD values in reports seem much too high to stay below the 22% tax bracket.  Please review for logic errors.

### Completed Tasks
- [x] Round all currency values in output reports to the nearest whole dollar.
- [x] Add yearly tabulations for each scenario.
    - [x] Each scenario will have a separate csv file located in the "yearly" subdirectory.
    - [x] **Columns to add:**
        - [x] Each expense identified in `annual_expenses`
        - [x] Required Minimum Distribution (RMD)
        - [x] Income Related Monthly Adjusted Amount (IRMAA)
        - [x] Roth Conversions Amount
        - [x] Taxes
        - [x] Total Expenses
        - [x] Total Savings
        - [x] **Capital in each of the savings categories:**
            - [x] Taxable
            - [x] Roth
            - [x] Traditional
- [x] Clear out files and subdirectories under `reports` each run.
- [x] Add age columns to yearly reports.
- [x] Move age columns between Total Expenses and RMD columns.
- [x] Increase Property Taxes by 7% per year.
- [x] Read the program file `retirement_model_v9.py` and `Instructions.md` to understand the logic.
