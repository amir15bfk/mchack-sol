import os
import easyocr
import math
import numpy as np
class Cursor:
    def __init__(self,doc):
        self.pos = 0
        self.maxpos = len(doc)
    def move_left(self):
        if self.pos <1:
            self.pos = self.maxpos
        else:
            self.pos-=1
    def move_right(self):
        if self.pos >=self.maxpos:
            self.pos = 0
        else:
            self.pos+=1 
    def remove(self):
        self.pos-=1
        self.maxpos-=1
    def write(self):
        self.pos+=1
        self.maxpos+=1
class Env:
    options = ["remove","mv_l","mv_r"," ","\n"]+list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMOPQRSTUVWXYZ/*-\\_.,?!$£%@()")
    def __init__(self) -> None:
        self.reader = easyocr.Reader(['en'])
        self.windowsize = 5
        self.docs = [i for i in os.listdir('/home/amir/Documents/mchack/findit2/train') if i.endswith(".txt")]
        self.get_doc()
    def get_state(self):
        state = [
            self.cursor.pos,
            self.cursor.maxpos]+[ord(self.false_doc[i]) for i in range(self.cursor.pos-self.windowsize,self.cursor.pos+self.windowsize+1) if (i>=0 and i<=self.cursor.maxpos) else ord("#")]
        return np.array(state,dtype=int)

    def get_doc(self):
        self.doc = self.docs.pop()
        with open(self.doc,"r") as f:
            self.doc_true = list("".join(f.readlines()))
        self.true_tokenes = self.get_tokenes(self.doc_true)    
        # Read text from an image
        self.false_doc = list("".join([detection[1] for detection in self.reader.readtext(self.doc[-3:]+'png')]))
        self.false_tokenes = self.get_tokenes(self.false_doc)
        self.dist = self.compare_docs(self.true_tokenes,self.false_tokenes)
        self.cursor = Cursor(self.false_doc)
        self.rest_iters = 2000
        self.game_over = False
    def get_tokenes(self,doc):
        return "".join(doc).split(" ")  
    def play_round(self,action,move):
        if move==0:
            reward = self.remove()
        elif move==1:
            reward = self.move_left()
        elif move==2:
            reward = self.move_right()
        else:
            reward = self.write(Env.options[move])
        if self.dist == 0:
            reward = 100
            game_over = True
            self.get_doc()
        elif self.rest_iters==0:
            reward = -20
            game_over=True
            self.get_doc()
        else:
            self.rest_iters -=1
        return reward,game_over , self.dist

    def write(self,letter):
        self.false_doc.insert(self.cursor.pos+1,letter)
        self.cursor.write()
        self.false_tokenes = self.get_tokenes(self.false_doc)
        newdist = self.compare_docs(self.true_tokenes,self.false_tokenes)
        if newdist < self.dist:
            reward = 5
        elif newdist > self.dist:
            reward = -5
        else:
            reward = -1
        self.dist = newdist

        return reward
    def remove(self):
        self.false_doc.pop(self.cursor.pos)
        self.cursor.remove()
        self.false_tokenes = self.get_tokenes(self.false_doc)
        newdist = self.compare_docs(self.true_tokenes,self.false_tokenes)
        if newdist < self.dist:
            reward = 5
        elif newdist > self.dist:
            reward = -5
        else:
            reward = -1
        self.dist = newdist
        return reward

    def move_left(self):
        self.cursor.move_left()
        reward = -0.1
        return reward
    
    def move_right(self):
        self.cursor.move_left()
        reward = -0.1
        return reward
    
    def compare_docs(self,doc1,doc2):
        com_dict = dict()
        for i in doc1:
            if com_dict.get(i):
                com_dict[i]+=1
            else:
                com_dict[i]=1
        for i in doc2:
            if com_dict.get(i):
                com_dict[i]-=1
            else:
                com_dict[i]=-1
        dist = 0
        for i in com_dict.values():
            dist += math.abs(i)
        return dist
    def visu(self):
        os.system('cls')
        if self.cursor.pos>0:
            print(self.false_doc[:self.cursor.pos],end="")
        print("\033[92m\033[1m"+self.false_doc[:self.cursor.pos]+"\033[0m",end="")
        if self.cursor.pos<self.cursor.maxpos:
            print(self.false_doc[:self.cursor.pos])
    def run(self):
        self.get_doc()
        self.visu()
        self.move_right()
        self.visu()
        self.write("a")
        self.visu()