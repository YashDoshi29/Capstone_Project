# import json
# import pandas as pd
# import numpy as np
# import torch
# from torch.utils.data import Dataset
# from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments
# from sklearn.model_selection import train_test_split
# import os
# os.environ["CUDA_VISIBLE_DEVICES"] = ""

# # -----------------------------
# # Helper function: Load JSONL file
# # -----------------------------
# def load_jsonl(filepath):
#     data = []
#     with open(filepath, "r", encoding="utf-8") as f:
#         for line in f:
#             data.append(json.loads(line))
#     return data

# # -----------------------------
# # Step 1: Load the Pre-Split Datasets
# # -----------------------------
# train_data = load_jsonl("data/finetune/splits/train.jsonl")
# val_data = load_jsonl("data/finetune/splits/val.jsonl")
# test_data = load_jsonl("data/finetune/splits/test.jsonl")

# print("Train examples:", len(train_data))
# print("Validation examples:", len(val_data))
# print("Test examples:", len(test_data))

# train_df = pd.DataFrame(train_data)
# val_df = pd.DataFrame(val_data)
# test_df = pd.DataFrame(test_data)

# # -----------------------------
# # Step 2: Define a Custom PyTorch Dataset for T5 Fine-Tuning
# # -----------------------------
# class FinetuneDataset(Dataset):
#     def __init__(self, df, tokenizer, max_input_length=128, max_target_length=16):
#         self.df = df.reset_index(drop=True)
#         self.tokenizer = tokenizer
#         self.max_input_length = max_input_length
#         self.max_target_length = max_target_length
        
#         # Pre-tokenize prompts and responses.
#         self.inputs = tokenizer(
#             self.df["prompt"].tolist(),
#             max_length=self.max_input_length,
#             truncation=True,
#             padding="max_length",
#             return_tensors="np"
#         )
#         self.targets = tokenizer(
#             self.df["response"].tolist(),
#             max_length=self.max_target_length,
#             truncation=True,
#             padding="max_length",
#             return_tensors="np"
#         )
#         # Replace padding token IDs in labels with -100 to ignore during loss computation.
#         self.targets["input_ids"][self.targets["input_ids"] == tokenizer.pad_token_id] = -100

#     def __len__(self):
#         return len(self.df)

#     def __getitem__(self, idx):
#         return {
#             "input_ids": torch.tensor(self.inputs["input_ids"][idx], dtype=torch.long),
#             "attention_mask": torch.tensor(self.inputs["attention_mask"][idx], dtype=torch.long),
#             "labels": torch.tensor(self.targets["input_ids"][idx], dtype=torch.long)
#         }

# # -----------------------------
# # Step 3: Initialize T5 Model and Tokenizer
# # -----------------------------
# model_name = "t5-small"  # Use t5-base if resources permit.
# tokenizer = T5Tokenizer.from_pretrained(model_name)
# model = T5ForConditionalGeneration.from_pretrained(model_name)

# # -----------------------------
# # Step 4: Create Dataset Objects for Training, Validation, and Testing
# # -----------------------------
# train_dataset = FinetuneDataset(train_df, tokenizer, max_input_length=128, max_target_length=16)
# val_dataset = FinetuneDataset(val_df, tokenizer, max_input_length=128, max_target_length=16)
# test_dataset = FinetuneDataset(test_df, tokenizer, max_input_length=128, max_target_length=16)

# # -----------------------------
# # Step 5: Define TrainingArguments and a compute_metrics Function
# # -----------------------------
# training_args = TrainingArguments(
#     output_dir="./t5_finetuned",
#     num_train_epochs=3,                     # Adjust number of epochs as needed.
#     per_device_train_batch_size=4,
#     per_device_eval_batch_size=4,
#     learning_rate=5e-5,
#     evaluation_strategy="steps",            # Evaluate every fixed steps.
#     eval_steps=50,                          # Evaluate every 50 steps.
#     logging_steps=50,                       # Log progress every 50 steps.
#     save_steps=50,                          # Save a checkpoint every 50 steps.
#     save_total_limit=2,                     # Keep only the 2 most recent checkpoints.
#     logging_dir="./logs",
#     load_best_model_at_end=True,
#     metric_for_best_model="accuracy",
#     report_to=["tensorboard"]

#     # report_to=["console"],                  # Report progress to console.
# )

# def compute_metrics(eval_pred):
#     logits, labels = eval_pred
#     predictions = np.argmax(logits, axis=-1)
#     # Decode predictions and labels to text strings.
#     decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
#     # Replace -100 in the labels with pad_token_id for decoding.
#     labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
#     decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    
#     # Compute accuracy as a simple percentage of exact matches (case-insensitive).
#     matches = [1 if pred.strip().lower() == label.strip().lower() else 0 
#                for pred, label in zip(decoded_preds, decoded_labels)]
#     accuracy = sum(matches) / len(matches) if matches else 0
#     return {"accuracy": accuracy}

