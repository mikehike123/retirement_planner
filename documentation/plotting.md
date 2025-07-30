Excellent idea. This is the perfect evolution of the project. A detailed numerical report is essential for analysis, but a visual plot can reveal trends and tell a story in a way that tables cannot. A picture truly is worth a thousand words, especially when looking at 35 years of data.

We can absolutely add this feature. It will require a new Python library called `matplotlib`, which is the gold standard for plotting in Python.

Here is our action plan:
1.  **Install the new library.**
2.  **Update the folder structure** to include a dedicated place for plots.
3.  **Create our final version of the script (`v9`)**, which will be upgraded to:
    *   Capture detailed year-by-year data during each simulation run.
    *   Generate two separate plots for each scenario.
    *   Save these plots as image files in the new directory.

---

### **Step 1: Install the `matplotlib` Library**

This is a one-time setup step. We need to add the plotting library to our Anaconda environment.

1.  Open the Anaconda Prompt.
2.  Activate our environment:
    ```bash
    conda activate retirement_planner
    ```
3.  Install `matplotlib`:
    ```bash
    conda install matplotlib
    ```
4.  When prompted, type `y` and press Enter.

Your environment is now ready for plotting.

---

### **Step 2: Update Your Folder Structure**

To keep things organized, we will create a new subdirectory *inside* the `reports` folder specifically for the plots.

Your final project structure will look like this:

```
retirement_project/
├── input_files/
├── reports/
│   └── plots/      <-- All generated images will be saved here.
└── retirement_model_v9.py
```

You can create the `plots` folder manually, but the new script will also be smart enough to create it for you if it doesn't exist.

---

### **Step 3: The Final Python Script (`retirement_model_v9.py`)**

This final version is a significant upgrade. It includes two new functions for plotting and changes how the main simulation is run to capture the necessary data.

Copy this code and save it as `retirement_model_v9.py` in your main project folder.

