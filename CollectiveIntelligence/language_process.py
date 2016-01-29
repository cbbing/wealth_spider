#coding=utf8

from nltk import FreqDist
from nltk.corpus import brown

def gender_features(word):
    return {'suffix1':word[-1:],
            'suffix2':word[-2:]}

def gender_features2(name):
    features = {}
    features['firstletter'] = name[0].lower()
    features['lastletter'] = name[-1].lower()
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        features['count({})'.format(letter)] = name.lower().count(letter)
        features['has({})'.format(letter)] = (letter in name.lower())
    return features

#print gender_features2('John')

from nltk.corpus import names
import random
import nltk
names = ([(name, 'male') for name in names.words('male.txt')] + [(name, 'female') for name in names.words('female.txt')])
random.shuffle(names)

#featuresets = [(gender_features2(n), g) for (n, g) in  names]

train_names = names[1500:]
devtest_names = names[500:1500]
test_names = names[:500]

train_set = [(gender_features(n), g) for (n, g) in train_names]
devtest_set = [(gender_features(n), g) for (n, g) in devtest_names]
test_set = [(gender_features(n), g) for (n, g) in test_names]
classifier = nltk.NaiveBayesClassifier.train(train_set)
print nltk.classify.accuracy(classifier, devtest_set)

errors = []
for (name, tag) in devtest_names:
    guess = classifier.classify(gender_features(name))
    if guess != tag:
        errors.append((tag, guess, name))

for (tag, guess, name) in sorted(errors):
    print 'correct=%-8s guess=%-8s name=%-30s' % (tag, guess, name)


# from nltk.corpus import movie_reviews
# documents = [(list(movie_reviews.words(fileid)), category)
#              for category in movie_reviews.categories() for fileid in movie_reviews.fileids(category)]
# random.shuffle(documents)
#
# all_words = nltk.FreqDist(w.lower() for w in movie_reviews.words())
# word_features = all_words.keys()[:2000]
# def document_features(document):
#     document_words = set(document)
#     features = {}
#     for word in word_features:
#         features['contains(%s)' % word] = (word in document_words)
#     return features
#
# print document_features(movie_reviews.words('pos/cv957_8737.txt'))
#
# featuresets = [(document_features(d), c) for (d, c) in documents]
# train_set, test_set = featuresets[100:], featuresets[:100]
# classifier = nltk.NaiveBayesClassifier.train(train_set)
# print nltk.classify.accuracy(classifier, test_set)
# print classifier.show_most_informative_features(5)

def pos_features(sentence, i, history):
    features = {'suffix(1)':sentence[i][-1:],
                'suffix(2)':sentence[i][-2:],
                'suffix(3)':sentence[i][-3:],}
    if i == 0:
        features['prev-word'] = "<START>"
        features['prev-tag'] = "<START>"
    else:
        features['prev-word'] = sentence[i-1]
        features['prev-tag'] = history[i-1]
    return features

class ConsecutivePosTagger(nltk.TaggerI):
    def __init__(self, train_sents):
        train_set = []
        for tagged_sent in train_set:
            untagged_sent = nltk.tag.untag(tagged_sent)
            history = []
            for i, (word, tag) in enumerate(tagged_sent):
                featuresets = pos_features(untagged_sent, i, history)
                train_set.append((featuresets, tag))
                history.append(tag)

        self.classifier = nltk.NaiveBayesClassifier.train(train_set)

    def tag(self, sentence):
        history = []
        for i, word in enumerate(sentence):
            featuresets = pos_features(sentence, i, history)
            tag = self.classifier.classify(featuresets)
            history.append(tag)
        return zip(sentence, history)

# tagged_sents = brown.tagged_sents(categories='news')
# size = int(len(tagged_sents) * 0.1)
# train_sents, test_sents = tagged_sents[size:], tagged_sents[:size]
# tagger = ConsecutivePosTagger(train_sents)
# print tagger.evaluate(test_sents)