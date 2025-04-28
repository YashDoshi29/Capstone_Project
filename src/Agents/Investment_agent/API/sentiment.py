# import pandas as pd
# from transformers import pipeline
# import nltk
# nltk.download('vader_lexicon')
# from nltk.sentiment.vader import SentimentIntensityAnalyzer

# # Initialize models for RoBERTa and FinBERT sentiment analysis
# roberta_pipeline = pipeline("sentiment-analysis", model="roberta-base", tokenizer="roberta-base")
# finbert_pipeline = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone", tokenizer="yiyanghkust/finbert-tone")

# # Initialize VADER sentiment analyzer
# vader_analyzer = SentimentIntensityAnalyzer()

# # Function to get sentiment from RoBERTa
# def roberta_sentiment(text):
#     result = roberta_pipeline(text)[0]
#     return result['label']

# # Function to get sentiment from VADER
# def vader_sentiment(text):
#     score = vader_analyzer.polarity_scores(text)
#     if score['compound'] >= 0.05:
#         return 'Positive'
#     elif score['compound'] <= -0.05:
#         return 'Negative'
#     else:
#         return 'Neutral'

# # Function to get sentiment from FinBERT
# def finbert_sentiment(text):
#     result = finbert_pipeline(text)[0]
#     return result['label']

# # Function to combine the three models (Ensemble)
# def ensemble_sentiment(roberta_label, vader_label, finbert_label):
#     labels = [roberta_label, vader_label, finbert_label]
#     # Count the occurrences of each sentiment and return the one with the most votes
#     most_common = max(set(labels), key=labels.count)
#     return most_common

# # Load your dataset
# file_path = '/Users/yashdoshi/capstone5/Capstone_Project/src/app/src/API/stock_news_master.csv'
# stock_news_df = pd.read_csv(file_path)

# # Apply sentiment analysis using RoBERTa, VADER, and FinBERT, then combine the results
# final_sentiments = []
# for content in stock_news_df['content']:
#     roberta_label = roberta_sentiment(content)
#     vader_label = vader_sentiment(content)
#     finbert_label = finbert_sentiment(content)
    
#     # Combine the results using the ensemble approach
#     final_label = ensemble_sentiment(roberta_label, vader_label, finbert_label)
    
#     final_sentiments.append(final_label)

# # Add the final sentiment labels to the DataFrame
# stock_news_df['ensemble_sentiment_label'] = final_sentiments

# # Save the updated dataset with ensemble sentiment labels
# output_file_path_ensemble = '/Users/yashdoshi/capstone5/Capstone_Project/src/app/src/API/stock_news_with_ensemble_labels.csv'
# stock_news_df.to_csv(output_file_path_ensemble, index=False)

# # Display the first few rows of the updated dataset
# print(stock_news_df.head())



# import pandas as pd
# import nltk
# from nltk.sentiment.vader import SentimentIntensityAnalyzer
# from transformers import pipeline

# # Download VADER lexicon if not already done
# nltk.download('vader_lexicon')

# # Initialize models for RoBERTa and FinBERT sentiment analysis
# roberta_pipeline = pipeline("sentiment-analysis", model="roberta-base", tokenizer="roberta-base")
# finbert_pipeline = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone", tokenizer="yiyanghkust/finbert-tone")

# # Initialize VADER sentiment analyzer
# vader_analyzer = SentimentIntensityAnalyzer()

# # Function to get sentiment from RoBERTa
# def roberta_sentiment(text):
#     result = roberta_pipeline(text)[0]
#     return result['label']

# # Function to get sentiment from VADER
# def vader_sentiment(text):
#     score = vader_analyzer.polarity_scores(text)
#     if score['compound'] >= 0.05:
#         return 'Positive'
#     elif score['compound'] <= -0.05:
#         return 'Negative'
#     else:
#         return 'Neutral'

# # Function to get sentiment from FinBERT
# def finbert_sentiment(text):
#     result = finbert_pipeline(text)[0]
#     return result['label']

# # Function to combine the three models (Ensemble)
# def ensemble_sentiment(roberta_label, vader_label, finbert_label):
#     labels = [roberta_label, vader_label, finbert_label]
#     # Count the occurrences of each sentiment and return the one with the most votes
#     most_common = max(set(labels), key=labels.count)
#     return most_common

