import pandas as pd
import sys
import pathlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import shutil

# --- Directory and File Path Definitions ---
INPUT_DIR = pathlib.Path("input_files")
REPORTS_DIR = pathlib.Path("reports")
PLOT_DIR = REPORTS_DIR / "plots"
YEARLY_DIR = REPORTS_DIR / "yearly"

# --- Core Financial Logic & Data (Base Year: 2025) ---
IRS_UNIFORM_LIFETIME_TABLE = {
    75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1, 80: 20.2,
    81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2,
    87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8,
    93: 10.1, 94: 9.5, 95: 8.9
}
MEDICARE_IRMAA_BRACKETS = [
    {'threshold': 750000, 'part_b_surcharge': 432.70, 'part_d_surcharge': 83.60},
    {'threshold': 392000, 'part_b_surcharge': 396.60, 'part_d_surcharge': 76.80},
    {'threshold': 336000, 'part_b_surcharge': 288.50, 'part_d_surcharge': 55.70},
    {'threshold': 270000, 'part_b_surcharge': 180.30, 'part_d_surcharge': 34.50},
    {'threshold': 216000, 'part_b_surcharge': 72.10,  'part_d_surcharge': 13.40},
    {'threshold': 0,      'part_b_surcharge': 0,      'part_d_surcharge': 0}
]
BASE_FEDERAL_TAX_BRACKETS = {
    'Married Filing Jointly': {
        0.10: (0, 23200), 0.12: (23201, 94300), 0.22: (94301, 201050),
        0.24: (201051, 383900), 0.32: (383901, 487450), 0.35: (487451, 731200),
        0.37: (731201, float('inf'))
    }
}
BASE_FEDERAL_STANDARD_DEDUCTION = {'Married Filing Jointly': 29200}

# --- Scenarios to Run ---
SCENARIOS_TO_RUN = [
    {
        'name': '1. Baseline (SS @ 67, No Roth)',
        'Mike_ss_age': 67, 'Cindy_ss_age': 67, 'roth_strategy': 'none',
    },
    {
        'name': '2. Baseline (SS @ 67, Roth $50K)',
        'Mike_ss_age': 67, 'Cindy_ss_age': 67, 'roth_strategy': 'till_2028',
        'roth_amount': 50000, 'roth_end_year': 2028
    },
    {
        'name': '3. Maximize SS (SS @ 70, No Roth)',
        'Mike_ss_age': 70, 'Cindy_ss_age': 70, 'roth_strategy': 'none',
    },
    {
        'name': '4. Max SS + Fill 22% Bracket',
        'Mike_ss_age': 70, 'Cindy_ss_age': 70, 'roth_strategy': 'fill_bracket',
        'roth_target_bracket_rate': 0.22, 'roth_end_year': 2034
    },
    {
        'name': '5. Max SS + Fixed $80k Roth',
        'Mike_ss_age': 70, 'Cindy_ss_age': 70, 'roth_strategy': 'fixed_amount',
        'roth_amount': 80000, 'roth_end_year': 2034
    },
    {
        'name': '5. HIGH INFLATION (Max SS, No Roth)',
        'Mike_ss_age': 70, 'Cindy_ss_age': 70, 'roth_strategy': 'none',
        'inflation_rate_general': 0.045, 'inflation_rate_healthcare': 0.065
    }
]

# --- Helper Functions ---

def load_data():
    try:
        config_df = pd.read_csv(INPUT_DIR / 'config.csv').set_index('parameter')['value']
        accounts_df = pd.read_csv(INPUT_DIR / 'accounts.csv', dtype={'balance': float, 'annual_tax_rate': float})
        income_df = pd.read_csv(INPUT_DIR / 'income_streams.csv', dtype={'annual_amount': float})
        ss_df = pd.read_csv(INPUT_DIR / 'social_security.csv', dtype={'fra_benefit': float})
        expenses_df = pd.read_csv(INPUT_DIR / 'annual_expenses.csv', dtype={'annual_amount': float})
        # Use 'Taxable' as a synonym for 'Brokerage' for backward compatibility
        accounts_df['account_type'] = accounts_df['account_type'].replace('Taxable', 'Brokerage')
        return config_df, accounts_df, income_df, ss_df, expenses_df
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"FATAL ERROR in loading data. Check your CSV files in '{INPUT_DIR}'. Ensure 'annual_tax_rate' column exists in accounts.csv. Error: {e}"); sys.exit()

