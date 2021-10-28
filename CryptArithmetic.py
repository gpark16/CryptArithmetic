import copy

# Letter Class
# Used to represent one letter of the CryptArithmetic Problem
# Each letter has a letter associated with it, a range of values from 0..9
# depending on what is valid for it, a count with the number of values
# left in the range and the frequency of the letter in the puzzle.
class Letter:
    def __init__(self, row, col, let):
        self.letter = let
        if((col == 0 and row == 2) or (col == 0 and row == -1)):
            self.letterRange = createRange(1, 1)
        elif(col == 0):
            self.letterRange = createRange(1, 9)
        elif(row != -1):
            self.letterRange = createRange(0, 9)
        else:
            self.letterRange = createRange(0, 1)
        self.count = len(self.letterRange)
        self.frequency = 1

    def removeValue(self, val):
        if(val in self.letterRange):
            self.letterRange.remove(val)
            self.count = self.count - 1

    def setValue(self, val):
        self.letterRange = [val]
        self.count = 1

    def incrementFrequency(self):
        self.frequency += 1

    def getValue(self):
        if(self.count == 0):
            return -999
        elif(self.count == 1):
            return self.letterRange[0]
        else:
            return -1

    def getRange(self):
        return self.letterRange

    def getLetter(self):
        return self.letter
    
    def __lt__(self, other):
        if(self.count < other.count):
            return True
        elif(self.count > other.count):
            return False
        elif(self.frequency > other.frequency):
            return True
        else:
            return False

# Base Class Constraint
# Used to represent the two kinds of constraints that appear for 
# this CSP problem.  The first is the AllDiff which is all different
# for each letter in the list.  The second is the Equal constraint
# which means the left-hand side of the expression must be the same
# as the right-hand side.
class Constraint:
    def __init__(self): { }

    def isValid(self, dict):
        return True

# AllDiff Constraint
# Used to represent a list (clist) of variables that must be
# all different from each other.
class AllDiffConstraint(Constraint):
    def __init__(self, clist):
        self.clist = clist

    def isValid(self, dict):
        for i in range(0, len(self.clist)):
            for j in range(0, len(self.clist)):
                if(i != j and dict[self.clist[i]].getValue() != -1 and dict[self.clist[j]].getValue() != -1 
                          and dict[self.clist[i]].getValue() == dict[self.clist[j]].getValue()):
                    return False
        return True
    
# AllDiff Constraint
# Used to represent two lists (llist and rlist) of variables that must be
# have the sum of both lists equaling each other.
class EqualConstraint(Constraint):
    def __init__(self, llist, rlist):
        self.llist = llist
        self.rlist = rlist
        
    def isValid(self, dict):
        diff = 0

        for i in range(0, len(self.llist)):
            if(dict[self.llist[i]].getValue() == -1):
                return True

            diff += dict[self.llist[i]].getValue()
            
        for i in range(0, len(self.rlist)):
            if(dict[self.rlist[i]].getValue() == -1):
                return True

            diff -= dict[self.rlist[i]].getValue() * (10 if (len(dict[self.rlist[i]].getLetter()) == 2) else 1)

        return (diff == 0)

# Read the information from the file and create the dictionary
# and constraints from the file given by path.
def readFile(path):
    with open(path) as file_ptr:
        lines = file_ptr.readlines()
        dict = {}

        for i in range(0,3):
            for j in range(0,4 + (1 if (i == 2) else 0)):
                if(not (lines[i][j] in dict)):
                    dict[lines[i][j]] = Letter(i, j, lines[i][j])
                else:
                    dict[lines[i][j]].incrementFrequency()

        for i in range(0,4):
            dict["C" + str(i)] = Letter(-1, i, "C" + str(i))

        keyList = []
        for k in dict.keys():
            if(len(k) == 1):
                keyList.append(k)

        keyList.sort()
        constList = [AllDiffConstraint(keyList)]

        for i in range(0,5):
            llist = []
            rlist = []

            if(i < 4):
                llist.append("C" + str(i))

            if(i >= 1):
                rlist.append("C" + str(i-1))
                llist.append(lines[0][i-1])
                llist.append(lines[1][i-1])

            rlist.append(lines[2][i])

            constList.append(EqualConstraint(llist, rlist))

    return dict, constList, lines

# Write everything to the file given by path.
# Lines is used to represent what the result should be
# and vars is the answer assignments.
def writeFile(path, lines, vars):
    file_ptr = open(path, "w")

    for i in range(0,3):
        for j in range(0,4 + (1 if (i == 2) else 0)):
            file_ptr.write(str(vars[lines[i][j]]))
        file_ptr.write("\n")

    file_ptr.close()

def createRange(a, b):
    return list(range(a, b + 1))

# Solves the CSP problem given by the CryptArithmetic Problem
# Recursively calls backtrack to do this problem.
def backtrackingSearch(dict, consList):
    return backtrack({}, dict, consList)

# Recursive Solution to the CryptArithmetic Problem.
# Follows the methodology given in the book about Backtrack Searching
# for CSPs.
def backtrack(vars, dict, csp):
    if (len(vars) == len(dict)):
        return vars

    letter = selectUnassignedVariable(vars, dict)

    for val in letter.getRange():
        if(isNotAssigned(letter.getLetter(), val, vars)):
            vars[letter.getLetter()] = val

            copydict = copy.deepcopy(dict)

            if(inference(letter.getLetter(), val, copydict, csp)):
                result = backtrack(vars, copydict, csp)

                if result is not None:
                    return result

            vars.pop(letter.getLetter())

    return None

# Choose an unassigned variable that is not used yet.
# Go through all variables, sort them using (__lt__)
# and then choose the best (first) one.
def selectUnassignedVariable(vars, dict):
    bestLetter = []

    for k in dict.keys():
        if(not (k in vars)):
            bestLetter.append(dict[k])

    bestLetter.sort()
    return bestLetter[0]

# Inference Function
# Make inferences when an assignment is made. When
# a value is taken, it is removed off the table for other
# variables too.  It also enforces the validity of the CSP
# If it cannot then it will fail.
def inference(letter, val, dict, csp):
    if(len(letter) == 1):
        for k in dict.keys():
            if(k == letter):
                dict[k].setValue(val)
            elif(len(k) == 1):
                dict[k].removeValue(val)
    else:
        dict[letter].setValue(val)

    for c in csp:
        if(not c.isValid(dict)):
            return False
    return True

# Check if that value val is not assigned in vars.
# If it is then return True, otherwise False.
def isNotAssigned(letter, val, vars):
    if((len(letter) == 2) and not (letter in vars)):
        return True

    for k in vars.keys():
        if(len(k) == 1 and vars[k] == val):
            return False

    return True

# Main Program.
# Read a file, solve the problem, then write to a file.
dict, consList, lines = readFile("Input2.txt")
vars = backtrackingSearch(dict, consList)
writeFile("Output2.txt", lines, vars)