📌 Project Overview
Medical Symptom Analyzer is a web-based application that uses BioBERT for NLP-based disease prediction. Users enter symptoms, and the system predicts possible diseases, retrieving descriptions and precautions from a MySQL database.

🔧 Tech Stack
Backend: Python (Flask), BioBERT, MySQL

Frontend: HTML, CSS, Bootstrap

AI Model: Fine-tuned BioBERT on a symptom-disease dataset

🚀 Features
User
✅ Enter symptoms for analysis
✅ AI-based disease prediction using BioBERT
✅ View disease description & precautions

Admin
✅ Manage symptoms, diseases & precautions
✅ View registered users

## 📂 Dataset

The dataset used for training BioBERT can be downloaded from the following link:

🔗 **[Download Dataset]("itachi9604/disease-symptom-description-dataset")**  
📌 *Credits: [Dataset Author]([https://www.kaggle.com/author-profile](https://www.kaggle.com/itachi9604))*  

After downloading, place the dataset in the `backend` directory:

you could also use other dataset ,then change biobert training code according to it

## 🛠️ Database Setup

1. **Create the Database**  
   Open MySQL and run:
   ```sql
   CREATE DATABASE medical_symptom_analyzer;
