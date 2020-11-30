import pandas as pd
from textslack.textslack import TextSlack
from gensim.models import doc2vec

class NLPModel:
    def __init__(self, sp, conn):
        self.sp = sp
        self.conn = conn
        self.slack = TextSlack(variety='BrE', lang='english')

    def _create_tagged_document(self, list_of_list_of_words):
        for i, list_of_words in enumerate(list_of_list_of_words):
            yield doc2vec.TaggedDocument(list_of_words, [i])

    def _training_data(self):
        df = pd.read_sql_table('SPOTIFY_DATA', con=engine)
        df['key_features'] = df['album'] + df['name'] + df['artist']
        df.drop(['uid', 'track_number', 'id', 'uri'], axis=1, inplace=True)
        df['cleaned_key_features'] = self.slack.transform(df['key_features'])
        cleaned_features= df['cleaned_key_features'].tolist()
        list_list_words = [sent.split() for sent in cleaned_features]
        return list_list_words, df

    def build_model(self):
        list_list_words, _ = self._training_data()
        train_data = list(self._create_tagged_document(list_list_words))
        model = doc2vec.Doc2Vec(vector_size=50, min_count=2, epochs=40)
        model.build_vocab(train_data)
        model.train(train_data, total_examples=model.corpus_count, epochs=model.epochs)
        model.save('doc2vec_model.pkl')

    # def retrain_model(self):
    #     model = doc2vec.Doc2Vec.load('doc2vec_model.pkl')
    #     list_list_words, _ = self._training_data()
    #     train_data = list(self._create_tagged_document(list_list_words))
    #     model.build_vocab(train_data)
    #     model.train(train_data, total_examples=model.corpus_count, epochs=model.epochs)
    #     model.save('doc2vec_model.pkl')

    def generate_predictions(self):


