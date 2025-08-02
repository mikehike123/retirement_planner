import pandas as pd
import sys
import pathlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import shutil

# --- Directory and File Path Definitions ---
INPUT_DIR = pathlib.Path("input_files_v10")
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

# --- HISTORICAL DATA SETS FOR STRESS TESTING ---
HISTORICAL_DATA_1970S = {
    # Year: (S&P 500, Inflation, Cash/T-Bill Rate)
    1973: (-0.147, 0.088, 0.070), 1974: (-0.265, 0.122, 0.078),
    1975: ( 0.372, 0.070, 0.058), 1976: ( 0.238, 0.049, 0.050),
    1977: (-0.072, 0.067, 0.053), 1978: ( 0.066, 0.090, 0.072),
    1979: ( 0.184, 0.133, 0.100), 1980: ( 0.325, 0.125, 0.115),
    1981: (-0.049, 0.089, 0.140), 1982: ( 0.216, 0.038, 0.107),
}
HISTORICAL_DATA_2009S = {
    # Year: (S&P 500, Inflation, Cash/T-Bill Rate)
    2009: ( 0.265, -0.004, 0.001), 2010: ( 0.151,  0.016, 0.001),
    2011: ( 0.021,  0.032, 0.000), 2012: ( 0.160,  0.021, 0.001),
    2013: ( 0.324,  0.015, 0.000), 2014: ( 0.137,  0.016, 0.000),
    2015: ( 0.014,  0.001, 0.000), 2016: ( 0.120,  0.013, 0.003),
    2017: ( 0.218,  0.021, 0.009), 2018: (-0.044,  0.024, 0.019),
}

# --- Scenarios to Run ---
SCENARIOS_TO_RUN = [
    { 'name': '1. Baseline (SS @ 67, No Roth)', 'Mike_ss_age': 67, 'Cindy_ss_age': 67, 'roth_strategy': 'none' },
    { 'name': '2. Baseline (SS @ 67, Roth $50K)', 'Mike_ss_age': 67, 'Cindy_ss_age': 67, 'roth_strategy': 'till_2028', 'roth_amount': 50000, 'roth_end_year': 2028 },
    { 'name': '3. Maximize SS (SS @ 70, No Roth)', 'Mike_ss_age': 70, 'Cindy_ss_age': 70, 'roth_strategy': 'none' },
    { 'name': '4. Max SS + Fill 22% Bracket', 'Mike_ss_age': 70, 'Cindy_ss_age': 70, 'roth_strategy': 'fill_bracket', 'roth_target_bracket_rate': 0.22, 'roth_end_year': 2034 },
    { 'name': '5. Max SS + Fixed $80k Roth', 'Mike_ss_age': 70, 'Cindy_ss_age': 70, 'roth_strategy': 'fixed_amount', 'roth_amount': 80000, 'roth_end_year': 2034 },
    { 'name': '6. HIGH INFLATION (Max SS, No Roth)', 'Mike_ss_age': 70, 'Cindy_ss_age': 70, 'roth_strategy': 'none', 'inflation_rate_general': 0.045, 'inflation_rate_healthcare': 0.065 },
    { 'name': '7.Match Bolden (Max SS, No Roth)', 'Mike_ss_age': 67, 'Cindy_ss_age': 67, 'roth_strategy': 'none', 'inflation_rate_general': 0.025, 'inflation_rate_healthcare': 0.065 },
    { 'name': '8. 1970s Stagflation Stress Test', 'Mike_ss_age': 70, 'Cindy_ss_age': 70, 'roth_strategy': 'none', 'historical_data': HISTORICAL_DATA_1970S },
    { 'name': '9. 2009 Zero-Interest Rate Stress Test', 'Mike_ss_age': 70, 'Cindy_ss_age': 70, 'roth_strategy': 'none', 'historical_data': HISTORICAL_DATA_2009S }
]

# --- Helper Functions ---
def validate_dataframe_column(df, column_name, allowed_values, df_name):
    if column_name not in df.columns: return
    allowed_set = set(allowed_values)
    user_values = set(df[column_name].dropna().unique())
    invalid_entries = user_values - allowed_set
    if invalid_entries:
        print(f"\n--- FATAL INPUT ERROR ---\nInvalid value(s) in '{column_name}' of '{df_name}'.")
        print(f"Invalid entries: {sorted(list(invalid_entries))}")
        print(f"Allowed values: {sorted(list(allowed_set))}\n")
        sys.exit()

