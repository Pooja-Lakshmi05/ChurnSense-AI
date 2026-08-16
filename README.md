# ChurnSense AI

## An AI-Driven Customer Lifetime Value Prediction System

ChurnSense AI is an AI-driven customer lifecycle intelligence platform designed to help businesses identify customers at risk of churn, analyze engagement patterns, and estimate Customer Lifetime Value (CLV).

The system integrates three machine learning models — Engagement Prediction, Churn Prediction, and Customer Lifetime Value (CLV) Estimation — and combines their outputs into a unified Customer Health Score. The results are presented through an interactive Streamlit dashboard to support data-driven customer retention strategies.

## 🎯 Objectives

- Predict customers who are at risk of churn
- Analyze customer engagement levels
- Estimate Customer Lifetime Value
- Generate a unified Customer Health Score
- Identify priority customer segments for retention
- Provide actionable insights through an interactive dashboard

## 🧠 Machine Learning Architecture

ChurnSense AI consists of three integrated prediction modules:

### 1. Engagement Prediction

An **XGBoost Classifier** is used to classify customers into:

- Low Engagement
- Medium Engagement
- High Engagement

The model uses behavioral signals such as login frequency, session duration, email open rate, app usage, and cart activity.

### 2. Churn Prediction

A **Random Forest Classifier** predicts the probability of customer churn using behavioral and transactional features.

The system generates:

- Churn Probability
- Churn Prediction

### 3. Customer Lifetime Value Prediction

A **Random Forest Regressor** estimates the predicted lifetime value of each customer using purchase history, transaction frequency, average order value, and customer tenure.

## 📊 Customer Health Score

The outputs from the three models are combined into a unified Customer Health Score.

The score considers:

- Churn Probability
- Engagement Strength
- Customer Lifetime Value

Customers are categorized as:

- **Healthy**
- **Moderate**
- **Critical**

This allows businesses to prioritize customers who require retention interventions.

## 🔄 Data Processing

The project uses a 50,000-customer e-commerce dataset containing 42 behavioral and transactional features.

The preprocessing pipeline includes:

- Missing value handling
- Categorical encoding
- Min-Max normalization
- SMOTE-based class balancing
- Feature engineering

Feature engineering expands the original dataset to 73 structured features.

## 📈 Dashboard

The interactive dashboard is developed using **Streamlit** and provides:

- Customer churn analysis
- Engagement analysis
- Customer Lifetime Value insights
- Customer Health Scores
- Platform-wise analytics
- Customer segmentation
- Interactive filtering
- Retention recommendations

## 🚨 Intervention Engine

The system provides rule-based retention recommendations based on customer risk and value.

Examples include:

- Priority VIP Rescue
- Urgent Win-Back Campaign
- Personalized Discount Coupons
- Re-Engagement Push Notifications
- Dedicated Support Escalation

## 🛠️ Technology Stack

- Python
- Machine Learning
- Pandas
- Scikit-learn
- XGBoost
- Streamlit
- HTML/CSS

## 📊 Dataset

The project was developed using a 50,000-customer e-commerce dataset containing behavioral, transactional, demographic, and platform usage information.

The dataset covers customers across:

- Amazon
- Flipkart
- Meesho
- Myntra

## 👩‍💻 Role

**Individual Project**

Designed and developed the project, including the data processing pipeline, machine learning models, customer health scoring approach, and interactive Streamlit dashboard.

## 📌 Key Outcomes

The system integrates multiple predictive models into a unified customer lifecycle intelligence platform.

The models produced:

- Churn probability predictions
- Customer engagement classifications
- Customer Lifetime Value estimates
- Customer Health Scores
- Customer-specific retention recommendations

## 🔮 Future Improvements

- Deploy the application as a publicly accessible web application
- Improve model performance through additional hyperparameter tuning
- Integrate real-time customer data
- Implement automated model retraining
- Expand customer segmentation and recommendation capabilities

## 📄 Research Paper

**ChurnSense AI: An AI-Driven Customer Lifetime Value Prediction System**

Conference research paper covering the architecture, machine learning methodology, Customer Health Score, dashboard, and results of the ChurnSense AI system.

## ⚠️ Repository Note

Some trained model files exceed GitHub's standard browser upload size limit and are therefore not included in this repository.

Sensitive files containing user account information are intentionally excluded from the public repository.
