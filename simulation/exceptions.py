class CollisionErrorException(Exception):
    def __init__(self):
        super().__init__("Dos vehiculos se han chocado")