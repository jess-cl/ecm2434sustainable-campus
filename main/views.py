from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from pathlib import Path
from .models import UserForest, UserInventory, Plant, UserHighScore, Customisations
from shop.models import UserBalance
from django.http import HttpResponse, JsonResponse
from random import randint
from django.views.decorators.csrf import csrf_exempt
import datetime
from math import floor

def first_page(request):
    return redirect('accounts:login')

@login_required
def map(request):
    markers = ""
    path = Path(__file__).parent / "../sustainableCampus/static/js/markers.json"
    with path.open() as markerFile:
        for line in markerFile:
            print("JSON FILE LINE: " + line)
            markers += line
    print("markers data: " + markers)
    user_inventory = ""
    try:
        user_inventory = UserInventory.objects.get(user=request.user)
    except UserInventory.DoesNotExist:
        # adds a new record to the table if one does not exist for the user
        user_inventory = UserInventory(user_id = request.user.id)
        user_inventory.save()
    collected = user_inventory.collected_markers
    print("inv: ", user_inventory)
    print("collected markers: ", collected)
    return render(request, "map.html", {"data": markers, "collected" : collected})

@login_required
def forest(request):
    # gets the state of the user's forest saved to the database
    user_forest = ""
    try:
        user_forest = UserForest.objects.get(user=request.user)
    except UserForest.DoesNotExist:
        # adds a new record to the table if one does not exist for the user
        user_forest = UserForest(user_id = request.user.id)
        user_forest.save()
    print("before growth check: " + user_forest.last_growth_check_date)
    check_if_plants_should_grow(user_forest)
    print("after growth check: " + user_forest.last_growth_check_date)
    user_inventory = ""
    try:
        user_inventory = UserInventory.objects.get(user=request.user)
    except UserInventory.DoesNotExist:
        # adds a new record to the table if one does not exist for the user
        user_inventory = UserInventory(user_id = request.user.id)
        user_inventory.save()
    # gets all relevant information from the plants table, allowing it to be used within the view/page
    plant_string = ""
    for plant in Plant.objects.all():
        plant_string += str(plant.id) + "," + str(plant.requirement_type) + "," + str(plant.rarity) + "," + str(plant.plant_name) + ";"
    # converts the contents of the user's inventory to a more useful format to be given to the page
    user_inventory_dict = user_inventory.to_dict()
    print(user_inventory_dict)
    user_inventory_str = ""
    for key in user_inventory_dict.keys():
        user_inventory_str += str(user_inventory_dict[key]) + ","
    print(user_inventory_str)
    # calculates the forest value on page load
    value = calculate_forest_value(user_forest)
    # gets list of all customisation options
    customisation_string = ""
    for record in Customisations.objects.all():
        customisation_string += str(record.id) + "," + str(record.customisation_type) + "," + str(record.primary_colour_code) + "," + str(record.secondary_colour_code) + ";"

    return render(request, "forest.html", {"user_forest" : user_forest.cells, "user_inventory" : user_inventory_str, "plant_list" : plant_string, "forest_value" : value, "customisations" : customisation_string, "selected_customisations" : user_forest.customisations})

@login_required
def check_if_plants_should_grow(forest):
    # get current date
    print("checking if plants should grow")
    curr_date = datetime.datetime.now().isocalendar()
    curr_date = str(curr_date[0]) + "-" + str(curr_date[1]) + "-" + str(curr_date[2])
    print("current date: " + curr_date)
    last_growth_check = forest.last_growth_check_date
    print("last date checked: " + last_growth_check)

    # if the dates don't match, check if any plants need to grow
    if (curr_date != last_growth_check):
        forest_cells = forest.cells.split(";")
        cell_details = []
        new_forest_cells = ""
        for cell in forest_cells:
            cell_details.append(cell.split(","))
        # iterate through each of the cell's details and adjust the values if any of them should grow
        for cell_data in cell_details:
            # if a plant HAS been given the consumable it needs to grow (0 means it doesn't require anything)
            if (cell_data[2] == '0'):
                # only continues growing if it has not reached max growth
                if (int(cell_data[1]) < 2):
                    cell_data[1] = str(int(cell_data[1]) +  1) # increment growth stage
                    cell_data[2] == 1 # resets the value that tracks if the plant has been given the needed consumable
            new_forest_cells += cell_data[0] + "," + cell_data[1] + "," + cell_data[2] + ";" # refroms the forest data as it is stored in the database

        new_forest_cells = new_forest_cells[:-1] # removes the last ; from the string
        forest.cells = new_forest_cells
        forest.last_growth_check_date = curr_date
        forest.save()

