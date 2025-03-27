import requests
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline
import yfinance as yf

# Initialize NLP tools
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()
finbert = pipeline("text-classification", model="ProsusAI/finbert")


# --- 1. News Fetching System ---
class NewsCollector:
    def __init__(self, stock_symbol="AAPL"):
        self.stock_symbol = stock_symbol
        self.company_name = self._get_company_name()

    def _get_company_name(self):
        stock = yf.Ticker(self.stock_symbol)
        return stock.info['longName']

    def fetch_news_api(self, days=30):
        """Fetch news from NewsAPI"""
        API_KEY = "YOUR_NEWSAPI_KEY"
        from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        url = f"https://newsapi.org/v2/everything?q={self.company_name} OR {self.stock_symbol}&from={from_date}&sortBy=publishedAt&apiKey={API_KEY}"

        response = requests.get(url)
        articles = response.json().get('articles', [])

        return self._parse_articles(articles)

    def fetch_web_news(self):
        """Fallback web scraper"""
        url = f"https://www.google.com/search?q={self.stock_symbol}+stock+news&tbm=nws"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        articles = []
        for item in soup.find_all('div', class_='BNeawe vvjwJb AP7Wnd'):
            articles.append({'title': item.text, 'source': 'Google News'})

        return articles

    def _parse_articles(self, articles):
        """Standardize article format"""
        parsed = []
        for article in articles:
            parsed.append({
                'date': article['publishedAt'][:10],
                'title': article['title'],
                'content': article['description'],
                'source': article['source']['name'],
                'url': article['url']
            })
        return parsed


# --- 2. News Processing Pipeline ---
class NewsProcessor:
    def __init__(self):
        self.sentiment_analyzer = finbert

    def clean_text(self, text):
        """Basic text cleaning"""
        text = text.lower()
        text = ''.join([c for c in text if c.isalnum() or c.isspace()])
        return text

    def analyze_sentiment(self, text):
        """Hybrid sentiment analysis"""
        # VADER for quick analysis
        vader_score = sia.polarity_scores(text)['compound']

        # FinBERT for financial context
        finbert_result = self.sentiment_analyzer(text[:512])[0]  # Truncate to 512 tokens
        finbert_score = 1 if finbert_result['label'] == 'positive' else -1

        # Combined score
        return {
            'vader': vader_score,
            'finbert': finbert_score,
            'combined': (vader_score + finbert_score) / 2
        }

    def process_articles(self, articles):
        """Process all articles"""
        processed = []
        for article in articles:
            clean_content = self.clean_text(f"{article['title']}. {article.get('content', '')}")
            sentiment = self.analyze_sentiment(clean_content)

            processed.append({
                'date': article['date'],
                'source': article['source'],
                'content': clean_content,
                'sentiment_vader': sentiment['vader'],
                'sentiment_finbert': sentiment['finbert'],
                'sentiment_combined': sentiment['combined'],
                'urgency': self._detect_urgency(clean_content)
            })
        return pd.DataFrame(processed)

    def _detect_urgency(self, text):
        """Detect urgency keywords"""
        urgency_words = ['urgent', 'immediate', 'critical', 'alert', 'warning']
        return any(word in text for word in urgency_words)


# --- 3. Integration with Stock Data_Synthesizer ---
def get_stock_data(symbol, start_date):
    """Fetch historical stock data"""
    df = yf.download(symbol, start=start_date)
    df = df.reset_index()
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    return df


# --- 4. Execution Pipeline ---
if __name__ == "__main__":
    # Fetch news
    collector = NewsCollector("AAPL")
    articles = collector.fetch_news_api()  # Fallback: collector.fetch_web_news()

    # Process news
    processor = NewsProcessor()
    news_df = processor.process_articles(articles)

    # Aggregate daily sentiment
    daily_sentiment = news_df.groupby('date').agg({
        'sentiment_combined': 'mean',
        'urgency': 'sum'
    }).reset_index()

    # Get stock data
    stock_df = get_stock_data("AAPL", news_df['date'].min())

    # Merge datasets
    merged_df = pd.merge(stock_df, daily_sentiment, left_on='Date', right_on='date', how='left')
    merged_df.fillna({'sentiment_combined': 0, 'urgency': 0}, inplace=True)

    # Save for model training
    merged_df.to_csv("aapl_news_stock_data.csv", index=False)
    print("Dataset ready for modeling. Sample output:")
    print(merged_df.tail())

# --- 5. Sample Model Integration ---
# Use the CSV with columns: Date, Open, High, Low, Close, Volume, sentiment_combined, urgency
# Can create features like:
# - 3-day sentiment moving average
# - Urgency count per week
# - Sentiment vs price change correlations