import pandas as pd
import subprocess
import tempfile
import os
from email.utils import formatdate

def format_email(content):
    email_template = f"""From: sender@example.com
To: recipient@example.com
Subject: Email Content
Date: {formatdate(localtime=True)}

{content}"""
    return email_template

def check_spam(email_content):
    formatted_email = format_email(str(email_content))  # Convert to string
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write(formatted_email)
        tmp_path = tmp.name
    
    try:
        result = subprocess.run(['spamassassin', '-t', tmp_path], 
                              capture_output=True, 
                              text=True)
        #print (result.stdout)
        #print (result.stderr)
        print("email proccessed: " + str(email_content)[0:10])
        
        is_spam = 'X-Spam-Flag: YES' in result.stdout
        score_line = [line for line in result.stdout.split('\n') 
                     if 'X-Spam-Status' in line]
        score = float(score_line[0].split('score=')[1].split()[0]) if score_line else None
        
        return is_spam, score
    
    finally:
        os.unlink(tmp_path)

def process_csv(csv_path, limit=1000): # number of emails
    df = pd.read_csv(csv_path)
    df = df.head(limit)
    
    results = []
    for _, row in df.iterrows():
        is_spam, score = check_spam(row['Email Text'])  # Use 'Email Text' column
        results.append({
            'email_number': _,
            'content': str(row['Email Text'])[:100] + '...',
            'actual_class': row['Email Type'],
            'predicted_spam': is_spam,
            'spam_score': score
        })
    
    results_df = pd.DataFrame(results)
    return results_df

def calculate_accuracy_metrics(results_df):
    # Convert actual_class to boolean (True if Phishing Email)
    results_df['actual_phishing'] = results_df['actual_class'] == 'Phishing Email'
    
    # Calculate metrics
    total_phishing = results_df['actual_phishing'].sum()
    total_safe = len(results_df) - total_phishing
    
    # True Positives: Correctly identified phishing emails
    true_positives = sum((results_df['actual_phishing']) & (results_df['predicted_spam']))
    
    # True Negatives: Correctly identified safe emails
    true_negatives = sum((~results_df['actual_phishing']) & (~results_df['predicted_spam']))
    
    # False Positives: Safe emails incorrectly marked as phishing
    false_positives = sum((~results_df['actual_phishing']) & (results_df['predicted_spam']))
    
    # False Negatives: Phishing emails missed
    false_negatives = sum((results_df['actual_phishing']) & (~results_df['predicted_spam']))
    
    # Calculate accuracy metrics
    accuracy = (true_positives + true_negatives) / len(results_df)
    
    # Calculate precision and recall for phishing detection
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / total_phishing if total_phishing > 0 else 0

    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        'Total Emails': len(results_df),
        'Total Phishing Emails': total_phishing,
        'Total Safe Emails': total_safe,
        'Correctly Identified Phishing': true_positives,
        'Correctly Identified Safe': true_negatives,
        'False Positives': false_positives,
        'False Negatives': false_negatives,
        'Overall Accuracy': accuracy * 100,
        'Precision': precision * 100,
        'Recall': recall * 100,
        'F1 Score': f1_score * 100
    }

if __name__ == '__main__':
    results_df = process_csv('Phishing_Email/Phishing_Email.csv')
    results_df.to_csv('spam_results.csv', index=False)
    
    # Calculate and display accuracy metrics
    metrics = calculate_accuracy_metrics(results_df)
    print("\nAccuracy Metrics:")
    for metric, value in metrics.items():
        if 'Total' in metric:
            print(f"{metric}: {int(value)}")
        else:
            print(f"{metric}: {value:.2f}%")