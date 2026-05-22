import pandas as pd
def validate_row_counts(raw_data: pd.DataFrame, outputs: dict, exclude_buckets: list = None) -> dict:
    """
    Validates that the total number of rows in raw data equals the sum of rows in output buckets.
    This handles duplicate rows correctly since we're counting rows, not unique IDs.
    
    Args:
        raw_data: Input DataFrame
        outputs: Dictionary of output buckets (DataFrames)
        exclude_buckets: List of bucket names to exclude from count (e.g., ['other'])
    
    Returns:
        Dictionary with validation results
    """
    if exclude_buckets is None:
        exclude_buckets = []
    
    # Count rows in raw data
    raw_row_count = len(raw_data)
    
    # Sum rows from all output buckets
    total_output_rows = 0
    bucket_counts = {}
    
    for bucket_name, df in outputs.items():
        bucket_counts[bucket_name] = len(df)
        if bucket_name not in exclude_buckets:
            total_output_rows += len(df)
    
    # Calculate difference
    difference = raw_row_count - total_output_rows
    
    # Prepare result
    result = {
        "raw_data_rows": raw_row_count,
        "total_output_rows": total_output_rows,
        "difference": difference,
        "is_valid": difference == 0,
        "bucket_counts": bucket_counts
    }
    
    return result


def print_validation_report(raw_data: pd.DataFrame, outputs: dict, exclude_buckets: list = None):
    """Prints a formatted validation report comparing raw data rows to output bucket rows."""
    result = validate_row_counts(raw_data, outputs, exclude_buckets)
    
    print("\n" + "="*60)
    print("ROW COUNT VALIDATION REPORT")
    print("="*60)
    
    print(f"\n📊 Raw Data Rows: {result['raw_data_rows']:,}")
    print(f"📦 Total Output Rows: {result['total_output_rows']:,}")
    print(f"📉 Difference: {result['difference']:,}")
    
    print(f"\n✅ Validation {'PASSED' if result['is_valid'] else 'FAILED'}")
    
    if not result['is_valid']:
        print(f"\n⚠️  Missing {abs(result['difference']):,} row(s) from output buckets!")
    
    print("\n--- Bucket Breakdown ---")
    for bucket, count in result['bucket_counts'].items():
        print(f"  {bucket}: {count:,} row(s)")
    
    print("="*60 + "\n")
    
    return result