# # Define a function to adjust 'Neutral' labels based on keywords in the text
# def adjust_sentiment_based_on_keywords(text, current_label):
#     positive_keywords = ['gain', 'increase', 'up', 'rise', 'growth', 'positive', 'surge']
#     negative_keywords = ['loss', 'decline', 'down', 'drop', 'fall', 'negative', 'crash']

#     if current_label == 'Neutral':
#         text_lower = text.lower()

#         # If any positive keyword is found, label it as Positive
#         if any(keyword in text_lower for keyword in positive_keywords):
#             return 'Positive'

#         # If any negative keyword is found, label it as Negative
#         elif any(keyword in text_lower for keyword in negative_keywords):
#             return 'Negative'

#     return current_label  # Return the original label if no adjustment is made

# # Load your dataset
# file_path = '/Users/yashdoshi/capstone5/Capstone_Project/src/app/src/API/stock_news_with_ensemble_labels.csv'
# stock_news_df = pd.read_csv(file_path)

# # Clean and ensure the 'content' column is of type string
# stock_news_df['content'] = stock_news_df['content'].fillna("").astype(str)

# # Apply sentiment analysis using RoBERTa, VADER, and FinBERT, then combine the results
# final_sentiments = []
# for content in stock_news_df['content']:
#     roberta_label = roberta_sentiment(content)
#     vader_label = vader_sentiment(content)
#     finbert_label = finbert_sentiment(content)
    
#     # Combine the results using the ensemble approach
#     final_label = ensemble_sentiment(roberta_label, vader_label, finbert_label)
    
#     # Adjust the sentiment if it's Neutral based on keywords
#     final_label = adjust_sentiment_based_on_keywords(content, final_label)
    
#     final_sentiments.append(final_label)

# # Add the final sentiment labels to the DataFrame
# stock_news_df['refined_sentiment_label'] = final_sentiments

# # Save the updated dataset with refined sentiment labels
# output_file_path_refined = '/Users/yashdoshi/capstone5/Capstone_Project/src/app/src/API/stock_news_with_refined_labels.csv'
# stock_news_df.to_csv(output_file_path_refined, index=False)

# # Display the first few rows of the updated dataset
# stock_news_df.head(), output_file_path_refined
# import pandas as pd
# from sklearn.model_selection import train_test_split
# from transformers import RobertaForSequenceClassification, RobertaTokenizer, Trainer, TrainingArguments
# from datasets import Dataset
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
# import torch

# # Step 1: Load the dataset (make sure it's in the correct format)
# df = pd.read_csv('/Users/yashdoshi/capstone5/Capstone_Project/src/app/src/API/stock_news_with_refined_labels.csv')  # Update path accordingly

# # Step 2: Split the dataset into train and test (80% train, 20% test)
# train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['refined_sentiment_label'])

# # Step 3: Convert DataFrame to HuggingFace Dataset format
# train_dataset = Dataset.from_pandas(train_df)
# test_dataset = Dataset.from_pandas(test_df)

# # Step 4: Tokenizer setup for RoBERTa
# tokenizer = RobertaTokenizer.from_pretrained("roberta-base")

# # Preprocessing function for the dataset
# def preprocess_data(examples):
#     # Ensure that 'title' and 'description' are converted to strings and handle missing data
#     titles = [str(x) for x in examples['title']]  # Convert titles to strings
#     descriptions = [str(x) for x in examples['description']]  # Convert descriptions to strings

#     # Combine 'title' and 'description' to form the 'text' column
#     examples['text'] = [title + " " + description for title, description in zip(titles, descriptions)]
    
#     # The target labels (refined sentiment labels)
#     examples['labels'] = examples['refined_sentiment_label']  # Use the refined sentiment labels as ground truth
#     return examples

# # Apply the preprocessing to both train and test datasets
# train_dataset = train_dataset.map(preprocess_data, batched=True)
# test_dataset = test_dataset.map(preprocess_data, batched=True)

# # Step 5: Tokenize the datasets
# def tokenize_function(examples):
#     return tokenizer(examples['text'], padding="max_length", truncation=True)

# train_dataset = train_dataset.map(lambda x: tokenize_function(x), batched=True)
# test_dataset = test_dataset.map(lambda x: tokenize_function(x), batched=True)

