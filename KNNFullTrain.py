import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
import joblib

# Load your dataset
data = pd.read_csv('Phishing_email.csv', usecols=['Email Text', 'Email Type'])

# Fill missing values in 'Email Text' column with an empty string
data['Email Text'] = data['Email Text'].fillna('')

# Separate features and labels
X = data['Email Text']  # Email content
y = data['Email Type']  # Label (phishing or safe)

print(data['Email Type'].unique())

# Ensure all values in the dataset are strings
X = X.astype(str)

# Vectorize the email text using TF-IDF
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
# removes common words not informative like the, is, etc.
# converts to a matrix of token counts with tf-idf weights

X_tfidf = tfidf_vectorizer.fit_transform(X)

# Initialize the Naive Bayes classifier
kn_classifier = KNeighborsClassifier()

# Train the model on the entire dataset
kn_classifier.fit(X_tfidf, y)

# Save the trained model and vectorizer
joblib.dump(kn_classifier, 'knn_model.pkl')
joblib.dump(tfidf_vectorizer, 'knn_vectorizer.pkl')

print("Model and vectorizer saved successfully!")