def load_data():
    try:
        ALLOWED_ACCOUNT_TYPES = {'cash', 'brokerage', 'traditional', 'roth', 'taxable'}
        ALLOWED_ASSET_CLASSES = {'equity', 'cash', 'custom'}
        ALLOWED_INFLATION_CATEGORIES = {'general', 'healthcare', 'custom'}
        ALLOWED_FILING_STATUSES = {'married filing jointly'}
        
        config_column_names = ['parameter', 'value']
        account_column_names = ['account_name', 'account_type', 'balance', 'asset_class', 'custom_annual_rate']
        expense_column_names = ['expense_name', 'start_year', 'end_year', 'annual_amount', 'inflation_category', 'custom_inflation_rate']
        income_column_names = ['stream_name', 'annual_amount', 'start_year', 'end_year', 'is_inflation_adjusted']
        ss_column_names = ['person_name', 'fra_benefit', 'fra_age']
        
        config_df = pd.read_csv(INPUT_DIR / 'config.csv', names=config_column_names, header=0)
        status_param = 'federal_filing_status'
        filing_status_series = config_df.loc[config_df['parameter'] == status_param, 'value']
        if filing_status_series.empty:
            print(f"FATAL ERROR: Parameter '{status_param}' not found in config.csv.")
            sys.exit()
        original_status = filing_status_series.iloc[0]
        clean_status = original_status.strip().lower()
        if clean_status not in ALLOWED_FILING_STATUSES:
             print(f"\n--- FATAL INPUT ERROR ---\nInvalid value for 'federal_filing_status' in 'config.csv'.")
             print(f"Found: '{original_status}'. Allowed: {list(ALLOWED_FILING_STATUSES)}\n")
             sys.exit()
        config_df.loc[config_df['parameter'] == status_param, 'value'] = clean_status
        
        accounts_df = pd.read_csv(INPUT_DIR / 'accounts.csv', names=account_column_names, header=0, dtype={'custom_annual_rate': float})
        accounts_df['account_type'] = accounts_df['account_type'].str.strip().str.lower()
        validate_dataframe_column(accounts_df, 'account_type', ALLOWED_ACCOUNT_TYPES, 'accounts.csv')
        
        if 'asset_class' in accounts_df.columns:
            accounts_df['asset_class'] = accounts_df['asset_class'].str.strip().str.lower()
            validate_dataframe_column(accounts_df, 'asset_class', ALLOWED_ASSET_CLASSES, 'accounts.csv')
        else:
            print(f"FATAL ERROR: The required column 'asset_class' is missing from accounts.csv.")
            sys.exit()
        
        income_df = pd.read_csv(INPUT_DIR / 'income_streams.csv', names=income_column_names, header=0, dtype={'annual_amount': float})
        ss_df = pd.read_csv(INPUT_DIR / 'social_security.csv', names=ss_column_names, header=0, dtype={'fra_benefit': float})
        
        expenses_df = pd.read_csv(INPUT_DIR / 'annual_expenses.csv', names=expense_column_names, header=0, dtype={'annual_amount': float})
        if 'inflation_category' in expenses_df.columns:
            expenses_df['inflation_category'] = expenses_df['inflation_category'].str.strip().str.lower()
            validate_dataframe_column(expenses_df, 'inflation_category', ALLOWED_INFLATION_CATEGORIES, 'annual_expenses.csv')

        for df in [config_df, accounts_df, income_df, ss_df, expenses_df]:
            for col in df.select_dtypes(include=['object']).columns:
                if col not in ['account_type', 'inflation_category', 'value', 'asset_class']:
                     df[col] = df[col].str.strip()
        
        config_df = config_df.set_index('parameter')['value']
        accounts_df['account_type'] = accounts_df['account_type'].replace('taxable', 'brokerage')
        return config_df, accounts_df, income_df, ss_df, expenses_df
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"FATAL ERROR in loading data. Check your CSV files in '{INPUT_DIR}'. Error: {e}")
        sys.exit()

def calculate_ss_benefit(fra_benefit, fra_age, claim_age):
    if claim_age == fra_age: return fra_benefit
    elif claim_age > fra_age: return fra_benefit * (1 + (claim_age - fra_age) * 0.08)
    else:
        months_early = (fra_age - claim_age) * 12; reduction = 0
        if months_early > 36: reduction += (months_early - 36) * (5/12/100); months_early = 36
        reduction += months_early * (5/9/100)
        return fra_benefit * (1 - reduction)

