import pandas as pd
import numpy as np
import joblib
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load data
sales_data = pd.read_csv('sales_data.csv', parse_dates=['sales_date'])
new_products = pd.read_csv('new_products.csv', parse_dates=['release_date'])

# Load models and encoders
rf_model = joblib.load('rf_model.pkl')
le_category = joblib.load('le_category.pkl')

# Add season feature
def add_season_feature(df, date_column):
    df['month'] = df[date_column].dt.month
    conditions = [
        (df['month'].isin([1, 2, 3])),
        (df['month'].isin([4, 5, 6])),
        (df['month'].isin([7, 8, 9])),
        (df['month'].isin([10, 11, 12]))
    ]
    choices = [1, 2, 3, 4]
    df['season'] = np.select(conditions, choices, default=0)
    df.drop('month', axis=1, inplace=True)
    return df

sales_data = add_season_feature(sales_data, 'sales_date')
new_products = add_season_feature(new_products, 'release_date')

# Function to predict demand with handling for unseen categories
def predict_demand(category, price, profit, season):
    try:
        category_enc = le_category.transform([category])[0]
    except ValueError:
        category_enc = -1  # or some other default value
    prediction_input = pd.DataFrame([[category_enc, price, profit, season]],
                                    columns=['category_encoded', 'price_per_unit', 'profit', 'season'])
    return rf_model.predict(prediction_input)[0]

# Calculate dynamic thresholds
def calculate_thresholds(df):
    units_sold_thresholds = np.percentile(df['units_sold'], [33, 67])
    profit_thresholds = np.percentile(df['profit'], [33, 67])
    price_per_unit_thresholds = np.percentile(df['price_per_unit'], [33, 67])

    return {
        'units_sold': units_sold_thresholds,
        'profit': profit_thresholds,
        'price_per_unit': price_per_unit_thresholds
    }

# Define dynamic thresholds for non-profitable and profitable products
def categorize_products(df, thresholds):
    non_profitable = df[
        (df['units_sold'] <= thresholds['units_sold'][0]) &
        (df['profit'] <= thresholds['profit'][0]) &
        (df['price_per_unit'] <= thresholds['price_per_unit'][0])
    ]

    profitable = df[
        (df['units_sold'] >= thresholds['units_sold'][1]) &
        (df['profit'] >= thresholds['profit'][1]) &
        (df['price_per_unit'] >= thresholds['price_per_unit'][1])
    ]

    return non_profitable, profitable

# Analysis for past 3 years
cutoff_date_3_years = pd.Timestamp.today() - pd.Timedelta(days=3 * 365)
sales_data_3_years = sales_data[sales_data['sales_date'] >= cutoff_date_3_years]

thresholds_3_years = calculate_thresholds(sales_data_3_years)
non_profitable_3_years, profitable_3_years = categorize_products(sales_data_3_years, thresholds_3_years)

# Analysis for past 28 days
cutoff_date_28_days = pd.Timestamp.today() - pd.Timedelta(days=28)
new_items_28_days = new_products[new_products['release_date'] >= cutoff_date_28_days]

thresholds_28_days = calculate_thresholds(new_items_28_days)
non_profitable_28_days, profitable_28_days = categorize_products(new_items_28_days, thresholds_28_days)

# Suggest reorder points
def suggest_reorder_points(df):
    suggestions = []
    for _, row in df.iterrows():
        predicted_demand = predict_demand(row['category'], row['price_per_unit'], row['profit'], row['season'])
        reorder_point = max(1, int(predicted_demand * 1.5))
        suggestions.append({'product_id': row['product_id'], 'reorder_point': reorder_point})
    return suggestions

# Reorder suggestions for past 3 years
reorder_suggestions_3_years = suggest_reorder_points(sales_data_3_years)

# Reorder suggestions for past 28 days
reorder_suggestions_28_days = suggest_reorder_points(new_items_28_days)

# Convert Timestamp to string for JSON serialization
def convert_timestamps(data):
    for record in data:
        if 'sales_date' in record and isinstance(record['sales_date'], pd.Timestamp):
            record['sales_date'] = record['sales_date'].isoformat()
        if 'release_date' in record and isinstance(record['release_date'], pd.Timestamp):
            record['release_date'] = record['release_date'].isoformat()
    return data

# Create JSON data for analysis results
analysis_results = {
    'past_3_years': {
        'non_profitable_items': convert_timestamps(non_profitable_3_years.to_dict(orient='records')),
        'profitable_items': convert_timestamps(profitable_3_years.to_dict(orient='records')),
        'reorder_suggestions': reorder_suggestions_3_years
    },
    'past_28_days': {
        'non_profitable_items': convert_timestamps(non_profitable_28_days.to_dict(orient='records')),
        'profitable_items': convert_timestamps(profitable_28_days.to_dict(orient='records')),
        'reorder_suggestions': reorder_suggestions_28_days
    }
}

# Save analysis results to a JSON file
with open('analysis_results.json', 'w') as json_file:
    json.dump(analysis_results, json_file, indent=4)

logging.info("Analysis complete and results saved to analysis_results.json.")
