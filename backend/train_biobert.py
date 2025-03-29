from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from sklearn.preprocessing import LabelEncoder
import torch
from torch.utils.data import Dataset
import pandas as pd
from sklearn.model_selection import train_test_split

# Load and preprocess the dataset
df = pd.read_csv('dataset.csv')
df['symptoms'] = df.iloc[:, 1:].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1)
df = df[['Disease', 'symptoms']]
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# Encode labels
label_encoder = LabelEncoder()
train_df['label'] = label_encoder.fit_transform(train_df['Disease'])
test_df['label'] = label_encoder.transform(test_df['Disease'])

# Tokenizer
tokenizer = BertTokenizer.from_pretrained('monologg/biobert_v1.1_pubmed')

# Dataset class
class SymptomDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

# Create datasets
max_len = 128
train_dataset = SymptomDataset(train_df['symptoms'].tolist(), train_df['label'].tolist(), tokenizer, max_len)
test_dataset = SymptomDataset(test_df['symptoms'].tolist(), test_df['label'].tolist(), tokenizer, max_len)

# Load BioBERT model
model = BertForSequenceClassification.from_pretrained('monologg/biobert_v1.1_pubmed', num_labels=len(label_encoder.classes_))

# Training arguments
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset
)

# Fine-tune the model
trainer.train()

# Save the fine-tuned model and tokenizer
model.save_pretrained('./fine_tuned_biobert')
tokenizer.save_pretrained('./fine_tuned_biobert')

# Save the label encoder
import joblib
joblib.dump(label_encoder, 'label_encoder.pkl')