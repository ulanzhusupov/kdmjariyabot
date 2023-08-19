

class Ad:


    def __init__(self, category, photo, description, username):
        self.category = category
        self.photo = photo
        self.description = description
        self.username = username

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        self._category = value

    @property
    def photo(self):
        return self._photo

    @photo.setter
    def photo(self, value):
        self._photo = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value
    
    