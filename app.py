from flask import Flask, request, jsonify
from analysis import (
    predict_demand,
    reorder_suggestions_3_years, reorder_suggestions_28_days,
    non_profitable_3_years, profitable_3_years,
    non_profitable_28_days, profitable_28_days
)

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    category = data.get('category')
    price_per_unit = data.get('price_per_unit')
    profit = data.get('profit')
    season = data.get('season')
    predicted_demand = predict_demand(category, price_per_unit, profit, season)
    return jsonify({'predicted_demand': predicted_demand})


@app.route('/analysis_results', methods=['GET'])
def get_analysis_results():
    dataset = request.args.get('dataset', '3_years')
    if dataset == '28_days':
        return jsonify({
            'non_profitable_items': non_profitable_28_days.to_dict(orient='records'),
            'profitable_items': profitable_28_days.to_dict(orient='records')
        })
    else:
        return jsonify({
            'non_profitable_items': non_profitable_3_years.to_dict(orient='records'),
            'profitable_items': profitable_3_years.to_dict(orient='records')
        })

if __name__ == '__main__':
    app.run(debug=True)