def get_inflated_tax_data(year, start_year, inflation_rate, filing_status):
    filing_status_key = filing_status.title()
    compounding_factor = (1 + inflation_rate) ** (year - start_year)
    inflated_brackets = {}
    for rate, (lower, upper) in BASE_FEDERAL_TAX_BRACKETS[filing_status_key].items():
        inflated_brackets[rate] = (lower * compounding_factor, upper * compounding_factor)
    inflated_deduction = BASE_FEDERAL_STANDARD_DEDUCTION[filing_status_key] * compounding_factor
    return inflated_brackets, inflated_deduction

def calculate_federal_tax(taxable_income, filing_status, brackets, deduction):
    taxable_income_after_deduction = max(0, taxable_income - deduction)
    tax = 0
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
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(df['Year'], df['Total Expenses'], label='Annual Expenses', color='red', marker='o', markersize=4)
    ax.plot(df['Year'], df['Total Savings'], label='Total Savings', color='green', marker='o', markersize=4)
    ax.set_title(f'Financial Overview: {scenario_name}', fontsize=16)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Amount ($)', fontsize=12)
    formatter = mticker.FuncFormatter(lambda x, p: f'${x:,.0f}')
    ax.yaxis.set_major_formatter(formatter)
    ax.legend(fontsize=12)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    safe_filename = "".join([c for c in scenario_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    plt.savefig(output_dir / f'{safe_filename}_overview.png')
    plt.close(fig)

def plot_savings_breakdown(df, scenario_name, output_dir):
    fig, ax = plt.subplots(figsize=(12, 8))
    labels = ['Cash', 'Brokerage', 'Traditional', 'Roth']
    colors = ['#c7c7c7', '#4c72b0', '#dd8452', '#55a868']
    ax.stackplot(df['Year'], df['Cash Balance'], df['Brokerage Balance'], df['Traditional Balance'], df['Roth Balance'], labels=labels, colors=colors)
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

def run_single_scenario(scenario_config):
    config_df, accounts_df, income_df, ss_df, expenses_df = load_data()
    initial_portfolio_value = accounts_df['balance'].sum()
    if 'custom_inflation_rate' not in expenses_df.columns: expenses_df['custom_inflation_rate'] = pd.NA
    expenses_df['custom_inflation_rate'] = pd.to_numeric(expenses_df['custom_inflation_rate'], errors='coerce')
    accounts_df = accounts_df.copy()
    start_year = int(config_df['start_year']); projection_years = int(config_df['projection_years']); filing_status = config_df['federal_filing_status']
    
    historical_data = scenario_config.get('historical_data')
    if historical_data:
        historical_sequence = list(historical_data.values())
        historical_period_length = len(historical_sequence)
    
    baseline_inf_general = float(scenario_config.get('inflation_rate_general', config_df['inflation_rate_general']))
    baseline_inf_health = float(scenario_config.get('inflation_rate_healthcare', config_df['inflation_rate_healthcare']))
    baseline_equity_return = float(config_df['baseline_equity_return'])
    baseline_cash_return = float(config_df['baseline_cash_return'])

    pensions = income_df.copy()
    ss_data = ss_df.set_index('person_name').to_dict('index')
    person1_name = list(ss_data.keys())[0]; person2_name = list(ss_data.keys())[1]
    person1_ss_age_key = f"{person1_name}_ss_age"; person2_ss_age_key = f"{person2_name}_ss_age"
    person1_ss_benefit = calculate_ss_benefit(ss_data[person1_name]['fra_benefit'], ss_data[person1_name]['fra_age'], scenario_config[person1_ss_age_key])
    person2_ss_benefit = calculate_ss_benefit(ss_data[person2_name]['fra_benefit'], ss_data[person2_name]['fra_age'], scenario_config[person2_ss_age_key])
    total_taxes_paid = 0; total_irmaa_paid = 0; yearly_data_list = []

    for i in range(projection_years):
        current_year = start_year + i
        current_age = 63 + i

        if historical_data and i < historical_period_length:
            year_stock_return, year_inflation, year_cash_return = historical_sequence[i]
            inf_general = year_inflation
            inf_health = year_inflation
        else:
            year_stock_return = baseline_equity_return
            year_cash_return = baseline_cash_return
            inf_general = baseline_inf_general
            inf_health = baseline_inf_health

        inflated_brackets, inflated_deduction = get_inflated_tax_data(current_year, start_year, inf_general, filing_status)

        for idx, row in expenses_df.iterrows():
            if current_year > row['start_year']:
                rate = row['custom_inflation_rate'] if pd.notna(row['custom_inflation_rate']) else (inf_health if row['inflation_category'] == 'healthcare' else inf_general)
                expenses_df.loc[idx, 'annual_amount'] *= (1 + rate)
        
        if current_age > scenario_config[person1_ss_age_key]: person1_ss_benefit *= (1 + inf_general)
        if current_age > scenario_config[person2_ss_age_key]: person2_ss_benefit *= (1 + inf_general)
        for idx, row in pensions.iterrows():
            if row['is_inflation_adjusted'] and current_year > row['start_year']:
                pensions.loc[idx, 'annual_amount'] *= (1 + inf_general)
        
        irmaa_surcharge = 0
        if current_year >= 2027 and len(yearly_data_list) >= 2:
            magi_prev = yearly_data_list[i-2].get('MAGI', 0)
            for bracket in MEDICARE_IRMAA_BRACKETS:
                if magi_prev > bracket['threshold']:
                    irmaa_surcharge = (bracket['part_b_surcharge'] + bracket['part_d_surcharge']) * 2 * 12
                    break
        total_irmaa_paid += irmaa_surcharge
        
        start_of_year_balances = accounts_df.copy()
        prior_trad_bal = start_of_year_balances[start_of_year_balances['account_type'] == 'traditional']['balance'].sum()

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
            withdraw_from_account(accounts_df, roth_conversion_amount, 'traditional')
            accounts_df.loc[accounts_df['account_type'] == 'roth', 'balance'] += roth_conversion_amount

        for idx, account in accounts_df.iterrows():
            balance = account['balance']
            if account['asset_class'] == 'equity':
                growth_rate = year_stock_return
            elif account['asset_class'] == 'cash':
                growth_rate = year_cash_return
            else: # asset_class is 'custom'
                growth_rate = account['custom_annual_rate']
            accounts_df.loc[idx, 'balance'] = balance * (1 + growth_rate)

        income_on_accounts = 0
        for index, row in start_of_year_balances.iterrows():
            if row['account_type'] in ['brokerage', 'cash']:
                if row['asset_class'] == 'equity':
                    rate_to_use = year_stock_return
                elif row['asset_class'] == 'cash':
                    rate_to_use = year_cash_return
                else: # asset_class is 'custom'
                    rate_to_use = row['custom_annual_rate']
                income_on_accounts += row['balance'] * rate_to_use
                
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
             non_retirement_cash = accounts_df.loc[accounts_df['account_type'].isin(['cash', 'brokerage']), 'balance'].sum()
             traditional_withdrawal = max(0, cash_needed_for_spending - non_retirement_cash)

        traditional_withdrawal = max(rmd_amount, traditional_withdrawal)
        
        AGI_Proxy = pension_income + roth_conversion_amount + traditional_withdrawal + income_on_accounts
        MAGI = AGI_Proxy + ss_income
        
        if MAGI > inflated_brackets.get(0.22, (float('inf'),))[0]: final_taxable_income = AGI_Proxy + (ss_income * 0.85)
        elif MAGI > inflated_brackets.get(0.12, (float('inf'),))[0]: final_taxable_income = AGI_Proxy + (ss_income * 0.50)
        else: final_taxable_income = AGI_Proxy
            
        tax_from_ordinary_income = calculate_federal_tax(final_taxable_income, filing_status, inflated_brackets, inflated_deduction)
        federal_tax = tax_from_ordinary_income; total_taxes_paid += federal_tax
        cash_needed_from_portfolio = cash_needed_for_spending + federal_tax
            
        withdrawn_so_far = 0
        withdrawal_hierarchy = ['cash', 'brokerage', 'traditional', 'roth']
        for acc_type in withdrawal_hierarchy:
            needed = cash_needed_from_portfolio - withdrawn_so_far
            if needed <= 0: break
            withdrawn = withdraw_from_account(accounts_df, needed, acc_type)
            withdrawn_so_far += withdrawn
        
        current_year_data = {
            'Year': current_year, f'{person1_name} (age)': current_age, f'{person2_name} (age)': current_age,
            'AGI_Proxy': AGI_Proxy, 'MAGI': MAGI, "Accounts Income":income_on_accounts, 'Pension Income': pension_income, 'Total SS': ss_income,
            f'{person1_name} SS': person1_ss_payment, f'{person2_name} SS': person2_ss_payment, 'Total Expenses': year_expenses, 'Roth Conversion': roth_conversion_amount,
            'RMD': rmd_amount, "Final Taxable Income":final_taxable_income, "Tax Ordinary Income": tax_from_ordinary_income,'Federal Taxes': federal_tax, 'IRMAA': irmaa_surcharge,
            'Total Savings': accounts_df['balance'].sum(), 'Cash Balance': accounts_df[accounts_df['account_type'] == 'cash']['balance'].sum(),
            'Brokerage Balance': accounts_df[accounts_df['account_type'] == 'brokerage']['balance'].sum(), 'Traditional Balance': accounts_df[accounts_df['account_type'] == 'traditional']['balance'].sum(),
            'Roth Balance': accounts_df[accounts_df['account_type'] == 'roth']['balance'].sum()
        }
        for _, row in expenses_df.iterrows():
            if row['start_year'] <= current_year <= row['end_year']: current_year_data[row['expense_name']] = row['annual_amount']
            else: current_year_data[row['expense_name']] = 0
        for key, value in current_year_data.items():
            if isinstance(value, (int, float)) and key != 'Year': current_year_data[key] = round(value)
        yearly_data_list.append(current_year_data)
        
        if withdrawn_so_far < cash_needed_from_portfolio - 1:
            details_df = pd.DataFrame(yearly_data_list)
            summary = {'Scenario Name': scenario_config['name'], 'Total Lifetime Taxes': total_taxes_paid, 'Total IRMAA Paid': total_irmaa_paid, 'Final Portfolio Value': 0, 'Present Value': 0, 'CAGR': -1.0, 'Age Portfolio Depleted': current_age}
            print(f"\n***********************************************************************")
            print(f"MONEY DEPLETED in {scenario_config['name']} during {current_year} at age {current_age}.")
            print(f"***********************************************************************\n")
            return summary, details_df
            
    final_portfolio_value = accounts_df['balance'].sum()
    
    summary_inflation = baseline_inf_general
    if projection_years > 0:
        present_value = final_portfolio_value / ((1 + summary_inflation) ** projection_years)
        cagr = ((final_portfolio_value / initial_portfolio_value) ** (1 / projection_years) - 1) if initial_portfolio_value > 0 else 0.0
    else:
        present_value = final_portfolio_value; cagr = 0.0

    summary = {'Scenario Name': scenario_config['name'], 'Total Lifetime Taxes': total_taxes_paid, 'Total IRMAA Paid': total_irmaa_paid, 'Final Portfolio Value': final_portfolio_value, 'Present Value': present_value, 'CAGR': cagr, 'Age Portfolio Depleted': 'N/A'}
    details_df = pd.DataFrame(yearly_data_list)
    return summary, details_df

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
    summary_df['Present Value'] = summary_df['Present Value'].round().map('${:,.0f}'.format)
    summary_df['Final Portfolio Value'] = summary_df['Final Portfolio Value'].round().map('${:,.0f}'.format)
    summary_df['CAGR'] = summary_df['CAGR'].map('{:.2%}'.format)
    summary_df['Total Lifetime Taxes'] = summary_df['Total Lifetime Taxes'].round().map('${:,.0f}'.format)
    summary_df['Total IRMAA Paid'] = summary_df['Total IRMAA Paid'].round().map('${:,.0f}'.format)
    column_order = ['Scenario Name', 'Final Portfolio Value', 'Present Value', 'CAGR', 'Total Lifetime Taxes', 'Total IRMAA Paid', 'Age Portfolio Depleted']
    summary_df = summary_df[column_order]
    
    print("\n--- FINAL SCENARIO COMPARISON REPORT ---")
    print(summary_df.to_string(index=False))
    
    output_filename = REPORTS_DIR / 'summary_report_final.csv'
    summary_df.to_csv(output_filename, index=False)
    print(f"\nSummary report saved to {output_filename}")
    print(f"All plots and yearly details saved in the '{REPORTS_DIR}' directory.")