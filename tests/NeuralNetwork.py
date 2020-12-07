import pySAD as ad
import numpy as np

nNodes = np.array([3, 7, 7, 1])

def calcLayerNN(prev, weights, biases):
    
    curr = ad.matmul(weights, prev) + biases
    curr = curr / (1.0 + ad.exp(-curr))
    return curr

def calcNN(nodes=[nNodes[0]], theta=[sum(nNodes[1:]+sum(nNodes[:-1]*nNodes[1:]))], **kwargs):
    
    beg = 0
    
    for i in range(len(nNodes)-1):
        
        biases = theta[beg:beg+nNodes[i+1]]
        beg += nNodes[i+1]

        weights = theta[beg:beg+nNodes[i+1]*nNodes[i]]
        weights.data.resize((nNodes[i+1], nNodes[i]))
        beg += nNodes[i+1]*nNodes[i]

        nodes = calcLayerNN(nodes, weights, biases)

    return nodes

if __name__=="__main__":

    tape = ad.AD_Tape()
    tape.compile(calcNN)
    tape.write("nnTape", readable=True)
