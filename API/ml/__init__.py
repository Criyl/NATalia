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


def format_text(unformatted, stop_list):
    result = unformatted.lower()

    result = result.split()
    regex = re.compile('.*\\W+.*')
    result = [word for word in result if (len(word) > 0) and (not regex.match(word)) and (word not in stop_list)]

    return result


def word_count(formatted_text):
    # Takes formatted string and returns a dataframe of words and counts

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


class PredictionModel(object):
    dataframe: pd.DataFrame
    stop_list: []

    def __init__(self, modelFrame, stopList):
        if modelFrame is None:
            self.dataframe = pd.DataFrame(columns=['word', 'count_pos', 'count_neg', 'word|pos', 'word|neg']).set_index('word')
        else:
            self.dataframe = modelFrame
        self.stop_list = stopList

    def __str__(self):
        return self.dataframe.__str__()

    def message_is_positive(self, message):
        formatted = format_text(message, self.stop_list)
        prob = 0
        for word in formatted:
            if word in self.dataframe.index:
                prob += m.log10(self.dataframe['word|pos'][word])
        p_pos = prob

        prob = 0
        for word in formatted:
            if word in self.dataframe.index:
                prob += m.log10(self.dataframe['word|neg'][word])
        p_neg = prob

        return p_pos - p_neg

    def add_data(self, message, positive):
        formatted = format_text(message, self.stop_list)
        print(formatted)
        if positive:
            column = "count_pos"
        else:
            column = "count_neg"

        counts = word_count(formatted).rename(columns={'count': column})
        self.dataframe[column] = (self.dataframe[column] + counts[column]).fillna(self.dataframe[column]).fillna(0)
        if positive:
            self.dataframe["count_neg"] = self.dataframe["count_neg"].fillna(0)
        if not positive:
            self.dataframe["count_pos"] = self.dataframe["count_pos"].fillna(0)

        append_dict = {
            'word': [],
            'count_pos': [],
            'count_neg': [],
            'word|pos': [],
            'word|neg': []
        }
        for key in counts.index:
            if key not in self.dataframe.index:
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
        self.dataframe = pd.concat([self.dataframe, pd.DataFrame(append_dict).set_index('word')])

        V = len(self.dataframe.index)
        sum_pos = sum(self.dataframe['count_pos'])
        sum_neg = sum(self.dataframe['count_neg'])

        self.dataframe['word|pos'] = (self.dataframe['count_pos'] + 1) / (sum_pos + V)
        self.dataframe['word|neg'] = (self.dataframe['count_neg'] + 1) / (sum_neg + V)

        return self.dataframe
