import yaml
from pathlib import Path

home = str(Path.home())

class Config():
    def __init__(self):
        self.path = F"{str(Path.home())}/.oat.conf"
        self.dict = {}
        try:
            with open(self.path, "r") as stream:
                try:
                    self.dict = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
        except BaseException as err:
            print(err)

    def write(self):
        with open(self.path, "w") as stream:
            try:
                yaml.safe_dump(self.dict, stream)
            except yaml.YAMLError as exc:
                print(exc)
    
    def values(self):
        return self.dict
    
    def set_value(self,key,val):
        self.dict[key] = val

    def get_value(self,key):
        return self.dict[key]
