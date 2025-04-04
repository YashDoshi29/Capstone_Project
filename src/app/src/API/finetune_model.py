# from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, DataCollatorWithPadding
# from datasets import load_dataset

# # Load your fine-tuning dataset from the JSONL file.
# dataset = load_dataset("json", data_files={"train": "data/finetune/finetune_dataset.jsonl"}, split="train")

# # Map the response ("Up"/"Down") to numeric labels.
# def map_labels(example):
#     example["label"] = 1 if example["response"].strip().lower() == "up" else 0
#     return example

# dataset = dataset.map(map_labels)
# # Remove the original response and rename "prompt" to "text" for the model's input.
# dataset = dataset.remove_columns(["response"])
# dataset = dataset.rename_column("prompt", "text")

# # Inspect one example.
# print(dataset[0])

# # Use a finance-focused model such as FinBERT.
# model_name = "ProsusAI/finbert"  # Replace with your chosen model if needed.

# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

# # Tokenize the dataset.
# def tokenize_function(example):
#     return tokenizer(example["text"], truncation=True, max_length=256)

# tokenized_dataset = dataset.map(tokenize_function, batched=True)

# # Use a data collator to pad inputs during batching.
# data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# training_args = TrainingArguments(
#     output_dir="./finetuned_finbert",
#     evaluation_strategy="no",
#     learning_rate=2e-5,
#     per_device_train_batch_size=8,
#     num_train_epochs=3,
#     weight_decay=0.01,
# )

# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=tokenized_dataset,
#     tokenizer=tokenizer,
#     data_collator=data_collator,
# )

# # Fine-tune the model.
# trainer.train()

# # Save the fine-tuned model and tokenizer.
# model.save_pretrained("./finetuned_finbert")
# tokenizer.save_pretrained("./finetuned_finbert")

# print("Fine-tuning complete. Model saved to ./finetuned_finbert")


from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, DataCollatorWithPadding
from datasets import load_dataset
import evaluate
import numpy as np
from transformers import TrainerCallback

class CheckpointLogger(TrainerCallback):
    def on_save(self, args, state, control, **kwargs):
        print(f"Checkpoint saved at step {state.global_step} in {args.output_dir}")
        return control

# 1. Load the fine-tuning dataset from the JSONL file.
dataset = load_dataset("json", data_files={"train": "data/finetune/finetune_dataset.jsonl"}, split="train")

# 2. Map the response to a numeric label: 1 for "Up", 0 for "Down".
def map_labels(example):
    example["label"] = 1 if example["response"].strip().lower() == "up" else 0
    return example

dataset = dataset.map(map_labels)
# Remove the original "response" field and rename "prompt" to "text" (the model's input)
dataset = dataset.remove_columns(["response"])
dataset = dataset.rename_column("prompt", "text")

# 3. Split the dataset into training and evaluation sets.
split_dataset = dataset.train_test_split(test_size=0.1, seed=42)
train_dataset = split_dataset["train"]
eval_dataset = split_dataset["test"]

# 4. Load the tokenizer and the FinBERT model.
model_name = "ProsusAI/finbert"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=2,
    ignore_mismatched_sizes=True  # Reinitialize classification head for 2 labels.
)

# 5. Tokenize the datasets.
def tokenize_function(example):
    return tokenizer(example["text"], truncation=True, max_length=256)

train_dataset = train_dataset.map(tokenize_function, batched=True)
eval_dataset = eval_dataset.map(tokenize_function, batched=True)

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# 6. Set up the evaluation metric (accuracy) using the evaluate library.
metric = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

# 7. Define training arguments with checkpoint saving.
training_args = TrainingArguments(
    output_dir="./finetuned_finbert",
    evaluation_strategy="epoch",  # Evaluate at the end of each epoch.
    save_strategy="steps",          # Save checkpoints at specified steps.
    save_steps=1000,                # Save a checkpoint every 1000 steps.
    save_total_limit=2,             # Keep only the latest 2 checkpoints.
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=100,
)

# 8. Initialize the Trainer.
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
    callbacks=[CheckpointLogger()]
)

# 9. Fine-tune the model.
trainer.train()

# 10. Evaluate the model on the evaluation set.
eval_results = trainer.evaluate()
print("Evaluation results:", eval_results)

# 11. Save the final fine-tuned model.
model.save_pretrained("/Users/nemi/finetuned_finbert")
tokenizer.save_pretrained("/Users/nemi/finetuned_finbert")