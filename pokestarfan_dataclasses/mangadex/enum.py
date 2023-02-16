import enum


class Status(enum.IntEnum):
    Ongoing = 1
    Completed = 2
    Cancelled = 3
    Hiatus = 4


class Demographic(enum.IntEnum):
    NONE = 0
    Shounen = 1
    Shoujo = 2
    Seinen = 3
    Josei = 4


class Relation(enum.IntEnum):
    Prequel = 1
    Sequel = 2
    Adapted_From = Adapted = 3
    Spin_Off = Spin = 4
    Side_Story = Side = 5
    Main_Story = Main = 6
    Alternate_Story = Alternate = 7
    Doujinshi = 8
    Based_on = Based = 9
    Coloured = Colored = 10
    Monochrome = 11
    Shared_Universe = Shared = 12
    Same_Franchise = Same = 13
    Pre_Serialization = Pre = 14
    Serialization = 15

    @property
    def formatted_name(self):
        if int(self) == 4:
            return "Spin-Off"
        else:
            return self.name.replace("_", " ")


class Following(enum.IntEnum):
    Not_Following = All = 0
    Reading = 1
    Completed = 2
    On_Hold = 3
    Plan_To_Read = 4
    Dropped = 5
    Re_Reading = 6

    @property
    def formatted_name(self):
        if int(self) == 6:
            return "Re-Reading"
        else:
            return self.name.replace("_", " ")
