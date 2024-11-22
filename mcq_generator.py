import time
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
import spacy
from sense2vec import Sense2Vec
import numpy
from nltk import FreqDist
from nltk.corpus import brown
from strsimpy.normalized_levenshtein import NormalizedLevenshtein
from questgen_helper import *


def generate_mcq_questions(keyword_sent_mapping, device, tokenizer, model, sense2vec, normalized_levenshtein):
    print('generate_mcq_questions')
    batch_text = []
    answers = keyword_sent_mapping.keys()
    for answer in answers:
        txt = keyword_sent_mapping[answer]
        context = "context: " + txt
        text = context + " " + "answer: " + answer + " </s>"
        batch_text.append(text)

    encoding = tokenizer.batch_encode_plus(batch_text, pad_to_max_length=True, return_tensors="pt")
    input_ids, attention_masks = encoding["input_ids"].to(device), encoding["attention_mask"].to(device)

    with torch.no_grad():
        outs = model.generate(input_ids=input_ids,
                              attention_mask=attention_masks,
                              max_length=150)

    output_array = dict()
    output_array["questions"] = []

    for index, val in enumerate(answers):
        individual_question = {}
        out = outs[index, :]
        dec = tokenizer.decode(out, skip_special_tokens=True, clean_up_tokenization_spaces=True)

        question = dec.replace("question:", "")
        question = question.strip()
        individual_question["question_statement"] = question
        individual_question["question_type"] = "MCQ"
        individual_question["answer"] = val
        individual_question["id"] = index + 1
        individual_question["options"], individual_question["options_algorithm"] = get_options(val, sense2vec)

        individual_question["options"] = filter_phrases(individual_question["options"], 10, normalized_levenshtein)
        index = 3
        individual_question["extra_options"] = individual_question["options"][index:]
        individual_question["options"] = individual_question["options"][:index]
        individual_question["context"] = keyword_sent_mapping[val]

        if len(individual_question["options"]) > 0:
            output_array["questions"].append(individual_question)

    return output_array


class MCQGen:

    def __init__(self):
        self.tokenizer = T5Tokenizer.from_pretrained('t5-base')
        model = T5ForConditionalGeneration.from_pretrained('Parth/result')
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        # model.eval()
        self.device = device
        self.model = model
        self.nlp = spacy.load('en_core_web_sm')
        self.s2v = Sense2Vec().from_disk('s2v_old')
        self.fdist = FreqDist(brown.words())
        self.normalized_levenshtein = NormalizedLevenshtein()
        self.set_seed(42)

    @staticmethod
    def set_seed(seed):
        numpy.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

    def mcq_questions(self, payload):
        print('MCQGen: mcq_questions')
        start = time.time()
        inp = {
            "input_text": payload.get("input_text"),
            "max_questions": payload.get("max_questions", 4)
        }

        text = inp['input_text']
        sentences = tokenize_sentences(text)
        joiner = " "
        modified_text = joiner.join(sentences)

        keywords = get_keywords(self.nlp, modified_text, inp['max_questions'], self.s2v, self.fdist,
                                self.normalized_levenshtein, len(sentences))

        keyword_sentence_mapping = get_sentences_for_keyword(keywords, sentences)

        for k in keyword_sentence_mapping.keys():
            text_snippet = " ".join(keyword_sentence_mapping[k][:3])
            keyword_sentence_mapping[k] = text_snippet

        final_output = {}

        if len(keyword_sentence_mapping.keys()) == 0:
            return final_output
        else:
            try:
                generated_questions = generate_mcq_questions(keyword_sentence_mapping, self.device, self.tokenizer,
                                                             self.model, self.s2v, self.normalized_levenshtein)

            except (TypeError, Exception):
                return final_output
            end = time.time()

            final_output["statement"] = modified_text
            final_output["questions"] = generated_questions["questions"]
            final_output["time_taken"] = end - start

            if torch.device == 'cuda':
                torch.cuda.empty_cache()

            return final_output
