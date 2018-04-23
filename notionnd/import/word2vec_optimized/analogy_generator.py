import numpy as np


def generate_domain_analogies(model):
    analogies = []

    brands = {'widgets': 'acme', 'carrots': 'bunny'}
    for key1, val1 in brands.items():
        for key2, val2 in brands.items():
            if key1 != key2:
                analogies.append([key1, val1, key2, val2])
            if val1 != val2:
                analogies.append([val1, key1, val2, key2])

    questions = []
    analogiesAdded = 0
    for i in range(0, int(len(analogies) / 4)):
        ids = [model.word_id(w.strip()) for w in analogies[i]]
        if None in ids or len(ids) != 4:
            pass
        else:
            questions.append(np.array(ids))
            analogiesAdded += 1

    print 'added %d domain analogies' % analogiesAdded
    return questions


def evaluate_domain_analogies(model):
    try:
        total = model.domain_analogies.shape[0]
    except AttributeError as _:
        raise AttributeError("Need to read analogy question")
    correct = 0
    start = 0
    while start < total:
        limit = start + 2500
        sub = model.domain_analogies[start:limit, :]
        idx = model.predict(sub)
        start = limit
        for question in xrange(sub.shape[0]):
            for j in xrange(4):
                if idx[question, j] == sub[question, 3]:
                    # Bingo! We predicted correctly. E.g., [italy, rome,
                    # france, paris].
                    correct += 1
                    break
                elif idx[question, j] in sub[question, :3]:
                    # We need to skip words already in the question.
                    continue
                else:
                    # The correct label is not the precision@1
                    break

    print "domaineval %4d/%d domainaccuracy = %4.1f%%" % (correct, total, correct * 100.0 / total)
    return float(correct) / float(total)

