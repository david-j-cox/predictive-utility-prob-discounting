import pandas as pd
from pathlib import Path

# Set paths
raw_data_path = Path('../01_raw_data')
processed_data_path = Path('../02_processed_data')
processed_data_path.mkdir(exist_ok=True)

# Process all CSV files
csv_files = list(raw_data_path.glob('*.csv'))
csv_dfs = []

for csv_file in csv_files:
    try:
        df = pd.read_csv(csv_file)
        csv_dfs.append(df)
    except Exception as e:
        print(f"Error processing {csv_file}: {str(e)}")

# Combine all CSV data
if csv_dfs:
    combined_csv = pd.concat(csv_dfs, ignore_index=True)
    
    # Save the combined data
    combined_csv.to_csv(processed_data_path / 'combined_csv_data.csv', index=False)
    
    # Print summary
    print(f"Total CSV records: {len(combined_csv)}")
    print(f"Unique participants in CSV: {combined_csv['participantId'].nunique()}")
    
    print("\nSample of CSV data:")
    print(combined_csv.head())
    
    print("\nColumns in CSV data:")
    print(combined_csv.columns.tolist())
else:
    print("No CSV files were successfully processed.") 