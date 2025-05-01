import json
import os
from pathlib import Path

def process_keyword_postings():
    # Define file paths
    data_dir = Path('data')
    original_file = data_dir / 'keyword_postings.json'
    large_file = data_dir / 'keyword_postings_full.json'
    temp_file = data_dir / 'keyword_postings_temp.json'
    
    # Check if original file exists
    if not original_file.exists():
        print(f"Error: {original_file} does not exist")
        return
    
    print("Processing keyword_postings.json...")
    
    # Read first 2 million rows
    count = 0
    with open(original_file, 'r') as f_in, open(temp_file, 'w') as f_out:
        for line in f_in:
            if count >= 2000000:
                break
            f_out.write(line)
            count += 1
    
    print(f"Processed {count} rows")
    
    # Rename original file to indicate it's the full version
    os.rename(original_file, large_file)
    print(f"Renamed original file to {large_file}")
    
    # Rename temp file to original name
    os.rename(temp_file, original_file)
    print(f"Renamed temp file to {original_file}")
    
    print("Processing complete!")

if __name__ == "__main__":
    process_keyword_postings() 