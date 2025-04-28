import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
from ta.trend import MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

def calculate_technical_indicators(df):
    """Calculate professional-grade technical indicators"""
    # MACD (12,26,9)
    macd = MACD(close=df['Close'], 
                window_slow=26,
                window_fast=12, 
                window_sign=9)
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_hist'] = macd.macd_diff()  # Histogram
    
    # RSI (14 period)
    rsi = RSIIndicator(close=df['Close'], window=14)
    df['rsi'] = rsi.rsi()
    
    # ATR (14 period)
    atr = AverageTrueRange(high=df['High'],
                          low=df['Low'],
                          close=df['Close'],
                          window=14)
    df['atr'] = atr.average_true_range()
    
    # Bollinger Bands (20,2)
    df['sma20'] = df['Close'].rolling(20).mean()
    df['upper_band'] = df['sma20'] + 2*df['Close'].rolling(20).std()
    df['lower_band'] = df['sma20'] - 2*df['Close'].rolling(20).std()
    df['bollinger_pct'] = (df['Close'] - df['lower_band']) / (df['upper_band'] - df['lower_band'])
    
    # Volume features
    df['volume_ma10'] = df['Volume'].rolling(10).mean()
    df['volume_ratio'] = df['Volume'] / df['volume_ma10']
    
    return df

def create_lagged_features(df, lookback=3):
    """Create lagged features to avoid lookahead bias"""
    features = ['macd', 'macd_signal', 'macd_hist', 'rsi', 'atr',
               'bollinger_pct', 'volume_ratio', 'Close']
    
    for feature in features:
        for lag in range(1, lookback+1):
            df[f'{feature}_lag{lag}'] = df.groupby('ticker')[feature].shift(lag)
    
    # Price change targets
    for days in [1, 3, 5]:  # Multiple horizons
        df[f'target_{days}d'] = (df.groupby('ticker')['Close'].shift(-days) > df['Close']).astype(int)
    
    return df.dropna()

def prepare_datasets(df, target_days=1):
    """Prepare train/test sets with time-based split"""
    features = [col for col in df.columns if '_lag' in col]
    target = f'target_{target_days}d'
    
    # Time-based split
    split_date = df['Date'].quantile(0.8)
    train = df[df['Date'] < split_date]
    test = df[df['Date'] >= split_date]
    
    X_train = train[features]
    y_train = train[target]
    X_test = test[features]
    y_test = test[target]
    
    # Scale features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    return X_train, y_train, X_test, y_test

def train_evaluate_model(X_train, y_train, X_test, y_test):
    """Train and evaluate XGBoost model"""
    model = XGBClassifier(
        n_estimators=1000,
        max_depth=4,
        learning_rate=0.01,
        subsample=0.8,
        colsample_bytree=0.8,
        early_stopping_rounds=50,
        random_state=42,
        eval_metric='auc',
        tree_method='gpu_hist'  # Remove if no GPU
    )
    
    # Train with validation set
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.2, shuffle=False)
    
    model.fit(X_train, y_train,
             eval_set=[(X_val, y_val)],
             verbose=50)
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:,1]
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    print(f"\nAUC-ROC: {roc_auc_score(y_test, y_proba):.4f}")
    
    # Plot feature importance
    plt.figure(figsize=(12,8))
    xgb.plot_importance(model, max_num_features=20)
    plt.show()

if __name__ == "__main__":
    # Load data
    df = pd.read_csv('modified_data.csv', parse_dates=['Date'])
    df = df.sort_values(['ticker', 'Date'])
    
    # Calculate indicators
    df = df.groupby('ticker').apply(calculate_technical_indicators)
    
    # Create lagged features
    df = create_lagged_features(df)
    
    # Train model for 1-day prediction
    X_train, y_train, X_test, y_test = prepare_datasets(df, target_days=1)
    train_evaluate_model(X_train, y_train, X_test, y_test)