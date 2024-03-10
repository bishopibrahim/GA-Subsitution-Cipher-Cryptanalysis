#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 19:06:30 2024

@author: bishopibrahim
"""

#math is imported for the logarithm function, random is imported for use by the genetic algorihtm, and io is imported for file handling purposes.
import math
import random
import io

class Organism():
    alphabet = "abcdefghijklmnopqrstuvwxyz" #Alphabet can be changed if necessary to accommodate other languages.
    
    def __init__(self, ciphertextPath="", ciphertext="", cipherGuess="", plaintextGuess="", 
                 listOfStandardDistributions = [], listOfNgramSizes = [2, 3, 4], ngramFitnessWeights = [0.5, 0.3, 0.2]):
        self.ciphertextPath = ciphertextPath #String representing the filepath of the ciphertext.
        self.ciphertext = ciphertext #String representing the ciphertext.
        self.cipherGuess = cipherGuess #String representing the cipher alphabet.
        self.plaintextGuess = plaintextGuess
        self.fitness = 0
        self.listOfStandardDistributions = listOfStandardDistributions
        self.listOfNgramSizes = listOfNgramSizes
        self.ngramFitnessWeights = ngramFitnessWeights
    
    def initiateCiphertext(self):
        ciphertextFile = open(self.ciphertextPath, "r")
        self.ciphertext = ""
        for line in ciphertextFile.readlines():
            newLine = ""
            for letter in line:
                if letter.lower() in self.alphabet:
                    newLine += letter.lower()
            self.ciphertext += newLine
            self.ciphertext += "\n"
    
    def findNgrams(self, text):
        listOfMaps = []
        for n in self.listOfNgramSizes:
            listOfMaps.append(genNgrams(text, n))
        return listOfMaps
    
    def imageCiphertext(self): #Updates decryption guess with current key
        image = ""
        cipherMap = {}
        for i in range(0, 26):
            cipherMap[self.cipherGuess[i]] = self.alphabet[i]
        for letter in self.ciphertext:
            if letter in self.alphabet:
                image += cipherMap[letter]
            elif letter not in self.alphabet:
                image += letter
        self.plaintextGuess = image
    
    def randomMutate(self, n=1):
        for i in range(0, n):
            a = random.randint(0, 25)
            b = random.randint(0, 25)
            letterList = list(self.cipherGuess)  
            letterList[a], letterList[b] = letterList[b], letterList[a] 
            newGuess = "".join(letterList)  
            self.cipherGuess = newGuess

    def evaluateLogarithmicFitness(self, listOfStandardDistributions):
        listOfFitnessesByNgram = []
        for i in range(0, len(listOfStandardDistributions)):
            ngramFitness = 0
            ngramList = listNgrams(self.plaintextGuess, self.listOfNgramSizes[i])
            for ngram in ngramList:
                if ngram in listOfStandardDistributions[i]:
                    ngramFitness += math.log2(listOfStandardDistributions[i][ngram])
            listOfFitnessesByNgram.append(ngramFitness)
            
        totalFitness = 0
        for i in range(0, len(listOfFitnessesByNgram)):
            weightedNgramFitness = listOfFitnessesByNgram[i] * self.ngramFitnessWeights[i]
            totalFitness += weightedNgramFitness

        self.fitness = totalFitness
            
    def randomizeGuess(self):
        guess = ""
        alphabetList = [x for x in "abcdefghijklmnopqrstuvwxyz"]
        for letter in "abcdefghijklmnopqrstuvwxyz":
            choice = random.choice(alphabetList)
            alphabetList.remove(choice)
            guess += choice
            
        self.cipherGuess = guess
    
    def copy(self):
        copy = Organism()
        copy.ciphertextPath = self.ciphertextPath
        copy.ciphertext = self.ciphertext
        copy.cipherGuess = self.cipherGuess
        copy.plaintextGuess = self.plaintextGuess
        copy.fitness = self.fitness
        copy.listOfStandardDistributions = self.listOfStandardDistributions
        copy.listOfNgramSizes = self.listOfNgramSizes
        copy.ngramFitnessWeights = self.ngramFitnessWeights
        return copy
     
        
class Environment():
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    
    def __init__(self, ciphertext = "", ciphertextPath = "", sampletextPath = "", sampletext = "", generations = 200, population = 30, populationList = []):
        self.sampletextPath = sampletextPath
        self.sampletext = sampletext
        self.generations = generations
        self.population = population
        self.ciphertextPath = ciphertextPath
        self.samplePath = ""
        self.sampleText = ""
        self.ciphertext = ciphertext
        self.populationList = populationList
        self.listOfNgramSizes = [2, 3, 4]
        self.standardDists = []
        
    def setCiphertextFromFile(self):
        ciphertextFile = open(self.ciphertextPath)
        stringText = ""
        for line in ciphertextFile.readlines():
            for char in line:
                if char.lower() in self.alphabet:
                    stringText += char.lower()
        self.ciphertext = stringText
        
    def setSampleFromFile(self):
        sampletextFile = open(self.samplePath)
        stringText = ""
        for line in sampletextFile.readlines():
            for char in line:
                if char.lower() in self.alphabet:
                    stringText += char.lower()
        self.sampleText = stringText
    
    def initiateStandardDists(self, text):
        distList = []
        if type(text) == type(""):
            for n in self.listOfNgramSizes:
                newNgramList = genNgrams(text, n)
                distList.append(newNgramList)
        
        elif isinstance(text, io.IOBase):
            stringText = ""
            for line in text.readlines():
                for char in line:
                    if char.lower() in self.alphabet:
                        stringText += char.lower()
            for n in self.listOfNgramSizes:
                newNgramList = genNgrams(text, n)
                distList.append(newNgramList)
        self.standardDists = distList
        
    def populate(self):
        for i in range(self.population):
            candidate = Organism(ciphertext=self.ciphertext)
            candidate.randomizeGuess()
            candidate.imageCiphertext()
            self.populationList.append(candidate)
    
    def solve(self):
        self.populate()
        previousMaxFitness = 0
        generationsWithoutImprovement = 0
        threshold = 20
        
        #for i in range(self.generations):
        while generationsWithoutImprovement <= threshold:
            fitnessList = []
    
            for candidate in self.populationList:
                candidate.imageCiphertext()
                candidate.evaluateLogarithmicFitness(self.standardDists)
                
                fitnessList.append(candidate.fitness)
            
            indexOfWinner = fitnessList.index(max(fitnessList))
            winner = self.populationList[indexOfWinner].copy()
            #print(winner.plaintextGuess)
            
            if previousMaxFitness >= winner.fitness:
                generationsWithoutImprovement += 1
                #print(generationsWithoutImprovement, winner.fitness)
                
            elif previousMaxFitness < winner.fitness:
                generationsWithoutImprovement = 0
                previousMaxFitness = winner.fitness
            self.populationList = []
            self.populationList.append(winner)
            
            for j in range(1, self.population):
                child = winner.copy()
                if j < (self.population * 0.7):
                    n = 1
                elif j >= (self.population * 0.7):
                    n = 4 + math.floor(generationsWithoutImprovement / 2)
                child.randomMutate(n)
                self.populationList.append(child)
                
            currentWinner = winner
        cipherGuess = currentWinner.cipherGuess
        currentWinner.imageCiphertext()
       
        return currentWinner.plaintextGuess, cipherGuess, currentWinner.fitness
            
                
def genNgrams(text, n):
    strippedText = "".join([c for c in text if c.isalpha()])
    countMap = {}
    for i in range(0, len(strippedText) + 1 - n):
        ngram = ""
        for j in range(0, n):
            ngram += strippedText[i+j]
        if ngram in countMap.keys():
            countMap[ngram] += 1
        elif ngram not in countMap.keys():
            countMap[ngram] = 1
    return countMap

def listNgrams(text, n):
    strippedText = "".join([c for c in text if c.isalpha()])
    ngramList = []
    for i in range(0, len(strippedText) + 1 - n):
        ngram = ""
        for j in range(0, n):
            ngram += strippedText[i+j]
        ngramList.append(ngram)
    return ngramList

def guessCorrelationIndex(alph1, alph2):
    correlationCount = 0
    for i in range(0, len(alph1)):
        if alph1[i] == alph2[i]:
            correlationCount += 1
    return correlationCount
        
def solve(ciphertextPath, samplePath, n = 4): 
    plaintextList = []
    cipherGuessList = []
    fitnessList = []
    for i in range(n):
        environment = Environment()
        environment.ciphertextPath = ciphertextPath
        environment.samplePath = samplePath
        environment.setCiphertextFromFile()
        environment.setSampleFromFile()
        environment.initiateStandardDists(environment.sampleText)
        plaintext, cipherGuess, fitness = environment.solve()
        plaintextList.append(plaintext)
        cipherGuessList.append(cipherGuess)
        fitnessList.append(fitness)
    indexOfWinner = fitnessList.index(max(fitnessList))
    print("Plaintext:\n" + plaintextList[indexOfWinner])
    print("Cipher Guess:", cipherGuessList[indexOfWinner])
    print("Fitness:", fitnessList[indexOfWinner])
    
