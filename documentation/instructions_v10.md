# Retirement Portfolio & Tax Simulator: Documentation (Version v10)

## Introduction

This document provides a complete guide to the Python-based retirement simulator we have built. The program is designed as a powerful, personal modeling tool to help retirees make strategic financial decisions by comparing the long-term outcomes of different scenarios.

The primary purpose of this tool is to provide data-driven answers to critical retirement questions, such as:
*   When is the optimal time to claim Social Security?
*   What is the long-term impact of performing Roth conversions?
*   How does my plan hold up under different inflation and market return scenarios?
*   What is the lifetime cost of taxes and Medicare surcharges in different strategies?

This document will guide you through the setup, usage, maintenance, and interpretation of the simulator.

---

## **Part 1: Key Features at a Glance**

This simulator is more than just a calculator; it's a strategic analysis engine. Here are some of its most powerful features:

*   **Unlimited Scenario Analysis:** You are not limited to a handful of comparisons. The program is designed to run dozens of scenarios at once, allowing you to tweak variables like Social Security claiming ages, Roth conversion amounts, and baseline assumptions.
*   **Historical Stress Testing:** Test your plan's resilience by running it against real-world historical data from challenging economic periods, such as the 1970s stagflation or the post-2008 zero-interest-rate environment.
*   **Advanced Asset Modeling:** The model accurately simulates portfolios with mixed assets. It correctly handles accounts with different allocations of stocks and cash, models the long-term drift of non-rebalanced accounts, and allows for custom, fixed-rate assets like I-Bonds or CDs.
*   **Flexible Expense Modeling:** Life's expenses aren't flat. This tool allows you to define specific **start and end years** for any expense. This is incredibly useful for modeling real-world costs accurately, such as a mortgage that gets paid off or a car loan with a fixed term.
*   **Comprehensive Summary Report:** The final output is a clean, consolidated report that places all scenarios side-by-side, making it easy to see which assumptions drove which outcome.
*   **Key Performance Metrics:** The summary report uses powerful financial metrics to judge success, including Final Portfolio Value, inflation-adjusted Present Value, and Compound Annual Growth Rate (CAGR).
*   **"Show Your Work" Transparency:** For every scenario, the simulator produces a detailed year-by-year spreadsheet showing all the inner workings of the model. This transparency is crucial for building confidence in the results.
*   **Powerful Visualizations:** The program generates two publication-quality charts for each scenario that visually represent your financial journey.
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
├── input_files_v10/        <-- Your 5 personal data files go here.
│   ├── accounts.csv
│   ├── annual_expenses.csv
│   ├── config.csv
│   ├── income_streams.csv
│   └── social_security.csv
├── reports/                <-- The program will save its output files here.
│   ├── plots/
│   └── yearly/
├── retirement_model_v10.py <-- The main program script.
└── .gitignore              <-- (Optional) Protects your private data on GitHub.
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

