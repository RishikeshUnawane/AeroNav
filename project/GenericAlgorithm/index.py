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