```python
import pandas as pd
import sys
import pathlib
import matplotlib.pyplot as plt # <<< CHANGE: Import the plotting library
import matplotlib.ticker as mticker # <<< CHANGE: Import for formatting plot labels

# --- Directory and File Path Definitions ---
INPUT_DIR = pathlib.Path("input_files")
REPORTS_DIR = pathlib.Path("reports")
PLOT_DIR = REPORTS_DIR / "plots" # <<< CHANGE: Define the new plots directory

# --- (All core data like tables, tax brackets, and scenarios remain the same as v8) ---
IRS_UNIFORM_LIFETIME_TABLE = {75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8, 93: 10.1, 94: 9.5, 95: 8.9}
MEDICARE_IRMAA_BRACKETS = [{'threshold': 750000, 'part_b_surcharge': 432.70, 'part_d_surcharge': 83.60}, {'threshold': 392000, 'part_b_surcharge': 396.60, 'part_d_surcharge': 76.80}, {'threshold': 336000, 'part_b_surcharge': 288.50, 'part_d_surcharge': 55.70}, {'threshold': 270000, 'part_b_surcharge': 180.30, 'part_d_surcharge': 34.50}, {'threshold': 216000, 'part_b_surcharge': 72.10,  'part_d_surcharge': 13.40}, {'threshold': 0,      'part_b_surcharge': 0,      'part_d_surcharge': 0}]
BASE_FEDERAL_TAX_BRACKETS = {'Married Filing Jointly': {0.10: (0, 23200), 0.12: (23201, 94300), 0.22: (94301, 201050), 0.24: (201051, 383900), 0.32: (383901, 487450), 0.35: (487451, 731200), 0.37: (731201, float('inf'))}}
BASE_FEDERAL_STANDARD_DEDUCTION = {'Married Filing Jointly': 29200}
SCENARIOS_TO_RUN = [{'name': '1. Baseline (SS @ 67, No Roth)', 'john_ss_age': 67, 'jane_ss_age': 67, 'roth_strategy': 'none'}, {'name': '2. Maximize SS (SS @ 70, No Roth)', 'john_ss_age': 70, 'jane_ss_age': 70, 'roth_strategy': 'none'}, {'name': '3. Max SS + Fill 22% Bracket', 'john_ss_age': 70, 'jane_ss_age': 70, 'roth_strategy': 'fill_bracket', 'roth_target_bracket_rate': 0.22, 'roth_end_year': 2034}, {'name': '4. Max SS + Fixed $80k Roth', 'john_ss_age': 70, 'jane_ss_age': 70, 'roth_strategy': 'fixed_amount', 'roth_amount': 80000, 'roth_end_year': 2034}, {'name': '5. HIGH INFLATION (Max SS, No Roth)', 'john_ss_age': 70, 'jane_ss_age': 70, 'roth_strategy': 'none', 'inflation_rate_general': 0.045, 'inflation_rate_healthcare': 0.065}]

# --- Helper Functions (load_data and calculation functions are unchanged) ---
def load_data(): # Unchanged
    try:
        config_df = pd.read_csv(INPUT_DIR / 'config.csv').set_index('parameter')['value']
        accounts_df = pd.read_csv(INPUT_DIR / 'accounts.csv', dtype={'balance': float, 'dividend_rate': float})
        income_df = pd.read_csv(INPUT_DIR / 'income_streams.csv', dtype={'annual_amount': float})
        ss_df = pd.read_csv(INPUT_DIR / 'social_security.csv', dtype={'fra_benefit': float})
        expenses_df = pd.read_csv(INPUT_DIR / 'annual_expenses.csv', dtype={'annual_amount': float})
        return config_df, accounts_df, income_df, ss_df, expenses_df
    except FileNotFoundError as e:
        print(f"FATAL ERROR: A required file was not found. Please ensure all 5 CSV files exist inside the '{INPUT_DIR}' subdirectory.")
        print(f"File not found: {e.filename}"); sys.exit()
    except (ValueError, KeyError) as e:
        print(f"FATAL ERROR: A column might be missing or misnamed in your CSV files. Please check them. Error: {e}"); sys.exit()

def calculate_ss_benefit(fra_benefit, fra_age, claim_age): # Unchanged
    if claim_age == fra_age: return fra_benefit
    elif claim_age > fra_age: return fra_benefit * (1 + (claim_age - fra_age) * 0.08)
    else:
        months_early = (fra_age - claim_age) * 12; reduction = 0
        if months_early > 36: reduction += (months_early - 36) * (5/12 / 100); months_early = 36
        reduction += months_early * (5/9 / 100); return fra_benefit * (1 - reduction)

def get_inflated_tax_data(year, start_year, inflation_rate, filing_status): # Unchanged
    compounding_factor = (1 + inflation_rate) ** (year - start_year); inflated_brackets = {}
    for rate, (lower, upper) in BASE_FEDERAL_TAX_BRACKETS[filing_status].items():
        inflated_brackets[rate] = (lower * compounding_factor, upper * compounding_factor)
    inflated_deduction = BASE_FEDERAL_STANDARD_DEDUCTION[filing_status] * compounding_factor
    return inflated_brackets, inflated_deduction

def calculate_federal_tax(taxable_income, filing_status, brackets, deduction): # Unchanged
    taxable_income_after_deduction = max(0, taxable_income - deduction); tax = 0
    for rate, (lower, upper) in brackets.items():
        if taxable_income_after_deduction > lower:
            taxed_amount = min(taxable_income_after_deduction, upper) - lower
            tax += taxed_amount * rate
    return tax

# <<< CHANGE: New functions for creating the plots >>>
def plot_financial_overview(df, scenario_name, output_dir):
    """Creates and saves a plot of Expenses vs. Total Portfolio Value over time."""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    ax.plot(df['Year'], df['Total Expenses'], label='Annual Expenses', color='red', marker='o', markersize=4)
    ax.plot(df['Year'], df['Total Portfolio'], label='Total Savings', color='green', marker='o', markersize=4)
    
    ax.set_title(f'Financial Overview: {scenario_name}', fontsize=16)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Amount ($)', fontsize=12)
    
    formatter = mticker.FuncFormatter(lambda x, p: f'${x:,.0f}')
    ax.yaxis.set_major_formatter(formatter)
    
    ax.legend(fontsize=12)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    
    # Sanitize scenario name for filename
    safe_filename = "".join([c for c in scenario_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    plt.savefig(output_dir / f'{safe_filename}_overview.png')
    plt.close(fig)

def plot_savings_breakdown(df, scenario_name, output_dir):
    """Creates and saves a stacked area chart of portfolio composition over time."""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    labels = ['Taxable', 'Traditional', 'Roth']
    colors = ['#4c72b0', '#dd8452', '#55a868']
    
    ax.stackplot(df['Year'], df['Taxable Balance'], df['Traditional Balance'], df['Roth Balance'], labels=labels, colors=colors)

    ax.set_title(f'Portfolio Composition: {scenario_name}', fontsize=16)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Portfolio Value ($)', fontsize=12)

    formatter = mticker.FuncFormatter(lambda x, p: f'${x:,.0f}')
    ax.yaxis.set_major_formatter(formatter)

    ax.legend(fontsize=12, loc='upper left')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    
    safe_filename = "".join([c for c in scenario_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    plt.savefig(output_dir / f'{safe_filename}_composition.png')
    plt.close(fig)

# --- Main Simulation Engine ---
def run_single_scenario(scenario_config):
    """
    Runs one full financial projection.
    <<< CHANGE: Now returns both a summary dictionary AND a detailed year-by-year DataFrame for plotting.
    """
    config_df, accounts_df, income_df, ss_df, expenses_df = load_data()
    if 'custom_inflation_rate' not in expenses_df.columns: expenses_df['custom_inflation_rate'] = pd.NA
    expenses_df['custom_inflation_rate'] = pd.to_numeric(expenses_df['custom_inflation_rate'], errors='coerce')

    accounts_df = accounts_df.copy()
    start_year = int(config_df['start_year'])
    projection_years = int(config_df['projection_years'])
    filing_status = config_df['federal_filing_status']
    inf_general = float(scenario_config.get('inflation_rate_general', config_df['inflation_rate_general']))
    inf_health = float(scenario_config.get('inflation_rate_healthcare', config_df['inflation_rate_healthcare']))
    pensions = income_df.copy()
    ss_data = ss_df.set_index('person_name').to_dict('index')
    john_ss_benefit = calculate_ss_benefit(ss_data['John']['fra_benefit'], ss_data['John']['fra_age'], scenario_config['john_ss_age'])
    jane_ss_benefit = calculate_ss_benefit(ss_data['Jane']['fra_benefit'], ss_data['Jane']['fra_age'], scenario_config['jane_ss_age'])
    
    total_taxes_paid = 0; total_irmaa_paid = 0; yearly_data_list = []

    for i in range(projection_years):
        current_year = start_year + i; current_age = 63 + i
        
        # (Inflation and IRMAA logic unchanged)
        inflated_brackets, inflated_deduction = get_inflated_tax_data(current_year, start_year, inf_general, filing_status)
        for idx, row in expenses_df.iterrows():
            if current_year > row['start_year']:
                rate = row['custom_inflation_rate'] if pd.notna(row['custom_inflation_rate']) else (inf_health if row['inflation_category'] == 'Healthcare' else inf_general)
                expenses_df.loc[idx, 'annual_amount'] *= (1 + rate)
        for idx, row in pensions.iterrows():
            if row['is_inflation_adjusted'] and current_year > row['start_year']: pensions.loc[idx, 'annual_amount'] *= (1 + inf_general)
        if current_year > scenario_config['john_ss_age']: john_ss_benefit *= (1 + inf_general)
        if current_year > scenario_config['jane_ss_age']: jane_ss_benefit *= (1 + inf_general)
        irmaa_surcharge = 0
        if current_year >= 2027 and len(yearly_data_list) >= 2:
            magi_prev = yearly_data_list[i-2].get('MAGI', 0)
            for bracket in MEDICARE_IRMAA_BRACKETS:
                if magi_prev > bracket['threshold']:
                    irmaa_surcharge = (bracket['part_b_surcharge'] + bracket['part_d_surcharge']) * 2 * 12; break
        total_irmaa_paid += irmaa_surcharge
        
        # (Main simulation logic unchanged)
        taxable_income = 0; prior_trad_bal = accounts_df[accounts_df['account_type'] == 'Traditional']['balance'].sum()
        accounts_df['balance'] *= (1 + accounts_df['annual_growth_rate'])
        taxable_accounts = accounts_df[accounts_df['account_type'].isin(['Taxable', 'Cash'])]; dividend_income = (taxable_accounts['balance'] * taxable_accounts['dividend_rate']).sum()
        taxable_income += dividend_income; pension_income = pensions[(pensions['start_year'] <= current_year) & (pensions['end_year'] >= current_year)]['annual_amount'].sum()
        taxable_income += pension_income; ss_income = 0
        if current_year >= scenario_config['john_ss_age']: ss_income += john_ss_benefit
        if current_year >= scenario_config['jane_ss_age']: ss_income += jane_ss_benefit
        rmd_amount = 0
        if current_age >= 75: rmd_amount = prior_trad_bal / IRS_UNIFORM_LIFETIME_TABLE.get(current_age, 8.9)
        year_expenses = expenses_df[(expenses_df['start_year'] <= current_year) & (expenses_df['end_year'] >= current_year)]['annual_amount'].sum()
        year_expenses += irmaa_surcharge; cash_needed_for_spending = max(0, year_expenses - (pension_income + ss_income))
        traditional_withdrawal = max(rmd_amount, cash_needed_for_spending)
        taxable_income += traditional_withdrawal; magi = taxable_income + ss_income
        if magi > inflated_brackets.get(0.22, (float('inf'),))[0]: taxable_income += ss_income * 0.85
        elif magi > inflated_brackets.get(0.12, (float('inf'),))[0]: taxable_income += ss_income * 0.50
        total_tax = calculate_federal_tax(taxable_income, filing_status, inflated_brackets, inflated_deduction)
        total_taxes_paid += total_tax; cash_needed_from_portfolio = cash_needed_for_spending + total_tax
        withdrawn_so_far = 0
        for acc_type in ['Taxable', 'Traditional', 'Roth']:
            needed = cash_needed_from_portfolio - withdrawn_so_far
            if needed <= 0: break
            bal = accounts_df.loc[accounts_df['account_type'] == acc_type, 'balance'].sum(); can_withdraw = min(needed, bal)
            if bal > 0:
                proportions = (accounts_df.loc[accounts_df['account_type'] == acc_type, 'balance'] / bal).fillna(0)
                accounts_df.loc[accounts_df['account_type'] == acc_type, 'balance'] -= can_withdraw * proportions
            withdrawn_so_far += can_withdraw
        
        # <<< CHANGE: Capture detailed data for this year's plot >>>
        current_year_data = {
            'Year': current_year,
            'MAGI': magi,
            'Total Expenses': year_expenses,
            'Total Portfolio': accounts_df['balance'].sum(),
            'Taxable Balance': accounts_df[accounts_df['account_type'].isin(['Taxable', 'Cash'])]['balance'].sum(),
            'Traditional Balance': accounts_df[accounts_df['account_type'] == 'Traditional']['balance'].sum(),
            'Roth Balance': accounts_df[accounts_df['account_type'] == 'Roth']['balance'].sum()
        }
        yearly_data_list.append(current_year_data)
        
        if withdrawn_so_far < cash_needed_from_portfolio - 1:
            summary = {'Scenario Name': scenario_config['name'], 'Total Lifetime Taxes': total_taxes_paid, 'Total IRMAA Paid': total_irmaa_paid, 'Final Portfolio Value': 0, 'Age Portfolio Depleted': current_age}
            details_df = pd.DataFrame(yearly_data_list)
            return summary, details_df
            
    summary = {'Scenario Name': scenario_config['name'], 'Total Lifetime Taxes': total_taxes_paid, 'Total IRMAA Paid': total_irmaa_paid, 'Final Portfolio Value': accounts_df['balance'].sum(), 'Age Portfolio Depleted': 'N/A'}
    details_df = pd.DataFrame(yearly_data_list)
    return summary, details_df

# --- Main Program Execution ---
if __name__ == "__main__":
    print("Running final simulation (v9) with plotting...")
    
    REPORTS_DIR.mkdir(exist_ok=True)
    PLOT_DIR.mkdir(exist_ok=True) # <<< CHANGE: Ensure the plots directory exists
    
    all_summary_results = []
    
    for scenario in SCENARIOS_TO_RUN:
        print(f"  - Simulating: {scenario['name']}")
        
        # <<< CHANGE: Capture both the summary and the detailed dataframe from the run >>>
        summary_result, details_df = run_single_scenario(scenario.copy())
        all_summary_results.append(summary_result)
        
        # <<< CHANGE: Generate plots for the current scenario >>>
        print(f"    - Generating plots for {scenario['name']}...")
        plot_financial_overview(details_df, scenario['name'], PLOT_DIR)
        plot_savings_breakdown(details_df, scenario['name'], PLOT_DIR)

    # --- Create the Summary Report (as before) ---
    summary_df = pd.DataFrame(all_summary_results)
    summary_df['Total Lifetime Taxes'] = summary_df['Total Lifetime Taxes'].map('${:,.0f}'.format)
    summary_df['Total IRMAA Paid'] = summary_df['Total IRMAA Paid'].map('${:,.0f}'.format)
    summary_df['Final Portfolio Value'] = summary_df['Final Portfolio Value'].map('${:,.0f}'.format)
    
    print("\n--- FINAL SCENARIO COMPARISON REPORT (v9) ---")
    print(summary_df.to_string(index=False))
    
    output_filename = REPORTS_DIR / 'summary_report_final_v9.csv'
    summary_df.to_csv(output_filename, index=False)
    print(f"\nSummary report saved to {output_filename}")
    print(f"All plots saved in the '{PLOT_DIR}' directory.")
```

