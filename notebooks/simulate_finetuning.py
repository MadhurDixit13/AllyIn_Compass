import json
from datasets import Dataset

# 1. Load and prepare positive examples
data = []
with open("../src/feedback/feedback_log.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        if item["rating"] == 1:
            data.append({
                "prompt": f"Context: {item['query']}\nAnswer:",
                "completion": item["answer"]
            })

dataset = Dataset.from_list(data)
dataset = dataset.train_test_split(test_size=0.2)

# 2. Model setup
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from peft import get_peft_model, LoraConfig, TaskType

model_id = "tiiuae/falcon-rw-1b"

# Load tokenizer and patch pad token
tokenizer = AutoTokenizer.from_pretrained(model_id)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

model = AutoModelForCausalLM.from_pretrained(model_id, pad_token_id=tokenizer.pad_token_id)

# Apply LoRA
peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=16,
    lora_dropout=0.1,
    inference_mode=False
)

model = get_peft_model(model, peft_config)

# 3. Tokenization
def tokenize(example):
    full_text = example["prompt"] + " " + example["completion"]
    tokenized = tokenizer(
        full_text,
        truncation=True,
        padding="max_length",
        max_length=256
    )
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

tokenized_ds = dataset.map(tokenize, remove_columns=["prompt", "completion"])

# 4. Training setup
training_args = TrainingArguments(
    per_device_train_batch_size=2,
    output_dir="../models/lora_adapter",
    num_train_epochs=2,
    logging_steps=10,
    save_strategy="epoch",
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_ds["train"],
    eval_dataset=tokenized_ds["test"]
)

# 5. Run training
trainer.train()

# 6. Save model and tokenizer
model.save_pretrained("../models/lora_adapter")
tokenizer.save_pretrained("../models/lora_adapter")
