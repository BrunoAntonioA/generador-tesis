import copy

from numpy import isfinite
import utilsListOfListCPMP as utils
import os
import itertools
import pandas as pd

def generatePermutations(states):
    newStates = []
    for state in states:
        statePermutations = itertools.permutations(state)
        for stPer in statePermutations:
            if not stPer in newStates:
                newStates.append(stPer)
    return newStates

def listToDict(states, moves):
    newStates = []
    for i,state in enumerate(states):
        dictState = []
        for j, stack in enumerate(state):
            isInit = False
            isFinal = False
            if moves[i][0] == j+1:
                isInit = True
            if moves[i][1] == j+1:
                isFinal = True
            dictState.append({
                "isInit": isInit,
                "isFinal": isFinal,
                "stack": copy.deepcopy(stack)
            })
        newStates.append(copy.deepcopy(dictState))
    return newStates

def getMaxItem(state):
    mayor = 0
    for stack in state:
        for item in stack:
            if item > mayor:
                mayor = item
    return mayor

def stateTransform(state, opt, h):
    maxItem = getMaxItem(state)
    if opt['compact']:
        state = utils.compactState(state)
    if opt['norm']:
        state = utils.normalizeState(state, maxItem)
    if opt['elevate']:
        if opt['norm']:
            state = utils.elevateState(state, h, 1.2)
        else:
            state = utils.elevateState(state, h, maxItem+1)
    else:
        state = utils.fillStacksWithCeros(state, h)
        
    return state

def deleteZeros(state):
    for stack in state:
        while 0 in stack:
            stack.remove(0)
    return state

def traspuestaState(state):
    newState = []
    for i in range(len(state[0])):
        stack = []
        for row in state:
            stack.append(row[i])
        stack.reverse()
        newState.append(copy.deepcopy(stack))
    newState = deleteZeros(newState)
    return newState

def lineToMove(line):
    indexArrow = line.index('->')
    move = (int(line[indexArrow-1]), int(line[indexArrow+2]))
    return move

def lineToCol(line):
    indexDict = {
        0: 4,
        1: 8,
        2: 12,
        3: 16,
        4: 20,
        5: 24,
        6: 28,
    }
    col = []
    for i in range(7):
        idx = indexDict[i]
        item = line[idx:idx+2]
        if item == '  ': 
            col.append(0)
        else:
            col.append(int(item))
    return col

def extractData(file_path, maxHeigth, opt):
    h = maxHeigth
    with open(file_path) as f:

        lines = f.readlines() 
        cont = 0
        states = []
        moves = []
        state = []
        isInit = True
        isReadMode = False
        isGettingHeigth = True
        heigth = 0

        for line in lines:
            if 'Initial configuration' in line:
                isReadMode = True
                state = []
                continue
            if isReadMode:
                if isInit:
                    if isGettingHeigth:
                        heigth = int(line[1])
                        cont = heigth - 1
                        isGettingHeigth = False
                        state.append(lineToCol(line))
                    else:
                        cont -= 1
                        state.append(lineToCol(line))
                        if cont == 0:
                            isInit = False
                            state = traspuestaState(state)
                            states.append(stateTransform(state, opt, h))
                else:
                    if 'Relocation' in line:
                        isGettingHeigth = True
                        state = []
                        moves.append(lineToMove(line))
                        continue
                    else:
                        if isGettingHeigth:
                            isGettingHeigth = False
                            cont = int(line[1]) - 1
                            state.append(lineToCol(line))
                        else:
                            if cont > 0:
                                cont -= 1
                                state.append(lineToCol(line))
                                if cont == 0:
                                    state = traspuestaState(state)
                                    states.append(stateTransform(state, opt, h))
                            else:
                                continue
    
    states = states[0:len(states)-1]
    dictStates = listToDict(states, moves)
    permutations = generatePermutations(dictStates)
    return permutations

def addPropsToTuple(props, tuple):
    for prop in props:
        for item in prop:
            tuple.append(item)
    return tuple


def generateExcelFromStates(dictStates, name, opt):   
    states = []
    for state in dictStates:
        currState = []
        currStacks = []
        init = 0
        final = 0
        for i, col in  enumerate(state):
            currStacks.append(col['stack'])
            if col['isInit']:
                init = i+1
            if col['isFinal']:
                final = i+1
            for item in col['stack']:
                currState.append(item)
        currProps = utils.getPropertiesFromState(currStacks, opt['elevate'])
        currState = addPropsToTuple(currProps, currState)
        currState.append(init)
        currState.append(final)
        states.append(copy.deepcopy(currState))
    
    df = pd.DataFrame(states)
    df.to_csv('./GeneratedData/'+name+'.csv', header=None, index=False)

def shuffleDataSet():

    opt = {
        'elevate': False,
        'compact': False,
        'norm': False
    }   
    dataSets = []
    path = './GeneratedData/';
    files = os.listdir(path)
    ext = ".csv"
    aux = pd.DataFrame([])
    for i,f in enumerate(files):
        base = f[0:5]
        epot_text = ""
        if opt['compact']:
            epot_text += "-compact"
        if opt['elevate']:
            epot_text += "-elevate"
        if opt['norm']:
            epot_text += "-norm"
        final = base + epot_text + ext
        if final == f: 
            final = path + final
            currentDataSet = pd.read_csv(final, header=None)
            currentDataSet = pd.DataFrame(currentDataSet)
            currentDataSet.sample(frac = 1)
            currentDataSet = pd.DataFrame(currentDataSet[0:25000])
            if i == 0:
                aux = currentDataSet
                continue
            aux = aux.append(currentDataSet)
    if epot_text == "": epot_text = " normal"
    savePath = epot_text + ext
    savePath = savePath[1:]
    savePath = path + savePath
    aux.to_csv(savePath, header=None, index=False)


def main(opt): 
    path = './DLTS/reference_solutions/7x5_cv1_test';
    files = os.listdir(path)
    file_name = '5.out'
    excelFileName = file_name.replace('.','-')
    if opt['compact']:
        excelFileName += '-compact'
    if opt['elevate']:
        excelFileName += '-elevate'
    if opt['norm']:
        excelFileName += '-norm'
    permutations = extractData(path+'/'+file_name, 7, opt)
    generateExcelFromStates(permutations, excelFileName, opt)

opt = {
        'compact': True,
        'elevate': True,
        'norm': True
    }
main()

opt = {
        'compact': True,
        'elevate': False,
        'norm': True
    }
main()

opt = {
        'compact': False,
        'elevate': False,
        'norm': True
    }
main()

opt = {
        'compact': False,
        'elevate': False,
        'norm': False
    }
main()


                

                 