def calculate_ss_benefit(fra_benefit, fra_age, claim_age):
    if claim_age == fra_age: return fra_benefit
    elif claim_age > fra_age: return fra_benefit * (1 + (claim_age - fra_age) * 0.08)
    else:
        months_early = (fra_age - claim_age) * 12; reduction = 0
        if months_early > 36: reduction += (months_early - 36) * (5/12 / 100); months_early = 36
        reduction += months_early * (5/9 / 100); return fra_benefit * (1 - reduction)

def get_inflated_tax_data(year, start_year, inflation_rate, filing_status):
    compounding_factor = (1 + inflation_rate) ** (year - start_year); inflated_brackets = {}
    for rate, (lower, upper) in BASE_FEDERAL_TAX_BRACKETS[filing_status].items():
        inflated_brackets[rate] = (lower * compounding_factor, upper * compounding_factor)
    inflated_deduction = BASE_FEDERAL_STANDARD_DEDUCTION[filing_status] * compounding_factor
    return inflated_brackets, inflated_deduction

def calculate_federal_tax(taxable_income, filing_status, brackets, deduction):
    taxable_income_after_deduction = max(0, taxable_income - deduction); tax = 0
    for rate, (lower, upper) in brackets.items():
        if taxable_income_after_deduction > lower:
            taxed_amount = min(taxable_income_after_deduction, upper) - lower
            tax += taxed_amount * rate
    return tax

def withdraw_from_account(accounts_df, amount, acc_type):
    balance = accounts_df.loc[accounts_df['account_type'] == acc_type, 'balance'].sum()
    withdrawal_amount = min(amount, balance)
    if balance > 0:
        proportions = (accounts_df.loc[accounts_df['account_type'] == acc_type, 'balance'] / balance).fillna(0)
        accounts_df.loc[accounts_df['account_type'] == acc_type, 'balance'] -= withdrawal_amount * proportions
    return withdrawal_amount

def plot_financial_overview(df, scenario_name, output_dir):
    fig, ax = plt.subplots(figsize=(12, 8)); ax.plot(df['Year'], df['Total Expenses'], label='Annual Expenses', color='red', marker='o', markersize=4); ax.plot(df['Year'], df['Total Savings'], label='Total Savings', color='green', marker='o', markersize=4); ax.set_title(f'Financial Overview: {scenario_name}', fontsize=16); ax.set_xlabel('Year', fontsize=12); ax.set_ylabel('Amount ($)', fontsize=12); formatter = mticker.FuncFormatter(lambda x, p: f'${x:,.0f}'); ax.yaxis.set_major_formatter(formatter); ax.legend(fontsize=12); ax.grid(True, which='both', linestyle='--', linewidth=0.5); plt.tight_layout(); safe_filename = "".join([c for c in scenario_name if c.isalpha() or c.isdigit() or c==' ']).rstrip(); plt.savefig(output_dir / f'{safe_filename}_overview.png'); plt.close(fig)

def plot_savings_breakdown(df, scenario_name, output_dir):
    fig, ax = plt.subplots(figsize=(12, 8)); labels = ['Cash', 'Brokerage', 'Traditional', 'Roth']; colors = ['#c7c7c7', '#4c72b0', '#dd8452', '#55a868']; ax.stackplot(df['Year'], df['Cash Balance'], df['Brokerage Balance'], df['Traditional Balance'], df['Roth Balance'], labels=labels, colors=colors); ax.set_title(f'Portfolio Composition: {scenario_name}', fontsize=16); ax.set_xlabel('Year', fontsize=12); ax.set_ylabel('Portfolio Value ($)', fontsize=12); formatter = mticker.FuncFormatter(lambda x, p: f'${x:,.0f}'); ax.yaxis.set_major_formatter(formatter); ax.legend(fontsize=12, loc='upper left'); ax.grid(True, which='both', linestyle='--', linewidth=0.5); plt.tight_layout(); safe_filename = "".join([c for c in scenario_name if c.isalpha() or c.isdigit() or c==' ']).rstrip(); plt.savefig(output_dir / f'{safe_filename}_composition.png'); plt.close(fig)

