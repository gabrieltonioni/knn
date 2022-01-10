import util
import math
import sys
import random
import time

class kdTree():

    pq = util.PriorityQueue()
    
    def __init__(self, P, depth = 0):
        	# BuildKdTree(P, depth)
	        # Input: a set of points P and the current depth "depth".
	        # Output: the root of a kd-tree storing P.

            self.leftChild = self.rightChild = self.pointValue = self.splitValue = None
            self.depth = depth
            
            n = len(P)

	        # if P contains only one point
		    #     then return a leaf storing this point
            if n == 1:
                self.pointValue = P[0]
            else:
                # else if depth is even
                #     then Split P into two subsets with a vertical line l through the
                #         median x-coordinate of the points in P. Let P1 be the set of
                #         points to the left of l or on l, and let P2 be the set of points
                #         to the right of l.
                # else 
                #     then Split P into two subsets with a horizontal line l through
                #     the median y-coordinate of the points in P. Let P1 be the
                #     set of points below l or on l, and let P2 be the set of points
                #     above l.
                middlePoint = n // 2
                P.sort(key = lambda x: x[depth])
                depth = (depth + 1) % len(P[0])

                # vleft <- BuildKdTree(P1, depth+1)
                # vright <- BuildKdTree(P2, depth+1)
                # Create a node v storing l, make vleft the left child of v, and make
                # vright the right child of v.
                self.leftChild = kdTree(P[:middlePoint], depth)
                self.rightChild = kdTree(P[middlePoint:], depth)
                self.lineValue = P[middlePoint][depth]

    def knnSearch(self, testPoint, k = 1):
        # for each point
        #     start at the root
        #     traverse the tree to the section where the new point belongs
        if (self.leftChild and self.rightChild) != None:
            if testPoint[self.depth] < self.lineValue:
                self.leftChild.knnSearch(testPoint, k)
                
                # check if there could be yet better points on the other side
                # if there could be, go down again on the other side. Otherwise,
                # go up another level
                circleRadius, worstEstimate = kdTree.pq.pop()
                circleRadius = -1 * circleRadius

                if (kdTree.pq.size() < k):
                    kdTree.pq.push(worstEstimate, -1*circleRadius)
                    self.rightChild.knnSearch(testPoint, k)
                elif ((kdTree.pq.size() == k) and (abs(self.lineValue - testPoint[self.depth])\
                        <= circleRadius)):
                    kdTree.pq.push(worstEstimate, -1*circleRadius)
                    self.rightChild.knnSearch(testPoint, k)
            else:
                self.rightChild.knnSearch(testPoint, k)
                
                # check if there could be yet better points on the other side
                # if there could be, go down again on the other side. Otherwise,
                # go up another level
                circleRadius, worstEstimate = kdTree.pq.pop()
                circleRadius = -1 * circleRadius

                if (kdTree.pq.size() < k):
                    kdTree.pq.push(worstEstimate, -1*circleRadius)
                    self.leftChild.knnSearch(testPoint, k)
                elif ((kdTree.pq.size() == k) and (abs(self.lineValue - testPoint[self.depth])\
                        <= circleRadius)):
                    kdTree.pq.push(worstEstimate, -1*circleRadius)
                    self.leftChild.knnSearch(testPoint, k)
        else:
            # found a leaf; store it's point
            deltaX = testPoint[0] - self.pointValue[0]
            deltaY = testPoint[1] - self.pointValue[1]
            distance = math.sqrt((deltaX ** 2) + (deltaY ** 2))

            if (kdTree.pq.size() < k):
                kdTree.pq.push(self.pointValue, -1*distance)
            elif (kdTree.pq.size() == k):
                distance2, worstEstimate = kdTree.pq.pop()
                distance2 = -1 * distance2

                if (distance2 < distance):
                    kdTree.pq.push(worstEstimate, -1*distance2)
                else:
                    kdTree.pq.push(self.pointValue, -1*distance)

class xNN():

    def __init__(self, trainingP, testingP):
        self.trainingP = trainingP
        self.testingP = testingP
        
        P = list(self.trainingP.keys())
        self.tree = kdTree(P)
        
        self.neighbors = {}
        self.predictions = {}

        self.precision = None
        self.recall = None
        self.accuracy = None

    def classify(self, x = 1):
        for testPoint, _ in self.testingP.items():
            self.tree.knnSearch(testPoint, x)
            
            aux1 = []
            aux2 = []
            while not self.tree.pq.isEmpty():
                _, closestPoint = self.tree.pq.pop()
                aux1.insert(0, closestPoint)
                aux2.insert(0, self.trainingP[closestPoint])
            
            self.neighbors[testPoint] = aux1
            self.predictions[testPoint] = max(aux2, key=aux2.count)

    def getStatistics(self):
        tPositive = 0
        tNegative = 0
        fPositive = 0
        fNegative = 0

        for testPoint, actualClass in self.testingP.items():
            predictedClass = self.predictions[testPoint]

            if (actualClass == 'positive') and (predictedClass == 'positive'):
                tPositive += 1
            elif (actualClass == 'positive') and (predictedClass == 'negative'):
                fNegative += 1
            elif (actualClass == 'negative') and (predictedClass == 'positive'):
                fPositive += 1
            elif (actualClass == 'negative') and (predictedClass == 'negative'):
                tNegative += 1
            

        self.precision = tPositive / (tPositive + fPositive)
        self.recall = tPositive / (tPositive + fNegative)
        self.accuracy = (tPositive + tNegative) / (tPositive + tNegative +\
            fPositive + fNegative)

trainingP = {}
testingP = {}

for line in sys.stdin:
    l = line.split(',')

    pointClass = l.pop()
    l = [float(item) for item in l]
    point = tuple(l)

    if (pointClass == '1.0\n'):
        pointClass = 'positive'
    elif (pointClass == '-1.0\n'):
        pointClass = 'negative'
    elif (pointClass == '1\n'):
        pointClass = 'positive'
    elif (pointClass == '2\n'):
        pointClass = 'negative'
    elif (pointClass == '0\n'):
        pointClass = 'negative'
    elif (pointClass == ' 1\n'):
        pointClass = 'positive'
    elif (pointClass == ' 0\n'):
        pointClass = 'negative'

    if (random.random() < 0.7):
        trainingP[point] = pointClass
    else:
        testingP[point] = pointClass

x = 1000
startTime = time.perf_counter()
classifier = xNN(trainingP, testingP)
classifier.classify(x)
classifier.getStatistics()
endTime = time.perf_counter()

print(f"Looking for {x} nearest neighbors. There are {len(trainingP)}\
points in training set and {len(testingP)} points in testing set")
print(f"Time: {endTime - startTime:0.4f} seconds for {len(list(trainingP.keys())[0])} dimensional data")
print(f"Precision: {classifier.precision}")
print(f"Recall: {classifier.recall}")
print(f"Acuracy: {classifier.accuracy}")
