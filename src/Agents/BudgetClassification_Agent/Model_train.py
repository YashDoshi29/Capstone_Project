import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import Dataset
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
import torch
from sklearn.preprocessing import LabelEncoder

# 1. Load Data
df = pd.read_csv("/Users/Admin/OneDrive/Desktop/USA/Masters/Capstone/data/synthetic_transactions_ctgan.csv")
df.dropna(subset=["merchant_name", "category", "mapped_category"], inplace=True)

# Optional: Filter to common categories (reduce noise)
top_categories = df["mapped_category"].value_counts().nlargest(10).index.tolist()
df = df[df["mapped_category"].isin(top_categories)]

# 2. Create input text
df["text"] = df["merchant_name"] + " | " + df["category"]

# 3. Encode labels
label_encoder = LabelEncoder()
df["label"] = label_encoder.fit_transform(df["mapped_category"])

# 4. Split dataset
train_df, val_df = train_test_split(df, test_size=0.2, stratify=df["label"], random_state=42)

# 5. HuggingFace Dataset
train_dataset = Dataset.from_pandas(train_df[["text", "label"]])
val_dataset = Dataset.from_pandas(val_df[["text", "label"]])

# 6. Tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

def tokenize(batch):
    return tokenizer(batch["text"], padding="max_length", truncation=True, max_length=64)

train_dataset = train_dataset.map(tokenize, batched=True)
val_dataset = val_dataset.map(tokenize, batched=True)

# Remove columns not needed for training
train_dataset.set_format("torch", columns=["input_ids", "attention_mask", "label"])
val_dataset.set_format("torch", columns=["input_ids", "attention_mask", "label"])

# 7. Model
model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=len(label_encoder.classes_))

# 8. Training args
training_args = TrainingArguments(
    output_dir="./bert_classifier",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    num_train_epochs=3,
    weight_decay=0.01,
    load_best_model_at_end=True,
)

# 9. Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

# 10. Train
trainer.train()

# ✅ Save model and encoder
model.save_pretrained("bert_classifier")
tokenizer.save_pretrained("bert_classifier")
import joblib
joblib.dump(label_encoder, "label_encoder.pkl")

print("✅ Fine-tuning complete. Model saved.")


# Load your CSV
