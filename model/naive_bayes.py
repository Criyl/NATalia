import os
import re
import math as m
import pandas as pd


def read_stop(filename):
    stop_list = []
    file = open(filename)

    for line in file:
        stop_list.append(line.replace('\n', ''))
    file.close()
    return stop_list


def format_file(unformatted, stop_list):
    result = unformatted.lower()

    result = result.split()
    regex = re.compile('.*\\W+.*')
    result = [word for word in result if (len(word) > 0) and (not regex.match(word)) and (word not in stop_list)]

    return result


def word_count(formatted_text):
    count_dict = {}

    for word in formatted_text:
        if word in count_dict:
            count_dict[word] += 1
        else:
            count_dict[word] = 1
    data_dict = {
        'word': list(count_dict.keys()),
        'count': list(count_dict.values())
    }
    df = pd.DataFrame(data_dict, columns=['word', 'count']).set_index('word').sort_index().astype(int)
    return df


class Model(object):
    model: pd.DataFrame
    stop_list: []

    def __init__(self, model_path, stop_path):
        self.model = pd.read_pickle(model_path)
        self.stop_list = read_stop(stop_path)

    def __str__(self):
        return self.model.__str__()

    def message_is_positive(self, message):
        sum_pos = sum(self.model['count_pos'])
        sum_neg = sum(self.model['count_neg'])

        formatted = format_file(message, self.stop_list)
        prob = 0
        for word in formatted:
            if word in self.model.index:
                prob += m.log10(self.model['word|pos'][word])
        p_pos = prob

        prob = 0
        for word in formatted:
            if word in self.model.index:
                prob += m.log10(self.model['word|neg'][word])
        p_neg = prob

        return p_pos - p_neg

    def add_data(self, message, positive):
        formatted = format_file(message, self.stop_list)

        if positive:
            column = "count_pos"
        else:
            column = "count_neg"

        counts = word_count(formatted).rename(columns={'count': column})
        self.model[column] = (self.model[column] + counts[column]).fillna(self.model[column])
        append_dict = {
            'word': [],
            'count_pos': [],
            'count_neg': [],
            'word|pos': [],
            'word|neg': []
        }
        for key in counts.index:
            if key not in self.model.index:
                append_dict['word'] += [key]
                if positive:
                    append_dict['count_pos'] += [counts[column][key]]
                    append_dict['count_neg'] += [0]
                else:
                    append_dict['count_pos'] += [0]
                    append_dict['count_neg'] += [counts[column][key]]

                append_dict['word|pos'] += [0]
                append_dict['word|neg'] += [0]
        print(append_dict)
        self.model = pd.concat([self.model, pd.DataFrame(append_dict).set_index('word')])

        V = len(self.model.index)
        sum_pos = sum(self.model['count_pos'])
        sum_neg = sum(self.model['count_neg'])

        self.model['word|pos'] = (self.model['count_pos'] + 1) / (sum_pos + V)
        self.model['word|neg'] = (self.model['count_neg'] + 1) / (sum_neg + V)

        return self.model