@login_required
@csrf_exempt
def claim_blue_marker(request):
    print("blue claimed")
    user_inventory = UserInventory.objects.get(user=request.user)
    # blue markers give paper and sometimes seedlings
    user_inventory.paper += randint(1, 4)
    user_inventory = drop_seedling(user_inventory)
    # update collected markers (needs id of marker)
    if (request.method == 'POST' and 'marker_id' in request.POST):
        marker_id = request.POST['marker_id']
        user_inventory.collected_markers += (marker_id + ",")
        curr_date = datetime.datetime.now().isocalendar()
        print("iso date:", curr_date)
        user_inventory.last_collected = str(curr_date[0]) + "-" + str(curr_date[1]) + "-" + str(curr_date[2])
        print("MARKER CLAIMED AT: " + user_inventory.last_collected)
    else:
        return JsonResponse({"result" : "error when recieving marker id"})
    user_inventory.save()
    return JsonResponse({"result" : 1})

@login_required
@csrf_exempt
def claim_red_marker(request):
    print("red claimed")
    user_inventory = UserInventory.objects.get(user=request.user)
    # red markers give plastic and sometimes seedlings
    user_inventory.plastic += randint(1, 4)
    user_inventory = drop_seedling(user_inventory)
    # update collected markers (needs id of marker)
    if (request.method == 'POST' and 'marker_id' in request.POST):
        marker_id = request.POST['marker_id']
        user_inventory.collected_markers += (marker_id + ",")
        curr_date = datetime.datetime.now().isocalendar()
        print("iso date:", curr_date)
        user_inventory.last_collected = str(curr_date[0]) + "-" + str(curr_date[1]) + "-" + str(curr_date[2])
        print("MARKER CLAIMED AT: " + user_inventory.last_collected)
    else:
        return JsonResponse({"result" : "error when recieving marker id"})
    user_inventory.save()
    return JsonResponse({"result" : 1})

@login_required
@csrf_exempt
def claim_green_marker(request):
    print("green claimed")
    user_inventory = UserInventory.objects.get(user=request.user)
    # green markers give compost and sometimes seedlings
    user_inventory.compost += randint(1, 4)
    user_inventory = drop_seedling(user_inventory)
    # update collected markers (needs id of marker)
    if (request.method == 'POST' and 'marker_id' in request.POST):
        marker_id = request.POST['marker_id']
        user_inventory.collected_markers += (marker_id + ",")
        curr_date = datetime.datetime.now().isocalendar()
        print("iso date:", curr_date)
        user_inventory.last_collected = str(curr_date[0]) + "-" + str(curr_date[1]) + "-" + str(curr_date[2])
        print("MARKER CLAIMED AT: " + user_inventory.last_collected)
    else:
        return JsonResponse({"result" : "error when recieving marker id"})
    user_inventory.save()
    return JsonResponse({"result" : "updated user inventory successfully"})


@login_required
def drop_seedling(inv):
    # sometimes gives a seedling
    if (randint(1, 10) > 5):
        # there are different rarities of sapling
        rarity = 0
        rand_num_rarity = randint(1, 100)
        if (rand_num_rarity > 90):
            rarity = 2
        elif (rand_num_rarity > 75):
            rarity = 1
        # else rarity remains 0
        # plants that can be obtained depend on the rarity
        match rarity:
            case 0:
                # there are three plants in this rarity
                plant_got = randint(0, 2)
                match plant_got:
                    case 0:
                        inv.oak += 1
                    case 1:
                        inv.birch += 1
                    case 2:
                        inv.poppy += 1
            case 1:
                # only two plants in this rarity
                if (randint(0, 1)):
                    inv.fir += 1
                else:
                    inv.red_campion += 1
            case 2:
                inv.cotoneaster += 1
    return inv

@login_required
def update_inv_on_page(request):
    # used in the geolocSystem itself to update the inventory data on the map page when a user collects a marker
    # this prevents them from collecting the same marker multiple times
    inv_data = UserInventory.objects.get(user=request.user)
    collected = inv_data.collected_markers
    # if the date of the last collected marker is not the current date, reset collected markers so they can all be collected again
    if (collected != ""):
        print("LAST COLLECTED: " + inv_data.last_collected)
        curr_date = datetime.datetime.now().isocalendar()
        curr_date = str(curr_date[0]) + "-" + str(curr_date[1]) + "-" + str(curr_date[2])
        print("CURRENT DATE: " + curr_date)
        if (inv_data.last_collected != curr_date):
            print("Resetting collected markers, the date has changed")
            inv_data.collected_markers = ""
            collected = ""
            inv_data.save()
        else:
            print("Collected markers do not need to be reset")

    return JsonResponse({"collected":collected})

