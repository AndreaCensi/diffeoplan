def load_pickle(pickle):
    return safe_pickle_load(pickle)
    

def safe_pickle_load(filename):
    import cPickle as pickle
    # TODO: add debug check 
    with open(filename, 'rb') as f:
        return pickle.load(f)
