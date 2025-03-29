# analyze.py

import torch
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.preprocessing import LabelEncoder
import joblib

# Load the fine-tuned model, tokenizer, and label encoder
model = BertForSequenceClassification.from_pretrained('./fine_tuned_biobert')
tokenizer = BertTokenizer.from_pretrained('./fine_tuned_biobert')
label_encoder = joblib.load('label_encoder.pkl')

# Function to predict disease from symptoms
def predict_disease(symptoms, max_len=128):
    # Tokenize the input symptoms
    encoding = tokenizer.encode_plus(
        symptoms,
        add_special_tokens=True,
        max_length=max_len,
        return_token_type_ids=False,
        padding='max_length',
        truncation=True,
        return_attention_mask=True,
        return_tensors='pt',
    )

    # Make prediction
    with torch.no_grad():
        input_ids = encoding['input_ids']
        attention_mask = encoding['attention_mask']
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        preds = torch.argmax(logits, dim=1).cpu().numpy()

    # Decode the predicted label
    predicted_label = label_encoder.inverse_transform(preds)[0]
    return predicted_label