@login_required
def update_forest_on_page(request):
    user_forest = UserForest.objects.get(user=request.user)
    forest_value = calculate_forest_value(user_forest)
    print("UPDATE FOREST DATA ON THE PAGE")
    return JsonResponse({"user_forest" : user_forest.cells, "forest_value" : forest_value})

@login_required
def update_inventory_on_forest(request):
    user_inventory = UserInventory.objects.get(user=request.user)
    
    user_inventory_dict = user_inventory.to_dict()
    print(user_inventory_dict)
    user_inventory_str = ""
    for key in user_inventory_dict.keys():
        user_inventory_str += str(user_inventory_dict[key]) + ","
    print("UPDATE INVENTORY ON THE PAGE" + user_inventory_str)
    return JsonResponse({"user_inventory" : user_inventory_str})

@login_required
def calculate_forest_value(forest):
    plant_list = []
    for plant in Plant.objects.all():
        curr_plant_list = [plant.id, plant.requirement_type, plant.rarity, plant.requirement_type]
        plant_list.append(curr_plant_list)
    # gets the details of each cell in the user's forest, used here to calculate the value of the forest
    forest_cells = forest.cells.split(";")
    cell_details = []
    for cell in forest_cells:
        cell_details.append(cell.split(","))
    print(cell_details)
    # value calculation: 
    # iterate over each cell: if there is a plant in a cell +(100 for common, 150 for uncommon, 200 for rare), account for growth stage (seedlings are worth 0 regardless of rarity, mid stage plants are worth half)
    # count how many unique plants are used
    # multiply total by 1.(number of unique plants)
    unique_plants_count = 0
    unique_plants = [] # stores ids of unique plants in the forest
    value = 0
    for cell in cell_details:
        # if cell is empty skip it
        if cell[0] == '0':
            continue
        else:
            cell_val = 0
            growth_stage = cell[1]
            plant_id = cell[0]
            rarity = plant_list[int(plant_id) - 1][2]

            # checks if the plant is (in the cells that have been iterated through already) unique
            if (plant_id not in unique_plants):
                unique_plants_count += 1
                unique_plants.append(plant_id)

            # seedling only contribute to biodiversity, not the value
            if (growth_stage == '0'):
                continue

            # now check rarity and assign base value accordingly
            if (rarity == '2'):
                cell_val = 200
            elif (rarity == '1'):
                cell_val = 150
            else:
                cell_val = 100
            
            # half the value if the plant is in the middle growth stage
            if (growth_stage == '1'):
                cell_val *= 0.5
            
            value += cell_val
    
    # multiplies the value by 1.(number of unique plants)
    value *= (1 + (unique_plants_count/10))

    print("calculated value: " + str(value))
    value = floor(value) # converts to int from float
    return str(value)

@login_required
def get_recycled_count(request):
    user_inv = UserInventory.objects.get(user=request.user)
    recycled_paper = user_inv.recycled_paper
    recycled_plastic = user_inv.recycled_plastic
    recycled_compost = user_inv.recycled_compost
    return JsonResponse({"count_paper" : recycled_paper, "count_plastic" : recycled_plastic, "count_compost" : recycled_compost})

@login_required
@csrf_exempt
def handle_recycling(request):
    user_inv = UserInventory.objects.get(user=request.user)
    if (request.method == 'POST' and 'type' in request.POST):
        recycling_type = request.POST['type']
        match recycling_type:
            case "paper":
                # a paper is recycled; if the user has 5 recycled papers they are automatically
                # turned into a tree guard
                user_inv.paper -= 1
                user_inv.recycled_paper += 1
                if (user_inv.recycled_paper == 5):
                    print("made tree guard")
                    user_inv.tree_guard += 1
                    user_inv.recycled_paper = 0
            case "plastic":
                # works just as paper, but a rain catcher is made instead of a tree guard
                user_inv.plastic -= 1
                user_inv.recycled_plastic += 1
                if (user_inv.recycled_plastic == 5):
                    print("made rain catcher")
                    user_inv.rain_catcher += 1
                    user_inv.recycled_plastic = 0
            case "compost":
                # works just as paper, but fertilizer is made instead of a tree guard
                user_inv.compost -= 1
                user_inv.recycled_compost += 1
                if (user_inv.recycled_compost == 5):
                    print("made fertilizer")
                    user_inv.fertilizer += 1
                    user_inv.recycled_compost = 0
    else:
        return JsonResponse({"result" : "error when recieving recycling data"})
    user_inv.save()
    return JsonResponse({"result" : "database updated to reflect recyled item successfully"})

