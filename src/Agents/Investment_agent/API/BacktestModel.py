import os
import json
from datetime import datetime

import pandas as pd
import torch
import yfinance as yf
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report
)
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import ta  # technical indicators

# ─── CONFIG ────────────────────────────────────────────────────────────────
TICKERS      = [
    'AAPL','MSFT','NVDA','AMD','JNJ','PFE','JPM','GS',
    'KO','PEP','XOM','NEE','CVX','WMT','HD','GME',
    'TSLA','F','COIN','MRNA'
]
BACKTEST_DIR = "data/backtest"
os.makedirs(BACKTEST_DIR, exist_ok=True)

# Backtest window
START_DATE = "2025-01-01"
END_DATE   = datetime.today().strftime("%Y-%m-%d")

# Model dirs
MODEL_DIR  = "./finbert_finetuned_10y"
BASE_MODEL = "ProsusAI/finbert"

# ─── 1) FETCH RAW (SKIP IF EXISTS) ────────────────────────────────────────
def fetch_backtest():
    for sym in TICKERS:
        out_path = os.path.join(BACKTEST_DIR, f"{sym}.csv")
        if os.path.exists(out_path):
            print(f"[SKIP] {sym}.csv already exists")
            continue
        print(f"Fetching {sym} {START_DATE}→{END_DATE}")
        df = yf.download(sym, start=START_DATE, end=END_DATE, progress=False)
        if df is None or df.empty:
            print(f"  [WARN] no data for {sym}")
            continue
        df.index.name = "Date"
        df.to_csv(out_path)

# ─── 2) LOAD & CLEAN ───────────────────────────────────────────────────────
def load_and_clean(path):
    """
    Read CSV using first column as index, then convert that index to datetime.
    Ensure OHLCV columns are numeric and drop NaNs.
    """
    # 1) Read, treat the first column as index, no parse_dates
    df = pd.read_csv(path, index_col=0)
    # 2) Convert index to datetime, drop rows where it fails
    df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[~df.index.isna()]
    df.index.name = "Date"

    # 3) Convert key columns to numeric
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # 4) Drop any rows missing core data
    df.dropna(subset=["Open", "High", "Low", "Close", "Volume"], inplace=True)

    return df

# ─── 3) BUILD PROMPTS & TRUE LABELS ────────────────────────────────────────
def build_backtest_dataset():
    records = []
    for sym in TICKERS:
        path = os.path.join(BACKTEST_DIR, f"{sym}.csv")
        if not os.path.exists(path):
            print(f"[WARN] Missing {path}")
            continue
        df = load_and_clean(path)
        if len(df) < 2:
            continue

        # Technical indicators
        df["SMA20"] = df["Close"].rolling(20).mean()
        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["RSI14"] = ta.momentum.RSIIndicator(df["Close"],14).rsi()
        macd = ta.trend.MACD(df["Close"])
        df["MACD"]        = macd.macd()
        df["MACD_signal"] = macd.macd_signal()
        df["MACD_diff"]   = macd.macd_diff()
        df["OBV"]         = ta.volume.OnBalanceVolumeIndicator(
                                df["Close"], df["Volume"]
                            ).on_balance_volume()
        df["ATR14"] = ta.volatility.AverageTrueRange(
                            df["High"], df["Low"], df["Close"],14
                        ).average_true_range()

        # True label: tomorrow Up (1) or Down (0)
        df["target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
        df = df.dropna(subset=[
            "target","SMA20","EMA20","RSI14",
            "MACD","OBV","ATR14"
        ])
        df["true_label"] = df["target"].map({1:"Up",0:"Down"})

        # Build prompts
        for date, row in df.iterrows():
            # Now date is a Timestamp, so .date() works
            prompt = (
                f"Stock: {sym}, Date: {date.date()}, Close: {row.Close:.2f}, "
                f"SMA20: {row.SMA20:.2f}, EMA20: {row.EMA20:.2f}, RSI14: {row.RSI14:.2f}, "
                f"MACD: {row.MACD:.2f}, OBV: {int(row.OBV)}, ATR14: {row.ATR14:.2f}. "
                "Predict if tomorrow's price will go Up or Down:"
            )
            records.append({
                "ticker": sym,
                "date": date,
                "prompt": prompt,
                "true_label": row.true_label
            })
    return pd.DataFrame(records)

# ─── 4) LOAD BEST CHECKPOINT ────────────────────────────────────────────────
def get_best_checkpoint(model_dir):
    # Try reading trainer_state.json
    state_file = os.path.join(model_dir, "trainer_state.json")
    if os.path.isfile(state_file):
        state = json.load(open(state_file))
        best = state.get("best_model_checkpoint")
        if best:
            p = os.path.join(model_dir, best)
            if os.path.isdir(p):
                return p
    # Fallback: pick highest checkpoint-*
    ckpts = [
        os.path.join(model_dir, d)
        for d in os.listdir(model_dir)
        if d.startswith("checkpoint-") and os.path.isdir(os.path.join(model_dir,d))
    ]
    if not ckpts:
        raise FileNotFoundError(f"No checkpoints in {model_dir}")
    return sorted(ckpts)[-1]

device    = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

ckpt_dir = get_best_checkpoint(MODEL_DIR)
print(f"→ Loading best checkpoint from {ckpt_dir}")
model = AutoModelForSequenceClassification.from_pretrained(ckpt_dir)
model.to(device)
model.eval()

# ─── 5) INFERENCE ───────────────────────────────────────────────────────────
def infer(df):
    preds, probs, trues = [], [], []
    for _, row in df.iterrows():
        tok = tokenizer(
            row.prompt,
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=128
        ).to(device)
        with torch.no_grad():
            out = model(**tok)
            logits = out.logits.squeeze(0)
            sm     = torch.softmax(logits, dim=0).cpu().numpy()
            idx    = int(sm.argmax())
        preds.append("Up" if idx==1 else "Down")
        probs.append(float(sm[idx]))
        trues.append(row.true_label)
    df["predicted"]  = preds
    df["confidence"] = probs
    df["true_label"] = trues
    return df

# ─── 6) EVALUATION ─────────────────────────────────────────────────────────
def evaluate(df):
    y_true = df["true_label"]
    y_pred = df["predicted"]
    acc    = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", pos_label="Up"
    )
    print("\nBacktest Metrics (Up=positive):")
    print(f"  Accuracy : {acc:.3f}")
    print(f"  Precision: {prec:.3f}")
    print(f"  Recall   : {rec:.3f}")
    print(f"  F1-score : {f1:.3f}\n")
    print("Classification report:")
    print(classification_report(y_true, y_pred, digits=3))
    print("\nTop 10 high‑confidence predictions:")
    sample = df.sort_values("confidence", ascending=False).head(10)
    print(sample[["ticker","date","true_label","predicted","confidence"]].to_string(index=False))

# ─── MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("1) Fetching raw backtest data…")
    fetch_backtest()

    print("\n2) Building dataset…")
    backtest_df = build_backtest_dataset()
    print(f"  Examples: {len(backtest_df)}")

    print("\n3) Running inference…")
    results_df = infer(backtest_df)

    print("\n4) Evaluating…")
    evaluate(results_df)
