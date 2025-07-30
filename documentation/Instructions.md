# Retirement Portfolio & Tax Simulator: Documentation (v12)

## Introduction

This document provides a complete guide to the Python-based retirement simulator we have built. The program is designed as a powerful, personal modeling tool to help retirees make strategic financial decisions by comparing the long-term outcomes of different scenarios.

The primary purpose of this tool is to provide data-driven answers to critical retirement questions, such as:
*   When is the optimal time to claim Social Security?
*   What is the long-term impact of performing Roth conversions?
*   How does my plan hold up under different inflation scenarios?
*   What is the lifetime cost of taxes and Medicare surcharges in different strategies?

This document will guide you through the setup, usage, maintenance, and interpretation of the simulator.

---

## **IMPORTANT: Disclaimer**

This program is a **modeling and educational tool ONLY**. It is not a substitute for professional financial, tax, or legal advice. The results and scenarios generated are based on the data you provide and the simplified financial models built into the code. All financial decisions have real-world consequences, and you should consult with a qualified professional before taking any action based on the output of this program.

---

## Part 1: Getting Started

### 1.1 Folder Structure
The program is designed to use a clean and organized folder structure. Your main project directory should be set up as follows:

```
retirement_project/
├── input_files/            <-- Your 5 personal data files go here.
│   ├── accounts.csv
│   ├── annual_expenses.csv
│   ├── config.csv
│   ├── income_streams.csv
│   └── social_security.csv
├── reports/                <-- The program will save its output files here.
│   ├── plots/
│   └── yearly/
├── retirement_model_v12.py <-- The main program script.
└── .gitignore              <-- The file that protects your private data on GitHub.
```

### 1.2 Installation (One-Time Setup)
The program runs in a self-contained Anaconda environment and requires the `pandas` and `matplotlib` libraries.

1.  **Open the Anaconda Prompt** from your Windows Start Menu.
2.  **Create the environment** by running this command:
    ```bash
    conda create --name retirement_planner python=3.11 pandas matplotlib
    ```
3.  When prompted, type `y` and press Enter.

### 1.3 Running the Program
To run a simulation, follow these steps:

1.  **Open the Anaconda Prompt** (or a VSCode terminal configured for Anaconda).
2.  **Activate the environment:**
    ```bash
    conda activate retirement_planner
    ```
3.  **Navigate to your project folder:**
    ```bash
    cd C:\path\to\your\retirement_project
    ```
4.  **Run the script:**
    ```bash
    python retirement_model_v12.py
    ```

The program will print its progress and save all reports and plots to the appropriate subdirectories inside the `reports/` folder.

---

## Part 2: The User Guide - Your Input Files

(This section is unchanged as the input file structure is stable.)

The engine is powered by five CSV files located in the `input_files/` directory. The accuracy of the simulation depends entirely on the quality of this data.

### 2.1 `config.csv`
Holds the global settings for the simulation.

| parameter | value | Description |
| :--- | :--- | :--- |
| `start_year` | 2025 | The first year of the simulation. |
| `projection_years`| 35 | The number of years the simulation will run. |
| `federal_filing_status` | Married Filing Jointly | Your tax filing status. |
| `state` | California | Your state of residence. (Note: State tax logic is not implemented). |
| `inflation_rate_general`| 0.03 | The default annual inflation rate for most expenses. |
| `inflation_rate_healthcare`| 0.05 | The default annual inflation rate for healthcare. |

### 2.2 `accounts.csv`
Lists all your financial accounts.

| Column | Description |
| :--- | :--- |
| `account_name` | A unique name for each account. |
| `account_type` | Critical for tax logic. Must be one of: **`Taxable`**, **`Traditional`**, **`Roth`**, or **`Cash`**. |
| `balance` | The starting balance of the account. |
| `annual_growth_rate`| The estimated **TOTAL** annual return for the account. |
| `dividend_rate` | The portion of the return that is a taxable distribution (dividends/interest). For `Traditional` and `Roth`, this must be `0`. For `Cash`, this must equal `annual_growth_rate`. |

### 2.3 `income_streams.csv`
For external, non-Social Security income.

| Column | Description |
| :--- | :--- |
| `stream_name` | Name of the income source (e.g., "Pension"). |
| `annual_amount` | The gross annual amount. |
| `start_year` | The year the income begins. |
| `end_year` | The year the income ends. |
| `is_inflation_adjusted` | `TRUE` if it receives a COLA, otherwise `FALSE`. |

### 2.4 `social_security.csv`
Holds your base Social Security data.

| Column | Description |
| :--- | :--- |
| `person_name` | Your names (e.g., "Mike", "Cindy"). |
| `fra_benefit` | The estimated **annual** benefit at your Full Retirement Age (FRA). |
| `fra_age` | Your Full Retirement Age (e.g., 67). |

### 2.5 `annual_expenses.csv`
Lists all your planned expenses.

| Column | Description |
| :--- | :--- |
| `expense_name` | The name of the expense. |
| `annual_amount` | The starting annual cost. |
| `start_year` | The first year the expense occurs. |
| `end_year` | The last year the expense occurs. |
| `inflation_category` | The default inflation category. Use **`Healthcare`**, **`General`**, or **`Custom`**. |
| `custom_inflation_rate` | **Optional.** If a rate is entered here (e.g., 0.06), it will **override** the category-based inflation for this one expense. |

---

## Part 3: The Simulation Engine - Calculations & Data

(This section is unchanged as the core logic is stable.)

The program simulates your financial life year by year, modeling key financial events such as Social Security benefits, RMDs, Medicare IRMAA surcharges, tax drag from investments, federal income tax, and inflation.

---

## Part 4: Understanding the Output (Reports & Plots)