# --- Main Simulation Engine (Simplified Tax Model) ---

def run_single_scenario(scenario_config):
    config_df, accounts_df, income_df, ss_df, expenses_df = load_data()
    if 'custom_inflation_rate' not in expenses_df.columns: expenses_df['custom_inflation_rate'] = pd.NA
    expenses_df['custom_inflation_rate'] = pd.to_numeric(expenses_df['custom_inflation_rate'], errors='coerce')
    accounts_df = accounts_df.copy(); start_year = int(config_df['start_year']); projection_years = int(config_df['projection_years']); filing_status = config_df['federal_filing_status']
    inf_general = float(scenario_config.get('inflation_rate_general', config_df['inflation_rate_general'])); inf_health = float(scenario_config.get('inflation_rate_healthcare', config_df['inflation_rate_healthcare']))
    pensions = income_df.copy(); ss_data = ss_df.set_index('person_name').to_dict('index')
    person1_name = list(ss_data.keys())[0]; person2_name = list(ss_data.keys())[1]
    person1_ss_age_key = f"{person1_name}_ss_age"; person2_ss_age_key = f"{person2_name}_ss_age"
    person1_ss_benefit = calculate_ss_benefit(ss_data[person1_name]['fra_benefit'], ss_data[person1_name]['fra_age'], scenario_config[person1_ss_age_key])
    person2_ss_benefit = calculate_ss_benefit(ss_data[person2_name]['fra_benefit'], ss_data[person2_name]['fra_age'], scenario_config[person2_ss_age_key])
    total_taxes_paid = 0; total_irmaa_paid = 0; yearly_data_list = []

    for i in range(projection_years):
        current_year = start_year + i; current_age = 63 + i
        inflated_brackets, inflated_deduction = get_inflated_tax_data(current_year, start_year, inf_general, filing_status)
        for idx, row in expenses_df.iterrows():
            if current_year > row['start_year']:
                rate = row['custom_inflation_rate'] if pd.notna(row['custom_inflation_rate']) else (inf_health if row['inflation_category'] == 'Healthcare' else inf_general)
                expenses_df.loc[idx, 'annual_amount'] *= (1 + rate)
        if current_age > scenario_config[person1_ss_age_key]: person1_ss_benefit *= (1 + inf_general)
        if current_age > scenario_config[person2_ss_age_key]: person2_ss_benefit *= (1 + inf_general)
        for idx, row in pensions.iterrows():
            if row['is_inflation_adjusted'] and current_year > row['start_year']: pensions.loc[idx, 'annual_amount'] *= (1 + inf_general)
        
        irmaa_surcharge = 0
        if current_year >= 2027 and len(yearly_data_list) >= 2:
            magi_prev = yearly_data_list[i-2].get('MAGI', 0)
            for bracket in MEDICARE_IRMAA_BRACKETS:
                if magi_prev > bracket['threshold']:
                    irmaa_surcharge = (bracket['part_b_surcharge'] + bracket['part_d_surcharge']) * 2 * 12; break
        total_irmaa_paid += irmaa_surcharge
        
        start_of_year_balances = accounts_df.copy()
        prior_trad_bal = start_of_year_balances[start_of_year_balances['account_type'] == 'Traditional']['balance'].sum()

        # --- Roth Conversion (Happens at Start of Year, Before Growth) ---
        roth_conversion_amount = 0
        preliminary_taxable_income = pensions[(pensions['start_year'] <= current_year) & (pensions['end_year'] >= current_year)]['annual_amount'].sum()
        if current_year <= scenario_config.get('roth_end_year', 0):
            if scenario_config.get('roth_strategy') == 'fixed_amount':
                roth_conversion_amount = scenario_config.get('roth_amount', 0)
            elif scenario_config.get('roth_strategy') == 'fill_bracket':
                rate = scenario_config.get('roth_target_bracket_rate', 0)
                if rate in inflated_brackets:
                    target_top = inflated_brackets[rate][1]
                    roth_conversion_amount = max(0, target_top - (preliminary_taxable_income - inflated_deduction))
            elif scenario_config.get('roth_strategy') == 'till_2028':
                roth_conversion_amount = scenario_config.get('roth_amount', 0)

        if roth_conversion_amount > 0:
            roth_conversion_amount = max(0, min(roth_conversion_amount, prior_trad_bal))
            withdraw_from_account(accounts_df, roth_conversion_amount, 'Traditional')
            accounts_df.loc[accounts_df['account_type'] == 'Roth', 'balance'] += roth_conversion_amount
        
        # --- Account Growth ---
        accounts_df['balance'] *= (1 + accounts_df['annual_growth_rate'])
        
        income_on_accounts = 0
        for index, row in start_of_year_balances.iterrows():
            if row['account_type'] in ['Brokerage', 'Cash']:
                balance = row['balance']
                annual_rate = row['annual_rate']
                income_on_accounts += balance *  annual_rate
                
        
        pension_income = pensions[(pensions['start_year'] <= current_year) & (pensions['end_year'] >= current_year)]['annual_amount'].sum()
        person1_ss_payment = person1_ss_benefit if current_age >= scenario_config[person1_ss_age_key] else 0
        person2_ss_payment = person2_ss_benefit if current_age >= scenario_config[person2_ss_age_key] else 0
        ss_income = person1_ss_payment + person2_ss_payment
        
        rmd_amount = 0
        if current_age >= 75: rmd_amount = prior_trad_bal / IRS_UNIFORM_LIFETIME_TABLE.get(current_age, 8.9)
        
        year_expenses = expenses_df[(expenses_df['start_year'] <= current_year) & (expenses_df['end_year'] >= current_year)]['annual_amount'].sum()
        year_expenses += irmaa_surcharge
        cash_needed_for_spending = max(0, year_expenses - (pension_income + ss_income))

        traditional_withdrawal = 0
        if cash_needed_for_spending > 0:
             non_retirement_cash = accounts_df.loc[accounts_df['account_type'].isin(['Cash', 'Brokerage']), 'balance'].sum()
             traditional_withdrawal = max(0, cash_needed_for_spending - non_retirement_cash)

        traditional_withdrawal = max(rmd_amount, traditional_withdrawal)
        
        AGI_Proxy = pension_income + roth_conversion_amount + traditional_withdrawal + income_on_accounts
        MAGI = AGI_Proxy + ss_income
        
        if MAGI > inflated_brackets.get(0.22, (float('inf'),))[0]: final_taxable_income = AGI_Proxy + (ss_income * 0.85)
        elif MAGI > inflated_brackets.get(0.12, (float('inf'),))[0]: final_taxable_income = AGI_Proxy + (ss_income * 0.50)
        else: final_taxable_income = AGI_Proxy
            
        tax_from_ordinary_income = calculate_federal_tax(final_taxable_income, filing_status, inflated_brackets, inflated_deduction)
        
        federal_tax = tax_from_ordinary_income 
        total_taxes_paid += federal_tax
        
        cash_needed_from_portfolio = cash_needed_for_spending + federal_tax
            
        withdrawn_so_far = 0
        withdrawal_hierarchy = ['Cash', 'Brokerage', 'Traditional', 'Roth']
        for acc_type in withdrawal_hierarchy:
            needed = cash_needed_from_portfolio - withdrawn_so_far
            if needed <= 0: break
            withdrawn = withdraw_from_account(accounts_df, needed, acc_type)
            withdrawn_so_far += withdrawn
        
        current_year_data = {
            'Year': current_year, f'{person1_name} (age)': current_age, f'{person2_name} (age)': current_age,
            'AGI_Proxy': AGI_Proxy, 'MAGI': MAGI, "Accounts Income":income_on_accounts, 'Pension Income': pension_income, 'Total SS': ss_income,
            f'{person1_name} SS': person1_ss_payment, f'{person2_name} SS': person2_ss_payment,
            'Total Expenses': year_expenses, 'Roth Conversion': roth_conversion_amount,
            'RMD': rmd_amount, "Final Taxable Income":final_taxable_income, "Tax Ordinary Income": tax_from_ordinary_income,'Federal Taxes': federal_tax, 'IRMAA': irmaa_surcharge,
            'Total Savings': accounts_df['balance'].sum(), 'Cash Balance': accounts_df[accounts_df['account_type'] == 'Cash']['balance'].sum(),
            'Brokerage Balance': accounts_df[accounts_df['account_type'] == 'Brokerage']['balance'].sum(),
            'Traditional Balance': accounts_df[accounts_df['account_type'] == 'Traditional']['balance'].sum(),
            'Roth Balance': accounts_df[accounts_df['account_type'] == 'Roth']['balance'].sum()
        }
        for _, row in expenses_df.iterrows():
            if row['start_year'] <= current_year <= row['end_year']: current_year_data[row['expense_name']] = row['annual_amount']
            else: current_year_data[row['expense_name']] = 0
        for key, value in current_year_data.items():
            if isinstance(value, (int, float)) and key != 'Year': current_year_data[key] = round(value)
        yearly_data_list.append(current_year_data)
        
        if withdrawn_so_far < cash_needed_from_portfolio - 1:
            summary = {'Scenario Name': scenario_config['name'], 'Total Lifetime Taxes': total_taxes_paid, 'Total IRMAA Paid': total_irmaa_paid, 'Final Portfolio Value': 0, 'Age Portfolio Depleted': current_age}
            details_df = pd.DataFrame(yearly_data_list); return summary, details_df
            
    summary = {'Scenario Name': scenario_config['name'], 'Total Lifetime Taxes': total_taxes_paid, 'Total IRMAA Paid': total_irmaa_paid, 'Final Portfolio Value': accounts_df['balance'].sum(), 'Age Portfolio Depleted': 'N/A'}
    details_df = pd.DataFrame(yearly_data_list); return summary, details_df

