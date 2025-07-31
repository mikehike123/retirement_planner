That is an absolutely essential and responsible final addition. Acknowledging a model's assumptions and simplifications is just as important as documenting its features. It ensures that the results are always interpreted with the proper context.

This is the perfect "capstone" to our documentation. Here is the new section.

---

### **New Section for the Documentation**

This section should be added between **Part 3: The Simulation Engine** and **Part 4: Understanding the Output**.

### **Part 3.5: Important Assumptions & Simplifications**

This simulator is a powerful strategic tool, but it is not a perfect representation of the entire U.S. tax code. To keep the model manageable and focused, several important simplifications have been made. It is critical to understand these assumptions when interpreting the results.

#### **1. Taxation of Taxable Account Growth (The Biggest Simplification)**
*   **The Simplification:** The model significantly simplifies how investment returns in `Brokerage` and `Cash` accounts are taxed. Instead of tracking capital gains and dividends separately, it calculates the total estimated growth for the year (`income_on_accounts`) and adds this amount directly to your other ordinary income (pensions, RMDs, taxable Social Security, etc.). This entire amount is then taxed together using the standard federal income tax brackets. The model does not use a separate, lower tax rate for long-term capital gains or qualified dividends.
*   **The Impact:** This approach is **intentionally conservative**. It will likely **overestimate the taxes** you pay in a given year compared to reality, where qualified dividends and long-term capital gains would be taxed at lower rates. Because the growth is taxed annually as income, subsequent withdrawals of principal *or* gains from these accounts are treated as simple transfers and are not taxed again. This abstracts away the need to track cost basis.
*   **Why It's Acceptable:** Because this conservative tax treatment is applied consistently across all scenarios, the *comparison* between them remains valid and meaningful. If a plan is successful under these higher tax assumptions, it will likely be even more successful in the real world.

#### **2. State and Local Taxes**
*   **The Simplification:** The model **does not calculate state or local income taxes**. The `state` parameter in `config.csv` is a placeholder for future development.
*   **The Impact:** The `Total Lifetime Taxes` reported is for **federal taxes only**. Your actual lifetime tax burden will be higher, especially if you live in a high-income-tax state.
*   **How to Mitigate:** You can approximate state taxes by adding a new line item to your `annual_expenses.csv` file called "State Taxes" with your best estimate of the annual cost.

#### **3. Social Security Taxability Thresholds**
*   **The Simplification:** The model uses the lower boundaries of the inflation-adjusted 12% and 22% tax brackets as proxies for the official Social Security taxability thresholds ($32,000 and $44,000 for MFJ, before inflation).
*   **The Impact:** This is a very close and reasonable approximation. Since the official thresholds are also indexed to inflation, using the tax brackets as a stand-in ensures that the trigger points for Social Security taxation rise realistically over time.

#### **4. Single Age Assumption**
*   **The Simplification:** The model assumes both partners are the same age for the purpose of the main simulation loop (`current_age = 63 + i`).
*   **The Impact:** This has a negligible effect on the overall financial outcome. RMDs are based on individual ages, but our model simplifies this to a single age for the lookup. The most important age-related calculations (Social Security claiming and Medicare start) are handled correctly based on the specific ages you define in the scenarios.

Understanding these assumptions is key to using this tool wisely. It is a strategic compass to point you in the right direction, not a GPS to give you a precise dollar amount.

---

### **The Final, Complete Document**

Here is the entire documentation from start to finish with this crucial new section included. This is the definitive user guide for our project.

***

# Retirement Portfolio & Tax Simulator: Documentation (Final Version)

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
├── retirement_model_final.py <-- The main program script.
└── .gitignore              <-- The file that protects your private data on GitHub.
```

### 1.2 Installation (One-Time Setup)
The program runs in a self-contained Anaconda environment and requires the `pandas` and `matplotlib` libraries.

1.  **Open the Anaconda Prompt** from your Windows Start Menu.
2.  **Create the environment** by running this command:
    ```bash
    conda create --name retirement_planner python=3.11 pandas matplotlib
    ```3.  When prompted, type `y` and press Enter.

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
    python retirement_model_final.py
    ```

The program will print its progress and save all reports and plots to the appropriate subdirectories inside the `reports/` folder.

---

