import numpy as np

def compactState(yard):
    sort = []
    for stack in yard:
      for container in stack:
        if not container in sort:
          sort.append(container)
    sort = sorted(sort)
    maxValue = 0
    for i in range(len(yard)):
      for j in range(len(yard[i])):
        yard[i][j] = sort.index(yard[i][j]) + 1
        if yard[i][j] > maxValue:
          maxValue = yard[i][j]
    return yard

def fillStacksWithCeros(yard, h):
    for stack in yard:
      while len(stack) < h:
        stack.append(0)
    return yard

def elevateState(yard, h, max_item):
    for stack in yard:
      while len(stack) < h:
        stack.insert(0, max_item)
    return yard

def getStackValues(yard): #sorted stacks?
    values = []
    for stack in yard:
        cont = 0
        isUnordened = False
        for i in range(len(stack)):
            if i==0:
                continue
            if isUnordened:
                cont +=1
                continue
            else:
                if stack[i] > stack[i-1]:
                    isUnordened = True
                    cont += 1
                    continue
        values.append(cont)
    return values

def getStackLen(yard):
    lens = []
    for stack in yard:
        lens.append(len(stack))
    return lens

def getTopStacks(yard,max_item):
    tops = []
    for stack in yard:
        if len(stack) != 0:
            tops.append(stack[len(stack)-1])
        else:
            tops.append(max_item)
    return tops

def flattenState(state):
    flatten = []
    for lista in state:
        for item in lista:
            flatten.append(item)
    return flatten

def normalizeState(state, max_item):
    newState = []
    for stack in state:
        col = []
        for item in stack:
            col.append(item/max_item)
        newState.append(col)
    return newState
        

def getMaxs(state):
    maxList = []
    for stack in state:
        maxList.append(max(stack, default=0))
    return maxList

def getPropertiesFromState(state, isElevate=True):
    properties = []
    properties.append(getMaxs(state))
    properties.append(getStackValues(state))
    if not isElevate:
        properties.append(getStackLen(state))
    return properties