# --- Main Program Execution ---
if __name__ == "__main__":
    print("Running final simulation (Simplified Tax Model)...")
    if REPORTS_DIR.exists(): shutil.rmtree(REPORTS_DIR)
    REPORTS_DIR.mkdir(exist_ok=True); PLOT_DIR.mkdir(exist_ok=True); YEARLY_DIR.mkdir(exist_ok=True)
    
    all_summary_results = []
    
    for scenario in SCENARIOS_TO_RUN:
        print(f"  - Simulating: {scenario['name']}")
        summary_result, details_df = run_single_scenario(scenario.copy())
        all_summary_results.append(summary_result)
        
        safe_name = "".join([c for c in scenario['name'] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        details_df.to_csv(YEARLY_DIR / f"{safe_name}_yearly.csv", index=False)
        
        print(f"    - Generating plots for {scenario['name']}")
        plot_financial_overview(details_df, scenario['name'], PLOT_DIR)
        plot_savings_breakdown(details_df, scenario['name'], PLOT_DIR)
        
    summary_df = pd.DataFrame(all_summary_results)
    summary_df['Total Lifetime Taxes'] = summary_df['Total Lifetime Taxes'].round().map('${:,.0f}'.format)
    summary_df['Total IRMAA Paid'] = summary_df['Total IRMAA Paid'].round().map('${:,.0f}'.format)
    summary_df['Final Portfolio Value'] = summary_df['Final Portfolio Value'].round().map('${:,.0f}'.format)
    
    print("\n--- FINAL SCENARIO COMPARISON REPORT ---")
    print(summary_df.to_string(index=False))
    
    output_filename = REPORTS_DIR / 'summary_report_final.csv'
    summary_df.to_csv(output_filename, index=False)
    print(f"\nSummary report saved to {output_filename}")
    print(f"All plots and yearly details saved in the '{REPORTS_DIR}' directory.")