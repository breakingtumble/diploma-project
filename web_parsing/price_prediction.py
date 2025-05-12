import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import psycopg2
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
import math

# ------------------------------------------------------
# 1. Database Connection (psycopg2 for cursor batching)
# ------------------------------------------------------
def get_db_connection():
    return psycopg2.connect(
        dbname   = os.getenv("DB_NAME",     "parse_db"),
        user     = os.getenv("DB_USER",     "parser"),
        password = os.getenv("DB_PASSWORD", "123456"),
        host     = os.getenv("DB_HOST",     "localhost"),
        port     = os.getenv("DB_PORT",     "5432")
    )

# ------------------------------------------------------
# 2. SQLAlchemy engine for bulk inserts & reads
# ------------------------------------------------------
def get_sqlalchemy_engine():
    user = os.getenv("DB_USER", "parser")
    pw   = os.getenv("DB_PASSWORD", "123456")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    db   = os.getenv("DB_NAME", "parse_db")
    url  = f"postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}"
    return create_engine(url)

# ------------------------------------------------------
# 3. Fetch product IDs in batches
# ------------------------------------------------------
def fetch_product_id_batches(batch_size=1000):
    conn = get_db_connection()
    cur  = conn.cursor(name="prod_id_cursor")
    cur.itersize = batch_size
    try:
        cur.execute("SELECT id FROM products")
        while True:
            rows = cur.fetchmany(batch_size)
            if not rows:
                break
            yield [r[0] for r in rows]
    finally:
        cur.close()
        conn.close()

# ------------------------------------------------------
# 4. Fetch price history for one product
# ------------------------------------------------------
def fetch_price_history(product_id):
    sql = """
        SELECT etl_date, price_proceeded AS price
        FROM parsed_products
        WHERE product_id = %s
        ORDER BY etl_date
    """
    engine = get_sqlalchemy_engine()
    df     = pd.read_sql(sql, con=engine, params=(product_id,))
    df['etl_date'] = pd.to_datetime(df['etl_date'])
    return df

# ------------------------------------------------------
# 5. Preprocess & remove outliers
# ------------------------------------------------------
def preprocess(df):
    df = df.dropna(subset=['price']).copy()
    mu, sigma = df['price'].mean(), df['price'].std()
    mask = (df['price'] >= mu - 3*sigma) & (df['price'] <= mu + 3*sigma)
    return df.loc[mask].sort_values('etl_date')

# ------------------------------------------------------
# 6. Feature engineering
# ------------------------------------------------------
def engineer_features(df):
    df = df.copy()
    df['t']    = (df['etl_date'] - df['etl_date'].min()).dt.days
    df['dow']  = df['etl_date'].dt.dayofweek
    df['lag1'] = df['price'].shift(1)
    df['ma7']  = df['price'].rolling(7, min_periods=1).mean()
    df = df.dropna()
    X = df[['t', 'dow', 'lag1', 'ma7']]
    y = df['price']
    return X, y, df

# ------------------------------------------------------
# 7. Train & evaluate models
# ------------------------------------------------------
def train_and_evaluate(X, y):
    tscv   = TimeSeriesSplit(n_splits=3)
    models = {'OLS': LinearRegression(), 'Ridge': Ridge(alpha=1.0)}
    results = {}
    for name, model in models.items():
        mae_list, rmse_list = [], []
        for train_idx, test_idx in tscv.split(X):
            X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
            y_tr, y_te = y.iloc[train_idx], y.iloc[test_idx]
            model.fit(X_tr, y_tr)
            pred = model.predict(X_te)
            mae_list.append(mean_absolute_error(y_te, pred))
            rmse_list.append(math.sqrt(mean_squared_error(y_te, pred)))
        results[name] = {
            'MAE':  np.mean(mae_list),
            'RMSE': np.mean(rmse_list)
        }
    # retrain best (Ridge) on full set
    best = Ridge(alpha=1.0)
    best.fit(X, y)
    return results, best

# ------------------------------------------------------
# 8. Predict + change-index
# ------------------------------------------------------
def predict_and_index(model, df, days_ahead=1):
    last_dt = df['etl_date'].max()
    future  = last_dt + timedelta(days=days_ahead)
    t0      = df['etl_date'].min()
    t       = (future - t0).days
    dow     = future.dayofweek
    lag1    = df.loc[df['etl_date']==last_dt, 'price'].iloc[0]
    ma7     = df[df['etl_date'] > last_dt - timedelta(days=7)]['price'].mean()
    X_new   = pd.DataFrame({'t':[t],'dow':[dow],'lag1':[lag1],'ma7':[ma7]})
    pred    = float(model.predict(X_new)[0])
    change  = (pred - lag1) / lag1 * 100
    return pred, future, change

# ------------------------------------------------------
# 9. Bulk insert predictions
# ------------------------------------------------------
def insert_predictions_batch(records):
    engine = get_sqlalchemy_engine()
    df = pd.DataFrame(records)
    df.to_sql(
        'product_price_predictions',
        con=engine,
        if_exists='append',
        index=False,
        method='multi'
    )

# ------------------------------------------------------
# 10. Orchestration: batch over all products
# ------------------------------------------------------
def batch_main(days_ahead=30):
    for batch in fetch_product_id_batches(batch_size=1000):
        preds = []
        now   = datetime.now()
        for pid in batch:
            hist = fetch_price_history(pid)
            if len(hist) < 5:
                continue
            clean = preprocess(hist)
            X, y, feat = engineer_features(clean)
            _, model = train_and_evaluate(X, y)
            price, fut_dt, ch_idx = predict_and_index(model, clean, days_ahead)
            preds.append({
                'product_id':      pid,
                'predicted_price': price,
                'change_index':    ch_idx,
                'etl_date':        now
            })
        if preds:
            insert_predictions_batch(preds)
            print(f"Inserted {len(preds)} predictions for this batch at {now.isoformat()}")
    print("All batches processed.")

if __name__ == '__main__':
    batch_main(days_ahead=30)