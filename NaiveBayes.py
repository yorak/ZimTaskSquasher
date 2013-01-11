# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 14:56:23 2011

@author: juherask
"""

import re
from operator import mul
from collections import defaultdict

## Just few helper functions ##

class NaiveBayes:
    def __init__(self, prior_per_teach=True):
        """ Create new Naive Bayes Classifier.
        if prior_per_teach==True,
         only the teach method *calls* are considered to label prior
        if prior_per_teach==False,
         the tokens are considered to label prior       
        """
        self._prior_per_teach = prior_per_teach
        
        self._teachTotal=0
        self._teachesPerLabel=defaultdict(int)
        
        self._countsTotal=0
        self._countsPerLabel=defaultdict(int)
        self._countsPerTokenAndLabel=defaultdict(lambda : defaultdict(int))
        self._countsPerToken=defaultdict(int)
        
    def teach_tokens(self, label, tokens):
        """ Teach the Naive Bayes Classifier that the label (aka.  class) 
         appears together with given tokens (aka. features, inputs).
         
         Your teaching should follow the distribution of instances. That is
          if 'label1' is present 1/3 of the time in real data, then 1/3 of the
          teaching should be done on it. This is to get the prior probability
          for the labels right.
          
         The tokens on the other hand should be a good reprsentative sample
          of the true distribution. All the tokens are independent, that is
          calling (if prior_per_teach=False)
          
             nb.teach_tokens("c1", ["a","b","c","d"]) 
             vs.
             nb.teach_tokens("c1", ["a","b"]) 
             nb.teach_tokens("c1", ["c","d"]) 
             
          produce equal classifier.
          
        """
        # For label probability
        self._teachTotal+=1
        self._teachesPerLabel[label]+=1
        
        # For label probability
        self._countsTotal+=len(tokens)
        self._countsPerLabel[label]+=len(tokens)
        
        # For token in label probability
        for token in tokens:
            self._countsPerToken[token]+=1
            self._countsPerTokenAndLabel[token][label]+=1
                
    def get_labels(self):
        """ Get the list of labels (classes) of this Naive Bayes Classifier.
        """
        return self._countsPerLabel
        
    def get_probability(self, forLabel, withTokens):
        """ Returns the Naive Bayesian probablilty
        for a specific label.
        
        See get_probabilites() for more details.
        """

        results = self.get_probabilites(withTokens)
        for prob, label in results:
            if label==forLabel:
                return prob
    
    def get_probabilites(self, withTokens):
        """ Returns the Naive Bayesian probablilty
        for each label stating the possibility that tokens 
        appear for that label.
        Returned as list of pairs [ (float(probability1), str(label1))...]
        
        p(C|X) = p(C) p(X|C) / p(X), where
        P(C) is the prior probability of any input to belong to a class with 
         any input, and p(X|C) is the likelyhood of the input X given class C.
        
        if assumed p(X_1)=p(X_2) forall X_i, we can simplify to 
        q(C|X) = p(C) p(X|C), which can be compared
        
        """
        probs = []
        normsum = 0  
        for label in self.get_labels():
            
            # Find the label probability, that is p(C)
            if self._prior_per_teach:
                labelProb = float(self._teachesPerLabel[label])/self._teachTotal
            else:
                labelProb = float(self._countsPerLabel[label])/self._countsTotal
            
            # Find the likelyhood of tokens for this label that is p(x_i|C)
            labelProbabilities = []
            activeTokens = []
            for token in withTokens:                
                if token in self._countsPerTokenAndLabel:
                    # Laplacian normalization
                    lprob = 1.0/(len(self._countsPerLabel))
                    #print "laplacian", token, label, lprob
                    if label in self._countsPerTokenAndLabel[token]:
                        matches = self._countsPerTokenAndLabel[token][label]
                        lprob = float(matches)/self._countsPerToken[token]                
                        #print "calcd", token, label, lprob
                    labelProbabilities.append(lprob)
                    activeTokens.append(token)
               
            # reduce(mul,lst,1.0) does a product over independet assumption
            #  for p(x_i|C) to get p(X|C)
            labelprob = labelProb*reduce(mul, labelProbabilities, 1.0)
            probs.append( (labelprob , label) )
            normsum+=labelprob
        
        # Sort and normalize
        probs.sort(reverse=True)
        nprobs = []
        for prob,label in probs:
            nprobs.append( (prob/normsum, label) )
        return nprobs
        

def tokenize_en(s):
    """Simple english word tokenizer
    """
    previous = None
    for word in (re.sub(r'\W+', ' ', s.lower())).split():
        # Skip word if preceeded by not
        word = word.rstrip('s')                
        if word not in ["has", "a", "and", "an", "is", "in", "the", "have"]:
            if previous == "not" and previous == "no":
                yield ' '.join(previous,word)
            else:
                yield word
            previous = word         
        

def test():
    """ Code that test the basic operation of the NaiveBayes classifier
    """

    # Teach
    nbc = NaiveBayes()
    for i in range(1):
        nbc.teach_tokens("A cat", list(tokenize_en("has four legs")))
        nbc.teach_tokens("A cat", list(tokenize_en("has pointy ears")))
        nbc.teach_tokens("A cat", list(tokenize_en("has fur and long tail")))
        nbc.teach_tokens("A cat", list(tokenize_en("is domesticated")))
        nbc.teach_tokens("A cat", list(tokenize_en("says meow.")))
          
        nbc.teach_tokens("A pig", list(tokenize_en("has four legs")))
        nbc.teach_tokens("A pig", list(tokenize_en("has floppy ears")))
        nbc.teach_tokens("A pig", list(tokenize_en("is domesticated")))
        nbc.teach_tokens("A pig", list(tokenize_en("has squiggly tail")))
        
        nbc.teach_tokens("A mouse", list(tokenize_en("has four legs")))
        nbc.teach_tokens("A mouse", list(tokenize_en("has round ears")))
        nbc.teach_tokens("A mouse", list(tokenize_en("is small")))
        nbc.teach_tokens("A mouse", list(tokenize_en("has fur and a long tail")))
        
        nbc.teach_tokens("A dog", list(tokenize_en("has four legs")))
        nbc.teach_tokens("A dog", list(tokenize_en("has fur")))
        nbc.teach_tokens("A dog", list(tokenize_en("is domesticated")))
        nbc.teach_tokens("A dog", list(tokenize_en("barks")))
        
        nbc.teach_tokens("A monkey", list(tokenize_en("has two legs")))
        nbc.teach_tokens("A monkey", list(tokenize_en("has fur")))
        nbc.teach_tokens("A monkey", list(tokenize_en("is intelligent")))
        nbc.teach_tokens("A monkey", list(tokenize_en( "lives in trees")))
        
        nbc.teach_tokens("A human", list(tokenize_en("speaks")))
        nbc.teach_tokens("A human", list(tokenize_en("is intelligent")))
        nbc.teach_tokens("A human", list(tokenize_en("walks on two feet")))
        nbc.teach_tokens("A human", list(tokenize_en("does not have tail")))
        nbc.teach_tokens("A human", list(tokenize_en("does not have fur")))
    
    # Test
    
    q_et_a = [
        ("What is an creature that lives in trees and has fur?", "A monkey"),
        ("What has fur, sometimes barks, and has four legs?", "A dog"),
        ("I speak, I walk, I wear clothing. What am I?", "A human"),
    ]
    
    for q, a in q_et_a:
            
        t = list(tokenize_en(q))
        print(q)
        probs = nbc.get_probabilites(t)

        assert(probs[0][1] == a)
        
        for prob, creature in probs:
            print "%s with probability of %i %%" % \
            (creature, int(prob*100))
        print
    
    
if __name__ == '__main__':
    test()    