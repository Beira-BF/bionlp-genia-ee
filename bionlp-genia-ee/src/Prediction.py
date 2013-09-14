'''
Created on Sep 10, 2013

@author: Andresta
'''
import os, json

from datetime import datetime as dt
from model.Dictionary import WordDictionary, TriggerDictionary
from model.Document import DocumentBuilder
from features.FeatureExtraction import FeatureExtraction
from classifier.SVM import SVM


class Prediction(object):
    '''
    classdocs
    '''
    
    # suffix and extension of id file
    DOCID_SUFFIX_EXT = "_doc_ids.json"
    
    # directory for saving svm model
    MODEL_DIR = "/model"

    # list of event name
    EVENT_NAME = ["None",
                  "Gene_expression",
                  "Transcription",
                  "Protein_catabolism",
                  "Phosphorylation",
                  "Localization",
                  "Binding",
                  "Regulation",
                  "Positive_regulation",
                  "Negative_regulation"]
        

    def __init__(self, source, dir_name, dict_type):
        '''
        Constructor
        '''
        self.src = source
        self.path = self.get_path(source, dir_name)
        
        self.dict_type = dict_type
        self.wdict = None
        self.tdict = None
        self.doc_builder = None
        self.extraction = None      
        
        self.docs = {}          
        
        self._set(dict_type)
    
    def _set(self, dict_type):
        """
        initialize dictionary type to be used in feature extraction process
        initialize document builder
        initialize feature extraction
        """       
        
        self.wdict = WordDictionary(self.src)    
        self.wdict.load(dict_type)
               
        self.tdict = TriggerDictionary(self.src)
        self.tdict.load(dict_type)
        
        self.doc_builder = DocumentBuilder(self.src, self.wdict, self.tdict)         
        self.extraction = FeatureExtraction(self.src, self.wdict, self.tdict)
        
        
    def get_path(self, source, dir_name):
        """
        check whether given dir_name is exist
        raise error if it does not exist
        return full path of dir_name
        """
        path = source + self.MODEL_DIR + '/' + dir_name
        if not os.path.exists(path):
            raise ValueError(path + "exist!!, chose anoher dir_name for learning")
        
        return path
        
    def get_feature(self, step):
        """
        extract feature and return X, Y for a given step
        step are either one of these:
        'tp' => trigger-protein relation
        'tt' => trigger-trigger relation to predict regulation event with trigger argument  
        """
        if step not in ["tt","tp"]:
            raise ValueError("only support step for tt and tp")
        
        X = []
        Y = []
        info = []
        
        dt_start = dt.now()        
        
        # reset statistic of extraction
        self.extraction.reset_statistic()
                      
        # init feature
        print "now extracting", len(self.docs), "docs"
        for doc_id in self.docs.keys():             
            o_doc = self.docs[doc_id]
            if step == 'tp':
                samples = self.extraction.extract_tp(o_doc)
            elif step == 'tt':
                samples = self.extraction.extract_tt(o_doc)
            
            for sample in samples:
                X.append(sample[2])
                Y.append(sample[1])      
                info.append(sample[0])             
        
        # print statistic
        pos = self.extraction.sample_pos
        neg = self.extraction.sample_neg
        stat = (pos, neg, pos + neg)
        print stat
        print "percentege of positif data:", pos * 100.0 / (pos + neg)        
        print "time to extract feature", dt.now() - dt_start
        
        return X,Y, info
    
    def set_prediction_docs(self,docid_list_fname):
        """
        build a document to be predicted
        """
        dt_start = dt.now()      
        self.docs = {}
        # get list of file
        doc_ids = self.get_docid_list(docid_list_fname)
        
        print "now building", len(doc_ids), "docs"
        for doc_id in doc_ids:
            self.docs[doc_id] = self.doc_builder.build(doc_id)
            
        print "finish built docs in:", dt.now() - dt_start

    def update_doc_info(self, info, target, arg_name, arg_type):
        """
        update trigger and relation of document
        """
        for i in range(0,len(info)):
            doc_id = info["doc"]
            self.docs[doc_id].update(info['sen'], info['t'], self.EVENT_NAME[target], info['a'], arg_name, arg_type)

    
    def get_docid_list(self, docid_list_fname):
        """
        return list of file
        """
        if not isinstance(docid_list_fname, list):
            # get list of doc ids from file
            path = self.src + '/' + docid_list_fname + self.DOCID_SUFFIX_EXT
            if not os.path.exists(path):
                raise ValueError(path + " is not exist")
            with open(path, 'r') as f: 
                doc_ids = json.loads(f.read())
        else:
            doc_ids = docid_list_fname
        
        return doc_ids
    
    def predict_tp(self, grid_search = True):
        """
        return prediction of given docid_list
        """
        if self.docs == {}:
            raise ValueError("docs have not been created. call set_prediction_docs first!")
        # get list of file
        #doc_ids = self.get_docid_list(docid_list_fname)
        
        # get features and target
        X, Y, info = self.get_feature('tp')
        
        # init svm classifier
        svm = SVM(self.path, "trig-prot", "linear", grid_search = grid_search, class_weight = 'auto')
        svm.load()
        
        return svm.predict(X), Y, info
        
    def predict_tt(self, grid_search = True):
        """
        return prediction of given docid_list
        """
        if self.docs == {}:
            raise ValueError("docs have not been created. call set_prediction_docs first!")
        # get list of file
        #doc_ids = self.get_docid_list(docid_list_fname)
        
        # get features and target
        X, Y, info = self.get_feature('tt')
        
        # init svm classifier
        svm = SVM(self.path, "trig-trig", "linear", grid_search = grid_search, class_weight = 'auto')
        svm.load()
        
        return svm.predict(X), Y, info
        
    def predict(self, docid_list_fname):
        
        # create document object for prediction
        self.set_prediction_docs(self,docid_list_fname)
        
        # predict trigger-protein relation
        Ypred, _, info = self.predict_tp(grid_search = True)
        # update document
        update_doc_info(info, Ypred, "Theme", "P"):
        
        # predict trigger-trigger relation
        Ypred, _, info = self.predict_tp(grid_search = True)
        update_doc_info(info, Ypred, "Theme", "E"):
        
        