## Part 2: The User Guide - Your Input Files

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
| `account_type` | Critical for tax logic. Must be one of: **`Brokerage`**, **`Traditional`**, **`Roth`**, or **`Cash`**. (`Taxable` is also accepted as a synonym for `Brokerage`). |
| `balance` | The starting balance of the account. |
| `annual_growth_rate`| The estimated **TOTAL** annual return for the account. |
| `annual_rate` | The estimated annual rate of return for the account. |

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

The program simulates your financial life year by year, modeling key financial events such as Social Security benefits, RMDs, Medicare IRMAA surcharges, taxes on investment growth, federal income tax, and inflation.

---

## Part 3.5: Important Assumptions & Simplifications

This simulator is a powerful strategic tool, but it is not a perfect representation of the entire U.S. tax code. To keep the model manageable and focused, several important simplifications have been made. It is critical to understand these assumptions when interpreting the results.

#### **1. Federal Tax Calculation (The Biggest Simplification)**
*   **The Simplification:** The model calculates taxes on all income (Pensions, RMDs, taxable Social Security, income from accounts, etc.) using the standard ordinary income tax brackets. It does not have a separate, parallel tax system for long-term capital gains and qualified dividends.
*   **The Impact:** This approach is **intentionally conservative**. It will likely **overestimate the taxes** you pay in a given year compared to reality, where qualified dividends and long-term capital gains from your brokerage account would be taxed at lower rates.
*   **Why It's Acceptable:** Because this conservative tax treatment is applied consistently across all scenarios, the *comparison* between them remains valid and meaningful. If the model shows a plan is successful under these higher tax assumptions, it will be even more successful in the real world.

#### **2. State and Local Taxes**
*   **The Simplification:** The model **does not calculate state or local income taxes**. The `state` parameter in `config.csv` is a placeholder for future development.
*   **The Impact:** The `Total Lifetime Taxes` reported is for **federal taxes only**. Your actual lifetime tax burden will be higher, especially if you live in a high-income-tax state.
*   **How to Mitigate:** You can approximate state taxes by adding a new line item to your `annual_expenses.csv` file called "State Taxes" with your best estimate of the annual cost.

#### **3. Withdrawal of Principal vs. Gains**
*   **The Simplification:** In the simplified model, we assume all growth is taxed annually. The subsequent withdrawal of principal from `Cash` and `Brokerage` accounts is then treated as a non-taxable event.
*   **The Impact:** This is an abstraction of reality. In the real world, you are taxed only on the *profit portion* of any shares you sell (the capital gain). Our model's approach effectively "pre-pays" the tax on the growth each year instead of at the moment of sale. This simplifies the model by eliminating the need to track cost basis for every investment.

#### **4. Social Security Taxability Thresholds**
*   **The Simplification:** The model uses the lower boundaries of the inflation-adjusted 12% and 22% tax brackets as proxies for the official Social Security taxability thresholds ($32,000 and $44,000 for MFJ, before inflation).
*   **The Impact:** This is a very close and reasonable approximation. Since the official thresholds are also indexed to inflation, using the tax brackets as a stand-in ensures that the trigger points for Social Security taxation rise realistically over time.

#### **5. Single Age Assumption**
*   **The Simplification:** The model assumes both partners are the same age for the purpose of the main simulation loop (`current_age = 63 + i`).
*   **The Impact:** This has a negligible effect on the overall financial outcome. RMDs are based on individual ages, but our model simplifies this to a single age for the lookup. The most important age-related calculations (Social Security claiming and Medicare start) are handled correctly based on the specific ages you define in the scenarios.

---

## Part 4: Understanding the Output (Reports & Plots)

The program generates three types of output for each scenario, all saved in the `reports/` directory.

### 4.1 The Summary Report (`summary_report_final.csv`)
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
    *   **The Colors:** Each colored area represents a different account type (Cash, Brokerage, Traditional, Roth).
    *   **Interpretation:** You can visually track the "withdrawal waterfall" as the model spends down your accounts in the correct order (Cash first, then Brokerage, etc.). In Roth conversion scenarios, you can see the orange "Traditional" area shrink while the green "Roth" area grows, providing a clear visual of the conversion strategy in action.

### 4.3 The Detailed Yearly Reports (`_yearly.csv`)
Saved in the `reports/yearly/` subdirectory, these detailed spreadsheets are your primary tool for debugging and deep analysis. They show the "workings" of the simulation for every single year.