def find_row_discrepancies(raw_data: pd.DataFrame, outputs: dict, 
                          compare_columns: list = None,
                          sample_size: int = 10) -> dict:
    """
    Finds discrepancies between raw data and output buckets by comparing row characteristics.
    Since rows can be duplicated, we compare distributions rather than individual rows.
    
    Args:
        raw_data: Input DataFrame
        outputs: Dictionary of output buckets
        compare_columns: List of columns to compare distributions
        sample_size: Number of sample rows to show for debugging
    
    Returns:
        Dictionary with discrepancy analysis
    """
    if compare_columns is None:
        # Default columns to check for routing decisions
        compare_columns = ['DEPARTURE_COUNTRY', 'ARRIVAL_COUNTRY', 'TRANSACTION_TYPE', 
                          'TAX_REPORTING_SCHEME']
        compare_columns = [c for c in compare_columns if c in raw_data.columns]
    
    # Combine all output buckets into one DataFrame
    all_outputs = pd.concat([df for df in outputs.values()], ignore_index=True)
    
    print("\n" + "="*60)
    print("ROW DISCREPANCY ANALYSIS")
    print("="*60)
    
    print(f"\n📊 Total rows in raw: {len(raw_data):,}")
    print(f"📊 Total rows in outputs: {len(all_outputs):,}")
    print(f"📉 Difference: {len(raw_data) - len(all_outputs):,}")
    
    if len(raw_data) == len(all_outputs):
        print("\n✅ Row counts match!")
        return {"matches": True, "difference": 0}
    
    # Analyze distributions to find what might be missing
    print("\n--- Distribution Comparison ---")
    discrepancies = {}
    
    for col in compare_columns:
        if col not in raw_data.columns or col not in all_outputs.columns:
            continue
            
        raw_dist = raw_data[col].value_counts(dropna=False)
        out_dist = all_outputs[col].value_counts(dropna=False)
        
        # Find values that are underrepresented in outputs
        diff = raw_dist.subtract(out_dist, fill_value=0)
        diff = diff[diff != 0]
        
        if not diff.empty:
            discrepancies[col] = diff
            print(f"\n{col}:")
            for val, count_diff in diff.head(5).items():
                print(f"  {val}: {count_diff:+,} row difference")
            if len(diff) > 5:
                print(f"  ... and {len(diff)-5} more")
    
    # Show samples of raw rows not in outputs (by content, not by index)
    print("\n--- Sample rows from raw that might be missing ---")
    
    # Convert outputs to a set of tuples for comparison (sampling to avoid memory issues)
    output_tuples = set()
    sample_cols = ['DEPARTURE_COUNTRY', 'ARRIVAL_COUNTRY', 'TRANSACTION_TYPE']
    sample_cols = [c for c in sample_cols if c in all_outputs.columns]
    
    if sample_cols and len(all_outputs) < 10000:  # Only for manageable datasets
        for _, row in all_outputs[sample_cols].iterrows():
            output_tuples.add(tuple(row.values))
        
        missing_samples = []
        for _, row in raw_data[sample_cols].iterrows():
            if tuple(row.values) not in output_tuples:
                missing_samples.append(row.values)
                if len(missing_samples) >= sample_size:
                    break
        
        if missing_samples:
            print(f"Found {len(missing_samples)} sample rows with unique combinations not in outputs:")
            for sample in missing_samples[:5]:
                print(f"  {dict(zip(sample_cols, sample))}")
        else:
            print("  No obvious missing row patterns found (may be due to other columns)")
    else:
        print("  Skipping detailed row comparison (too many rows or missing columns)")
    
    print("="*60 + "\n")
    
    return {"matches": False, "difference": len(raw_data) - len(all_outputs), "discrepancies": discrepancies}


def analyze_routing_effectiveness(raw_data: pd.DataFrame, outputs: dict) -> dict:
    """
    Analyzes how rows are distributed across buckets and identifies potential routing issues.
    """
    print("\n" + "="*60)
    print("ROUTING EFFECTIVENESS ANALYSIS")
    print("="*60)
    
    # Check which bucket gets the most rows
    bucket_sizes = {name: len(df) for name, df in outputs.items()}
    total_processed = sum(bucket_sizes.values())
    
    print(f"\n📊 Total rows processed: {total_processed:,}")
    print(f"📊 Total rows in raw: {len(raw_data):,}")
    
    if total_processed < len(raw_data):
        print(f"⚠️  {len(raw_data) - total_processed:,} rows are unaccounted for!")
    elif total_processed > len(raw_data):
        print(f"⚠️  {total_processed - len(raw_data):,} extra rows appeared! (possible duplication)")
    
    print("\n--- Bucket Distribution ---")
    for name, size in sorted(bucket_sizes.items(), key=lambda x: x[1], reverse=True):
        percentage = (size / total_processed * 100) if total_processed > 0 else 0
        print(f"  {name}: {size:,} rows ({percentage:.1f}%)")
    
    # Check 'other' bucket content if it exists
    if 'other' in outputs and not outputs['other'].empty:
        print("\n--- 'Other' Bucket Analysis ---")
        other_df = outputs['other']
        
        # Show what's in the 'other' bucket
        for col in ['DEPARTURE_COUNTRY', 'ARRIVAL_COUNTRY', 'TRANSACTION_TYPE']:
            if col in other_df.columns:
                print(f"\n  {col} in 'other':")
                for val, count in other_df[col].value_counts().head(5).items():
                    print(f"    {val}: {count}")
        
        print(f"\n  Total rows in 'other': {len(other_df):,}")
    
    print("="*60 + "\n")
    
    return {
        "total_processed": total_processed,
        "bucket_sizes": bucket_sizes,
        "unaccounted_rows": len(raw_data) - total_processed
    }



