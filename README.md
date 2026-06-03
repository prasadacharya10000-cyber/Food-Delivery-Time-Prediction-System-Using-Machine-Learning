# Food Delivery Time Predictor

A machine learning web application that predicts food delivery times based on order details, powered by a Flask REST API and a responsive Bootstrap frontend.

## Features
- ML regression model trained on real food delivery data
- Predicts delivery time based on distance, order size, weather, and traffic
- REST API for predictions
- Responsive web UI built with Bootstrap
- MySQL-backed order data

## Tech Stack
Python · Flask · scikit-learn · pandas · Bootstrap · MySQL · JavaScript

## Getting Started

### Installation
```bash
git clone https://github.com/prasadacharya10000-cyber/food-delivery-time-predictor.git
cd food-delivery-time-predictor
pip install -r requirements.txt
```

### Database Setup
```bash
mysql -u root -p < food.sql
```

### Run
```bash
python app.py
```
Open http://localhost:5000

## Model
- Algorithm: Linear Regression + ensemble models
- Dataset: Food_Delivery_Times.xls (included)
- Trained model saved as `delivery_time_model.pkl`
