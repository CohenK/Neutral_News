from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch


@torch.no_grad()
def infer(content: str, max_length: int = 512, stride: int = 128):
    """ uses NLP for rating news articles as Left, Neutral, or Right leaning """

    model_name = "premsa/political-bias-prediction-allsides-BERT"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    label_map = {0: "Left", 1: "Neutral", 2: "Right"}

    if not content or not content.strip():
        return None, None

    enc = tokenizer(
        content,
        truncation=True,
        max_length=max_length,
        stride=stride,
        return_overflowing_tokens=True,
        padding=True,              
        return_tensors="pt"
    )

    enc = {k: v.to(device) for k, v in enc.items() if k in ("input_ids", "attention_mask")}

    logits = model(**enc).logits
    probs = torch.softmax(logits, dim=-1)
    probs = probs.cpu().numpy()

    # Weighted vote: sum probabilities across chunks
    summed = probs.sum(axis=0)
    label_idx = int(summed.argmax())
    confidence = float(summed[label_idx] / summed.sum())

    return label_map[label_idx], confidence