"""
Created on Sep 5, 2013

@author: Andresta
"""

from features.Feature import Feature


class ChunkFeature(Feature):
    """
    classdocs
    """


    def __init__(self, prefix):
        """
        Constructor
        """
        self.prefix = prefix
        
           
    def get_prep_word(self, o_sen, trig_wn, arg_wn):
        """
        return string of prepositions and number of preposition between trig_wn and arg_wn
                
        """
        o_chunk = o_sen.chunk
        preps_word = ''
        n_prep = 0
        trig_chk_num = o_chunk.chunk_map[trig_wn]
        arg_chk_num = o_chunk.chunk_map[arg_wn]
        for chk_num in range(trig_chk_num+1, arg_chk_num):
            prep = o_chunk.prep_chunk.get(chk_num,'')
            if prep != '':
                preps_word += prep + '-'
                n_prep += 1
        
        return preps_word.rstrip('-'), n_prep
        
    
    def _extract_common_feature(self, o_sen, trig_wn, arg_wn, prefix = ''):
        """
        extract common chunk feature between trig_wn and arg_wn in o_sen
        """
        o_chunk = o_sen.chunk
        
                
        """ capture feature of events expressed in a chunk layer """
        # is in the same chunk
        if o_chunk.same_chunk(trig_wn, arg_wn):            
            self.add(prefix + '1chk',True)
            self.add(prefix + o_chunk.get_type(trig_wn), True)
                                            
        
        """ capture feature of events expressed in a phrase layer """
        # check any preposition chunk in between trigger and argument        
        if trig_wn < arg_wn:            
            prep_str, n_prep = self.get_prep_word(o_sen, trig_wn, arg_wn)
            if n_prep == 1:
                self.add(prefix+'has_prep', True)
                self.add(prefix+prep_str, True)
         
        """ capture feature of events expressed in a clause layer """
        # distance between chunk
        self.add(prefix + 'dist', o_chunk.distance(trig_wn, arg_wn))
               
        
    def extract_feature_tp(self, o_sen, trig_wn, arg_wn):
        """
        extract chunk feature between trig_wn and arg_wn in o_sen
        """       
        # reset feature
        self.feature = {}
        
        self._extract_common_feature(o_sen, trig_wn, arg_wn)
        
        
    def extract_feature_tt(self, o_sen, trig_wn, arg_wn):
        """
        extract chunk feature between trig_wn and arg_wn in o_sen
        """       
        # reset feature
        self.feature = {}
        
        self._extract_common_feature(o_sen, trig_wn, arg_wn)
        
        
    def extract_feature_tac(self, o_sen, trig_wn, theme_wn, cause_wn):
        """
        extract chunk feature for trigger-theme-cause relation
        """
        # reset feature
        self.feature = {}
        
        # extract common feature
        self._extract_common_feature(o_sen, trig_wn, theme_wn, prefix='a_')
        self._extract_common_feature(o_sen, trig_wn, cause_wn, prefix='c_')
        self._extract_common_feature(o_sen, theme_wn, cause_wn, prefix='ac')
        
        
    def extract_feature_t2(self, o_sen, trig_wn, theme1_wn, theme2_wn):
        """
        extract chunk feature for trigger-theme1-theme2 relation
        """
        # reset feature
        self.feature = {}
                        
        # extract common feature
        self._extract_common_feature(o_sen, trig_wn, theme1_wn, prefix='t1_')
        self._extract_common_feature(o_sen, trig_wn, theme2_wn, prefix='t2_')
        self._extract_common_feature(o_sen, theme1_wn, theme2_wn, prefix='t12_')
        
        
        
        