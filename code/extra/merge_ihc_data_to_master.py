import pandas as pd

# File paths
table1_path = "data/hari_BC/csv/BnW_combined.csv"
table2_path = "data/hari_BC/Original/Corresponding IHC data.xlsx"

# Read table 1
table1 = pd.read_csv(table1_path)

# Load all sheets from table 2
sheets = pd.read_excel(table2_path, sheet_name=None)  # returns a dict {sheetname: dataframe}

# Iterate through each sheet
for sheet_name, sheet_df in sheets.items():
    # Ensure necessary columns exist
    required_cols = {'Sample Barcode', 'Positivity', 'H-Score'}
    if not required_cols.issubset(sheet_df.columns):
        print(f"⚠️ Skipping sheet '{sheet_name}' — missing required columns.")
        continue

    # Merge with table1 on Barcode/Sample Barcode
    merged = pd.merge(
        table1,
        sheet_df[['Sample Barcode', 'Positivity', 'H-Score']],
        left_on='Barcode',
        right_on='Sample Barcode',
        how='left'
    )

    # Rename merged columns with sheet name prefix
    merged.rename(
        columns={
            'Positivity': f'{sheet_name}_Positivity',
            'H-Score': f'{sheet_name}_H-Score'
        },
        inplace=True
    )

    # Drop redundant 'Sample Barcode' column
    merged.drop(columns=['Sample Barcode'], inplace=True)

    # Update table1 for next iteration (so all sheets accumulate)
    table1 = merged

# Save the final merged result
output_path = "BnW_combined_with_IHC.csv"
table1.to_csv(output_path, index=False)

print(f"✅ Merged table saved as {output_path}")
