import pickle


def save_pickle(data, path):

    with open(path, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

def load_pickle(path):
    pass
