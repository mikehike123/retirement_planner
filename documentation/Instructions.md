Of course! That's a critical feature for realistic planning, and it absolutely deserves to be highlighted more prominently. A financial plan isn't static, and modeling temporary expenses is a key part of getting an accurate picture.

I have updated the documentation to emphasize this capability in two key places:

1.  I've added it as a new bullet point in **Part 1: Key Features at a Glance**.
2.  I've added a more descriptive paragraph in **Part 3: The User Guide** under the `annual_expenses.csv` section to explain its practical use.

Here is the final, polished version of the complete documentation.

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

## **Part 1: Key Features at a Glance**

This simulator is more than just a calculator; it's a strategic analysis engine. Here are some of its most powerful features:

*   **Unlimited Scenario Analysis:** You are not limited to a handful of comparisons. The program is designed to run dozens of scenarios at once, allowing you to tweak variables like Social Security claiming ages, Roth conversion amounts, and inflation rates to see a wide spectrum of possible outcomes.
*   **Flexible Expense Modeling:** Life's expenses aren't flat. This tool allows you to define specific **start and end years** for any expense. This is incredibly useful for modeling real-world costs accurately, such as a mortgage that gets paid off, a car loan with a fixed term, or even a one-time major vacation.
*   **Comprehensive Summary Report:** The final output isn't just a single number. The tool generates a clean, consolidated summary report that places all scenarios side-by-side. This report includes not only the final results but also the key input parameters for each scenario, making it easy to see what assumptions drove which outcome.
*   **Key Performance Metrics:** The summary report uses powerful financial metrics to help you judge the success of each strategy, including Final Portfolio Value, inflation-adjusted Present Value, and Compound Annual Growth Rate (CAGR).
*   **"Show Your Work" Transparency:** For every scenario, the simulator produces a detailed year-by-year spreadsheet. This report shows the inner workings of the model, including annual income, expenses, tax calculations, account balances, and more. This transparency is crucial for building confidence in the results.
*   **Powerful Visualizations:** The program generates two publication-quality charts for each scenario that visually represent your financial journey, making complex data immediately understandable.
*   **Conservative by Design:** The model's tax logic is intentionally conservative. A scenario that is successful in this model is highly likely to be successful in the real world.

---

## **IMPORTANT: Disclaimer**

This program is a **modeling and educational tool ONLY**. It is not a substitute for professional financial, tax, or legal advice. The results and scenarios generated are based on the data you provide and the simplified financial models built into the code. All financial decisions have real-world consequences, and you should consult with a qualified professional before taking any action based on the output of this program.

---

## Part 2: Getting Started

### 2.1 Folder Structure
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

### 2.2 Installation (One-Time Setup)
The program runs in a self-contained Anaconda environment and requires the `pandas` and `matplotlib` libraries.

1.  **Open the Anaconda Prompt** from your Windows Start Menu.
2.  **Create the environment** by running this command:
    ```bash
    conda create --name retirement_planner python=3.11 pandas matplotlib
    ```
3.  When prompted, type `y` and press Enter.

### 2.3 Running the Program
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

## Part 3: The User Guide - Your Input Files

The engine is powered by five CSV files located in the `input_files/` directory. The accuracy of the simulation depends entirely on the quality of this data.

### 3.1 `config.csv`
Holds the global settings for the simulation.

| parameter | value | Description |
| :--- | :--- | :--- |
| `start_year` | 2025 | The first year of the simulation. |
| `projection_years`| 35 | The number of years the simulation will run. |
| `federal_filing_status` | Married Filing Jointly | Your tax filing status. **Currently, this is the only supported status.** |
| `state` | California | Your state of residence. (Note: State tax logic is not implemented). |
| `inflation_rate_general`| 0.03 | The default annual inflation rate for most expenses. |
| `inflation_rate_healthcare`| 0.05 | The default annual inflation rate for healthcare. |

### 3.2 `accounts.csv`
Lists all your financial accounts.

| Column | Description |
| :--- | :--- |
| `account_name` | A unique name for each account. |
| `account_type` | Critical for tax logic. Must be one of: **`Brokerage`**, **`Traditional`**, **`Roth`**, or **`Cash`**. (`Taxable` is also accepted as a synonym for `Brokerage`). |
| `balance` | The starting balance of the account. |
| `annual_rate` | The estimated total annual rate of return for the account. |