# # Step 6: Define the model
# roberta_model = RobertaForSequenceClassification.from_pretrained("roberta-base", num_labels=3)

# # Step 7: Set up the training arguments with matching evaluation and save strategies
# training_args = TrainingArguments(
#     output_dir="./roberta_results",
#     num_train_epochs=3,
#     per_device_train_batch_size=8,
#     per_device_eval_batch_size=8,
#     evaluation_strategy="epoch",  # Evaluate at the end of each epoch
#     save_strategy="epoch",  # Save the model at the end of each epoch
#     logging_dir="./roberta_logs",
#     logging_steps=100,
#     load_best_model_at_end=True,  # Load the best model at the end of training
# )

# # Step 8: Define the Trainer
# trainer = Trainer(
#     model=roberta_model,
#     args=training_args,
#     train_dataset=train_dataset,
#     eval_dataset=test_dataset,
#     compute_metrics=lambda p: {
#         'accuracy': accuracy_score(p.label_ids, p.predictions.argmax(axis=-1)),
#         'precision': precision_score(p.label_ids, p.predictions.argmax(axis=-1), average='weighted'),
#         'recall': recall_score(p.label_ids, p.predictions.argmax(axis=-1), average='weighted'),
#         'f1': f1_score(p.label_ids, p.predictions.argmax(axis=-1), average='weighted')
#     },
# )

# # Step 9: Fine-tune the model
# trainer.train()

# # Step 10: Save the fine-tuned model
# roberta_model.save_pretrained("./fine_tuned_roberta_model")
# tokenizer.save_pretrained("./fine_tuned_roberta_model")

# # Step 11: Evaluate the fine-tuned model
# results = trainer.evaluate()

# # Print the evaluation metrics
# print(results)
 
###################################################### FINAL ################################################################

# from sklearn.metrics import accuracy_score
# from transformers import Trainer, TrainingArguments, BertForSequenceClassification, BertTokenizer
# from datasets import load_dataset, Dataset
# from sklearn.model_selection import train_test_split
# import torch

# def compute_metrics(p):  # This function computes the accuracy
#     predictions, labels = p
#     preds = predictions.argmax(axis=1)  # Convert logits to predictions
#     return {'eval_accuracy': accuracy_score(labels, preds)}

# def main():
#     # Load dataset
#     dataset = load_dataset("zeroshot/twitter-financial-news-sentiment")

#     # Convert dataset to pandas DataFrame
#     train_data = dataset["train"].to_pandas()

#     # Train/Validation split
#     train_data, valid_data = train_test_split(train_data, test_size=0.1, random_state=42)

#     # Tokenizer
#     tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

#     def tokenize_function(examples):
#         return tokenizer(examples['text'], padding="max_length", truncation=True, max_length=128)

#     # Convert to Dataset and Tokenize
#     train_data = Dataset.from_pandas(train_data)
#     valid_data = Dataset.from_pandas(valid_data)

#     train_data = train_data.map(tokenize_function, batched=True)
#     valid_data = valid_data.map(tokenize_function, batched=True)

#     # Format the datasets for PyTorch
#     train_data.set_format(type="torch", columns=['input_ids', 'attention_mask', 'label'])
#     valid_data.set_format(type="torch", columns=['input_ids', 'attention_mask', 'label'])

#     # Load the model
#     model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=3)

#     # Define TrainingArguments
#     training_args = TrainingArguments(
#         output_dir="./results", 
#         num_train_epochs=3,                
#         per_device_train_batch_size=4,     
#         per_device_eval_batch_size=8,      
#         evaluation_strategy="epoch",       
#         save_strategy="epoch",             
#         logging_dir='./logs',              
#         logging_steps=10,
#         save_steps=10,                     
#         load_best_model_at_end=True,       
#         metric_for_best_model="eval_accuracy",  # Track best model based on accuracy
#         eval_strategy="epoch",  # Use eval_strategy to enable evaluation at the end of each epoch
#         weight_decay=0.01,                 
#         fp16=False,  # Disable mixed precision training if using CPU
#         dataloader_num_workers=4,  # Use multiple workers for data loading
#         warmup_steps=500,  # Use warmup steps to stabilize training
#         logging_first_step=True,
#         disable_tqdm=False
#     )