# # -----------------------------
# # Step 6: Initialize Trainer and Train the Model
# # -----------------------------
# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=train_dataset,
#     eval_dataset=val_dataset,
#     compute_metrics=compute_metrics,
# )

# print("Starting training...")
# trainer.train()

# print("Training complete. Saving the fine-tuned model...")
# trainer.save_model("./t5_finetuned")
# tokenizer.save_pretrained("./t5_finetuned")

# print("Evaluating the model on the test set...")
# test_results = trainer.evaluate(test_dataset)
# print("Test Results:", test_results)




import json
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset
from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
import os

# Force the use of CPU.
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# -----------------------------
# Helper function: Load JSONL file
# -----------------------------
def load_jsonl(filepath):
    data = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return data

# -----------------------------
# Step 1: Load the Pre-Split Datasets
# -----------------------------
train_data = load_jsonl("data/finetune/splits/train.jsonl")
val_data = load_jsonl("data/finetune/splits/val.jsonl")
test_data = load_jsonl("data/finetune/splits/test.jsonl")

print("Train examples:", len(train_data))
print("Validation examples:", len(val_data))
print("Test examples:", len(test_data))

train_df = pd.DataFrame(train_data)
val_df = pd.DataFrame(val_data)
test_df = pd.DataFrame(test_data)

# -----------------------------
# Step 2: Define a Custom PyTorch Dataset for T5 Fine-Tuning
# -----------------------------
class FinetuneDataset(Dataset):
    def __init__(self, df, tokenizer, max_input_length=128, max_target_length=16):
        self.df = df.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_input_length = max_input_length
        self.max_target_length = max_target_length
        
        # Pre-tokenize prompts and responses.
        self.inputs = tokenizer(
            self.df["prompt"].tolist(),
            max_length=self.max_input_length,
            truncation=True,
            padding="max_length",
            return_tensors="np"
        )
        self.targets = tokenizer(
            self.df["response"].tolist(),
            max_length=self.max_target_length,
            truncation=True,
            padding="max_length",
            return_tensors="np"
        )
        # Replace padding token IDs in labels with -100 to ignore during loss computation.
        self.targets["input_ids"][self.targets["input_ids"] == tokenizer.pad_token_id] = -100

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        return {
            "input_ids": torch.tensor(self.inputs["input_ids"][idx], dtype=torch.long),
            "attention_mask": torch.tensor(self.inputs["attention_mask"][idx], dtype=torch.long),
            "labels": torch.tensor(self.targets["input_ids"][idx], dtype=torch.long)
        }

# -----------------------------
# Step 3: Initialize T5 Model and Tokenizer
# -----------------------------
model_name = "t5-small"  # Use "t5-base" if your resources allow.
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# -----------------------------
# Step 4: Create Dataset Objects for Training, Validation, and Testing
# -----------------------------
train_dataset = FinetuneDataset(train_df, tokenizer, max_input_length=128, max_target_length=16)
val_dataset = FinetuneDataset(val_df, tokenizer, max_input_length=128, max_target_length=16)
test_dataset = FinetuneDataset(test_df, tokenizer, max_input_length=128, max_target_length=16)

# -----------------------------
# Step 5: Define TrainingArguments and a compute_metrics Function
# -----------------------------
training_args = TrainingArguments(
    output_dir="./t5_finetuned",
    num_train_epochs=3,                     # Adjust as needed.
    per_device_train_batch_size=4,          # Reduced batch size.
    per_device_eval_batch_size=4,           # Reduced batch size.
    learning_rate=5e-5,
    evaluation_strategy="steps",            # Evaluation every fixed number of steps.
    eval_steps=50,                          # Evaluate every 50 steps.
    logging_steps=50,                       # Log progress every 50 steps.
    save_steps=50,                          # Save a checkpoint every 50 steps.
    save_total_limit=2,                     # Keep only the 2 most recent checkpoints.
    logging_dir="./logs",
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    no_cuda=True,                           # Force training on CPU.
    report_to=["tensorboard"]               # Use TensorBoard for logging.
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    # Decode predictions and labels to text strings.
    decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
    # Replace -100 in the labels with the pad token id for decoding.
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    
    # Compute accuracy as exact string matches (case-insensitive).
    matches = [1 if pred.strip().lower() == label.strip().lower() else 0 
               for pred, label in zip(decoded_preds, decoded_labels)]
    accuracy = sum(matches) / len(matches) if matches else 0
    return {"accuracy": accuracy}

# -----------------------------
# Step 6: Initialize Trainer and Train the Model
# -----------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
)

print("Starting training...")
trainer.train()

print("Training complete. Saving fine-tuned model...")
trainer.save_model("./t5_finetuned")
tokenizer.save_pretrained("./t5_finetuned")

print("Evaluating model on test set...")
test_results = trainer.evaluate(test_dataset)
print("Test Results:", test_results)
