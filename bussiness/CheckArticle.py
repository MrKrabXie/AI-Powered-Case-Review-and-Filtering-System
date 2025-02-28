import requests
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# 加载预训练的审核模型
model_name = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# 内容审核函数
def content_review(text):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
    predicted_class_id = logits.argmax().item()
    label = model.config.id2label[predicted_class_id]
    if label == "NEGATIVE":
        return "违规内容"
    else:
        return "正常内容"



# 主函数
def main():
    # 内容审核测试
    # test_text = "这是一段正常的网文内容。"
    # test_text = "hello world。"
    # test_text = "fuck you !"
    # test_text = "dirty talk"
    test_text = "good morning"
    review_result = content_review(test_text)
    print(f"内容审核结果: {review_result}")



if __name__ == "__main__":
    main()