#     # Define Trainer
#     trainer = Trainer(
#         model=model,
#         args=training_args,
#         train_dataset=train_data,
#         eval_dataset=valid_data,
#         tokenizer=tokenizer,
#         compute_metrics=compute_metrics,  # Pass the custom compute_metrics function
#     )

#     # Start training
#     trainer.train()

# if __name__ == '__main__':
#     main()


# import requests
# from bs4 import BeautifulSoup
# import yfinance as yf
# from typing import List, Dict

# # Configuration
# SUPPORTED_TICKERS = [
#     'AAPL', 'MSFT', 'NVDA', 'AMD', 'JNJ', 'PFE', 'JPM', 'GS',
#     'KO', 'PEP', 'XOM', 'NEE', 'CVX', 'WMT', 'HD', 'GME',
#     'TSLA', 'F', 'COIN', 'MRNA'
# ]

# COMPANY_NAMES = {
#     'AAPL': 'Apple',
#     'MSFT': 'Microsoft',
#     'NVDA': 'Nvidia',
#     'AMD': 'AMD',
#     'JNJ': 'Johnson & Johnson',
#     'PFE': 'Pfizer',
#     'JPM': 'JPMorgan',
#     'GS': 'Goldman Sachs',
#     'KO': 'Coca-Cola',
#     'PEP': 'Pepsi',
#     'XOM': 'Exxon',
#     'NEE': 'Next Era Energy',
#     'CVX': 'Chevron',
#     'WMT': 'Walmart',
#     'HD': 'Home Depot',
#     'GME': 'GameStop',
#     'TSLA': 'Tesla',
#     'F': 'Ford',
#     'COIN': 'Coinbase',
#     'MRNA': 'Moderna'
# }

# NEWSAPI_KEY = "4c310cb414224d468ee9087dd9f208d6"

# def get_yahoo_news(ticker: str, company_name: str) -> List[str]:
#     """Fetch news from Yahoo Finance"""
#     try:
#         news_items = yf.Ticker(ticker).news
#         headlines = []
#         for item in news_items:
#             title = item.get('title', '')
#             if title and (ticker.lower() in title.lower() or company_name.lower() in title.lower()):
#                 headlines.append(title)
#         return headlines[:5]
#     except Exception as e:
#         print(f"Yahoo Finance error: {e}")
#         return []

# def get_newsapi_news(ticker: str, company_name: str) -> List[str]:
#     """Fetch news from NewsAPI"""
#     if not NEWSAPI_KEY:
#         return []
    
#     try:
#         params = {
#             "q": f"{ticker} OR {company_name} AND (stock OR shares OR earnings)",
#             "domains": "bloomberg.com,reuters.com,cnbc.com,marketwatch.com",
#             "pageSize": 5,
#             "apiKey": NEWSAPI_KEY
#         }
#         response = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)
#         response.raise_for_status()
#         articles = response.json().get('articles', [])
#         return [
#             article['title'] 
#             for article in articles 
#             if ticker.lower() in article['title'].lower() or company_name.lower() in article['title'].lower()
#         ][:5]
#     except Exception as e:
#         print(f"NewsAPI error: {e}")
#         return []

# def get_stock_news(ticker: str) -> Dict[str, List[str]]:
#     """Get all available news for a stock"""
#     ticker = ticker.upper()
#     if ticker not in SUPPORTED_TICKERS:
#         return {"error": f"Ticker {ticker} not supported"}
    
#     company_name = COMPANY_NAMES.get(ticker, ticker)
#     results = {}
    
#     # Try Yahoo first
#     yahoo_news = get_yahoo_news(ticker, company_name)
#     if yahoo_news:
#         results['yahoo'] = yahoo_news
    
#     # Try NewsAPI if Yahoo didn't return anything
#     if not results:
#         newsapi_news = get_newsapi_news(ticker, company_name)
#         if newsapi_news:
#             results['newsapi'] = newsapi_news
    
#     # If still no results, return error
#     if not results:
#         return {"error": "No news found for this ticker"}
    
#     return results

# def main():
#     """Interactive version for easier testing"""
#     while True:
#         print("\nSupported tickers:", ", ".join(SUPPORTED_TICKERS))
#         ticker = input("Enter stock ticker (or 'quit' to exit): ").strip().upper()
        
