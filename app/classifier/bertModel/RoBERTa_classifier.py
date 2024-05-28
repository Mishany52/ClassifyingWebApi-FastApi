import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
from ...config import settings
class RoBERTaClassifier:

    def __init__(
            self,
            model_path=settings.ROBERTA_MODEL_NAME,
            tokenizer_path=settings.ROBERTA_MODEL_NAME,
            n_classes=3,
            max_len=512
        ):
        self.model = RobertaForSequenceClassification.from_pretrained(          
            pretrained_model_name_or_path = model_path,
            num_labels = n_classes,
            hidden_dropout_prob = 0.2,
            attention_probs_dropout_prob = 0.2
        )
        
        self.tokenizer = RobertaTokenizer.from_pretrained(tokenizer_path)
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = torch.load(settings.ROBERTA_PRETRAINED, map_location=self.device)
        
        self.model.to(self.device)
        self.max_len = max_len
        
    def predict(self, text):
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            truncation=True,
            padding='max_length',
            return_attention_mask=True,
            return_tensors='pt',
        )
        
        out = {
            'text': text,
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten()
        }
        
        input_ids = out["input_ids"].to(self.device)
        attention_mask = out["attention_mask"].to(self.device)
        
        outputs = self.model(
            input_ids=input_ids.unsqueeze(0),
            attention_mask=attention_mask.unsqueeze(0)
        )
        
        prediction = torch.argmax(outputs.logits, dim=1).cpu().numpy()[0]
        names_class = ['Games','Online Communities', 'People and Society']
        return names_class[prediction]
    
model = RoBERTaClassifier()

def get_model():
    return model

