import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification


if __name__ == '__main__':
    tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
    model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

    inputs = tokenizer("Hello, my dog is cute", return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits

    predicted_class_id = logits.argmax().item()
    var = model.config.id2label[predicted_class_id]
    print(var)
