

class Player(object):
    def __init__(self, info=None):
        if info is None:
            self.info = {
            "max bullets": 5,
            "orange_ducks": [],
            "level": 1,
            "scores": {}, 
            "stars": {}}
        else:
            self.info = info
        
    def save(self):
        p = os.path.join("resources", "player.json")
        with open(p, "w") as f:
            json.dump(self.info, f)

    def add_stars(self, level, num_stars):
        if num_stars > self.info["stars"][level]:
            self.info["stars"][level] = num_stars
        
    def add_score(self, level, score):
        if score > self.info["scores"][level]:
            self.info["scores"][level] = score
            