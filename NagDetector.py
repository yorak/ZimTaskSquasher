# -*- coding: utf-8 -*-

from ast import literal_eval
from collections import defaultdict
from NaiveBayes import NaiveBayes, tokenize_en

def test_if_should_nag(nagssifiers, requiredTags, onActivity, requireAll):
    tokens = list(tokenize_en(onActivity))
    isSuspicious = False
    doingTheTask = False
    for tag in requiredTags:
        utag = tag.upper()      
        prob = nagssifiers[utag].get_probability(utag, tokens)
        print utag, prob              
        if prob>=0.5:
            # Probably doing a task with this tag
            doingTheTask = True
        else:
             isSuspicious = True
    
    isSuspicious = isSuspicious and requireAll
    return True if not doingTheTask or isSuspicious else False
    
def teach_classifiers(fromfile):        
    nag_teach_file = open(fromfile, 'r')
        
    # Collect teach data 
    teach_data = defaultdict(list)
    for line in nag_teach_file.readlines():
        # Tab delimeted list with format:
        #  <timestamp> <tokenizable string> <list of tags (labels)>
        parts = line.strip().split('\t')
        tags = literal_eval(parts[1])
        tokens = list(tokenize_en(parts[2]))
        if len(tags)==0:
            teach_data[""]+=tokens
        for tag in tags:
            teach_data[tag]+=tokens
    nag_teach_file.close()
    
    # Teach new set of classifiers
    nagssifiers = defaultdict(NaiveBayes)
    for tag,tokens in teach_data.items():
        # Shorthand for "not tagged work"
        if tag=="":
            continue
        
        # Positive samples
        nagssifiers[tag].teach_tokens(tag, tokens)
        
        #TODO: Try out negative samples training with 
        # self.nagssifiers[""].teach_tokens("", teach_data[""])
        #  how does it affect the accuracy?

        # Negative samples            
        for ntag,ntokens in teach_data.items():
            if tag==ntag:
                continue
            nagssifiers[tag].teach_tokens("", ntokens)
    return nagssifiers
    
    
def verify_classifiers(nagssifiers, fromfile, verbose=0):    
    nag_teach_file = open(fromfile, 'r')
    slack_tag = r"""BREAK"""
    
    correct_per_tag = defaultdict(int)
    incorrect_per_tag = defaultdict(int)
    
    for line in nag_teach_file.readlines():
        parts = line.split('\t')
        tags = literal_eval(parts[1])
        tokens = list(tokenize_en(parts[2]))

        if len(tags)==0:
            # binary classificaiton result.
            prob = 1.0
            for tag in nagssifiers:
                prob *= nagssifiers[tag].get_probability("", tokens)
                
            if prob>=0.5:
                correct_per_tag[""]+=1
            else:
                incorrect_per_tag[""]+=1
            if verbose>1:
                 print("p(C|X)=%f, for C=%s and X=%s" % (prob, slack_tag, tokens))
        
        for tag in tags:
            # binary classificaiton result.
            prob = nagssifiers[tag].get_probability(tag, tokens)
            if prob>=0.5:
                correct_per_tag[tag]+=1
            else:
                incorrect_per_tag[tag]+=1
            if verbose>1:
                 print("p(C|X)=%f, for C=%s and X=%s" % (prob, tag, tokens))
    
    for tag in correct_per_tag.keys():            
        right = correct_per_tag[tag]
        wrong = incorrect_per_tag[tag]
        tot = right+wrong
        
        if verbose>0:
            if tag=="":
                tag = slack_tag
                
            print("%s: %d %% right, %d wrong" %
                (tag, right*100/tot, wrong*100/tot) )
    if verbose==0:
        print("They _do_ classify, up the verbiosity for more info.")
        