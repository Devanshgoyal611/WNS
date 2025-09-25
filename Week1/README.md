# Wine Clustering Project

## Project Overview
This project applies unsupervised machine learning techniques to perform clustering analysis on wine data. The goal is to identify distinct groups or clusters within the wine dataset based on various chemical properties, which could help in categorizing wines or understanding patterns in wine characteristics.

The project includes:
- Exploratory data analysis and preprocessing
- Multiple clustering algorithms (K-Means, DBSCAN, Hierarchical Clustering)
- Model evaluation and comparison
- An interactive Streamlit web application for clustering visualization

## Project Structure
```
WEEK1/
├── app/
│   └── WineClustering.py          # Streamlit application
├── data/
│   └── Wine-dataset.csv              # Dataset used for analysis
├── notebook/
│   └── WineCluster.ipynb          # Jupyter notebook with full analysis
├── saved_models/
│   ├── kmeans_model.pkl           # Saved K-Means model
│   ├── scaler.pkl                 # Saved StandardScaler
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Installation and Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd WEEK1
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Navigate to the app directory**
   ```bash
   cd app
   ```

2. **Start the Streamlit application**
   ```bash
   streamlit run WineClustering.py
   ```

3. **Access the application**
   - The application will open in your default web browser
   - If it doesn't open automatically, go to `http://localhost:8501`

## Usage

### Streamlit Application
The interactive web application allows you to know which cluster the alcohol belongs to based on it's chemical composition

### Jupyter Notebook
The notebook (`notebook/WineCluster.ipynb`) contains the complete analysis including:
- Data loading and exploration
- Data preprocessing and feature engineering
- Implementation of various clustering algorithms
- Model evaluation and comparison
- Visualization of results

## Data Description
The dataset contains various chemical properties of wines that are used as features for clustering. Key attributes may include:
- Alcohol content
- Malic acid
- Ash
- Alkalinity of ash
- Magnesium
- Total phenols
- Flavanoids
- Nonflavanoid phenols
- Proanthocyanins
- Color intensity
- Hue
- OD280/OD315 of diluted wines
- Proline

## Clustering Algorithms
The project implements and compares several clustering approaches:
- **K-Means**: Partition-based clustering with specified number of clusters
- **DBSCAN**: Density-based clustering that identifies outliers
- **Hierarchical Clustering**: Builds a hierarchy of clusters

## Model Persistence
Trained models are saved as pickle files in the `saved_models/` directory for reuse in the Streamlit application without retraining.

## Dependencies
Key Python packages required for this project:
- streamlit
- pandas
- numpy
- scikit-learn
- matplotlib
- seaborn
- jupyter
- pickle

See `requirements.txt` for the complete list of dependencies with versions.