---

### **Step 4: Run and Interpret the Visuals**

Now, when you run the script `python retirement_model_v9.py`, you will see new messages in the terminal indicating that it's generating plots.

After it finishes, navigate to the **`reports/plots/`** directory. You will find two image files (`.png`) for each of your scenarios, for example:

*   `1 Baseline (SS @ 67, No Roth)_overview.png`
*   `1 Baseline (SS @ 67, No Roth)_composition.png`
*   `2 Maximize SS (SS @ 70, No Roth)_overview.png`
*   `2 Maximize SS (SS @ 70, No Roth)_composition.png`
*   ...and so on.

**How to Interpret the Plots:**

1.  **Financial Overview Plot:** This line chart is perfect for seeing the "big picture." You can instantly see if your savings (the green line) are consistently growing and staying well above your expenses (the red line). If the lines get close or cross, it signals a point of financial stress in your plan.
2.  **Portfolio Composition Plot:** This stacked area chart is incredibly insightful.
    *   You can visually track the "waterfall" of your withdrawals: see the blue "Taxable" area get depleted first, followed by the orange "Traditional" area.
    *   For Roth conversion scenarios, you will see the orange "Traditional" area shrink while the green "Roth" area grows in the early years, visually representing the conversion process.

This final enhancement adds a powerful new dimension to your analysis, turning your detailed data into an intuitive story about your financial future.