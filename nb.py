# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 14:56:23 2011

@author: juherask
"""

import operator

def product(number_list):
    return reduce(operator.mul, number_list, 1)
    
def factorial(i):
    p = 1
    while i>0:
        p*=i
        i-=1
    return p
    
def combinations(n, k):
    return factorial(n) / (factorial(k)*factorial(n-k))
        

class NaiveBayes:
    def __init__(self):
        self._countsTotal=0
        self._countsPerLabel=dict()
        self._countsPerTokenAndLabel=dict()
        self._countsPerToken=dict()
        
    def AddTokens(self,label, tokens):
        self._countsTotal+=len(tokens)
        if not label in self._countsPerLabel:
            self._countsPerLabel[label]=0
        self._countsPerLabel[label]+=len(tokens)
            
        for token in tokens:
            if token in self._countsPerTokenAndLabel:
                self._countsPerToken[token]+=1
                if label in self._countsPerTokenAndLabel[token]:
                    self._countsPerTokenAndLabel[token][label]+=1
                else:
                    self._countsPerTokenAndLabel[token][label]=1                    
            else:
                self._countsPerTokenAndLabel[token]=dict()
                self._countsPerTokenAndLabel[token][label]=1
                self._countsPerToken[token]=1
                
    def Labels(self):
        return self._countsPerLabel
    
    def GetProbabilites(self, withTokens):
        probs = dict()
        normsum = 0  
        for label in self.Labels():
            
            # Find the label probability
            labelProb = float(self._countsPerLabel[label])/self._countsTotal
            
            # Find the probabilities of individual tokens with this label
            labelProbabilities = []
            activeTokens = []
            for token in withTokens:                
                if token in self._countsPerTokenAndLabel:
                    # Laplacian normalization
                    lprob = 1.0/(self._countsPerToken[token]**2)
                    if label in self._countsPerTokenAndLabel[token]:
                        matches = self._countsPerTokenAndLabel[token][label]
                        lprob = float(matches)/self._countsPerToken[token]                
                    labelProbabilities.append(lprob)
                    activeTokens.append(token)
                else:
                    continue
            
            print label
            print str(zip(activeTokens,labelProbabilities))
               
                
            
            probs[label]=labelProb*product(labelProbabilities)
            normsum+=probs[label]
            

        for label in self.Labels():
            probs[label] = probs[label]/normsum
        
        return probs
        
            
        
""" Code that test the basic operation of the RandomTuner """    
def main():
    def tokenize(s):
        for word in s.split():
            if word not in ["has", "a", "and", "an", "is", "the", "have"]:
                yield word
    
    # Build
    nbc = NaiveBayes()
    for i in range(1):
        nbc.AddTokens("Cat", list(tokenize("has four legs")))
        nbc.AddTokens("Cat", list(tokenize("has pointy ears")))
        nbc.AddTokens("Cat", list(tokenize("has fur and long tail")))
        nbc.AddTokens("Cat", list(tokenize("is domesticated")))
        nbc.AddTokens("Cat", list(tokenize("says meow.")))
          
        nbc.AddTokens("Pig", list(tokenize("has four legs")))
        nbc.AddTokens("Pig", list(tokenize("has floppy ears")))
        nbc.AddTokens("Pig", list(tokenize("is domesticated")))
        nbc.AddTokens("Pig", list(tokenize("has squiggly tail")))
        
        nbc.AddTokens("Mouse", list(tokenize("has four legs")))
        nbc.AddTokens("Mouse", list(tokenize("has round ears")))
        nbc.AddTokens("Mouse", list(tokenize("is small")))
        nbc.AddTokens("Mouse", list(tokenize("has fur")))
        nbc.AddTokens("Mouse", list(tokenize("has long tail")))
        
        nbc.AddTokens("Dog", list(tokenize("has four legs")))
        nbc.AddTokens("Dog", list(tokenize("has fur")))
        nbc.AddTokens("Dog", list(tokenize("is domesticated")))
        nbc.AddTokens("Dog", list(tokenize("barks")))
        
        nbc.AddTokens("Monkey", list(tokenize("has two legs")))
        nbc.AddTokens("Monkey", list(tokenize("has fur")))
        nbc.AddTokens("Monkey", list(tokenize("is intelligent")))
        nbc.AddTokens("Monkey", list(tokenize( "lives in trees")))
        
        nbc.AddTokens("Human", list(tokenize("has two legs")))
        nbc.AddTokens("Human", list(tokenize("speaks")))
        nbc.AddTokens("Human", list(tokenize("is intelligent")))
        nbc.AddTokens("Human", list(tokenize("does not have tail")))
        nbc.AddTokens("Human", list(tokenize("does not have fur")))
    
    # Test
    import re
    s = "What is an creature that lives in trees and has fur?"
    t = list(tokenize((re.sub(r'\W+', ' ', s))))
    print(s)
    probs = nbc.GetProbabilites(t)
    for creature in probs:
        print "%s with probability of %i %%" % \
        (creature, int(probs[creature]*100))
    print
    
    s = "What is an creature that has fur, barks loud and has four legs?"
    t = (re.sub(r'\W+', ' ', s)).split()
    print s
    probs = nbc.GetProbabilites(t)
    for creature in probs:
        print "%s with probability of %i %%" % \
        (creature, int(probs[creature]*100))
    print

    
if __name__ == '__main__':
    main()    
    
                
        