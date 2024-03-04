# IR Assignment 1
# Umair Amir
# K20-0133

import glob
import nltk
import os
import string
from nltk.stem import PorterStemmer
import re
Dictionary = {} #Create a global dictionary


def FileRead(): 
    Folder = 'Dataset'
    Pattern = '*.txt' 
    FList = glob.glob(os.path.join(Folder, Pattern)) #Finding all Files in the given Folder 
    for Path in FList: 
        with open(Path, 'r') as file: 
            FileContents = file.read() #Reading File text
            FileContents = FileContents.lower()
            File_name = Path.strip("Dataset\\.txt")
            FileContents = PunctuationRemove(FileContents)
            FileContents = FileContents.split() # Tokenizing string
            Stemmer = PorterStemmer()
            FileStem = []
            #Applying Stemming to all the tokens
            for words in list(FileContents):
                FileStem.append(Stemmer.stem(words))
            File_name = int(File_name)
            Dictionary = DictionaryBuilder(FileStem,File_name)
            Dictionary = sorted(Dictionary.items()) # Sorting the Dictionary by tokens
            Dictionary = dict(Dictionary)
            # Sorting Positional Index
            for key, value in sorted(Dictionary.items(), key=lambda item: item[0]):
                Dictionary[key] = {k: sorted(v) for k, v in sorted(value.items(), key=lambda x: x[0])}
    return Dictionary


def PunctuationRemove(File):
    File = File.replace('-', ' ') # Replacing hyphens with spaces
    File = File.translate(str.maketrans("", "", string.punctuation))
    return(File)


def DictionaryBuilder(File,File_Name):
    Stop = open(r'C:\Users\umair\Desktop\C\IR Assignment 1\Stopword-List.txt', 'r')
    StopContents = Stop.read()
    StopContents = StopContents.split()
    for i, words in enumerate(File): # Building Dictionary
        if(words not in StopContents):
            if(words not in Dictionary): # First time a word is added to Dictionary
                Dictionary[words] = {}
                Dictionary[words][File_Name] = [] #Creating Positional Index
                Dictionary[words][File_Name].append(i)
            else:
                if(File_Name not in Dictionary[words]):
                    Dictionary[words][File_Name] = []
                Dictionary[words][File_Name].append(i)
    return Dictionary   


def QueryProcessor(Query):
    Query = Query.split() #Splitting string into list with tokens
    if(len(Query) == 1): #Single word scenario with no Operators
        Query = QueryStemmer(Query)
        Query = PostingRetrieval(Query[0])
        Query = list(Query.keys())
        print('Retrieved Documents: ', Query)
        return
    else:    
        if('AND' in Query and 'OR' not in Query and 'NOT' not in Query): # Simple Scenario with single or multiple ANDs
            Query = QueryStemmer(Query)
            Result = QuerySolver(Query,1)
        elif('OR' in Query and 'NOT' not in Query and 'AND' not in Query):# Simple Scenario with single or multiple ORs
            Query = QueryStemmer(Query)
            Result = QuerySolver(Query,2)
        elif('NOT' in Query and 'OR' not in Query and 'AND' not in Query):# Simple Scenario with a NOT operator
            Query = QueryStemmer(Query)
            Result = PostingTraversalNOT(Query[0])
        elif('AND' not in Query and 'OR' not in Query and 'NOT' not in Query): # Phrase Query Scenario
            Query = QueryStemmer(Query)
            if(len(Query) == 2): # Simple Phase Query with no /k(Gap is assumed 1)
                Result = PhraseSolver(Query[0], Query[1],1) 
            else:
                for Words in Query: # Phase Query Scenario with /k
                    Match = re.match(r'/(\d+)', Words) #Checking to see if /k is there
                    if Match:
                        Gap = int(Match.group(1)) # Grabbing the k integer from /k
                        Result = PhraseSolver(Query[0], Query[1], Gap)
        else: # Complex Query Scenario
            Query = InfixToPostfix(Query) # Generating Postfix Expression 
            Result = Evaluator(Query)
    print('Retrieved Documents: ', Result)


