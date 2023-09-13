class Politician:
    def __init__(
        self, first_name, middle_name, last_name, nickname=None, image_path=None
    ):
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.nickname = nickname
        self.image = image_path
        self.name = self.first_name + " " + self.last_name

    def name_to_regex(self):
        """
        Creates regex expression from name_tuple containing a first, middle and last name
        ans an optional nickname
        """
        regex = r"\b"
        if self.nickname:
            regex += f"(({self.nickname}|{self.first_name})( {self.middle_name})?)?\s+"
        else:
            regex += f"({self.first_name}( {self.middle_name})?)?\s+"

        regex += rf"{self.last_name}\b"
        return regex


DONALD_TRUMP = Politician("Donald", "John", "Trump", "Don")
HILLARY_CLINTON = Politician("Hillary", "Rodham", "Clinton")
JOE_BIDEN = Politician("Joseph", "Robinete", "Biden", "Joe")
