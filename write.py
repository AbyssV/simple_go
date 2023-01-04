#!/usr/bin/env python
# -*- coding:utf-8 -*-
# ProjectName: HW2
# FileName: write
# Description:
# TodoList:

# agent use this function
def writeOutput(result, path="output.txt"):
    res = ""
    if result == "PASS":
    	res = "PASS"
    else:
	    res += str(result[0]) + ',' + str(result[1])

    with open(path, 'w') as f:
        f.write(res)
# agent use this function
def writePass(path="output.txt"):
	with open(path, 'w') as f:
		f.write("PASS")

# host use this function
def writeNextInput(piece_type, previous_board, board, path="input.txt"):
	res = ""
	res += str(piece_type) + "\n"
	for item in previous_board:
		res += "".join([str(x) for x in item])
		res += "\n"
        
	for item in board:
		res += "".join([str(x) for x in item])
		res += "\n"

	with open(path, 'w') as f:
		f.write(res[:-1]);

		