#         if ticker == 'QUIT':
#             break
            
#         if ticker not in SUPPORTED_TICKERS:
#             print(f"Error: {ticker} is not in the supported tickers list")
#             continue
            
#         news = get_stock_news(ticker)
        
#         if 'error' in news:
#             print(news['error'])
#             continue
            
#         print(f"\nLatest news for {ticker} ({COMPANY_NAMES.get(ticker, ticker)}):")
#         for source, headlines in news.items():
#             print(f"\nFrom {source.upper()}:")
#             for i, headline in enumerate(headlines, 1):
#                 print(f"{i}. {headline}")

# if __name__ == "__main__":
#     main()

# from datasets import load_dataset
# from transformers import pipeline

# # Load the only split directly
# ds = load_dataset("zeroshot/twitter-financial-news-sentiment", split="train")

# texts  = ds["text"]
# y_true = ds["label"]

# # Pipelines
# finbert = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")
# # roberta = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

# # Label mappings
# finbert_map = {"negative": 0, "neutral": 1, "positive": 2}
# roberta_map = {"LABEL_0": 0, "LABEL_1": 1, "LABEL_2": 2}

# # Predictions
# y_pred_finbert = [finbert_map[finbert(text)[0]["label"].lower()] for text in texts]
# # y_pred_roberta = [roberta_map[roberta(text)[0]["label"]]           for text in texts]

# # Evaluation
# total = len(y_true)
# correct_f = sum(1 for i, p in enumerate(y_pred_finbert) if p == y_true[i])
# # correct_r = sum(1 for i, p in enumerate(y_pred_roberta)   if p == y_true[i])

# print(f"FinBERT: {correct_f}/{total} → {correct_f/total:.3f}")
# # print(f"RoBERTa: {correct_r}/{total} → {correct_r/total:.3f}")

# #%%
# from datasets import load_dataset

# # Load the dataset
# ds = load_dataset("zeroshot/twitter-financial-news-sentiment", split="train")

# # Check number of examples
# print(f"Number of examples: {len(ds)}")

# # Display the first 5 entries
# for i in range(5):
#     print(ds[i])

# # %%

# from datasets import load_dataset
# from transformers import pipeline
# from sklearn.metrics import accuracy_score

# def main():
#     # Load up to 2000 examples
#     ds = load_dataset("zeroshot/twitter-financial-news-sentiment", split="train")
#     limit = min(500, len(ds))
#     texts  = ds["text"][:limit]
#     y_true = ds["label"][:limit]

#     # CPU-only FinBERT
#     finbert = pipeline(
#         "sentiment-analysis",
#         model="yiyanghkust/finbert-tone",
#         tokenizer="yiyanghkust/finbert-tone",
#         device=-1
#     )

#     # Map labels
#     finbert_map = {"negative": 0, "neutral": 1, "positive": 2}

#     # Batch inference
#     outputs = finbert(texts, batch_size=32)
#     y_pred = [finbert_map[o["label"].lower()] for o in outputs]

#     # Evaluate
#     total   = len(y_true)
#     correct = sum(p == t for p, t in zip(y_pred, y_true))
#     acc     = accuracy_score(y_true, y_pred)

#     print(f"Evaluated on {total} examples")
#     print(f"FinBERT correct: {correct}/{total}")
#     print(f"FinBERT accuracy: {acc:.3f}")

# if __name__ == "__main__":
#     main()
# # %%

# from datasets import load_dataset
# from transformers import pipeline
# from sklearn.metrics import accuracy_score

# def main():
#     # 1) Load up to 2000 examples from the HF dataset
#     ds = load_dataset("zeroshot/twitter-financial-news-sentiment", split="train")
#     limit = min(500, len(ds))
#     texts  = ds["text"][:limit]
#     y_true = ds["label"][:limit]

#     # 2) Initialize the RoBERTa sentiment-analysis pipeline on CPU
#     roberta = pipeline(
#         "sentiment-analysis",
#         model="cardiffnlp/twitter-roberta-base-sentiment",
#         device=-1  # force CPU
#     )

#     # 3) Map RoBERTa’s string labels to integers
#     roberta_map = {
#         "LABEL_0": 0,  # negative
#         "LABEL_1": 1,  # neutral
#         "LABEL_2": 2   # positive
#     }