| Column | Description & Calculation |
| :--- | :--- |
| `Year`, `[Name] (age)` | The current year and your age in that year. |
| **`Accounts Income`**| **Calculated.** This is the income generated from taxable accounts. It is calculated by summing the `Balance` multiplied by the `annual_rate` for all `Taxable` accounts at the beginning of the year. |
| **`AGI_Proxy`** | **Calculated.** Our model's proxy for Adjusted Gross Income. This is the critical number used to determine if your Social Security is taxable. <br> *Calculation:* `Pension Income` + `Roth Conversion` + `Traditional Withdrawal` + `Accounts Income` |
| **`MAGI`** | **Calculated.** Our model's Modified Adjusted Gross Income, used to calculate IRMAA surcharges. <br> *Calculation:* `AGI_Proxy` - `Traditional Withdrawal` + `Total SS` |
| `Pension Income` | The inflated value of any pension for that year. |
| `Total SS`, `[Name] SS` | The inflated Social Security benefits paid out in that year, based on your claiming age. |
| `Total Expenses` | **Calculated.** The total spending for the year. <br> *Calculation:* `Sum of all active, inflated expenses + IRMAA surcharge` |
| `Roth Conversion` | The amount converted from a Traditional to a Roth account in that year. |
| `RMD` | **Calculated.** Your Required Minimum Distribution. It appears only at age 75+. <br> *Calculation:* `Prior year-end Traditional balance / IRS factor for current age` |
| `Final Taxable Income` | **Calculated.** This is the final taxable income used to calculate the federal tax. <br> *Calculation:* `AGI_Proxy` + (`Total SS` * 0.85) if `MAGI` is in the 22% tax bracket or higher, `AGI_Proxy` + (`Total SS` * 0.50) if `MAGI` is in the 12% tax bracket, or `AGI_Proxy` otherwise. |
| `Tax Ordinary Income` | **Calculated.** This is the tax calculated on the `Final Taxable Income`. <br> *Calculation:* `calculate_federal_tax(Final Taxable Income, filing_status, inflated_brackets, inflated_deduction)` |
| `Federal Taxes` | **Calculated.** Your final federal income tax bill for the year. <br> **Calculation:** This is the final step in the tax waterfall. It is calculated by taking your `final_taxable_income` and applying the progressive tax brackets for the year after subtracting the standard deduction. The code equivalent is: <br> `calculate_federal_tax(final_taxable_income, filing_status, inflated_brackets, inflated_deduction)` |
| `IRMAA` | **Calculated.** Your annual Medicare premium surcharge. <br> *Calculation:* Based on your `MAGI` from two years prior. |
| `Total Savings` | **Calculated.** The sum of all account balances at the end of the year. |
| `Cash Balance`, `Brokerage Balance`, `Traditional Balance`, `Roth Balance`| **Calculated.** The year-end balance for each specific account type. |

---

## Part 5: Advanced Usage & Maintenance

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

---

## Part 7: Future Enhancements

### 7.1 Advanced Taxation Model for Brokerage Accounts

The current model simplifies the taxation of brokerage accounts by treating all returns as ordinary income. While this is a conservative and safe assumption, a more precise model could be implemented in the future to better reflect the U.S. tax code for investments in equities.

**Proposed Change:** Implement a dual-rate tax system that distinguishes between ordinary income and capital gains/qualified dividends.

**Input File Changes (`accounts.csv`):**

To support this, the `accounts.csv` file would be enhanced with additional columns for brokerage accounts:

| Column | Description |
| :--- | :--- |
| `dividend_yield` | The portion of the account's growth that is paid out as dividends. |
| `percent_qualified` | The percentage of those dividends that are "qualified" for lower tax rates. |
| `cost_basis_ratio` | The percentage of the account's value that is original principal (cost basis). This is essential for calculating the taxable gain when shares are sold. |

For `Cash` accounts, these new fields would be left blank.

**Simulation Logic Changes:**

1.  **Separate Income Buckets:** The simulation would maintain two distinct income buckets: one for ordinary income and one for capital gains.
2.  **Dividend Handling:** Annual dividend income would be calculated and split into qualified (taxed at capital gains rates) and non-qualified (taxed as ordinary income).
3.  **Capital Gains on Sale:** When assets are withdrawn from a brokerage account to cover expenses, the model would use the `cost_basis_ratio` to calculate the realized capital gain, which would then be taxed at the appropriate capital gains rate.
4.  **Final Tax Calculation:** The total federal tax for the year would be the sum of the tax calculated on ordinary income and the tax calculated on capital gains, each using their respective tax brackets.

This enhancement would provide a much more accurate picture of tax liability, especially for portfolios with a significant allocation to equities.