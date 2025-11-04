import pandas as pd
import json
import io
from typing import Dict, Any, List
import csv

def csv_parser(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Parse CSV string and return summary statistics"""
    try:
        csv_string = payload.get('csv_data', '')
        df = pd.read_csv(io.StringIO(csv_string))
        
        return {
            'success': True,
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'summary': df.describe().to_dict(),
            'head': df.head(5).to_dict(orient='records')
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def json_validator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate JSON structure"""
    try:
        json_string = payload.get('json_data', '')
        parsed = json.loads(json_string)
        return {
            'success': True,
            'valid': True,
            'type': type(parsed).__name__,
            'keys': list(parsed.keys()) if isinstance(parsed, dict) else None
        }
    except json.JSONDecodeError as e:
        return {'success': True, 'valid': False, 'error': str(e)}

def data_aggregator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Aggregate data by specified column"""
    try:
        data = payload.get('data', [])
        group_by = payload.get('group_by', '')
        agg_column = payload.get('aggregate_column', '')
        
        df = pd.DataFrame(data)
        result = df.groupby(group_by)[agg_column].agg(['sum', 'mean', 'count']).to_dict()
        
        return {'success': True, 'aggregation': result}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def data_filter(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Filter data based on conditions"""
    try:
        data = payload.get('data', [])
        column = payload.get('column', '')
        operator = payload.get('operator', '>')
        value = payload.get('value', 0)
        
        df = pd.DataFrame(data)
        
        if operator == '>':
            filtered = df[df[column] > value]
        elif operator == '<':
            filtered = df[df[column] < value]
        elif operator == '==':
            filtered = df[df[column] == value]
        else:
            return {'success': False, 'error': 'Invalid operator'}
        
        return {
            'success': True,
            'filtered_count': len(filtered),
            'data': filtered.to_dict(orient='records')
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def data_sorter(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Sort data by column"""
    try:
        data = payload.get('data', [])
        sort_by = payload.get('sort_by', '')
        ascending = payload.get('ascending', True)
        
        df = pd.DataFrame(data)
        sorted_df = df.sort_values(by=sort_by, ascending=ascending)
        
        return {
            'success': True,
            'data': sorted_df.to_dict(orient='records')
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def deduplicator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Remove duplicate rows"""
    try:
        data = payload.get('data', [])
        column = payload.get('column', None)
        
        df = pd.DataFrame(data)
        original_count = len(df)
        
        if column:
            df_dedup = df.drop_duplicates(subset=[column])
        else:
            df_dedup = df.drop_duplicates()
        
        return {
            'success': True,
            'original_count': original_count,
            'deduplicated_count': len(df_dedup),
            'duplicates_removed': original_count - len(df_dedup),
            'data': df_dedup.to_dict(orient='records')
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def data_merger(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two datasets"""
    try:
        data1 = payload.get('data1', [])
        data2 = payload.get('data2', [])
        on_column = payload.get('on', '')
        how = payload.get('how', 'inner')
        
        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)
        
        merged = pd.merge(df1, df2, on=on_column, how=how)
        
        return {
            'success': True,
            'merged_count': len(merged),
            'data': merged.to_dict(orient='records')
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def column_renamer(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Rename columns in dataset"""
    try:
        data = payload.get('data', [])
        rename_map = payload.get('rename_map', {})
        
        df = pd.DataFrame(data)
        df_renamed = df.rename(columns=rename_map)
        
        return {
            'success': True,
            'old_columns': list(df.columns),
            'new_columns': list(df_renamed.columns),
            'data': df_renamed.to_dict(orient='records')
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def missing_value_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle missing values in dataset"""
    try:
        data = payload.get('data', [])
        strategy = payload.get('strategy', 'drop')  # drop, fill, mean, median
        fill_value = payload.get('fill_value', 0)
        
        df = pd.DataFrame(data)
        missing_count = df.isnull().sum().sum()
        
        if strategy == 'drop':
            df_cleaned = df.dropna()
        elif strategy == 'fill':
            df_cleaned = df.fillna(fill_value)
        elif strategy == 'mean':
            df_cleaned = df.fillna(df.mean(numeric_only=True))
        elif strategy == 'median':
            df_cleaned = df.fillna(df.median(numeric_only=True))
        else:
            return {'success': False, 'error': 'Invalid strategy'}
        
        return {
            'success': True,
            'missing_values_found': int(missing_count),
            'rows_before': len(df),
            'rows_after': len(df_cleaned),
            'data': df_cleaned.to_dict(orient='records')
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def data_transpose(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Transpose dataset"""
    try:
        data = payload.get('data', [])
        df = pd.DataFrame(data)
        transposed = df.transpose()
        
        return {
            'success': True,
            'original_shape': df.shape,
            'transposed_shape': transposed.shape,
            'data': transposed.to_dict()
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def column_selector(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Select specific columns from dataset"""
    try:
        data = payload.get('data', [])
        columns = payload.get('columns', [])
        
        df = pd.DataFrame(data)
        selected = df[columns]
        
        return {
            'success': True,
            'selected_columns': columns,
            'data': selected.to_dict(orient='records')
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def row_slicer(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Slice rows from dataset"""
    try:
        data = payload.get('data', [])
        start = payload.get('start', 0)
        end = payload.get('end', None)
        
        df = pd.DataFrame(data)
        sliced = df[start:end]
        
        return {
            'success': True,
            'total_rows': len(df),
            'sliced_rows': len(sliced),
            'data': sliced.to_dict(orient='records')
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def data_groupby(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Group data and apply aggregation"""
    try:
        data = payload.get('data', [])
        group_by = payload.get('group_by', '')
        agg_func = payload.get('agg_func', 'sum')  # sum, mean, count, min, max
        
        df = pd.DataFrame(data)
        grouped = df.groupby(group_by).agg(agg_func).to_dict()
        
        return {
            'success': True,
            'grouped_by': group_by,
            'aggregation': agg_func,
            'result': grouped
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def csv_to_json(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convert CSV to JSON"""
    try:
        csv_data = payload.get('csv_data', '')
        df = pd.read_csv(io.StringIO(csv_data))
        json_data = df.to_dict(orient='records')
        
        return {
            'success': True,
            'records': len(json_data),
            'data': json_data
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def json_to_csv(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convert JSON to CSV"""
    try:
        json_data = payload.get('json_data', [])
        df = pd.DataFrame(json_data)
        csv_string = df.to_csv(index=False)
        
        return {
            'success': True,
            'csv_data': csv_string
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def data_pivot(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Pivot data table"""
    try:
        data = payload.get('data', [])
        index = payload.get('index', '')
        columns = payload.get('columns', '')
        values = payload.get('values', '')
        
        df = pd.DataFrame(data)
        pivoted = df.pivot(index=index, columns=columns, values=values)
        
        return {
            'success': True,
            'data': pivoted.to_dict()
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def data_describe(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Get statistical description of dataset"""
    try:
        data = payload.get('data', [])
        df = pd.DataFrame(data)
        description = df.describe(include='all').to_dict()
        
        return {
            'success': True,
            'statistics': description
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def column_dropper(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Drop specified columns"""
    try:
        data = payload.get('data', [])
        columns_to_drop = payload.get('columns', [])
        
        df = pd.DataFrame(data)
        df_dropped = df.drop(columns=columns_to_drop)
        
        return {
            'success': True,
            'dropped_columns': columns_to_drop,
            'remaining_columns': list(df_dropped.columns),
            'data': df_dropped.to_dict(orient='records')
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def data_sampler(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Sample random rows from dataset"""
    try:
        data = payload.get('data', [])
        n = payload.get('n', 5)
        
        df = pd.DataFrame(data)
        sampled = df.sample(n=min(n, len(df)))
        
        return {
            'success': True,
            'total_rows': len(df),
            'sampled_rows': len(sampled),
            'data': sampled.to_dict(orient='records')
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def value_counter(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Count unique values in a column"""
    try:
        data = payload.get('data', [])
        column = payload.get('column', '')
        
        df = pd.DataFrame(data)
        value_counts = df[column].value_counts().to_dict()
        
        return {
            'success': True,
            'column': column,
            'unique_values': len(value_counts),
            'counts': value_counts
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}