import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os

def prepare_data():
    input_file = 'datasets/processed/final_dataset_berlabel.csv'
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return
        
    print(f"Loading {input_file}...")
    df = pd.read_csv(input_file, sep='|', encoding='utf-8')
    
    print(f"Original shape: {df.shape}")
    
    # 1. Check and drop missing values
    missing_before = df.isnull().sum()
    print("\nMissing values before cleaning:")
    print(missing_before)
    
    df.dropna(subset=['Teks_Gabungan', 'Label_Sentimen'], inplace=True)
    
    # 2. Fix/clean labels
    df['Label_Sentimen'] = df['Label_Sentimen'].astype(str).str.strip().str.title()
    valid_labels = ['Positif', 'Negatif', 'Netral']
    
    # Check invalid labels
    invalid_mask = ~df['Label_Sentimen'].isin(valid_labels)
    if invalid_mask.any():
        print(f"\nFound {invalid_mask.sum()} invalid labels. Dropping them.")
        print(df[invalid_mask]['Label_Sentimen'].value_counts())
        df = df[~invalid_mask]
        
    # Drop rows where text is too short
    df = df[df['Teks_Gabungan'].str.len() > 20]
    
    # Drop duplicates
    duplicates = df.duplicated(subset=['Teks_Gabungan']).sum()
    print(f"\nFound {duplicates} duplicate texts. Dropping them.")
    df.drop_duplicates(subset=['Teks_Gabungan'], inplace=True)
    
    print(f"\nShape after cleaning: {df.shape}")
    
    # 3. Analyze distribution
    print("\nClass distribution:")
    dist = df['Label_Sentimen'].value_counts()
    print(dist)
    print("\nClass distribution (%):")
    print(df['Label_Sentimen'].value_counts(normalize=True) * 100)
    
    # 4. Shuffle / Randomize
    print("\nShuffling dataset...")
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # 5. Split into train, val, test (80%, 10%, 10%)
    print("\nSplitting into Train, Val, Test (80%, 10%, 10%)...")
    # First split into train (80%) and temp (20%)
    train_df, temp_df = train_test_split(df, test_size=0.2, stratify=df['Label_Sentimen'], random_state=42)
    # Then split temp into val (50% of 20% = 10%) and test (10%)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, stratify=temp_df['Label_Sentimen'], random_state=42)
    
    print("\nTrain Class distribution:")
    print(train_df['Label_Sentimen'].value_counts())
    
    print(f"\nFinal Train size: {train_df.shape[0]}")
    print(f"Val size: {val_df.shape[0]}")
    print(f"Test size: {test_df.shape[0]}")
    
    # Create processed directory
    os.makedirs('datasets/processed', exist_ok=True)
    
    # Save datasets
    train_df.to_csv('datasets/processed/train.csv', sep='|', index=False, encoding='utf-8')
    val_df.to_csv('datasets/processed/val.csv', sep='|', index=False, encoding='utf-8')
    test_df.to_csv('datasets/processed/test.csv', sep='|', index=False, encoding='utf-8')
    
    print("\nFiles saved successfully to 'datasets/processed/'!")
    

if __name__ == '__main__':
    prepare_data()
