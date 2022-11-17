from transformers import AutoTokenizer, AutoModelForTokenClassification, AutoModelForSequenceClassification
from transformers import pipeline
import pickle
import logging
import torch
from PatternExtractor.CudaDetect import detect_cuda_device_number

"""Docstring  
Usage: This file helps to load the part of speech models
The models can be either dowloaded immediately from Huggingface or 
loaded from the pretrained models file. 

"""
__authors__=("LNIT INTERN 2022-2023","LNIT")
__contact__=("LNIT")
__copyright__="MIT"
__data__="11/10/2022"
__version__="V0"


class Models:
    
    def __init__(self) -> None:
        self.device_number = detect_cuda_device_number()

        # todo  change logging system
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        handler.addFilter(logging.Filter('lnittransformer'))
        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
            datefmt='%m/%d/%Y %H:%M:%S',
            level=logging.INFO,
            handlers=[handler]
        )
        #send the model to cuda if GPU is available else leave model to cpu
        self._device = torch.device(
            "cuda" if torch.cuda.is_available()
            else "cpu"
        )
    
   
    def send2cuda(self,model):
        if self._device == 'cuda':
            model.to(self._device)
        self.logger.info("Using model: %s", self._device)
        return model
    
    def pickle_it(self, obj, file_name):
        #save the model
        with open(f'{"./Models/"+file_name}.pickle', 'wb') as f:
            pickle.dump(obj, f)

    def unpickle_it(self, file_name):
        #load the model
        with open(f'{"./Models/"+file_name}.pickle', 'rb') as f:
            return pickle.load(f)

    def load_trained_models(self, pickle=False):
     
        #Part of speech Tagging
        tokenizer_pos = AutoTokenizer.from_pretrained("gilf/french-postag-model")
        model_pos = AutoModelForTokenClassification.from_pretrained("gilf/french-postag-model")
        self.ner_pos = pipeline('ner', model=model_pos, tokenizer=tokenizer_pos, aggregation_strategy="simple",device=self.device_number)

        if pickle:
            self.pickle_models()
        
        return  self.ner_pos 
    
    def pickle_models(self):
        self.pickle_it(self.ner_pos, "pos_tagger_fast")


    def load_pickled_models(self):
        tagger = self.unpickle_it("pos_tagger_fast")
        tagger=self.send2cuda(tagger)
        return  tagger
    
 