import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from collections import defaultdict 


def data_cleaning(data: list[str], rm_stop_words=False) -> list[str]:
    #clean the corpus.
    sentences = []
    vocab = []
    for sent in data:
        x = word_tokenize(sent)
        sentence = [w.lower() for w in x if w.isalpha() ]
        sentences.append(sentence)
        for word in sentence:
            if word not in vocab:
                vocab.append(word)
    
    #number of words in the vocab
    len_vector = len(vocab)

    return vocab, len_vector, sentences

def vocab_to_dict(vocab:list):
    index_word = {}
    for i,word in enumerate(vocab):
        index_word[word] = i

    return index_word


def bag_of_words(sent, len_vector, index_word):
    count_dict = defaultdict(int)
    vec = np.zeros(len_vector)
    for item in sent:
        count_dict[item] += 1
    for key,item in count_dict.items():
        vec[index_word[key]] = item
    return vec  