@login_required
@csrf_exempt
def save_forest(request):
    user_forest = UserForest.objects.get(user=request.user)
    if (request.method == 'POST' and 'user_forest_cells' in request.POST):
        user_forest.cells = request.POST['user_forest_cells']
    else:
        return JsonResponse({"result" : "error when receiving user forest"})
    user_forest.save()
    return JsonResponse({"result" : "updated user forest successfully"})

@login_required
@csrf_exempt
def save_customisations(request):
    user_forest = UserForest.objects.get(user=request.user)
    if (request.method == 'POST' and 'selected_customisations' in request.POST):
        user_forest.customisations = request.POST['selected_customisations']
    else:
        return JsonResponse({"result" : "error when receiving user customisations"})
    user_forest.save()
    return JsonResponse({"result" : "updated user customisations successfully"})

@login_required
def get_plant_list(request):
    plantString = ""
    for plant in Plant.objects.all():
        plantString += plant.id + "," + plant.requirement_type + "," + plant.rarity + "," + plant.plant_name + ";"
    print("plants")
    return JsonResponse({"plant_list" : plantString})

@login_required
@csrf_exempt
def add_tokens(request):
    user_balance = ""
    try:
        user_balance = UserBalance.objects.get(user_id=request.user.id)
    except UserBalance.DoesNotExist:
        # adds a new record to the table if one does not exist for the user
        user_balance = UserBalance(user_id = request.user)
        user_balance.save()
    user_high_score = ""
    try:
        user_high_score = UserHighScore.objects.get(user=request.user)
    except UserHighScore.DoesNotExist:
        # adds a new record to the table if one does not exist for the user
        user_high_score = UserHighScore(user_id = request.user.id)
        user_high_score.save()
    print("previous balance: " + str(user_balance.currency))
    if (request.method == 'POST' and 'number_of_tokens' in request.POST):
        num_tokens = int(request.POST['number_of_tokens'])
        user_balance.currency += num_tokens
        if (num_tokens > user_high_score.high_score):
            print("new high score: " + str(num_tokens))
            user_high_score.high_score = num_tokens
            user_high_score.save()
    else:
        return JsonResponse({"result" : "error when adding tokens to user balance"})
    print("updated balance: " + str(user_balance.currency))
    user_balance.save()
    return JsonResponse({"result" : "updated user balance successfully"})

@login_required
@csrf_exempt
def remove_from_inv(request):
    user_inventory = UserInventory.objects.get(user=request.user)
    print("before decrementing:")
    print("oaks: " + str(user_inventory.oak) + " birch: " + str(user_inventory.birch) + " fir: " + str(user_inventory.fir) + " red campion: " + str(user_inventory.red_campion) + " poppy: " + str(user_inventory.poppy) + " cotoneaster: " + str(user_inventory.cotoneaster))
    if (request.method == 'POST' and 'plant_id' in request.POST):
        plant_id = request.POST['plant_id']
        match str(plant_id):
            case '1':
                user_inventory.oak -= 1
            case '2':
                user_inventory.birch -= 1
            case '3':
                user_inventory.fir -= 1
            case '4':
                user_inventory.red_campion -= 1
            case '5':
                user_inventory.poppy -= 1
            case '6':
                user_inventory.cotoneaster -= 1
        print("after decrementing:")
        print("oaks: " + str(user_inventory.oak) + " birch: " + str(user_inventory.birch) + " fir: " + str(user_inventory.fir) + " red campion: " + str(user_inventory.red_campion) + " poppy: " + str(user_inventory.poppy) + " cotoneaster: " + str(user_inventory.cotoneaster))
        user_inventory.save()
    else:
        return JsonResponse({"result" : "error when removing seedling from user's inventory"})
    return JsonResponse({"result" : "removed seedling from user's inventory successfully"})

@login_required
@csrf_exempt
def use_consumable(request):
    user_inventory = UserInventory.objects.get(user=request.user)
    print("before decrementing:")
    print("tree guards: " + str(user_inventory.tree_guard) + " rain catchers: " + str(user_inventory.rain_catcher) + " fertilizer: " + str(user_inventory.fertilizer))
    if (request.method == 'POST' and 'consumable_id' in request.POST):
        consumable_id = request.POST['consumable_id']
        match str(consumable_id):
            case '0':
                user_inventory.rain_catcher -= 1
            case '1':
                user_inventory.tree_guard -= 1
            case '2':
                user_inventory.fertilizer -= 1
        print("after decrementing:")
        print("tree guards: " + str(user_inventory.tree_guard) + " rain catchers: " + str(user_inventory.rain_catcher) + " fertilizer: " + str(user_inventory.fertilizer))
        user_inventory.save()
    else:
        return JsonResponse({"result" : "error when removing consumable from user's inventory"})
    return JsonResponse({"result" : "removed consumable from user's inventory successfully"})