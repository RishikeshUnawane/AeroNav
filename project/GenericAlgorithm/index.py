from math import cos, asin, sqrt, pi
from GenericAlgorithm.city import City
from GenericAlgorithm.algorithm import geneticAlgorithm

def findOptimizedPath(customers,distributor,vehicles):
    cityList = []
    print(distributor)
    cityList.append(City( distributor['x_cord'], distributor['y_cord']))
    
    for customer in customers:
        cityList.append(City( customer['x_cord'], customer['y_cord']))
    
    depot = [cityList[0].x, cityList[0].y]

    bestestRoute = geneticAlgorithm(cityList, popSize=100, eliteSize=20, mutationRate=0.01, generations=200, numOfDromes=int(vehicles))

    routesCords = []

    for vehicleRoute in bestestRoute:
        vehicleRoutesCords = []
        if len(vehicleRoute) != 1:
            for cord in vehicleRoute:
                cordinates = [cord.x,cord.y]
                vehicleRoutesCords.append(cordinates)
            vehicleRoutesCords.append(vehicleRoutesCords[0])
            routesCords.append(vehicleRoutesCords)

    return routesCords


def distance(lat1, lon1, lat2, lon2):
    r = 6371 # km
    p = pi / 180

    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return 2 * r * asin(sqrt(a))

def calculateDistance(routesCords):
    drone = 1
    data = []
    for vehicleRoute in routesCords:
      totalDistance = 0
      for i in range(1,len(vehicleRoute)):
        totalDistance += distance(vehicleRoute[i][0], vehicleRoute[i][1], vehicleRoute[i-1][0], vehicleRoute[i-1][1])
      data.append(totalDistance)
      drone += 1
    return data

def calculateDistanceForCustomer(routesCords, x, y):
    for vehicleRoute in routesCords:
      for cordinates in vehicleRoute:
          if cordinates[0]==x and cordinates[1]==y:
              totalDistance = 0
              for i in range(1,len(vehicleRoute)):
                  totalDistance += distance(vehicleRoute[i][0], vehicleRoute[i][1], vehicleRoute[i-1][0], vehicleRoute[i-1][1])
                  if(vehicleRoute[i][0]==x and vehicleRoute[i][1]==y):
                    return totalDistance