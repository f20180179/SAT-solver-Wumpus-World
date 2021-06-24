#!/usr/bin/env python3
from __future__ import print_function
from Agent import * # See the Agent.py file
from pysat.solvers import Glucose3
import math

#### All your code can go here.
g = Glucose3()

#### You can change the main function as you wish. 
#### Run this program to see the output. Also see Agent.py code.

dir_words = ['Up', 'Down', 'Left', 'Right']
dir_moves = [[0,1], [0,-1], [-1,0], [1,0]]

def movement(curLoc, adj):
    mv = [0,0]
    mv[0] = adj[0] - curLoc[0]
    mv[1] = adj[1] - curLoc[1]
    idx = dir_moves.index(mv)
    return dir_words[idx]

def getLocationKey(location):
    return (location[0]-1)*4 + location[1]

def findAdjacents(curLoc):
    adjacents = []
    for i in range(4):
        x = dir_moves[i][0] + curLoc[0]
        y = dir_moves[i][1] + curLoc[1]
        if x >= 1 and x <= 4 and y >= 1 and y <= 4:
            adjacents.append([x,y])
    return adjacents

def main():
    ag = Agent()
    locations = [i for i in range(1,17)]#16 variables for 16 places
    curLoc = ag.FindCurrentLocation()
    last_loc = [1,1]#initial location
    n_iter = 0#to count how many times simulation can run at max
    all_clauses = []#all the clauses which we keep on adding to the KB
    g.add_clause([getLocationKey([1,1])])#Add starting location as safe to the KB
    all_clauses.append([getLocationKey([1,1])])
    path = []
    print("Initial Location: [1, 1]")

    while curLoc!=[4,4] and n_iter <= 50:#not reached exit
        n_iter += 1
        curLoc = ag.FindCurrentLocation()#To know the current location in the world. One of the allowed function
        percept = ag.PerceiveCurrentLocation()#To get the perception of adjacent locations from the current location. One of the allowed function
        adjacents = findAdjacents(curLoc)
        adjacents_key = [getLocationKey(adj) for adj in adjacents]#Unique denotion of location. Like [1,1] -> 1, [1,2]-> 2, ..., [2,1]->5, ...
        adjacents_key.sort(reverse=True)#Sort in decreasing order of key. Helps in going to closest state to [4,4] first.
        path.append(curLoc)
        #print("curLoc: {}, percept: {}, adjacents: {}, last_loc: {}".format(curLoc, percept, adjacents, last_loc))

        #Adding clauses in DNF form to the KB
        if percept == '=0': #all adjacent locations are safe
            #add all adj locations to KB as safe
            for adj in adjacents_key:
                g.add_clause([adj])
                all_clauses.append([adj])

        elif percept == '=1': #only one adjacent location is unsafe
            num_adj = len(adjacents)
            if num_adj == 2: #Corner location; only two adjacents possible
                l1 = adjacents_key[0]
                l2 = adjacents_key[1]
                g.add_clause([l1, l2]), all_clauses.append([l1,l2])
                g.add_clause([-l1, -l2], all_clauses.append([l1,l2]))

            if num_adj == 3: #Border location; three adjacents possible
                l1 = adjacents_key[0]
                l2 = adjacents_key[1]
                l3 = adjacents_key[2]
                g.add_clause([-l1, -l2, -l3]), all_clauses.append([-l1,-l2,-l3])
                g.add_clause([l1, l2]), all_clauses.append([l1,l2])
                g.add_clause([l1, l3]), all_clauses.append([l1,l3])
                g.add_clause([l2, l3]), all_clauses.append([l2,l3])

            if num_adj == 4: #Middle location; four adjacents possible
                l1 = adjacents_key[0]
                l2 = adjacents_key[1]
                l3 = adjacents_key[2]
                l4 = adjacents_key[3]
                g.add_clause([l1, l2]), all_clauses.append([l1,l2])
                g.add_clause([l1, l3]), all_clauses.append([l1,l3])
                g.add_clause([l1, l4]), all_clauses.append([l1,l4])
                g.add_clause([l2, l3]), all_clauses.append([l2,l3])
                g.add_clause([l2, l4]), all_clauses.append([l2,l4])
                g.add_clause([l3, l4]), all_clauses.append([l3,l4])
                g.add_clause([-l1, -l2, -l3, -l4]), all_clauses.append([-l1, -l2, -l3, -l4])

        else: #More than one adjacent location is unsafe
            num_adj = len(adjacents)
            if num_adj == 2:
                l1 = adjacents_key[0]
                l2 = adjacents_key[1]
                g.add_clause([-l1]), all_clauses.append([-l1])
                g.add_clause([-l2]), all_clauses.append([-l2])
            
            if num_adj == 3:
                l1 = adjacents_key[0]
                l2 = adjacents_key[1]
                l3 = adjacents_key[2]
                g.add_clause([-l1, -l2]), all_clauses.append([-l1, -l2])
                g.add_clause([-l1, -l3,]), all_clauses.append([-l1, -l3])
                g.add_clause([-l2, -l3]), all_clauses.append([-l2, -l3])

            if num_adj == 4:
                l1 = adjacents_key[0]
                l2 = adjacents_key[1]
                l3 = adjacents_key[2]
                l4 = adjacents_key[3]
                g.add_clause([-l1, -l2, -l3]), all_clauses.append([-l1, -l2, -l3])
                g.add_clause([-l1, -l2, -l4]), all_clauses.append([-l1, -l2, -l4])
                g.add_clause([-l1, -l3, -l4]), all_clauses.append([-l1, -l3, -l4])
                g.add_clause([-l2, -l3, -l4]), all_clauses.append([-l2, -l3, -l4])

        g.solve()
        progress = False

        for adj in adjacents_key:#See the adjacent locations
            if adj == getLocationKey(last_loc):#Don't go to the state from where you came to this current state
                continue
            test_g = Glucose3()
            test_g.append_formula(all_clauses)
            test_g.add_clause([-adj])#Test for KB and negation of where we want we to go. If false, we can go; else we cannot.
            res = test_g.solve()
            if res == False:
                if adj%4==0:
                    x = adj/4
                    y = 4
                else:
                    x = adj//4 + 1
                    y = adj%4
                pos = [x, y]
                dir = movement(curLoc, pos)
                last_loc = curLoc#Update last_loc to use in next location
                ag.TakeAction(dir)
                progress = True
                break
        
        if progress == False:#If no adjacent locations are good, go to from where you came from to explore further and decide.
            dir = movement(curLoc, last_loc)
            last_loc = curLoc
            ag.TakeAction(dir)
       
    if n_iter > 50:
        print("\nExit Cannot be reached without taking risk.")
    else:
        print("\nSequence of path that leads to safe exit: ")
        for p in path:
            if p != [4,4]:
                print(p, end=" => ")
            else:
                print(p)


if __name__=='__main__':
    main()