from typing import List
from configparser import ConfigParser
import pandas as pd 
import re
import os 



from PatternExtractor.Models import Models

config=ConfigParser()
config.read(f"""{os.path.join(os.path.dirname(__file__),"..","Config","config.ini")}""")

class PatternExtractor():
    
    def __init__(self, pickleState :  bool) -> None:
        models=Models()
        self.tagger=models.load_trained_models(pickle=pickleState)
    
    def patternExtractor(self, P : str):
        """_summary_

        Args:
            [P (_type_=str): _description_= text in string format
            eg: <PER> Nicolas </PER> is a student]
        """
        
        "We want to delete all the tags inside the text P to be able to use the POS template properly"
        parserTagsRe=re.compile("<PER>|</PER>|<LOC>|</LOC>|<MISC>|</MISC>|<ORG>|</ORG>")
        P1=parserTagsRe.sub("",P)
    
        "POS entyties extraction"
        entitiesPos=self.tagger(P1)

        "get list of words"
        parserWordsRe=re.compile(r"\w+|\W+") 
        words=parserWordsRe.findall(P)

        "Replace all words per their POS category"
        for index_i,item_i in enumerate(words):
            for  item_j in entitiesPos:
                if item_i==item_j['word']:
                    words[index_i]=item_j['entity_group'] + ' '

        "delete all punctuations within pattern"         
        words=[''.join(letter for letter in word if letter not in """!#$%&()"*+,-.:;=?@[\]^_`{|}~""") for word in words]
        patternWithPunctuation="".join(words)
        
        "Delete all punctuations"
        pattern=re.sub(r">",'> ',patternWithPunctuation)
        parserCommaRe=re.compile("j'|c'|m'|l'|n'|t'|s'|d'|z'|q'")
        pattern=parserCommaRe.sub("CLS ",pattern)
        parserVerbRe=re.compile("'ai|'est|'es")
        pattern=parserVerbRe.sub("V ",pattern)

        formulatedPattern=""    
        for item in entitiesPos: 
            formulatedPattern=formulatedPattern + item['entity_group'] + " "
        formulatedPattern=formulatedPattern[:-1] 
        return pattern,formulatedPattern

    def patternExtractorShiftReduce (self, P : str):

        pattern,formulatedPattern = self.patternExtractor(P)
       
        #Shift-reduce operation (we will reduce the number of entities a bit by replacing the entity by the most generalized entity 
        # eg: Nom = NC/NPP and Adj= ADJ/ADJWH
        chunkGVRe=re.compile(" V VPP | V VIMP | V VPP | V VPR | VINF | V VS | V | VPP | VINF | VPP | VPR | VS|VINF ")
        pattern=chunkGVRe.sub(" GV ", pattern)
        formulatedPattern=chunkGVRe.sub(" GV ", formulatedPattern)

        chunkGNRe=re.compile(" NPP NPP| NP CC NPP| NPP NPP NPP| NPP NPP NPP NPP| NPP| NPP NPP NPP NPP NPP| NPP NPP|NPP | NPP ")
        pattern=chunkGNRe.sub(" GN ", pattern)
        formulatedPattern=chunkGVRe.sub(" GN ", formulatedPattern)

        return pattern,formulatedPattern
    
    
    def patternsExtractor(self, listP : List[str], fileName : str):
        """_summary_
        Args:
            listP (List[str]): list of sentences
        """
        
        libraryOutput={"Sentences":[],"Patterns":[],"formulatedPatterns":[]}
        
        for item in listP:
            pattern,formulatedPattern = self.patternExtractorShiftReduce(item)
            libraryOutput["Sentences"].append(item)
            libraryOutput["Patterns"].append(pattern)
            libraryOutput["formulatedPatterns"].append(formulatedPattern)
            
        Data=pd.DataFrame(libraryOutput)
        
        
        return Data.to_excel (r"{}/{}.xlsx".format(os.path.join(os.path.dirname(__file__),"..","ExcelFiles"),fileName), index = False, header=True)

    def lastMatchBelong2EndBoundary(self,entitySentence : List[str], startCompt : int ):

        if len(entitySentence[startCompt+1:])==0:
            return []

        elif entitySentence[startCompt] == "CLS":
            allMatchPossible = [item for item in entitySentence[startCompt+1 : ] if item in config.get("CLS","end")]
            return allMatchPossible[-1]

        elif entitySentence[startCompt]=="DET":
            allMatchPossible = [item for item in entitySentence[startCompt+1 : ] if item in config.get("DET","end")]
            return allMatchPossible[-1]

        elif entitySentence[startCompt]=="DETWH":
            allMatchPossible = [item for item in entitySentence[startCompt+1 : ] if item in config.get("DETWH","end")]
            return allMatchPossible[-1]
        
        elif entitySentence[startCompt]=="P":
            allMatchPossible = [item for item in entitySentence[startCompt+1 : ] if item in config.get("P","end")]
            return allMatchPossible[-1]

        elif entitySentence[startCompt]=="VIMP":
            allMatchPossible = [item for item in entitySentence[startCompt+1 : ] if item in config.get("VIMP","end")]
            return allMatchPossible[-1]

        elif entitySentence[startCompt]=="NC":
            allMatchPossible = [item for item in entitySentence[startCompt+1 : ] if item in config.get("NC","end")]
            return allMatchPossible[-1]

        elif entitySentence[startCompt]=="ADV":
            allMatchPossible = [item for item in entitySentence[startCompt+1 : ] if item in config.get("ADV","end")]
            return allMatchPossible[-1]

        elif entitySentence[startCompt]=="PRO":
            allMatchPossible = [item for item in entitySentence[startCompt+1 : ] if item in config.get("PRO","end")]
            return allMatchPossible[-1]

        elif entitySentence[startCompt]=="V":
            allMatchPossible = [item for item in entitySentence[startCompt+1 : ] if item in config.get("V","end")]
            return allMatchPossible[-1]
       
       


    def matchPattern(self, P : str):
        try:
            #Pattern extraction 
            pattern,formulatedPattern = self.patternExtractor(P)
            entitySentence=formulatedPattern.split(" ")
            startCompt=[]
            endCompt=[]
            #Match pattern
            for index,item in enumerate(entitySentence):
                if item in config.get("boundary","begining"):
                    startCompt.append(index)
                    compt=0
                    if len(self.lastMatchBelong2EndBoundary(entitySentence, startCompt[compt]))==0:
                        return []
                    else:
                        endCompt.append(entitySentence.index(self.lastMatchBelong2EndBoundary(entitySentence, startCompt[compt])))
                        compt=compt+1  
                else:
                    pass

            return [entitySentence[i:j+1] for i,j in zip(startCompt,endCompt)]
        except TypeError:
            return []
        

                    

        
        
        
        
        
        
        
        
    
    