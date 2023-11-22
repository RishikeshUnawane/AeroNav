from GenericAlgorithm.city import City
from GenericAlgorithm.fitness import Fitness

import random
import operator
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import folium

def createRoute(cityList, numOfDromes):
    #genrate random possible solution (chromosone)
    routes = []
    cityListCopy = cityList.copy()

    depot = cityList[0]
    cityListCopy.remove(depot)

    for _ in range(numOfDromes-1):
        route_size = random.randint(0, len(cityListCopy))
        random.shuffle(cityListCopy)

        current_route = cityListCopy[:route_size]

        for city in current_route:
            cityListCopy.remove(city)

        current_route.insert(0, depot)
        routes.append(current_route)

    current_route = cityListCopy
    current_route.insert(0, depot)
    routes.append(current_route)

    return routes

def initialPopulation(popSize, cityList, numOfDromes):
    #genrate random mutiple chromosones (possible solution)
    population = []

    for i in range(0, popSize):
        population.append(createRoute(cityList, numOfDromes))
    return population

def rankRoutes(population):
    fitnessResults = {}
    for i in range(0,len(population)):
        fitnessResults[i] = Fitness(population[i]).routeFitness()
    return sorted(fitnessResults.items(), key = operator.itemgetter(1), reverse = True)

#Remaining:
# popRanked is ranked population
def selection(popRanked, eliteSize):
    selectionResults = []
    df = pd.DataFrame(np.array(popRanked, dtype=object), columns=["Index","Fitness"])  # dtype = object argument added , as the method had something deprecated
    df['cum_sum'] = df.Fitness.cumsum()
    df['cum_perc'] = 100*df.cum_sum/df.Fitness.sum()

    # print(df) # added by rishikesh for testing

    for i in range(0, eliteSize):
        selectionResults.append(popRanked[i][0])
    for i in range(0, len(popRanked) - eliteSize):
        pick = 100*random.random()
        for i in range(0, len(popRanked)):
            if pick <= df.iat[i,3]:
                selectionResults.append(popRanked[i][0])
                break
    return selectionResults

def matingPool(population, selectionResults):
    matingpool = []
    for i in range(0, len(selectionResults)):
        index = selectionResults[i]
        matingpool.append(population[index])
    return matingpool

def breed(parent1, parent2):
    child = []
    childP1 = []
    childP2 = []

    geneA = int(random.random() * len(parent1))
    geneB = int(random.random() * len(parent1))

    startGene = min(geneA, geneB)
    endGene = max(geneA, geneB)

    for i in range(startGene, endGene):
        childP1.append(parent1[i])

      # [[1,2],[1,3,],[1,4], [1,6]]
      # [[1,4], [1,6],[1,2],[1,3]]
      # [1,2],[1,3,][1,2],[1,3,]

    childP2 = [item for item in parent2 if item not in childP1]

    child = childP1 + childP2
    newChild = []
    for i in range(0, len(child)):
      if(len(child[i]) != 1):
        newChild.append(child[i])
    # print(child)
    return newChild

def breedPopulation(matingpool, eliteSize):
    children = []
    length = len(matingpool) - eliteSize
    pool = random.sample(matingpool, len(matingpool)) #suffle

    for i in range(0,eliteSize):
        children.append(matingpool[i])

    for i in range(0, length):
        child = breed(pool[i], pool[len(matingpool)-i-1])
        children.append(child)
    return children

def mutate(individual, mutationRate):
    for swapped in range(len(individual)):
        if(random.random() < mutationRate):
            swapWith = int(random.random() * len(individual))

            city1 = individual[swapped]
            city2 = individual[swapWith]

            individual[swapped] = city2
            individual[swapWith] = city1
    return individual

def mutatePopulation(population, mutationRate):
    mutatedPop = []

    for ind in range(0, len(population)):
        mutatedInd = mutate(population[ind], mutationRate)
        mutatedPop.append(mutatedInd)
    return mutatedPop

def nextGeneration(currentGen, eliteSize, mutationRate):
    popRanked = rankRoutes(currentGen)
    selectionResults = selection(popRanked, eliteSize)
    matingpool = matingPool(currentGen, selectionResults)
    children = breedPopulation(matingpool, eliteSize)
    nextGeneration = mutatePopulation(children, mutationRate)
    return nextGeneration

def geneticAlgorithm(cityList, popSize, eliteSize, mutationRate, generations, numOfDromes):
    pop = initialPopulation(popSize, cityList, numOfDromes)
    print("Initial distance: " + str(1 / rankRoutes(pop)[-1][1]))

    for i in range(0, generations):
        pop = nextGeneration(pop, eliteSize, mutationRate)

    print("Final distance: " + str(1 / rankRoutes(pop)[0][1]))
    bestRouteIndex = rankRoutes(pop)[0][0]
    bestRoute = pop[bestRouteIndex]
    # print("Final dist: " + str(1/ rankRoutes(bestRoute)[0][1]))
    numberOfDrones = 0
    for i in range(0, len(bestRoute)):
      if(len(bestRoute[i]) > 1):
        numberOfDrones += 1
    print("Number of drones required: " + str(numberOfDrones))
    return bestRoute


# cityList = []

# cityList.append(City( 18.46, 73.86))
# cityList.append(City( 18.88, 73.96))
# cityList.append(City( 18.42, 73.11))
# cityList.append(City( 18.55, 73.32))
# # cityList.append(City( 18.92, 73.90))
# # cityList.append(City( 18.51, 73.74))
# # cityList.append(City( 18.33, 73.28))
# # cityList.append(City( 18.76, 73.99))
# # cityList.append(City( 18.22, 73.01))
# # cityList.append(City( 18.08, 73.11))
# # cityList.append(City( 18.80, 73.10))
# # cityList.append(City( 18.75, 73.18))

# # for i in range(0,25):
# #     cityList.append(City(x=int(random.random() * 10 - 5), y=int(random.random() * 10 - 5)))

# depot = [cityList[0].x, cityList[0].y]

# bestestRoute = geneticAlgorithm(cityList, popSize=100, eliteSize=20, mutationRate=0.01, generations=200, numOfDromes=5)
# # bestestRoute = createRoute(cityList,4)

# print(bestestRoute)
# routesCords = []

# for vehicleRoute in bestestRoute:
#     vehicleRoutesCords = []
#     if len(vehicleRoute) != 1:
#         for cord in vehicleRoute:
#             cordinates = [cord.x,cord.y]
#             vehicleRoutesCords.append(cordinates)
#         vehicleRoutesCords.append(vehicleRoutesCords[0])
#         routesCords.append(vehicleRoutesCords)


# map = folium.Map(location=depot, zoom_start=13)
# colors = ['blue','red','green','orange','violet','black']

# i=0
# for vehicleRoute in routesCords:
#     print(vehicleRoute)
#     route = folium.PolyLine(locations=vehicleRoute, color=colors[i])
#     i += 1
#     for each in vehicleRoute:
#       folium.Marker(each).add_to(map)
#     route.add_to(map)