import os
from pathlib import Path

import pandas as pd


def parse_filename_metadata(filename: str) -> dict[str, str]:
    """
    Parse metadata from filename with pattern: company_month_year_category.csv
    
    Args:
        filename: The filename to parse (e.g., 'CIMSA_05_2025_agentes.csv')
    
    Returns:
        Dictionary with parsed metadata: company, month, year, category
    """
    # Remove file extension
    name_without_ext = filename.rsplit('.', 1)[0]
    
    # Split by underscore
    parts = name_without_ext.split('_')
    
    if len(parts) < 4:
        raise ValueError(f"Filename '{filename}' does not match expected pattern: company_month_year_category")
    
    return {
        'company': parts[0],
        'month': parts[1],
        'year': parts[2],
        'category': parts[3]
    }

def load_file_with_metadata(file_path: str) -> pd.DataFrame:
    """
    Load a CSV file and add metadata columns based on filename
    
    Args:
        file_path: Path to the CSV file
    
    Returns:
        DataFrame with original data plus metadata columns
    """
    # Extract filename from path
    filename = os.path.basename(file_path)
    
    # Parse metadata from filename
    metadata = parse_filename_metadata(filename)
    
    # Load CSV file with proper encoding
    try:
        df = pd.read_csv(file_path, sep=';', encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, sep=';', encoding='latin-1')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, sep=';', encoding='cp1252')
    
    # Add metadata columns
    for key, value in metadata.items():
        df[f'file_{key}'] = value
    
    # Add source filename for reference
    df['source_file'] = filename
    
    return df

def load_all_files_from_directory(directory_path: str) -> pd.DataFrame:
    """
    Load all CSV files from the raw data directory and combine them
    
    Args:
        directory_path: Path to directory containing CSV files
    
    Returns:
        Combined DataFrame with all data and metadata
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        raise FileNotFoundError(f"Directory '{directory_path}' does not exist")
    
    all_dataframes = []
    
    # Find all CSV files in the directory
    csv_files = list(directory.glob('*.csv'))
    
    if not csv_files:
        raise ValueError(f"No CSV files found in directory '{directory_path}'")
    
    print(f"Found {len(csv_files)} CSV files to process:")
    
    for file_path in csv_files:
        try:
            print(f"Loading: {file_path.name}")
            df = load_file_with_metadata(str(file_path))
            all_dataframes.append(df)
            print(f"  Loaded {len(df)} rows")
        except Exception as e:
            print(f"  Error loading {file_path.name}: {e}")
            continue
    
    if not all_dataframes:
        raise ValueError("No files were successfully loaded")
    
    # Combine all dataframes
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    print(f"\nTotal combined dataset: {len(combined_df)} rows")
    
    return combined_df

def main():
    """
    Main function to demonstrate usage
    """
    # Define the path to the raw data directory
    raw_data_path = "/Users/santiagoarielgiusiano/Desktop/GenAI Pathway/Paybot/data/raw"
    
    try:
        # Load all files from the directory
        combined_data = load_all_files_from_directory(raw_data_path)
        
        # Display basic information about the loaded data
        print(f"\nDataset shape: {combined_data.shape}")
        print(f"\nColumns: {list(combined_data.columns)}")
        
        # Show metadata summary
        print(f"\nMetadata summary:")
        print(f"Companies: {combined_data['file_company'].unique()}")
        print(f"Months: {combined_data['file_month'].unique()}")
        print(f"Years: {combined_data['file_year'].unique()}")
        print(f"Categories: {combined_data['file_category'].unique()}")
        
        # Show first few rows
        print(f"\nFirst 3 rows:")
        print(combined_data.head(3))
        
        return combined_data
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    main()
