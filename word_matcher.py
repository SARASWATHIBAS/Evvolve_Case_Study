from gensim.models import KeyedVectors # type: ignore
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class WordMatcher:
    def __init__(self, model_path: str):
        self.model = KeyedVectors.load_word2vec_format(model_path, binary=True)
    
    def get_similarity(self, words: list, sector: str) -> float:
        total_score = 0
        valid_words_count = 0
        
        for word in words:
            if word in self.model and sector in self.model:
                word_vector = self.model[word].reshape(1, -1)
                sector_vector = self.model[sector].reshape(1, -1)
                similarity = cosine_similarity(word_vector, sector_vector)[0][0]
                # Scale similarity to 0-100
                score = int(similarity * 100)
                total_score += score
                valid_words_count += 1
        
        if valid_words_count == 0:
            return 0  # or some default value indicating no similarity
        
        # Return the average score
        return total_score / valid_words_count