1.  **Open the Anaconda Prompt**.
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
    python retirement_model_v10.py
    ```

The program will print its progress and save all reports and plots to the appropriate subdirectories inside the `reports/` folder.

---

## Part 3: The User Guide - Your Input Files

The engine is powered by five CSV files located in the `input_files_v10/` directory. The accuracy of the simulation depends entirely on the quality of this data.

### 3.1 `config.csv`
Holds the global settings and baseline assumptions for the simulation.

| parameter | value | Description |
| :--- | :--- | :--- |
| `start_year` | 2025 | The first year of the simulation. |
| `projection_years`| 35 | The number of years the simulation will run. |
| `federal_filing_status` | Married Filing Jointly | Your tax filing status. **Currently, this is the only supported status.** |
| `inflation_rate_general`| 0.03 | The default long-term inflation rate for most expenses. |
| `inflation_rate_healthcare`| 0.05 | The default long-term inflation rate for healthcare expenses. |
| `baseline_equity_return`| 0.07 | Your long-term expected annual return for **equity** investments. |
| `baseline_cash_return`| 0.02 | Your long-term expected annual return for **cash** investments. |

### 3.2 `accounts.csv`
Lists all your financial accounts and their asset composition. This is the most important input file.

| Column | Description |
| :--- | :--- |
| `account_name` | A unique name for each account or portion of an account. |
| `account_type` | Critical for tax logic. Must be one of: **`brokerage`**, **`traditional`**, **`roth`**, or **`cash`**. (`taxable` is also accepted as a synonym for `brokerage`). |
| `balance` | The starting balance of the account (or portion). |
| `asset_class` | Determines which rate of return to use. Must be one of: **`equity`**, **`cash`**, or **`custom`**. |
| `custom_annual_rate` | **Only used if `asset_class` is `custom`**. Enter a fixed rate of return (e.g., 0.045 for an I-Bond). Leave blank otherwise. |

#### Important Concept: Modeling Non-Rebalanced Accounts
A key feature of this model is its ability to simulate the long-term "drift" of accounts that are not rebalanced. If you have a single real-world account with a mix of assets (e.g., a 60/40 IRA), you should model it as **two separate lines** in the CSV file.

**Example:** A single $100,000 Roth IRA that is 60% stocks and 40% cash and is **not rebalanced**.

```csv
account_name,account_type,balance,asset_class,custom_annual_rate
Jane's Roth (Stocks),roth,60000,equity,
Jane's Roth (Cash),roth,40000,cash,
```
The simulator will grow these two lines independently at their respective market rates, accurately capturing how the stock portion will likely grow to dominate the account over time. The withdrawal logic will still correctly treat both lines as part of the unified 'roth' bucket.

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
| `inflation_category` | The default inflation category. Use **`Healthcare`** or **`General`**. |
| `custom_inflation_rate` | **Optional.** If a rate is entered here (e.g., 0.0), it will **override** the category-based inflation for this one expense (perfect for a fixed mortgage). |

### 3.6 Sample Input Files
Here are five examples of what your input CSV files might look like for a hypothetical couple, Jack and Jane.

#### **`config.csv`**
```csv
parameter,value
start_year,2025
projection_years,35
federal_filing_status,Married Filing Jointly
inflation_rate_general,0.03
inflation_rate_healthcare,0.05
baseline_equity_return,0.07
baseline_cash_return,0.025
```

#### **`accounts.csv`**
This example demonstrates all the key features: 100% equity, 100% cash, a custom rate for I-Bonds, and a non-rebalanced Roth IRA split into two components.
```csv
account_name,account_type,balance,asset_class,custom_annual_rate
Jack 401k,traditional,450000,equity,
Joint Savings,cash,100000,cash,
Jane Roth (I-Bonds),roth,25000,custom,0.045
Jane Roth (Stocks),roth,140000,equity,
Jane Roth (Cash),roth,35000,cash,
```

#### **`income_streams.csv`**
```csv
stream_name,annual_amount,start_year,end_year,is_inflation_adjusted
Jack Pension,15000,2027,2060,TRUE
```

#### **`social_security.csv`**
```csv
person_name,fra_benefit,fra_age
Jack,36000,67
Jane,24000,67
```

#### **`annual_expenses.csv`**
```csv
expense_name,annual_amount,start_year,end_year,inflation_category,custom_inflation_rate
General Living,60000,2025,2060,General,
Healthcare,12000,2025,2060,Healthcare,
Mortgage,24000,2025,2035,General,0.0
European Vacation,15000,2028,2028,General,
```---

## Part 4: The Simulation Engine - Calculations & Data

The program simulates your financial life year by year, using a unified growth model.

### 4.1 How Growth is Calculated
The engine is sophisticated and handles all scenarios consistently. For each year of the simulation:
1.  It first determines the market rates for stocks and cash for that year. It pulls these either from a **historical data set** (for a stress test) or from the **baseline assumptions** in your `config.csv`.
2.  Then, for each account, it looks at the `asset_class` column to decide which rate to apply:
    *   If `equity`, it uses the stock market return.
    *   If `cash`, it uses the cash return.
    *   If `custom`, it ignores the market returns and uses the `custom_annual_rate` you provided for that specific account.

This structure gives you complete control over how each component of your portfolio behaves under different economic conditions.

---

## Part 4.5: Important Assumptions & Simplifications

This simulator is a powerful strategic tool, but it is not a perfect representation of the entire U.S. tax code. To keep the model manageable and focused, several important simplifications have been made.

#### **1. Taxation of Taxable Account Growth (The Biggest Simplification)**
*   **The Simplification:** The model calculates the total estimated growth for the year in `brokerage` and `cash` accounts and adds this amount directly to your ordinary income. It does not use a separate, lower tax rate for long-term capital gains.
*   **The Impact:** This approach is **intentionally conservative** and will likely **overestimate your taxes**.
*   **Why It's Acceptable:** Because this conservative treatment is applied consistently, the *comparison* between scenarios remains valid.

#### **2. State and Local Taxes**
*   **The Simplification:** The model **does not calculate state or local income taxes**.
*   **The Impact:** Your actual tax burden will be higher in states with an income tax. You can approximate this by adding "State Taxes" as an expense in `annual_expenses.csv`.

#### **3. Filing Status and Deductions**
*   **The Simplification:** The model is designed **only for "Married Filing Jointly"** and **uses only the standard deduction**. It is inaccurate for other statuses or for itemizers.

#### **4. Social Security Taxability Thresholds**
*   **The Simplification:** The model uses inflation-adjusted tax bracket boundaries as proxies for the official Social Security taxability thresholds. This is a very close and reasonable approximation.

#### **5. Single Age Assumption**
*   **The Simplification:** The model uses a single `current_age` for the main simulation loop. This has a negligible effect on the outcome.

---

## Part 5: Understanding the Output (Reports & Plots)

### 5.1 The Summary Report (`summary_report_final.csv`)
This is your high-level dashboard for comparing strategies.

| Column | How to Interpret It |
| :--- | :--- |
| `Scenario Name` | The descriptive name of the strategy being tested. |
| `Final Portfolio Value`| **(Output)** The total market value of all accounts at the end of the simulation. |
| `Present Value` | **(Output)** The `Final Portfolio Value` adjusted for inflation, showing its worth in today's dollars. This is a key metric for comparing scenarios with different inflation rates. |
| `CAGR` | **(Output)** The Compound Annual Growth Rate of your portfolio. |
| `Total Lifetime Taxes` | **(Output)** The sum of all federal income taxes paid over the entire simulation. |
| `Total IRMAA Paid` | **(Output)** The sum of all Medicare premium surcharges paid. |
| `Age Portfolio Depleted`| **(Output)** The age at which your money ran out. **`N/A` is the goal.** |

### 5.2 Visual Reports (The Plots)
*   **Portfolio Composition Plot (`_composition.png`):** A stacked area chart showing the value of your **Cash** (gray), **Brokerage** (blue), **Traditional** (orange), and **Roth** (green) accounts over time. This is the best way to visualize your financial strategy in action.
*   **Financial Overview Plot (`_overview.png`):** A line chart showing your **Total Savings** (green line) versus your **Total Annual Expenses** (red line). If the green line stays comfortably above the red line, the plan is sustainable.

### 5.3 The Detailed Yearly Reports (`_yearly.csv`)
Saved in the `reports/yearly/` subdirectory, these spreadsheets are your primary tool for deep analysis, showing the "workings" of the simulation for every single year.

---

## Part 6: Advanced Usage & Maintenance

### 6.1 Running New Scenarios
Edit the `SCENARIOS_TO_RUN` list in the `retirement_model_final.py` script to test new strategies. You can add new historical data sets or tweak the parameters of existing scenarios.

### 6.2 Annual Maintenance Plan
To keep the simulator accurate, update its data once a year.

| What to Update | Where to Update | How to Find the Data |
| :--- | :--- | :--- |
| **Account Balances**| `accounts.csv` | Log into your financial institutions. |
| **Baseline Returns**| `config.csv` | Review your long-term expectations for stocks and cash. |
| **Tax & IRS Data** | The constant dictionaries in the `.py` file. | Search online for the latest IRS tax brackets, standard deduction, IRMAA brackets, and RMD tables. |

---

## Part 7: Conclusion

This retirement simulator is a robust tool designed to bring clarity to complex financial decisions. By taking the time to provide accurate input data and to understand its key calculations and features, you can generate powerful, personalized insights into your financial future.

---

## Part 8: Future Enhancements

*   **Advanced Taxation Model:** Implement a dual-rate system to handle long-term capital gains.
*   **Flexible Filing Status & Itemized Deductions:** Expand the tax engine to support all filing statuses and itemized deductions.