#     # 4) Run batch inference (batch_size=32)
#     outputs = roberta(texts, batch_size=32)
#     y_pred = [roberta_map[o["label"]] for o in outputs]

#     # 5) Compute and print accuracy
#     total   = len(y_true)
#     correct = sum(p == t for p, t in zip(y_pred, y_true))
#     acc     = accuracy_score(y_true, y_pred)

#     print(f"Evaluated on    : {total} examples")
#     print(f"RoBERTa correct : {correct}/{total}")
#     print(f"RoBERTa accuracy: {acc:.3f}")

# if __name__ == "__main__":
#     main()
# # %%
# # ensemble_accuracy.py

# from datasets import load_dataset
# from transformers import pipeline as _hf_pipeline
# from nltk.sentiment.vader import SentimentIntensityAnalyzer
# from sklearn.metrics import accuracy_score

# # Initialize sentiment tools (CPU)
# finbert = _hf_pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone", device=-1)
# roberta = _hf_pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment", device=-1)
# vader = SentimentIntensityAnalyzer()

# def analyze_sentiment(text):
#     """Fixed-weight ensemble sentiment analysis using FinBERT, RoBERTa, and VADER."""
#     # FinBERT
#     res_f = finbert(text)[0]
#     f_label = res_f["label"].lower()
#     f_score =  1 if f_label == "positive" else -1 if f_label == "negative" else 0

#     # RoBERTa
#     res_r = roberta(text)[0]
#     r_label = res_r["label"]
#     if   r_label == "LABEL_2": r_score =  1
#     elif r_label == "LABEL_0": r_score = -1
#     else:                      r_score =  0

#     # VADER
#     v_score = vader.polarity_scores(text)["compound"]

#     # Weighted sum
#     weighted = 0.1 * f_score + 0.4 * r_score + 0.5 * v_score

#     # Final label
#     if weighted >  0.15: return "Positive", weighted
#     if weighted < -0.15: return "Negative", weighted
#     return "Neutral", weighted

# def main():
#     # Load and limit to 2000 examples
#     ds     = load_dataset("zeroshot/twitter-financial-news-sentiment", split="train")
#     limit  = min(500, len(ds))
#     texts  = ds["text"][:limit]
#     y_true = ds["label"][:limit]

#     # Predict
#     y_pred = []
#     for t in texts:
#         label, _ = analyze_sentiment(t)
#         y_pred.append(2 if label=="Positive" else 1 if label=="Neutral" else 0)

#     # Evaluate
#     correct = sum(p==t for p,t in zip(y_pred, y_true))
#     acc     = accuracy_score(y_true, y_pred)

#     print(f"Evaluated on      : {len(y_true)} examples")
#     print(f"Ensemble correct  : {correct}/{len(y_true)}")
#     print(f"Ensemble accuracy : {acc:.3f}")

# if __name__ == "__main__":
#     main()

# # %%
# # evaluate_personal_model.py

# # Requirements:
# # pip install datasets transformers scikit-learn nltk

# from datasets import load_dataset
# from transformers import pipeline, BertTokenizer, BertForSequenceClassification
# from nltk.sentiment.vader import SentimentIntensityAnalyzer
# from sklearn.metrics import accuracy_score

# # Load your fine-tuned model checkpoint
# checkpoint_path = './results/checkpoint-6441'
# tokenizer = BertTokenizer.from_pretrained(checkpoint_path)
# model     = BertForSequenceClassification.from_pretrained(checkpoint_path)
# sentiment_model = pipeline(
#     'sentiment-analysis',
#     model= model,
#     tokenizer= tokenizer,
#     device= -1        # force CPU
# )

# # VADER for ensemble
# vader = SentimentIntensityAnalyzer()

# # Your analysis function
# def analyze_sentiment(text):
#     """Analyze sentiment using the fine-tuned model + keyword overrides."""
#     res = sentiment_model(text)[0]
#     label = res['label']
#     score = res['score']
    
#     # keyword overrides
#     acquire_kw = ["increases position", "purchases more shares", "acquires", "buys"]
#     sell_kw    = ["sells shares", "decreases stake", "cuts position", "sells off"]
    
#     txt = text.lower()
#     if any(kw in txt for kw in acquire_kw):
#         return "POSITIVE", 1.0
#     if any(kw in txt for kw in sell_kw):
#         return "NEGATIVE", -1.0
    
