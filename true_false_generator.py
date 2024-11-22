import time
import torch
import random
from nltk.tokenize import sent_tokenize
from transformers import T5ForConditionalGeneration, T5Tokenizer

#
def tokenize_sentences(text):
    print('tokenize_sentences')
    sentences = [sent_tokenize(text)]
    sentences = [y for x in sentences for y in x]
    sentences = [sentence.strip() for sentence in sentences if len(sentence) > 20]
    return sentences


def beam_search_decoding(inp_ids, attn_mask, model, tokenizer):
    print('beam_search_decoding')
    beam_output = model.generate(input_ids=inp_ids,
                                 attention_mask=attn_mask,
                                 max_length=256,
                                 num_beams=10,
                                 num_return_sequences=3,
                                 no_repeat_ngram_size=2,
                                 early_stopping=True
                                 )
    questions = [tokenizer.decode(out, skip_special_tokens=True, clean_up_tokenization_spaces=True) for out in
                 beam_output]
    return [question.strip().capitalize() for question in questions]


def random_choice():
    a = random.choice([0, 1])
    return bool(a)


def set_seed(seed):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class TrueFalseGen:

    def __init__(self):
        self.tokenizer = T5Tokenizer.from_pretrained('t5-base')
        model = T5ForConditionalGeneration.from_pretrained('ramsrigouthamg/t5_boolean_questions')
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)

        self.device = device
        self.model = model
        set_seed(42)

    def true_false_questions(self, payload):
        print('TrueFalseGen: true_false_questions')
        inp = {
            "input_text": payload.get("input_text"),
            "max_questions": payload.get("max_questions", 4)
        }

        text = inp['input_text']
        num = inp['max_questions']
        sentences = tokenize_sentences(text)
        joiner = " "
        modified_text = joiner.join(sentences)
        answer = random_choice()
        form = "truefalse: %s passage: %s </s>" % (modified_text, answer)

        encoding = self.tokenizer.encode_plus(form, return_tensors="pt")
        input_ids, attention_masks = encoding["input_ids"].to(self.device), encoding["attention_mask"].to(self.device)

        output = beam_search_decoding(input_ids, attention_masks, self.model, self.tokenizer)
        if torch.device == 'cuda':
            torch.cuda.empty_cache()

        final = {'Text': text, 'Count': num, 'Boolean Questions': output}

        return final, answer
