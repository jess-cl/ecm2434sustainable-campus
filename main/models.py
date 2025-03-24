from django.db import models
import datetime

# Create your models here.
class UserInventory(models.Model):
    user = models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE, primary_key=True)
    # stores the number of each resource the player has
    paper = models.IntegerField(default=0)
    plastic = models.IntegerField(default=0)
    compost = models.IntegerField(default=0)
    recycled_paper = models.IntegerField(default=0)
    recycled_plastic = models.IntegerField(default=0)
    recycled_compost = models.IntegerField(default=0)
    tree_guard = models.IntegerField(default=0)
    rain_catcher = models.IntegerField(default=0)
    fertilizer = models.IntegerField(default=0)
    oak = models.IntegerField(default=0)
    birch = models.IntegerField(default=0)
    fir = models.IntegerField(default=0)
    red_campion = models.IntegerField(default=0)
    poppy = models.IntegerField(default=0)
    cotoneaster = models.IntegerField(default=0)
    # stores the markers the user has collected today, will reset when a marker is collected on a different date to last_collected
    collected_markers = models.TextField(default="")
    # stores the date that a marker was last collected
    last_collected = models.TextField(default=str(datetime.date))

    # returns a dictionary that represents the contents of the user's inventory
    def to_dict(self):
        return {"paper" : self.paper,
                "plastic" : self.plastic,
                "compost" : self.compost,
                "recycled_paper" : self.recycled_paper,
                "recycled_plastic" : self.recycled_plastic,
                "recycled_compost" : self.recycled_compost,
                "tree_guard" : self.tree_guard,
                "rain_catcher" : self.rain_catcher,
                "fertilizer" : self.fertilizer,
                "oak" : self.oak,
                "birch" : self.birch,
                "fir" : self.fir,
                "red_campion" : self.red_campion,
                "poppy" : self.poppy,
                "cotoneaster" : self.cotoneaster}

class UserForest(models.Model):
    user = models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE, primary_key=True)
    cells = models.TextField(default = "0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0")
    last_growth_check_date = models.TextField(default=str(datetime.date))
    customisations = models.TextField(default="0,1,2")

class Plant(models.Model):
    requirement_type = models.IntegerField()
    rarity = models.IntegerField()
    plant_name = models.TextField(default="plant")

class UserHighScore(models.Model):
    user = models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE, primary_key=True)
    high_score = models.IntegerField(default=0)

class Customisations(models.Model):
    customisation_type = models.IntegerField()
    primary_colour_code = models.TextField()
    secondary_colour_code = models.TextField()