#     return label, score

# # Map string labels to integers
# def label_to_int(label):
#     u = label.upper()
#     if u == "POSITIVE": return 2
#     if u == "NEGATIVE": return 0
#     return 1  # NEUTRAL or anything else

# def main():
#     # 1) load dataset and limit to 2000 examples
#     ds = load_dataset("zeroshot/twitter-financial-news-sentiment", split="train")
#     n  = min(1000, len(ds))
#     texts  = ds["text"][:n]
#     y_true = ds["label"][:n]
    
#     # 2) run analysis
#     y_pred = []
#     for t in texts:
#         lab, _ = analyze_sentiment(t)
#         y_pred.append(label_to_int(lab))
    
#     # 3) evaluate
#     correct = sum(p==t for p,t in zip(y_pred, y_true))
#     acc     = accuracy_score(y_true, y_pred)
#     print(f"Evaluated on      : {n} examples")
#     print(f"Correct predictions: {correct}/{n}")
#     print(f"Accuracy           : {acc:.3f}")

# if __name__ == "__main__":
#     main()

# # %%

import yfinance as yf
from typing import Dict, List
import numpy as np

class FinancialAnalyst:
    def __init__(self):
        """No model needed - we'll use deterministic analysis"""
        pass

    def get_financials(self, ticker: str) -> Dict[str, List[float]]:
        """Get clean financial data with error handling"""
        try:
            company = yf.Ticker(ticker)
            return {
                "revenue": company.financials.loc['Total Revenue'].iloc[0:3].tolist(),
                "net_income": company.financials.loc['Net Income'].iloc[0:3].tolist(),
                "total_debt": company.balance_sheet.loc['Total Debt'].iloc[0:3].tolist(),
                "operating_cash_flow": company.cashflow.loc['Operating Cash Flow'].iloc[0:3].tolist()
            }
        except Exception as e:
            raise ValueError(f"Data fetch error: {str(e)}")

    def analyze_trend(self, values: List[float]) -> str:
        """Deterministic trend analysis"""
        change = (values[-1] - values[0]) / values[0]
        abs_change = abs(change)
        
        if abs_change < 0.05:
            return "stable"
        elif change > 0:
            return f"up {abs_change:.1%}" if abs_change > 0.1 else "slightly up"
        else:
            return f"down {abs_change:.1%}" if abs_change > 0.1 else "slightly down"

    def generate_analysis(self, financials: Dict[str, List[float]]) -> str:
        """Template-based guaranteed analysis"""
        # Convert to billions
        rev = [x/1e9 for x in financials['revenue']]
        ni = [x/1e9 for x in financials['net_income']]
        debt = [x/1e9 for x in financials['total_debt']]
        cash = [x/1e9 for x in financials['operating_cash_flow']]
        
        # Calculate trends
        rev_trend = self.analyze_trend(rev)
        ni_trend = self.analyze_trend(ni)
        debt_trend = self.analyze_trend(debt)
        cash_trend = self.analyze_trend(cash)
        
        # Generate guaranteed structured output
        analysis = f"""
1. Revenue Trend: {rev_trend} (${rev[2]:.1f}B → ${rev[0]:.1f}B)
2. Profitability: {ni_trend} (${ni[2]:.1f}B → ${ni[0]:.1f}B)
3. Debt Health: {debt_trend} (${debt[2]:.1f}B → ${debt[0]:.1f}B)
4. Cash Position: {cash_trend} (${cash[2]:.1f}B → ${cash[0]:.1f}B)
"""
        return analysis

def main():
    print("🚀 Running RELIABLE Financial Analysis")
    
    try:
        analyst = FinancialAnalyst()
        
        print("\n🔍 Fetching AAPL fundamentals...")
        data = analyst.get_financials("AAPL")
        
        print("\n📊 Generating analysis...")
        analysis = analyst.generate_analysis(data)
        
        print("\n" + "="*50)
        print("💼 100% RELIABLE FINANCIAL ANALYSIS")
        print("="*50)
        print(analysis)
        
        print("\n" + "="*50)
        print("✅ ANALYSIS COMPLETE")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Quick fix: pip install --upgrade yfinance")

if __name__ == "__main__":
    main()