### 3.3 `income_streams.csv`
For external, non-Social Security income.

| Column | Description |
| :--- | :--- |
| `stream_name` | Name of the income source (e.g., "Pension"). |
| `annual_amount` | The gross annual amount. |
| `start_year` | The year the income begins. |
| `end_year` | The year the income ends. |
| `is_inflation_adjusted` | `TRUE` if it receives a COLA, otherwise `FALSE`. |

### 3.4 `social_security.csv`
Holds your base Social Security data.

| Column | Description |
| :--- | :--- |
| `person_name` | Your names (e.g., "Mike", "Cindy"). |
| `fra_benefit` | The estimated **annual** benefit at your Full Retirement Age (FRA). |
| `fra_age` | Your Full Retirement Age (e.g., 67). |

### 3.5 `annual_expenses.csv`
Lists all your planned expenses.

| Column | Description |
| :--- | :--- |
| `expense_name` | The name of the expense. |
| `annual_amount` | The starting annual cost. |
| `start_year` | The first year the expense occurs. |
| `end_year` | The last year the expense occurs. |
| `inflation_category` | The default inflation category. Use **`Healthcare`**, **`General`**, or **`Custom`**. |
| `custom_inflation_rate` | **Optional.** If a rate is entered here (e.g., 0.06), it will **override** the category-based inflation for this one expense. |

The inclusion of `start_year` and `end_year` columns is particularly powerful. It allows you to model your financial life with greater accuracy by planning for expenses that are not permanent. For example, you can account for a mortgage payment that ends in a specific year, a car loan with a defined term, or special, one-time expenditures like a major trip or home renovation.

---

## Part 4: The Simulation Engine - Calculations & Data

The program simulates your financial life year by year, modeling key financial events such as Social Security benefits, RMDs, Medicare IRMAA surcharges, taxes on investment growth, federal income tax, and inflation.

---

## Part 4.5: Important Assumptions & Simplifications

This simulator is a powerful strategic tool, but it is not a perfect representation of the entire U.S. tax code. To keep the model manageable and focused, several important simplifications have been made. It is critical to understand these assumptions when interpreting the results.

#### **1. Taxation of Taxable Account Growth (The Biggest Simplification)**
*   **The Simplification:** The model significantly simplifies how investment returns in `Brokerage` and `Cash` accounts are taxed. It calculates the total estimated growth for the year (`income_on_accounts`) and adds this amount directly to your other ordinary income to be taxed at standard federal rates. It does not use a separate, lower tax rate for long-term capital gains or qualified dividends.
*   **The Impact:** This approach is **intentionally conservative** and will likely **overestimate your taxes**. Subsequent withdrawals are treated as non-taxable transfers, abstracting away the need to track cost basis.
*   **Why It's Acceptable:** Because this conservative treatment is applied consistently, the *comparison* between scenarios remains valid. A plan that succeeds here will likely be even more successful in reality.

#### **2. State and Local Taxes**
*   **The Simplification:** The model **does not calculate state or local income taxes**.
*   **The Impact:** Your actual lifetime tax burden will be higher if you live in a state with an income tax. You can approximate this by adding "State Taxes" as a line item in your `annual_expenses.csv`.

#### **3. Filing Status and Deductions**
*   **The Simplification:** The model is designed **only for the "Married Filing Jointly" tax status** and **uses only the standard deduction**.
*   **The Impact:** The simulation will be inaccurate for other filing statuses or for those who itemize deductions.

#### **4. Social Security Taxability Thresholds**
*   **The Simplification:** The model uses inflation-adjusted tax bracket boundaries as proxies for the official Social Security taxability thresholds.
*   **The Impact:** This is a very close and reasonable approximation that ensures the trigger points for Social Security taxation rise realistically over time.

#### **5. Single Age Assumption**
*   **The Simplification:** The model uses a single `current_age` for the main simulation loop.
*   **The Impact:** This has a negligible effect on the outcome, as key calculations like Social Security and Medicare are handled correctly based on specific individual ages.

---

## Part 5: Understanding the Output (Reports & Plots)

The program generates three types of output for each scenario, all saved in the `reports/` directory.

