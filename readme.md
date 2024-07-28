 
# Inventory and Sales Analysis

This project aims to predict the demand for products, categorize products into profitable and non-profitable, and provide reorder suggestions based on historical sales data. It also includes a feature to handle different seasons for more accurate predictions.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Data Preparation](#data-preparation)
4. [Training the Model](#training-the-model)
5. [Running the Analysis](#running-the-analysis)
6. [Starting the Flask Application](#starting-the-flask-application)
7. [API Endpoints](#api-endpoints)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/your-repo/inventory-analysis.git
    cd inventory-analysis
    ```

2. Create and activate a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Data Preparation

Prepare your CSV files with the following format:

#### sales_data.csv
```csv
product_id,category,sales_date,units_sold,price_per_unit,profit,season
1,Cheese - Mix,2021-07-03,6393,13.54,1,1
2,Chocolate - Milk Coating,2021-07-12,3810,41.82,8,4
3,Chocolate - Dark Callets,2021-07-16,4979,50.42,1,2
...
```

#### new_products.csv
```csv
product_id,category,release_date,units_sold,price_per_unit,profit,season
1,Cheese - Mix,2024-07-03,6393,13.54,1,1
2,Chocolate - Milk Coating,2024-07-12,3810,41.82,8,4
3,Chocolate - Dark Callets,2024-07-16,4979,50.42,1,2
...
```

### Training the Model

1. Open `trainer.ipynb` in `Jupyter Notebook`:
    ```sh
    jupyter notebook trainer.ipynb
    ```

2. Run all cells to train the model and save the encoders. The model and encoders will be saved as `rf_model.pkl` and `le_category.pkl` respectively.

### Running the Analysis

1. Run `analysis.py` to perform the analysis and save the results:
    ```sh
    python analysis.py
    ```

2. The analysis results will be saved in `analysis_results.json`.

### Starting the Flask Application

1. Start the Flask application:
    ```sh
    python app.py
    ```

2. The Flask application will be available at `http://127.0.0.1:5000`.

## API Endpoints

### /predict

- **Method**: POST
- **Description**: Predict the demand for a product.
- **Endpoint**: `/predict`
- **Request Body**:
    ```json
    {
        "category": "Cheese - Mix",
        "price_per_unit": 13.54,
        "profit": 1,
        "season": 1
    }
    ```
- **Response**:
    ```json
    {
        "predicted_demand": 6393
    }
    ```

### /reorder_suggestions

- **Method**: GET
- **Description**: Get reorder suggestions.
- **Endpoint**: `/reorder_suggestions`
- **Query Parameters**:
    - `dataset`: Can be `3_years` (default) or `28_days`.
- **Response**:
    ```json
    [
        {
            "product_id": 1,
            "reorder_point": 9590
        },
        
    ]
    ```

### /analysis_results

- **Method**: GET
- **Description**: Get the analysis results for non-profitable and profitable items.
- **Endpoint**: `/analysis_results`
- **Query Parameters**:
    - `dataset`: Can be `3_years` (default) or `28_days`.
- **Response**:
    ```json
    {
        "non_profitable_items": [
            {
                "product_id": 1,
                "category": "Cheese - Mix",
                "sales_date": "2021-07-03T00:00:00",
                "units_sold": 6393,
                "price_per_unit": 13.54,
                "profit": 1,
                "season": 1
            },
            
        ],
        "profitable_items": [
            {
                "product_id": 2,
                "category": "Chocolate - Milk Coating",
                "sales_date": "2021-07-12T00:00:00",
                "units_sold": 3810,
                "price_per_unit": 41.82,
                "profit": 8,
                "season": 4
            },
            
        ]
    }
    ```
 