import extract_data as exd
from datetime import date
import tokenice as tok

if __name__ == "__main__":
    '''1: Extract the data collected between (start_date,end_date)'''
    # Start and End date
    start_date = date(2024,6,5)
    end_date = date(2024, 6, 8)

    # Generate the data using build_data
    status = exd.build_data(start_date, end_date)

    print(status)

    '''2: Use Bag-of-Words to the txt we have'''
    data = exd.text_to_list("./textos")

    vocab, len_vector,sentences = tok.data_cleaning(data)

    index_word = tok.vocab_to_dict(vocab)

    vector = tok.bag_of_words(sentences[0], len_vector, index_word)
    vector1 = tok.bag_of_words(sentences[1], len_vector, index_word)
    vector2 = tok.bag_of_words(sentences[2], len_vector, index_word)


    print(vector)
    print(vector1)
    print(vector2)
