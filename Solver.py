import os
import numpy as np

#Disables tensorflow warning, logs 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

import tensorflow as tf
import tensorflow.keras as keras

import source.utils as utils

from sys import stderr,argv
from copy import deepcopy
from time import time

from source.Exceptions import *

class Sudoku():
    def __init__(self, board):
        self.board = board
        self.rows = [0 for i in range(9)]
        self.cols = [0 for i in range(9)]
        self.boxes = [0 for i in range(9)]
        self.n = len(board)
        self.solvable = True
        for i in range(self.n):
            for j in range(self.n):
                val = self.board[i][j]
                if(val != 0):
                    msk = (1<<(val-1))
                    self.rows[i] ^= msk
                    self.cols[j] ^= msk
                    self.boxes[(i//3)*3+(j//3)] ^= msk
                    if(self.rows[i] or self.cols[j] or self.boxes[(i//3)*3+(j//3)]): self.solvable = False

    def Solvable(self):
        return self.solvable

    def Print_board(self):
        for i in range(self.n):
            for j in range(self.n):
                print(self.board[i][j], end = " ")
                if(j%3 == 2 and j != 8): print("|", end = " ")
            print()
            if(i%3 == 2 and i != 8): print(("-"*6)+"+"+("-"*7)+"+"+("-"*7))

    def options(self, i, j):
        msk = self.rows[i]|self.cols[j]|self.boxes[(i//3)*3+(j//3)]
        left = []
        for i in range(9):
            if (msk&(1<<i)) == 0: left.append(i+1)
        return left

    def place(self, i, j, val):
        self.board[i][j] = val
        msk = (1<<(val-1))
        self.rows[i] ^= msk
        self.cols[j] ^= msk
        self.boxes[(i//3)*3+(j//3)] ^= msk


def solve(puzzle):
    solved = False
    while not solved:
        solved = True
        changed = False
        for i in range(puzzle.n):
            for j in range(puzzle.n):
                if(puzzle.board[i][j] == 0):
                    solved = False
                    left = puzzle.options(i,j)
                    if(len(left) == 0): return False
                    if(len(left) == 1):
                        puzzle.place(i, j, left[0])
                        changed = True
        if not changed:
            if solved:
                puzzle.Print_board()
                return True
            min_needed = ((puzzle.n+1),[],(-1,-1))
            for i in range(puzzle.n):
                for j in range(puzzle.n):
                    if(puzzle.board[i][j] == 0):
                        left = puzzle.options(i,j)
                        min_needed = min(min_needed, (len(left),left,(i,j)))
            i, j = min_needed[2]
            for val in min_needed[1]:
                puzzle_next = deepcopy(puzzle)
                puzzle_next.place(i, j, val)
                solved = solve(puzzle_next)
                if solved: break
            return solved
    return solved


def make_board(string):
    board = []
    for i in range(81):
        val = string[i]
        if(val == '.'): val = '0'
        if(i%9 == 0):
            l = []
        l.append(ord(val)-ord('0'))
        if(i%9 == 8): board.append(l)
    return board

def get_input():
    string = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'

    board = [[9,7,0,0,0,2,0,0,0],[1,0,8,0,0,6,0,0,4],[0,0,2,0,0,0,7,0,0],
        [0,0,1,8,5,0,4,0,0],[5,4,7,0,2,1,0,0,9],[8,0,6,7,9,0,1,0,5],
        [3,0,0,5,0,8,0,0,0],[0,0,0,0,0,0,5,4,0],[7,2,0,0,4,0,0,8,0]]
    #make_board(string)
    return board


def main(argv):

    try:
        if len(argv) < 2:
            raise InsuffientArguments

        if not os.path.exists('./model.h5'):
            raise ModelNotFoundException

        #Loading Model
        model = keras.models.load_model('./model.h5')

        for path in argv[1:]:
            if not os.path.exists(path):
                raise FileNotFoundException(path)

            extracted_sudoku = utils.get_sudoku(path, model)
            sudoku = Sudoku(extracted_sudoku)
            sudoku.Print_board()
            print('\n\n')
            st = time()
            solve(sudoku)
            print('\n\n')
            en = time()
            # sudoku.Print_board()
            print()
            print(en-st,"seconds")
            os.system("rm "+argv[1])

    except InsuffientArguments:
        print('Please enter filename of image as argument!', file=stderr)

    except ModelNotFoundException:
        print('Please train the model by running \'train.py\'!', file=stderr)
    
    except FileNotFoundException as e:
        print(str(e), file=stderr)

if __name__ == '__main__':
    main(argv)