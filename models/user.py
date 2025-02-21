from abc import ABC, abstractmethod

class User(ABC):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @abstractmethod
    def get_dashboard(self):
        pass

class Customer(User):
    def get_dashboard(self):
        return "dashboard.html"

class Admin(User):
    def get_dashboard(self):
        return "admin_dashboard.html"

    def add_car(self, car_list, car):
        car_list.append(car)

    def remove_car(self, car_list, car_id):
        car_list[:] = [car for car in car_list if car.id != car_id]