### 5.1 The Summary Report (`summary_report_final.csv`)
This is your high-level dashboard for comparing strategies, showing both the inputs and the outcomes for each scenario.

| Column | How to Interpret It |
| :--- | :--- |
| `Scenario Name` | The descriptive name of the strategy being tested. |
| **`SS Claim Ages`** | **(Input)** The claiming ages for both individuals for this scenario. |
| **`General Inflation`**| **(Input)** The general inflation rate used in the simulation. |
| **`Healthcare Inflation`**| **(Input)** The healthcare-specific inflation rate used. |
| `Final Portfolio Value`| **(Output)** The total market value of your accounts at the end of the simulation. |
| `Present Value` | **(Output)** The `Final Portfolio Value` adjusted for inflation, showing its worth in today's dollars. |
| `CAGR` | **(Output)** Compound Annual Growth Rate of your portfolio. |
| `Total Lifetime Taxes` | **(Output)** The sum of all federal income taxes paid. |
| `Total IRMAA Paid` | **(Output)** The sum of all Medicare premium surcharges paid. |
| `Age Portfolio Depleted`| **(Output)** The age at which your money ran out. **`N/A` is the goal.** |

### 5.2 Visual Reports (The Plots)
The visual reports are a highlight of the program, turning complex data into an intuitive story.

*   **Portfolio Composition Plot (`_composition.png`):** This stacked area chart provides a powerful visual breakdown of your savings over time.
    *   **The Colors:** Each colored area represents a different account type: **Cash** (gray), **Brokerage** (blue), **Traditional** (orange), and **Roth** (green).
    *   **Interpretation:** This is the best way to visualize your financial strategy in action. You can see how the model spends down accounts in the correct order or how a Roth conversion strategy shifts assets from the Traditional to the Roth bucket over time.

*   **Financial Overview Plot (`_overview.png`):** This line chart shows the "big picture" of your plan's health.
    *   **Green Line (Total Savings):** The year-end value of your entire portfolio.
    *   **Red Line (Annual Expenses):** Your total inflated spending for the year.
    *   **Interpretation:** This plot answers the fundamental question: "Is my plan on track?" If the green line stays comfortably above the red line, the plan is sustainable.

### 5.3 The Detailed Yearly Reports (`_yearly.csv`)
Saved in the `reports/yearly/` subdirectory, these spreadsheets are your primary tool for deep analysis, showing the "workings" of the simulation for every single year.

| Column | Description |
| :--- | :--- |
| `Year`, `[Name] (age)` | The current year and your age. |
| **`Accounts Income`**| Income generated from `Cash` and `Brokerage` accounts. |
| **`AGI_Proxy`** | The model's Adjusted Gross Income, used for tax calculations. |
| **`MAGI`** | The model's Modified Adjusted Gross Income, used for IRMAA calculations. |
| `Total Expenses` | Sum of all active, inflated expenses plus any IRMAA surcharge. |
| `Federal Taxes` | Your final federal income tax bill for the year. |
| `Total Savings` | The sum of all account balances at year-end. |
| Account Balances | The year-end balance for each specific account type. |

---

## Part 6: Advanced Usage & Maintenance

### 6.1 Running New Scenarios
Edit the `SCENARIOS_TO_RUN` list in the `.py` script to test new strategies.

### 6.2 Annual Maintenance Plan
To keep the simulator accurate, update its data once a year.

| What to Update | Where to Update | How to Find the Data |
| :--- | :--- | :--- |
| **Account Balances**| `accounts.csv` | Log into your financial institutions. |
| **Tax & IRS Data** | The constant dictionaries in the `.py` file. | Search online for the latest IRS tax brackets, standard deduction, IRMAA brackets, and RMD tables. |

---

## Part 7: Conclusion

This retirement simulator is a robust tool designed to bring clarity to complex financial decisions. By taking the time to provide accurate input data and to understand its key calculations and features, you can generate powerful, personalized insights into your financial future.

---

## Part 8: Future Enhancements

The simulator is highly capable, but future versions could be enhanced in several key areas:
*   **Advanced Taxation Model:** Implement a dual-rate system to handle long-term capital gains and qualified dividends at their preferential rates.
*   **Flexible Filing Status & Itemized Deductions:** Expand the tax engine to support all filing statuses (Single, etc.) and to accommodate itemized deductions for users who do not take the standard deduction.