The program generates three types of output for each scenario, all saved in the `reports/` directory.

### 4.1 The Summary Report (`summary_report_final_v12.csv`)
This is your high-level dashboard for comparing strategies.

| Column | How to Interpret It |
| :--- | :--- |
| `Scenario Name` | The descriptive name of the strategy being tested. |
| `Total Lifetime Taxes` | The sum of all federal income taxes paid over the entire simulation. A key metric for comparing tax efficiency. |
| `Total IRMAA Paid` | The sum of all Medicare premium surcharges paid. Reveals the hidden costs of high-income years. |
| `Final Portfolio Value`| The total market value of all your accounts at the end of the simulation. A measure of the wealth you preserve or pass on. |
| `Age Portfolio Depleted`| If your money runs out, this shows the age at which it happened. **`N/A` is the goal**—it means your plan was successful. |

### 4.2 Visual Reports (The Plots)
Saved in the `reports/plots/` subdirectory, these images provide an intuitive story of your financial future for each scenario.

*   **Financial Overview Plot (`_overview.png`):** This line chart shows the "big picture."
    *   **Green Line (Total Savings):** The year-end value of your entire portfolio.
    *   **Red Line (Annual Expenses):** Your total inflated spending for the year.
    *   **Interpretation:** Ideally, you want to see the green line staying comfortably above the red line and, preferably, continuing to grow. If the lines converge or cross, it signals a point of financial stress in that scenario.

*   **Portfolio Composition Plot (`_composition.png`):** This stacked area chart gives you a powerful visual breakdown of your savings.
    *   **The Colors:** Each colored area represents a different account type (Cash, Taxable, Traditional, Roth).
    *   **Interpretation:** You can visually track the "withdrawal waterfall" as the model spends down your accounts in the correct order (Cash first, then Taxable, etc.). In Roth conversion scenarios, you can see the orange "Traditional" area shrink while the green "Roth" area grows, providing a clear visual of the conversion strategy in action.

### 4.3 The Detailed Yearly Reports (`_yearly.csv`)
Saved in the `reports/yearly/` subdirectory, these detailed spreadsheets are your primary tool for debugging and deep analysis. They show the "workings" of the simulation for every single year.

| Column | Description & Calculation |
| :--- | :--- |
| `Year`, `[Name] (age)` | The current year and your age in that year. |
| **`AGI_Proxy`** | **Calculated.** Our model's proxy for Adjusted Gross Income. This is the critical number used to determine if your Social Security is taxable. <br> *Calculation:* `Taxable Investment Income + Pension Income + Roth Conversion + Traditional Withdrawal` |
| **`MAGI`** | **Calculated.** Our model's Modified Adjusted Gross Income, used to calculate IRMAA surcharges. <br> *Calculation:* `AGI_Proxy + Total SS` |
| `Pension Income` | The inflated value of any pension for that year. |
| `Total SS`, `[Name] SS` | The inflated Social Security benefits paid out in that year, based on your claiming age. |
| `Total Expenses` | **Calculated.** The total spending for the year. <br> *Calculation:* `Sum of all active, inflated expenses + IRMAA surcharge` |
| `Taxable Investment Income`| **Calculated.** The "tax drag" from your non-retirement accounts. <br> *Calculation:* `Sum of (start-of-year balance * dividend_rate)` for all `Taxable` and `Cash` accounts. |
| `Roth Conversion` | The amount converted from a Traditional to a Roth account in that year. |
| `RMD` | **Calculated.** Your Required Minimum Distribution. It appears only at age 75+. <br> *Calculation:* `Prior year-end Traditional balance / IRS factor for current age` |
| `Federal Taxes` | **Calculated.** Your final tax bill for the year. <br> *Calculation:* Based on your `final_taxable_income` (`AGI_Proxy` + taxable portion of SS) run through the inflated tax brackets after the inflated standard deduction. |
| `IRMAA` | **Calculated.** Your annual Medicare premium surcharge. <br> *Calculation:* Based on your `MAGI` from two years prior. |
| `Total Savings` | **Calculated.** The sum of all account balances at the end of the year. |
| `Cash Balance`, `Taxable Acct Balance`, `Traditional Balance`, `Roth Balance`| **Calculated.** The year-end balance for each specific account type. |

---

## Part 5: Advanced Usage & Maintenance

(This section is unchanged.)

### 5.1 Running New Scenarios
Edit the `SCENARIOS_TO_RUN` list in the `.py` script to test new strategies.

### 5.2 Annual Maintenance Plan
To keep the simulator accurate, you should update its data once a year.

| What to Update | Where to Update | How to Find the Data |
| :--- | :--- | :--- |
| **Account Balances**| `accounts.csv` | Log into your financial institutions. |
| **Tax Brackets** | `BASE_FEDERAL_TAX_BRACKETS` in the `.py` file. | Search online for "IRS income tax brackets for [upcoming year]". |
| **Standard Deduction** | `BASE_FEDERAL_STANDARD_DEDUCTION` in the `.py` file.| Usually announced with the tax brackets. |
| **IRMAA Brackets** | `MEDICARE_IRMAA_BRACKETS` in the `.py` file.| Search online for "Medicare IRMAA brackets for [upcoming year]". |
| **RMD Table** | `IRS_UNIFORM_LIFETIME_TABLE` in the `.py` file.| Check every few years. Search for "IRS Uniform Lifetime Table". |

---

## Part 6: Conclusion

This retirement simulator is a robust tool designed to bring clarity to complex financial decisions. By taking the time to provide accurate input data and to understand the key calculations, you can generate powerful, personalized insights into your financial future. Use it to explore possibilities, stress-test your assumptions, and build confidence in your retirement plan.