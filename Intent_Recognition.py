import numpy as np # linear algebra
#import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
#import json
#import os
#from sklearn.metrics import roc_curve
#from sklearn.metrics import accuracy_score
#from sklearn.model_selection import train_test_split
#from tensorflow.keras.utils import to_categorical
#from tensorflow.keras.models import Sequential, Model
#from tensorflow.keras.layers import Input, Dense, Embedding, Activation, LSTM, SimpleRNN, Dropout
#from tensorflow.keras.optimizers import Adam
#from tensorflow.keras.preprocessing.text import Tokenizer
#from tensorflow.keras.preprocessing.sequence import pad_sequences
import bert
from tqdm import tqdm
#from tensorflow.keras import backend as K
import tensorflow as tf
import tensorflow_hub as hub
import streamlit as st

class BertModel(object):
    def __init__(self):
        self.max_len = 128
        bert_path = "https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4"
        FullTokenizer = bert.bert_tokenization.FullTokenizer
        
        self.bert_module = hub.KerasLayer(bert_path,trainable = True)
        self.vocab_file = self.bert_module.resolved_object.vocab_file.asset_path.numpy()
        self.do_lower_case = self.bert_module.resolved_object.do_lower_case.numpy()
        
        self.tokenizer = FullTokenizer(self.vocab_file,self.do_lower_case)
        
    def get_masks(self,tokens, max_seq_length):
        return [1]*len(tokens) + [0]*(max_seq_length-len(tokens))
        
    def get_segments(self,tokens, max_seq_length):
        segments = []
        current_segment_id = 0
        for token in tokens:
            segments.append(current_segment_id)
            if token == "[SEP]":
                current_segment_id = 1
        return segments + [0]*(max_seq_length-len(tokens)) 
    
    def get_ids(self,tokens,tokenizer, max_seq_length):
        token_ids = tokenizer.convert_tokens_to_ids(tokens)
        input_ids = token_ids + [0]*(max_seq_length-len(token_ids))
        return input_ids
    
    def create_single_input(self,sentence,maxlen):
        stokens = self.tokenizer.tokenize(sentence)
        stokens = stokens[:maxlen]
        stokens = ["[CLS]"] + stokens +  ["[SEP]"]
        
        ids = self.get_ids(stokens,self.tokenizer,self.max_len)
        masks =  self.get_masks(stokens, self.max_len)
        segments = self.get_segments(stokens, self.max_len)
        
        return ids, masks, segments
    
    def create_input_array(self,sentences):
        
        input_ids, input_masks, input_segments =[],[],[]
        
        for sentence in tqdm(sentences,position=0, leave = True):
            ids,masks,segments = self.create_single_input(sentence,self.max_len-2)
            
            input_ids.append(ids)
            input_masks.append(masks)
            input_segments.append(segments)
            
        tensor = [
            np.asarray(input_ids,dtype= 'int32'),
            np.asarray(input_masks,dtype= 'int32'),
            np.asarray(input_segments,dtype= 'int32')
        ]
        
        return tensor

@st.cache_resource
def load_model():
    bert_obj_model = BertModel()
    model = tf.keras.models.load_model('saved_model')    
    return model,bert_obj_model   

pred_number = 0

def prediction(sentence:str):
    query_sequences = bert_obj_model.create_input_array(sentences = [sentence])
    tf.compat.v1.enable_eager_execution()
    pred = model.predict(query_sequences)
    pred_number = np.argmax(pred)
    pred = np.max(pred)
    return pred,pred_number
