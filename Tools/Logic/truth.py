# nodes for proposition
class Proposition:
    def __init__(self, p):
        self.parent = None
        self.left = None
        self.right = None
        self.level = 0
        self.word = p
        self.value = False

    def setValue(self):
        if self.word == "and":
            self.value = self.left.value and self.right.value
        elif self.word == "or":
            self.value = self.left.value or self.right.value
        elif self.word == "not":
            self.value = not self.right.value
        elif self.word == "implies":
            self.value = (not self.left.value) or self.right.value
        elif self.word == "iff":
            self.value = (self.left.value == self.right.value)

    def updateValue(self):
        if self.left and not isinstance(self.left, Atomic):
            self.left.updateValue()
        if self.right and not isinstance(self.right, Atomic):
            self.right.updateValue()
        if not isinstance(self, Atomic): self.setValue()

    def getAllValue(self):
        string = ""
        if self.left:
            string = string + self.left.getAllValue()
        
        if self.value == True: string = string + "\\top & "
        else: string = string + "\\bot & "

        if self.right:
            string = string + self.right.getAllValue()
        
        return string

    def setLevel(self):
        if self.word == "not":
            self.level = self.right.level + 1
        else:
            self.level = \
            max(self.left.level, self.right.level) + 1
        print(self.word, self.level)

    def getAllLevel(self):
        string = ""
        if self.left:
            string = string + self.left.getAllLevel()
        string = string + str(self.level) + " & "
        if self.right:
            string = string + self.right.getAllLevel()
        
        return string

    def setParent(self, node = None):
        self.parent = node
    
# leaf node of tree
class Atomic(Proposition):
    def __init__(self, p):
        super().__init__(p)
        self.level = 1

    def setValue(self, truth):
        self.value = truth

    def getValue(self):
        return self.value

# get propositional formula
inputformula = input("Input string : ")
formula = inputformula.split()
n = len(formula)
    
# list of characters
prechars = ["not", "and", "or", "implies", "iff", "(", ")"]
operators = prechars[0:5]
symbols = ["\\neg", "\\wedge", "\\vee", "\\to", "\\iff"]

# generate postfix list
def precedence(op):
    if op == "(" or op == ")": return 0
    elif op == "implies" or op == "iff": return 1
    elif op == "and" or op == "or": return 2
    elif op == "not": return 3
    else: return -1

class Stack:
    def __init__(self) -> None:
        self.top = []
        
    def isEmpty(self): return len(self.top) == 0
    def size(self): return len(self.top)
    def clear(self): self.top = []
    
    def push(self, item):
        return self.top.append(item)
    
    def pop(self):
        if not self.isEmpty():
            return self.top.pop(-1)
    
    def peek(self):
        if not self.isEmpty():
            return self.top[-1]
    
def Infix2Postfix(expr):    # expr: 입력 리스트(중위 표기식)
    s = Stack()
    output = []    # output: 출력 리스트(후위 표기식)
    for term in expr:
        if term == '(': s.push('(')
        elif term == ')':
            while not s.isEmpty():
                op = s.pop()
                if op =='(':
                    break 
                else:
                    output.append(op)
        elif term in operators:
            while not s.isEmpty():
                op = s.peek()
                if precedence(term) <= precedence(op):
                    output.append(op)
                    s.pop()
                else:
                    break
            s.push(term)
        else:
            output.append(term)
            
    while not s.isEmpty():
        output.append(s.pop())
        
    return output

postfix = Infix2Postfix(formula)
print("Postfix : ", postfix)

# generate tree
s = Stack()
atoms = []
atomwords = []
for word in postfix:
    if word not in prechars:
        node = Atomic(word)
        s.push(node)
        atoms.append(node)
        if word not in atomwords:
            atomwords.append(word)
    elif word in operators:
        node = Proposition(word)
        if word == "not":
            node.right = s.pop()
            node.right.setParent(node)
            s.push(node)
        else:
            node.right = s.pop()
            node.left = s.pop()
            node.right.setParent(node)
            node.left.setParent(node)
            s.push(node)
        node.setValue()
        node.setLevel()

p = s.peek()
while p.parent != None:
    p = p.parent
root = p
print("Root :", root.word)

# print LaTeX code for variables
from itertools import product
print("\\begin{array}{", end = "")
string = ""
for i in range(0,len(atomwords)):
    string = string + "c "
print(string[:-1] + "}")
print("\\toprule")

# print formula
string = ""
for word in atomwords:
    string = string + word + " & "
print(string[:-2] + "\\\\")

print("\\midrule")

# print truth values
for p in product((True, False), repeat=len(atomwords)):
    string = ""
    for i in range(len(atomwords)):
        if p[i] == True: string = string + "\\top & "
        else: string = string + "\\bot & "
    print(string[:-2] + "\\\\")
print("\\midrule")
print("\\multicolumn{" + str(len(atomwords)) + "}{c}{\\text{Hierarchy}} \\\\")
print("\\bottomrule")
print("\\end{array}")

print("\\;")

# print LaTeX code for formula
def getIndex(target, list):
    for idx, word in enumerate(list):
        if target == word:
            return idx

print("\\begin{array}{", end = "")
for i in range(0,n):
    if i == 0:
        print("c", end = "")
    else:
        print(" c", end = "")
print("}")
print("\\toprule")

# print formula
string = ""
for idx, word in enumerate(formula):
    if word in operators:
        string = string + symbols[getIndex(word,operators)]
    else: string = string + word
    if idx + 1 < len(formula):
        string = string + " & "
print(string + " \\\\")
print("\\midrule")

# print truth values

for p in product((True, False), repeat=len(atomwords)):
    for atom in atoms:
        atom.setValue(p[getIndex(atom.word, atomwords)])
    root.updateValue()
    string = root.getAllValue()[:-3]
    cnt = 0
    for word in formula:
        if word == "(" or word == ")":
            string = string[0:cnt] + " & " + string[cnt:]
        else: cnt += 7
    print(string, "\\\\")

print("\\midrule")
string = root.getAllLevel()[:-2]
cnt = 0
for word in formula:
    if word == "(" or word == ")":
        string = string[0:cnt] + " & " + string[cnt:]
    else: cnt += 4
print(string)
print("\\\\")
print("\\bottomrule")
print("\\end{array}")