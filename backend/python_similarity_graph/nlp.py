from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from statistics import mode

model_name = "premsa/political-bias-prediction-allsides-BERT"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
nlp = pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    truncation=True,
    max_length=512,
    padding=True
)

def infer(content):
    """ uses NLP for rating news articles as Left, Neutral, or Right leaning """

    chunk_size, overlap = 1000, 200
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size - overlap)]
    
    labels, score = [], []
    results = nlp(chunks)
    for r in results:
        labels.append(r["label"])
        score.append(r["score"])
    
    label_map = {"LABEL_0": "Left", "LABEL_1": "Neutral", "LABEL_2": "Right"}

    return (label_map[mode(labels)], mode(score))