def QueryStemmer(Query):
    StemQuery = []
    Stop = open(r'C:\Users\umair\Desktop\C\IR Assignment 1\Stopword-List.txt', 'r')
    StopContents = Stop.read()
    StopContents = StopContents.split()
    Stemmer = PorterStemmer()
    Query = [Val for Val in Query if Val != 'AND' and Val != 'OR' and Val != 'NOT' and Val not in StopContents]
    for words in Query:
        StemQuery.append(Stemmer.stem(words))
    return StemQuery  


def QuerySolver(Query,Type):
    Result = Query[0]
    #Resolving Query of two words at a time
    for i in range(len(Query) - 1):
        if(Type == 1):
            Result = PostingTraversalAND(Result, Query[i + 1]) #Receiving posting list of query of two words
        if(Type == 2):
            Result = PostingTraversalOR(Result, Query[i + 1])    
    return sorted(Result) 


def PostingRetrieval(Word):
    Posting = {}
    #Retrieving Posting List of a word in Dictionary
    if(Word in Dictionary):
        Posting = Dictionary[Word]
    return Posting


def PostingTraversalAND(Word1, Word2):
    #Checking if sent word is a posting list or a string
    if(isinstance(Word1,str) == False and isinstance(Word2,str) == True):
        Word2 = PostingRetrieval(Word2)
        Word2 = list(Word2.keys())
    elif(isinstance(Word2,str) == False and isinstance(Word1, str) == True):
        Word1 = PostingRetrieval(Word1)
        Word1 = list(Word1.keys())
    elif(isinstance(Word1, str) == True and isinstance(Word2,str) == True):
        Word1 = PostingRetrieval(Word1)
        Word2 = PostingRetrieval(Word2)
        Word1 = list(Word1.keys())
        Word2 = list(Word2.keys())
    i = 0
    j = 0
    Result = []
    #Traversing through postings of both words
    while i < len(Word1) and j < len(Word2):
        if(Word1[i] == Word2[j]):
            Result.append(Word1[i])
            i+=1
            j+=1
        #Increase index of lower valued posting
        elif(Word1[i] > Word2[j]):
            j+=1
        elif(Word1[i] < Word2[j]):
            i+=1
    return Result


def PostingTraversalOR(Word1, Word2):
    #Checking if sent word is posting list or string
    if(isinstance(Word1,str) == False and isinstance(Word2,str) == True):
        Word2 = PostingRetrieval(Word2)
        Word2 = list(Word2.keys())
    elif(isinstance(Word2,str) == False and isinstance(Word1, str) == True):
        Word1 = PostingRetrieval(Word1)
        Word1 = list(Word1.keys())
    elif(isinstance(Word1, str) == True and isinstance(Word2,str) == True):
        Word1 = PostingRetrieval(Word1)
        Word2 = PostingRetrieval(Word2)
        Word2 = list(Word2.keys())
        Word1 = list(Word1.keys())
    i = 0
    j = 0
    Result = []
    #Traversing Postings of both words
    while i < len(Word1) or j < len(Word2):
        #Adding all postings if they do not already exist in the Result
        if(i < len(Word1) and Word1[i] not in Result):
            Result.append(Word1[i])
        if(j < len(Word2) and Word2[j] not in Result):
            Result.append(Word2[j])
        i+=1
        j+=1
    return Result


def PostingTraversalNOT(Word):
    if(isinstance(Word,str) == True):
        Word = PostingRetrieval(Word)
        Word = list(Word.keys())
    Result = []
    #Adding all postings to result that do not exist in posting list of word
    for i in range(1,31):
        if(i not in Word):
            Result.append(i)
    return Result


