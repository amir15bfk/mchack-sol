import random
from typing import final
import torch
import numpy as np
from env import Env
from collections import deque
from model import Linear_QNet ,QTrainer
MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.0005

class Agent:

    def __init__(self) :
        self.number_of_games = 0
        self.epsilon = 0 # randomness ??
        self.gamma = 0.9 # discount rate ??
        self.memory = deque(maxlen=MAX_MEMORY) # popleft() if is full
        self.model = Linear_QNet(13,256,71) 
        self.trainer = QTrainer(self.model,LR,self.gamma) 


    def remember(self,state,action,reward,next_state,game_over):
        self.memory.append((state,action,reward,next_state,game_over))

    def train_long_memory(self):
        if len(self.memory)>BATCH_SIZE:
            mini_sample = random.sample(self.memory,BATCH_SIZE)
        else:
            mini_sample = self.memory
        
        states,actions,rewards,next_states,game_overs = zip(*mini_sample)
        self.trainer.train_step(states,actions,rewards,next_states,game_overs)
    
    def train_short_memory(self,state,action,reward,next_state,game_over):
        self.trainer.train_step(state,action,reward,next_state,game_over)

    def get_move(self,state):
        # do a random move
        self.epsilon = 80 - self.number_of_games
        final_move = [0]*71

        if random.randint(0,200) < self.epsilon:
            move = random.randint(0,71)
            final_move[move]=1
        else:
            state0 = torch.tensor(state,dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move]=1
        return final_move,move
def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 100000000
    agent = Agent()
    game = Env()
    while True:
        # get corr state
        state = game.get_state()

        # get the move
        action = agent.get_move(state)
        
        # play the move
        reward , game_over , score = game.play_round(action,agent.number_of_games)

        # get the new state
        new_state = game.get_state()

        # train short memory
        agent.train_short_memory(state,action,reward,new_state,game_over)

        # remember
        agent.remember(state,action,reward,new_state,game_over)

        if game_over:
            agent.number_of_games += 1
            # train long memory
            agent.train_long_memory()

            if score < record :
                record = score
                agent.model.save('model_v9.pth')
            # TODO : plot
            plot_scores.append(score)
            total_score+= score
            mean_score = total_score/ agent.number_of_games

            print('Game:',agent.number_of_games,'Score:',score,'Record:',record,'Mean:',mean_score)
            
            # plot_mean_scores.append(mean_score)
            # plot(plot_scores,plot_mean_scores)





if __name__=='__main__' :
    train()