from PatternExtractor.PatternExtractor import PatternExtractor 
import Data.AnnotatedDataPer as dictPer
import Data.AnnotatedDataOrg as dictOrg
import Data.AnnotatedDataLoc as dictLoc

#if __name__=="__main__":
    #parser=PatternExtractor(pickleState=False)
    #parser.patternsExtractor(dictPer.data,"dataExcelPer")
    #parser.patternsExtractor(dictOrg.data,"dataExcelOrg")
    #parser.patternsExtractor(dictLoc.data,"dataExcelLoc")
    


            
parser=PatternExtractor("False")
resu=parser.matchPattern("le prénom c'est Fatiha F A T I H A")
print(resu)
