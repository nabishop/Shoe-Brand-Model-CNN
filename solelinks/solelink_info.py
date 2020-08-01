class ShoeInfo:
    def __init__(self, name, release_date):
        self.name = name
        self.release_date = release_date

    def __str__(self):
        return "Name: " + self.name + " Date: " + self.release_date
