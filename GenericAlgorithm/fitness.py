class Fitness:
    def __init__(self, routes):
        #each route in routes represent sequence of cities followed by each drone
        self.routes = routes
        self.maxTime = 0
        self.totalDistance = 0
        self.fitness= 0.0
        self.droneVelocity = 40 #TODO: fix velocity

    def routeDistance(self, route):
        #Cal total distance of route
        pathDistance = 0
        for i in range(0, len(route)):
            fromCity = route[i]
            toCity = None
            if i + 1 < len(route):
                toCity = route[i + 1]
            else:
                toCity = route[0]
            pathDistance += fromCity.distance(toCity)
        return pathDistance

    def routeTime(self,distance):
      return distance/self.droneVelocity

    def routeFitness(self):
        #finds route (trip) which take max time
        for route in self.routes:
            distance = self.routeDistance(route)
            # print(route)
            # print(distance)
            self.maxTime = max(self.maxTime, self.routeTime(distance))
            self.totalDistance += distance

        if self.fitness == 0:
            if self.totalDistance!=0:
                self.fitness = 1 / float(self.totalDistance)
            else:
                self.fitness = 1

        return self.fitness