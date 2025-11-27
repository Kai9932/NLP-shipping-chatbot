import re
import os
import random
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import spacy

try:
    from transformers import pipeline
    _TRANSFORMER_AVAILABLE = True
except Exception:
    _TRANSFORMER_AVAILABLE = False

BASE_DIR = os.path.dirname(__file__)
INTENTS_CSV = os.path.join(BASE_DIR, "data", "intents.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_PATH, exist_ok=True)

# Load spaCy
nlp_spacy = spacy.load("en_core_web_sm")

class NLPModel:
    def __init__(self):
        self.vectorizer = None
        self.clf = None
        self._load_or_train()

        self.generator = None
        if _TRANSFORMER_AVAILABLE:
            try:

                self.generator = pipeline("text-generation", model="microsoft/DialoGPT-small")
            except Exception:
                self.generator = None

    def _load_or_train(self):
        vec_path = os.path.join(MODEL_PATH, "vectorizer.joblib")
        clf_path = os.path.join(MODEL_PATH, "clf.joblib")

        if os.path.exists(vec_path) and os.path.exists(clf_path):
            self.vectorizer = joblib.load(vec_path)
            self.clf = joblib.load(clf_path)
            return

        # Train
        df = pd.read_csv(INTENTS_CSV)
        X = df['text'].astype(str).values
        y = df['intent'].astype(str).values

        self.vectorizer = TfidfVectorizer(ngram_range=(1,2))
        Xv = self.vectorizer.fit_transform(X)

        self.clf = LogisticRegression(max_iter=1000)
        self.clf.fit(Xv, y)

        joblib.dump(self.vectorizer, vec_path)
        joblib.dump(self.clf, clf_path)

    def predict_intent(self, text):
        text = str(text)
        Xv = self.vectorizer.transform([text])
        pred = self.clf.predict(Xv)[0]
        proba = max(self.clf.predict_proba(Xv)[0])
        return pred, float(proba)

    def extract_order_number(self, text):
        """
        Extract order numbers using regex and spaCy.
        Matches:
        - ORDER 12345
        - #12345
        - 12345 (when preceded by word 'order' or 'order number')
        """
        text = str(text)

        patterns = [
            r"order\s*[#:]?\s*(\d+)",
            r"#(\d+)",
            r"tracking\s*#?\s*(\w+)",
            r"\b(\d{5,12})\b"
        ]
        for p in patterns:
            m = re.search(p, text, flags=re.IGNORECASE)
            if m:
                return m.group(1)

        # spaCy
        doc = nlp_spacy(text)
        for ent in doc.ents:
            if ent.label_ in {"CARDINAL", "QUANTITY"} and re.search(r"\d", ent.text):
                return re.sub(r"\D", "", ent.text)

        return None

    def generate_free_response(self, prompt, max_length=80):
        """ Use transformer generator if available, otherwise simple fallback """
        if self.generator:
            try:
                out = self.generator(prompt, max_length=max_length, num_return_sequences=1)[0]["generated_text"]

                return out
            except Exception:
                pass

        fallbacks = [
            "I'm here to help — can you tell me more?",
            "Sorry, I don't have that info. Could you rephrase?",
            "I can help with orders, packages, and payments."
        ]
        return random.choice(fallbacks)

model = NLPModel()

if __name__ == "__main__":
    print("Test prediction examples:")
    for s in ["hello", "order 12345", "my package is missing", "refund please"]:
        print(s, "->", model.predict_intent(s), "order->", model.extract_order_number(s))
