import pySAD as sad
import numpy as np

# Number of nodes in each layer in the NN
nNodes = np.array([3, 7, 7, 1])

# prev: 1-D array containing previous node values
# weights: 2-D array containing weights
# biases: 1-D array containing biases
def calcLayerNN(prev, weights, biases):
    
    curr = sad.matmul(weights, prev) + biases
    curr = curr / (1.0 + sad.exp(-curr))
    return curr

# inputs: 1-D array of features
# theta: Parameter vector containing all weights and biases
def calcNN(inputs=[nNodes[0]], theta=[sum(nNodes[1:]+sum(nNodes[:-1]*nNodes[1:]))], **kwargs):
    
    beg = 0

    nodes = inputs
    
    for i in range(len(nNodes)-1):
        
        biases = theta[beg:beg+nNodes[i+1]]
        beg += nNodes[i+1]

        weights = theta[beg:beg+nNodes[i+1]*nNodes[i]]
        weights.resize((nNodes[i+1], nNodes[i]))
        beg += nNodes[i+1]*nNodes[i]

        nodes = calcLayerNN(nodes, weights, biases)

    return nodes

tape = sad.AD_Tape()
tape.compile(calcNN, kwargs={})
tape.write("nnTape", readable=True)
