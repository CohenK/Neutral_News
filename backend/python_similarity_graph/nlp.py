from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

model_name = "premsa/political-bias-prediction-allsides-BERT"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(DEVICE)
model.eval()
label_map = {0: "Left", 1: "Neutral", 2: "Right"}

@torch.inference_mode()
def infer(articles, max_length: int = 512, stride: int = 128, batch_chunks=64):
    """ uses NLP for rating news articles as Left, Neutral, or Right leaning """
    all_input_ids = []
    all_attention = []
    chunk_map = []

    # predefine shape of result to ensure empty articles don't misalign results
    result = [(None, None) for _ in range(len(articles))]
    active_article = [False] * len(articles)


    for article_id, article in enumerate(articles):
        content = article["content"]
        if not content or not content.strip():
            continue
        active_article[article_id] = True
        enc = tokenizer(
            content,
            truncation=True,
            max_length=max_length,
            stride=stride,
            return_overflowing_tokens=True,
            padding="max_length",              
            return_tensors="pt"
        )
        for ids, attentions in zip(enc["input_ids"], enc["attention_mask"]):
            all_input_ids.append(ids)
            all_attention.append(attentions)
            chunk_map.append(article_id)

    sums = torch.zeros((len(articles), 3), dtype=torch.float32) # table to eventually store the split up results

    for start in range(0, len(all_input_ids), batch_chunks):
        end = start + batch_chunks
        ids = all_input_ids[start:end]
        attentions = all_attention[start:end]

        # ensure both ids and attentions are of the same length for model
        ids = torch.nn.utils.rnn.pad_sequence(ids, batch_first=True, padding_value=tokenizer.pad_token_id)
        attentions = torch.nn.utils.rnn.pad_sequence(attentions, batch_first=True, padding_value=0)

        ids = ids.to(DEVICE)
        attentions = attentions.to(DEVICE)
        with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=(DEVICE.type=="cuda")):
            logits = model(input_ids=ids, attention_mask=attentions).logits
        probs = torch.softmax(logits, dim=-1).cpu()

        owners = chunk_map[start:end]
        for row, article_id in enumerate(owners):
            sums[article_id] += probs[row]


    for article_id, is_active in enumerate(active_article):
        total = sums[article_id].sum().item()
        if not is_active or total <= 0:
            continue
        label_id = int(sums[article_id].argmax().item())
        confidence = float((sums[article_id][label_id] / total).item())
        result[article_id] = (label_map[label_id], confidence)
    return result