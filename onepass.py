

class Wellford:

    def __init__(self) -> None:
        self.x_bar:float = 0.0
        self.v:float = 0.0
        self.i:int = 0

    def sample(self, val) -> None:
        self.i += 1

        self.v = self.v + ((self.i-1)/self.i) * ((val - self.x_bar)**2)
        self.x_bar = self.x_bar + (1/self.i)*(val - self.x_bar)

    def get_v(self) -> float:
        return self.v/self.i
    
    def get_x_bar(self) -> float:
        return self.x_bar
        

class Wellford_time:

    def __init__(self) -> None:
        self.x_bar:float = 0.0
        self.v:float = 0.0
        self.time = 0

    def sample(self, t, val) -> None:
        delta = t - self.time

        self.v = self.v + ((delta*self.time)/t) * ((val - self.x_bar)**2)
        self.x_bar = self.x_bar + (delta/t)*(val - self.x_bar)
        

        self.time = t

    def get_v(self) -> float:
        return self.v/self.time
    
    def get_x_bar(self) -> float:
        return self.x_bar
