class Car:
    def __init__(self, car_id, model, year, image, color, mileage, accessories):
        self.car_id = car_id
        self.model = model
        self.year = year
        self.image = image
        self.color = color
        self.mileage = mileage
        self.accessories = accessories
        self.is_available = True