def InfixToPostfix(Query):
    Operators = ['AND', 'OR', 'NOT', '(']  # collection of Operators
    Priority = {'AND':3, 'OR':2, 'NOT':1, '(':0} # dictionary having priorities of Operators
    Stack = [] # initialization of empty stack
    Output = []
    for Words in Query:
        #Operands are appended to output
        if(Words not in Operators and Words != ')'):
            Output.append(Words)
        elif(Words == '('):
            Stack.append(Words)
        elif(Words == ')'):
            while(Stack[-1] != '('):
                Output.append(Stack.pop())
            Stack.pop()
        #When Operators are detected
        else:
            while Stack and Stack[-1] != '(' and Priority[Words] <= Priority.get(Stack[-1], -1):
                Output.append(Stack.pop())
            Stack.append(Words)
    #Empty stack when we reach the end of the Query 
    while Stack:
        Output.append(Stack.pop())
    return ' '.join(Output)


def Evaluator(Query):
    Operators = ['AND', 'OR', 'NOT'] #Boolean operators
    Stack = []
    StemQuery = []
    #Steps for Stemming
    Stop = open(r'C:\Users\umair\Desktop\C\IR Assignment 1\Stopword-List.txt', 'r')
    StopContents = Stop.read()
    StopContents = StopContents.split()
    Query = Query.split()
    Stemmer = PorterStemmer()
    Query = [Val for Val in Query if Val not in StopContents]
    for Words in Query:
        if(Words not in Operators):
            StemQuery.append(Stemmer.stem(Words))
        else:
            StemQuery.append(Words)
    Query = StemQuery
    #Evaluating the Postfix Expression
    for Words in Query:
        #Operands get appended to stack
        if(Words not in Operators):
            Stack.append(Words)
        #2 Operands are popped when AND or OR operand is detected
        elif(Words == 'AND'):
            Word1 = Stack.pop()
            Word2 = Stack.pop()
            Temp = PostingTraversalAND(Word1, Word2)
            Stack.append(Temp) #Posting List of answer is pushed to stack
        elif(Words == 'OR'):
            Word1 = Stack.pop()
            Word2 = Stack.pop()
            Temp = PostingTraversalOR(Word1, Word2)
            Stack.append(Temp) #Posting List of answer is pushed to stack
        #1 Operand is popped when NOT operand is detected
        elif(Words == 'NOT'):
            Word1 = Stack.pop()
            Temp = PostingTraversalNOT(Word1)
            Stack.append(Temp)
    return(sorted(Stack[0])) #Stack has only one element which is the posting list for the Query
        


def PhraseSolver(Word1, Word2, Gap):
    #Finding Posting lists of words
    Word1 = PostingRetrieval(Word1)
    Word2 = PostingRetrieval(Word2)
    Word1List = list(Word1.keys())
    Word2List = list(Word2.keys())
    i = 0
    j = 0
    k = 0
    l = 0
    Result = []
    #Traversing the postings of both words
    while i < len(Word1List) and j < len(Word2List):
        k = 0
        l = 0
        if(Word1List[i] == Word2List[j]):
            #Traversing Positional Index of equated Posting of both words
            while k < len(Word1[Word1List[i]]) and l < len(Word2[Word2List[j]]):
                Temp = Word2[Word2List[j]][l] - Word1[Word1List[i]][k] #Calculating Gap between words
                if(Temp <= Gap and Temp > -1):
                    if(Word1List[i] not in Result): #Avoiding multiple entries of one Posting
                        Result.append(Word1List[i])
                    k+=1
                    l+=1
                #Lesser Valued Position has index increased
                elif(Word1[Word1List[i]][k] < Word2[Word2List[j]][l]):
                    k+=1
                else:
                    l+=1
            i+=1
            j+=1
        #Lesser Valued Posting has index increased     
        elif(Word1List[i] < Word2List[j]):
            i+=1
        else:
            j+=1
    return Result         
    


Dictionary = FileRead()
Query = ''
while(1):
    Query = input("Enter Query(Type -1 to exit): ")
    if(Query == '-1'):
        break
    QueryProcessor(str(Query))

#      cricket AND captain
#      goOd AND ChasE
#      pCb OR Psl
#      ground and statement and board
#      not ImPossiBle
#      international cricket /1
#      replacement players /9