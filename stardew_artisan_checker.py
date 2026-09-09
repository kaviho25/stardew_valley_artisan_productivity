"""
Stardew Valley Artisan Best Value Checker

Author: Katie Viola
Start Date: 8/26/26
End Date: 9/05/26
"""

### Load in files
with open("animal_products_original.csv") as animal_products_full:
    next(animal_products_full)
    animal_products = animal_products_full.readlines()

with open("keg_productivity_original.csv") as keg_productivity_full:
    next(keg_productivity_full)
    keg_productivity = keg_productivity_full.readlines()

with open("preserves_jar_productivity_original.csv") as preserves_jar_productivity_full:
    next(preserves_jar_productivity_full)
    preserves_jar_productivity = preserves_jar_productivity_full.readlines()

def find_row(master_list, item, quality):
    # Search through every row we've made so far
    for row in master_list:
        if row[0] == item and row[1] == quality:
            return row  # found it - hand back the actual row (not a copy)
    return None  # looped through everything, never found a match

def add_or_update_row(master_list, item, quality, base_price, index, price):
    row = find_row(master_list, item, quality)

    if row is None:
        new_row = [item, quality, base_price, None, None, None, None, None, None, None, None]
        new_row[index] = price
        master_list.append(new_row)
    else:
        if row[index] is None:      # <-- new check
            row[index] = price
        # else: slot already filled - this is a cask-upgrade duplicate, skip it

def get_machine_index(processed_item_name):
    if "Mayonnaise" in processed_item_name:
        return 8   # mayonnaise machine
    elif "Cheese" in processed_item_name:
        return 7   # cheese press
    elif "Cloth" in processed_item_name:
        return 9  # loom
    elif "Oil" in processed_item_name:
        return 5   # oil maker
    else:
        return None 

def clean_part(name):
    if "[" in name:
        name = name.split("[")[0]
    if "with" in name:
        name = name.split("with")[0]
    return name.strip()

def get_machine_name(i):
    machine_names = {
        2: "Item",
        3: "Keg",
        4: "Preserves Jar",
        5: "Oil Maker",
        6: "Dehydrator",
        7: "Cheese Press",
        8: "Mayonnaise Machine",
        9: "Loom",
        10: "Fish Smoker"
    }
    return machine_names[i]

def find_artisan_output(item):
    outputs = []
    for entry in artisan_recipes:
        output_name = entry[0]
        ingredients = entry[1]
        if item in ingredients:
            outputs.append(output_name)
    return outputs

def without(item_list, excluded_items):
    new_list = item_list.copy()
    for excluded_item in excluded_items:
        new_list.remove(excluded_item)
    return new_list

def find_in_recipe(item):
    recipes_found = []
    for recipe in recipes:
        name = recipe[0]
        ingredients = recipe[1]
        for ingredient in ingredients:
            check_item = item
            if ingredient[0] == "Any Fish" and item in fish:
                check_item = "Any Fish"
            if ingredient[0] == check_item:
                recipes_found.append(recipe)
                break
    return recipes_found

def find_gifts(item):
    lovers = []
    likers = []
    neutralers = []
    for villager in villagers_gifts:
        name = villager[0]
        birthday = villager[1]
        entry = f"{name} {birthday}"
        loves = villager[2]
        likes = villager[3]
        neutrals = villager[4]
        dislikes = villager[5]
        hates = villager[6]
        if name == "Sandy":
            if item == "Milk":
                if "Goat" in interest_item:
                    likers.append(entry)
                else:
                    neutralers.append(entry)
            continue
        if item in loves:
            lovers.append(entry)
        elif item in likes:
            likers.append(entry)
        elif item in neutrals:
            neutralers.append(entry)
        elif item not in dislikes and item not in hates:
            if item in universal_loves:
                lovers.append(entry)
            elif item in universal_likes:
                likers.append(entry)
            elif item in universal_neutrals:
                neutralers.append(entry)
    return lovers, likers, neutralers

"""
Organize into master list

0  item
1  quality
2  base price
3  keg price
4  preserves jar price
5  oil maker price
6  dehydrator price
7  cheese press price
8  mayonnaise machine price
9  loom price

"""

master_list = []

recipes = [
    ["Fried Egg", [["Egg", 1]]],
    ["Omelet", [["Egg", 1], ["Milk", 1]]],
    ["Salad", [["Leek", 1], ["Dandelion", 1], ["Vinegar", 1]]],
    ["Cheese Cauliflower", [["Cauliflower", 1], ["Cheese", 1]]],
    ["Baked Fish", [["Sunfish", 1], ["Bream", 1], ["Wheat Flour", 1]]],
    ["Parsnip Soup", [["Parsnip", 1], ["Milk", 1], ["Vinegar", 1]]],
    ["Vegetable Medley", [["Tomato", 1], ["Beet", 1]]],
    ["Complete Breakfast", [["Fried Egg", 1], ["Milk", 1], ["Hashbrowns", 1], ["Pancakes", 1]]],
    ["Fried Calamari", [["Squid", 1], ["Wheat Flour", 1], ["Oil", 1]]],
    ["Strange Bun", [["Wheat Flour", 1], ["Periwinkle", 1], ["Void Mayonnaise", 1]]],
    ["Lucky Lunch", [["Sea Cucumber", 1], ["Tortilla", 1], ["Blue Jazz", 1]]],
    ["Fried Mushroom", [["Common Mushroom", 1], ["Morel", 1], ["Oil", 1]]],
    ["Pizza", [["Wheat Flour", 1], ["Tomato", 1], ["Cheese", 1]]],
    ["Bean Hotpot", [["Green Bean", 2]]],
    ["Glazed Yams", [["Yam", 1], ["Sugar", 1]]],
    ["Carp Surprise", [["Carp", 4]]],
    ["Hashbrowns", [["Potato", 1], ["Oil", 1]]],
    ["Pancakes", [["Wheat Flour", 1], ["Egg", 1]]],
    ["Salmon Dinner", [["Salmon", 1], ["Amaranth", 1], ["Kale", 1]]],
    ["Fish Taco", [["Tuna", 1], ["Tortilla", 1], ["Red Cabbage", 1], ["Mayonnaise", 1]]],
    ["Crispy Bass", [["Largemouth Bass", 1], ["Wheat Flour", 1], ["Oil", 1]]],
    ["Pepper Poppers", [["Hot Pepper", 1], ["Cheese", 1]]],
    ["Bread", [["Wheat Flour", 1]]],
    ["Tom Kha Soup", [["Coconut", 1], ["Shrimp", 1], ["Common Mushroom", 1]]],
    ["Trout Soup", [["Rainbow Trout", 1], ["Green Algae", 1]]],
    ["Chocolate Cake", [["Wheat Flour", 1], ["Sugar", 1], ["Egg", 1]]],
    ["Pink Cake", [["Melon", 1], ["Wheat Flour", 1], ["Sugar", 1], ["Egg", 1]]],
    ["Rhubarb Pie", [["Rhubarb", 1], ["Wheat Flour", 1], ["Sugar", 1]]],
    ["Cookie", [["Wheat Flour", 1], ["Sugar", 1], ["Egg", 1]]],
    ["Spaghetti", [["Wheat Flour", 1], ["Tomato", 1]]],
    ["Fried Eel", [["Eel", 1], ["Oil", 1]]],
    ["Spicy Eel", [["Eel", 1], ["Hot Pepper", 1]]],
    ["Sashimi", [["Any Fish", 1]]],
    ["Maki Roll", [["Any Fish", 1], ["Seaweed", 1], ["Rice", 1]]],
    ["Tortilla", [["Corn", 1]]],
    ["Red Plate", [["Red Cabbage", 1], ["Radish", 1]]],
    ["Eggplant Parmesan", [["Eggplant", 1], ["Tomato", 1]]],
    ["Rice Pudding", [["Milk", 1], ["Sugar", 1], ["Rice", 1]]],
    ["Ice Cream", [["Milk", 1], ["Sugar", 1]]],
    ["Blueberry Tart", [["Blueberry", 1], ["Wheat Flour", 1], ["Sugar", 1], ["Egg", 1]]],
    ["Autumn's Bounty", [["Yam", 1], ["Pumpkin", 1]]],
    ["Pumpkin Soup", [["Pumpkin", 1], ["Milk", 1]]],
    ["Super Meal", [["Bok Choy", 1], ["Cranberries", 1], ["Artichoke", 1]]],
    ["Cranberry Sauce", [["Cranberries", 1], ["Sugar", 1]]],
    ["Stuffing", [["Bread", 1], ["Cranberries", 1], ["Hazelnut", 1]]],
    ["Farmer's Lunch", [["Omelet", 1], ["Parsnip", 1]]],
    ["Survival Burger", [["Bread", 1], ["Cave Carrot", 1], ["Eggplant", 1]]],
    ["Dish O' The Sea", [["Sardine", 2], ["Hashbrowns", 1]]],
    ["Miner's Treat", [["Cave Carrot", 2], ["Sugar", 1], ["Milk", 1]]],
    ["Roots Platter", [["Cave Carrot", 1], ["Winter Root", 1]]],
    ["Triple Shot Espresso", [["Coffee", 3]]],
    ["Seafoam Pudding", [["Flounder", 1], ["Midnight Carp", 1], ["Squid Ink", 1]]],
    ["Algae Soup", [["Green Algae", 4]]],
    ["Pale Broth", [["White Algae", 2]]],
    ["Plum Pudding", [["Wild Plum", 2], ["Wheat Flour", 1], ["Sugar", 1]]],
    ["Artichoke Dip", [["Artichoke", 1], ["Milk", 1]]],
    ["Stir Fry", [["Cave Carrot", 1], ["Common Mushroom", 1], ["Kale", 1], ["Oil", 1]]],
    ["Roasted Hazelnuts", [["Hazelnut", 3]]],
    ["Pumpkin Pie", [["Pumpkin", 1], ["Wheat Flour", 1], ["Milk", 1], ["Sugar", 1]]],
    ["Radish Salad", [["Oil", 1], ["Vinegar", 1], ["Radish", 1]]],
    ["Fruit Salad", [["Blueberry", 1], ["Melon", 1], ["Apricot", 1]]],
    ["Blackberry Cobbler", [["Blackberry", 2], ["Sugar", 1], ["Wheat Flour", 1]]],
    ["Cranberry Candy", [["Cranberries", 1], ["Apple", 1], ["Sugar", 1]]],
    ["Bruschetta", [["Bread", 1], ["Oil", 1], ["Tomato", 1]]],
    ["Coleslaw", [["Red Cabbage", 1], ["Vinegar", 1], ["Mayonnaise", 1]]],
    ["Fiddlehead Risotto", [["Oil", 1], ["Fiddlehead Fern", 1], ["Garlic", 1]]],
    ["Poppyseed Muffin", [["Poppy", 1], ["Wheat Flour", 1], ["Sugar", 1]]],
    ["Chowder", [["Clam", 1], ["Milk", 1]]],
    ["Fish Stew", [["Crayfish", 1], ["Mussel", 1], ["Periwinkle", 1], ["Tomato", 1]]],
    ["Escargot", [["Snail", 1], ["Garlic", 1]]],
    ["Lobster Bisque", [["Lobster", 1], ["Milk", 1]]],
    ["Maple Bar", [["Maple Syrup", 1], ["Sugar", 1], ["Wheat Flour", 1]]],
    ["Crab Cakes", [["Crab", 1], ["Wheat Flour", 1], ["Egg", 1], ["Oil", 1]]],
    ["Shrimp Cocktail", [["Tomato", 1], ["Shrimp", 1], ["Wild Horseradish", 1]]],
    ["Ginger Ale", [["Ginger", 3], ["Sugar", 1]]],
    ["Banana Pudding", [["Banana", 1], ["Milk", 1], ["Sugar", 1]]],
    ["Mango Sticky Rice", [["Mango", 1], ["Coconut", 1], ["Rice", 1]]],
    ["Poi", [["Taro Root", 4]]],
    ["Tropical Curry", [["Coconut", 1], ["Pineapple", 1], ["Hot Pepper", 1]]],
    ["Squid Ink Ravioli", [["Squid Ink", 1], ["Wheat Flour", 1], ["Tomato", 1]]],
    ["Moss Soup", [["Moss", 20]]],
]

eggs = [
    "Egg", "Brown Egg", "Large Egg", "Large Brown Egg", "Duck Egg", "Golden Egg", "Ostrich Egg", "Void Egg"
    ]
mushrooms = [
    "Chanterelle", "Common Mushroom", "Magma Cap", "Morel", "Purple Mushroom", "Red Mushroom"
    ]
fruit_tree_fruit = [
    "Apple", "Apricot", "Cherry", "Orange", "Peach", "Pomegranate"
                    ]
artisan_goods = [
    "Honey", "Wine", "Pale Ale", "Beer", "Mead", "Cheese", "Goat Cheese", "Vinegar", "Coffee", "Green Tea", "Juice", "Cloth", "Mayonnaise", "Duck Mayonnaise", "Void Mayonnaise", "Dinosaur Mayonnaise", "Truffle Oil", "Oil", "Pickles", "Jelly", "Caviar", "Aged Roe", "Dried Mushrooms", "Dried Fruit", "Raisins", "Smoked Fish"
    ]
cooking_items = [
    "Fried Egg", "Omelet", "Salad", "Cheese Cauliflower", "Baked Fish", "Parsnip Soup", "Vegetable Medley", "Complete Breakfast", "Fried Calamari", "Strange Bun", "Lucky Lunch", "Fried Mushroom", "Pizza", "Bean Hotpot", "Glazed Yams", "Carp Surprise", "Hashbrowns", "Pancakes", "Salmon Dinner", "Fish Taco", "Crispy Bass", "Pepper Poppers", "Bread", "Tom Kha Soup", "Trout Soup", "Chocolate Cake", "Pink Cake", "Rhubarb Pie", "Cookie", "Spaghetti", "Fried Eel", "Spicy Eel", "Sashimi", "Maki Roll", "Tortilla", "Red Plate", "Eggplant Parmesan", "Rice Pudding", "Ice Cream", "Blueberry Tart", "Autumn's Bounty", "Pumpkin Soup", "Super Meal", "Cranberry Sauce", "Stuffing", "Farmer's Lunch", "Survival Burger", "Dish O' The Sea", "Miner's Treat", "Roots Platter", "Triple Shot Espresso", "Seafoam Pudding", "Algae Soup", "Pale Broth", "Plum Pudding", "Artichoke Dip", "Stir Fry", "Roasted Hazelnuts", "Pumpkin Pie", "Radish Salad", "Fruit Salad", "Blackberry Cobbler", "Cranberry Candy", "Bruschetta", "Coleslaw", "Fiddlehead Risotto", "Poppyseed Muffin", "Chowder", "Fish Stew", "Escargot", "Lobster Bisque", "Maple Bar", "Crab Cakes", "Shrimp Cocktail", "Ginger Ale", "Banana Pudding", "Mango Sticky Rice", "Poi", "Tropical Curry", "Squid Ink Ravioli", "Moss Soup"
    ]
flowers = [
    "Sweet Pea", "Crocus", "Tulip", "Blue Jazz", "Summer Spangle", "Poppy", "Sunflower", "Fairy Rose"
    ]
foraged_minerals = [
    "Quartz", "Earth Crystal", "Frozen Tear", "Fire Quartz"
    ]
gems = [
    "Emerald", "Aquamarine", "Ruby", "Amethyst", "Topaz", "Jade", "Diamond", "Prismatic Shard"
    ]
vegetables = [
    "Amaranth", "Artichoke", "Beet", "Bok Choy", "Broccoli", "Carrot", "Cauliflower", "Corn", "Eggplant", "Fiddlehead Fern", "Garlic", "Green Bean", "Hops", "Kale", "Parsnip", "Potato", "Pumpkin", "Radish", "Red Cabbage", "Summer Squash", "Taro Root", "Tea Leaves", "Tomato", "Unmilled Rice", "Wheat", "Yam"
    ]
fruits = [
    "Ancient Fruit", "Apple", "Apricot", "Banana", "Blackberry", "Blueberry", "Cactus Fruit", "Cherry", "Coconut", "Cranberries", "Crystal Fruit", "Grape", "Hot Pepper", "Mango", "Melon", "Orange", "Peach", "Pineapple", "Pomegranate", "Powdermelon", "Qi Fruit", "Rhubarb", "Salmonberry", "Spice Berry", "Starfruit", "Strawberry", "Wild Plum"
    ]
books = [
    "Price Catalogue", "Mapping Cave Systems", "Way Of The Wind pt. 1", "Way Of The Wind pt. 2", "Monster Compendium", "Friendship 101", "Jack Be Nimble, Jack Be Thick", "Woody's Secret", "Raccoon Journal", "Jewels Of The Sea", "Dwarvish Safety Manual", "The Art O' Crabbing", "The Alleyway Buffet", "The Diamond Hunter", "Book of Mysteries", "Horse: The Book", "Treasure Appraisal Guide", "Ol' Slitherlegs", "Animal Catalogue", "Bait And Bobber", "Book Of Stars", "Combat Quarterly", "Mining Monthly", "Stardew Valley Almanac", "Woodcutter's Weekly", "Queen Of Sauce Cookbook"
    ]
fish = [
    "Pufferfish", "Anchovy", "Tuna", "Sardine", "Bream", "Largemouth Bass", "Smallmouth Bass", "Rainbow Trout", "Salmon", "Walleye", "Perch", "Carp", "Catfish", "Pike", "Sunfish", "Red Mullet", "Herring", "Eel", "Octopus", "Red Snapper", "Squid", "Sea Cucumber", "Super Cucumber", "Ghostfish", "Stonefish", "Ice Pip", "Lava Eel", "Sandfish", "Scorpion Carp", "Flounder", "Midnight Carp", "Sturgeon", "Tiger Trout", "Bullhead", "Tilapia", "Chub", "Dorado", "Albacore", "Shad", "Lingcod", "Halibut", "Woodskip", "Void Salmon", "Slimejack", "Stingray", "Lionfish", "Blue Discus", "Goby", "Midnight Squid", "Spook Fish", "Blobfish", "Crimsonfish", "Angler", "Legend", "Glacierfish", "Mutant Carp", "Son of Crimsonfish", "Ms. Angler", "Legend II", "Glacierfish Jr.", "Radioactive Carp", "Clam", "Lobster", "Crayfish", "Crab", "Cockle", "Mussel", "Shrimp", "Snail", "Periwinkle", "Oyster"
    ]
artifacts = [
    "Dwarf Scroll I", "Dwarf Scroll II", "Dwarf Scroll III", "Dwarf Scroll IV", "Chipped Amphora", "Arrowhead", "Ancient Doll", "Elvish Jewelry", "Chewing Stick", "Ornamental Fan", "Dinosaur Egg", "Rare Disc", "Ancient Sword", "Rusty Spoon", "Rusty Spur", "Rusty Cog", "Chicken Statue", "Ancient Seed", "Prehistoric Tool", "Dried Starfish", "Anchor", "Glass Shards", "Bone Flute", "Prehistoric Handaxe", "Dwarvish Helm", "Dwarf Gadget", "Ancient Drum", "Golden Mask", "Golden Relic", "Strange Doll", "Strange Doll", "Prehistoric Scapula", "Prehistoric Tibia", "Prehistoric Skull", "Skeletal Hand", "Prehistoric Rib", "Prehistoric Vertebra", "Skeletal Tail", "Nautilus Fossil", "Amphibian Fossil", "Palm Fossil", "Trilobite"
]
geode_minerals = [
    "Tigerseye", "Opal", "Fire Opal", "Alamite", "Bixite", "Baryte", "Aerinite", "Calcite", "Dolomite", "Esperite", "Fluorapatite", "Geminite", "Helvite", "Jamborite", "Jagoite", "Kyanite", "Lunarite", "Malachite", "Neptunite", "Lemon Stone", "Nekoite", "Orpiment", "Petrified Slime", "Thunder Egg", "Pyrite", "Ocean Stone", "Ghost Crystal", "Jasper", "Celestine", "Marble", "Sandstone", "Granite", "Basalt", "Limestone", "Soapstone", "Hematite", "Mudstone", "Obsidian", "Slate", "Fairy Stone", "Star Shards"
    ]
trinkets = [
    "Basilisk Paw", "Fairy Box", "Frog Egg", "Golden Spur", "Ice Rod", "Magic Hair Gel", "Magic Quiver", "Parrot Egg"
]
fish_prices = [
    ["Pufferfish", "Regular", 200],
    ["Pufferfish", "Silver", 250],
    ["Pufferfish", "Gold", 300],
    ["Pufferfish", "Iridium", 400],
    ["Anchovy", "Regular", 30],
    ["Anchovy", "Silver", 37],
    ["Anchovy", "Gold", 45],
    ["Anchovy", "Iridium", 60],
    ["Tuna", "Regular", 100],
    ["Tuna", "Silver", 125],
    ["Tuna", "Gold", 150],
    ["Tuna", "Iridium", 200],
    ["Sardine", "Regular", 40],
    ["Sardine", "Silver", 50],
    ["Sardine", "Gold", 60],
    ["Sardine", "Iridium", 80],
    ["Bream", "Regular", 45],
    ["Bream", "Silver", 56],
    ["Bream", "Gold", 67],
    ["Bream", "Iridium", 90],
    ["Largemouth Bass", "Regular", 100],
    ["Largemouth Bass", "Silver", 125],
    ["Largemouth Bass", "Gold", 150],
    ["Largemouth Bass", "Iridium", 200],
    ["Smallmouth Bass", "Regular", 50],
    ["Smallmouth Bass", "Silver", 62],
    ["Smallmouth Bass", "Gold", 75],
    ["Smallmouth Bass", "Iridium", 100],
    ["Rainbow Trout", "Regular", 65],
    ["Rainbow Trout", "Silver", 81],
    ["Rainbow Trout", "Gold", 97],
    ["Rainbow Trout", "Iridium", 130],
    ["Salmon", "Regular", 75],
    ["Salmon", "Silver", 93],
    ["Salmon", "Gold", 112],
    ["Salmon", "Iridium", 150],
    ["Walleye", "Regular", 105],
    ["Walleye", "Silver", 131],
    ["Walleye", "Gold", 157],
    ["Walleye", "Iridium", 210],
    ["Perch", "Regular", 55],
    ["Perch", "Silver", 68],
    ["Perch", "Gold", 82],
    ["Perch", "Iridium", 110],
    ["Carp", "Regular", 30],
    ["Carp", "Silver", 37],
    ["Carp", "Gold", 45],
    ["Carp", "Iridium", 60],
    ["Catfish", "Regular", 200],
    ["Catfish", "Silver", 250],
    ["Catfish", "Gold", 300],
    ["Catfish", "Iridium", 400],
    ["Pike", "Regular", 100],
    ["Pike", "Silver", 125],
    ["Pike", "Gold", 150],
    ["Pike", "Iridium", 200],
    ["Sunfish", "Regular", 30],
    ["Sunfish", "Silver", 37],
    ["Sunfish", "Gold", 45],
    ["Sunfish", "Iridium", 60],
    ["Red Mullet", "Regular", 75],
    ["Red Mullet", "Silver", 93],
    ["Red Mullet", "Gold", 112],
    ["Red Mullet", "Iridium", 150],
    ["Herring", "Regular", 30],
    ["Herring", "Silver", 37],
    ["Herring", "Gold", 45],
    ["Herring", "Iridium", 60],
    ["Eel", "Regular", 85],
    ["Eel", "Silver", 106],
    ["Eel", "Gold", 127],
    ["Eel", "Iridium", 170],
    ["Octopus", "Regular", 150],
    ["Octopus", "Silver", 187],
    ["Octopus", "Gold", 225],
    ["Octopus", "Iridium", 300],
    ["Red Snapper", "Regular", 50],
    ["Red Snapper", "Silver", 62],
    ["Red Snapper", "Gold", 75],
    ["Red Snapper", "Iridium", 100],
    ["Squid", "Regular", 80],
    ["Squid", "Silver", 100],
    ["Squid", "Gold", 120],
    ["Squid", "Iridium", 160],
    ["Sea Cucumber", "Regular", 75],
    ["Sea Cucumber", "Silver", 93],
    ["Sea Cucumber", "Gold", 112],
    ["Sea Cucumber", "Iridium", 150],
    ["Super Cucumber", "Regular", 250],
    ["Super Cucumber", "Silver", 312],
    ["Super Cucumber", "Gold", 375],
    ["Super Cucumber", "Iridium", 500],
    ["Ghostfish", "Regular", 45],
    ["Ghostfish", "Silver", 56],
    ["Ghostfish", "Gold", 67],
    ["Ghostfish", "Iridium", 90],
    ["Stonefish", "Regular", 300],
    ["Stonefish", "Silver", 375],
    ["Stonefish", "Gold", 450],
    ["Stonefish", "Iridium", 600],
    ["Ice Pip", "Regular", 500],
    ["Ice Pip", "Silver", 625],
    ["Ice Pip", "Gold", 750],
    ["Ice Pip", "Iridium", 0],
    ["Lava Eel", "Regular", 700],
    ["Lava Eel", "Silver", 875],
    ["Lava Eel", "Gold", 50],
    ["Lava Eel", "Iridium", 400],
    ["Sandfish", "Regular", 75],
    ["Sandfish", "Silver", 93],
    ["Sandfish", "Gold", 112],
    ["Sandfish", "Iridium", 150],
    ["Scorpion Carp", "Regular", 150],
    ["Scorpion Carp", "Silver", 187],
    ["Scorpion Carp", "Gold", 225],
    ["Scorpion Carp", "Iridium", 300],
    ["Flounder", "Regular", 100],
    ["Flounder", "Silver", 125],
    ["Flounder", "Gold", 150],
    ["Flounder", "Iridium", 200],
    ["Midnight Carp", "Regular", 150],
    ["Midnight Carp", "Silver", 187],
    ["Midnight Carp", "Gold", 225],
    ["Midnight Carp", "Iridium", 300],
    ["Sturgeon", "Regular", 200],
    ["Sturgeon", "Silver", 250],
    ["Sturgeon", "Gold", 300],
    ["Sturgeon", "Iridium", 400],
    ["Tiger Trout", "Regular", 150],
    ["Tiger Trout", "Silver", 187],
    ["Tiger Trout", "Gold", 225],
    ["Tiger Trout", "Iridium", 300],
    ["Bullhead", "Regular", 75],
    ["Bullhead", "Silver", 93],
    ["Bullhead", "Gold", 112],
    ["Bullhead", "Iridium", 150],
    ["Tilapia", "Regular", 75],
    ["Tilapia", "Silver", 93],
    ["Tilapia", "Gold", 112],
    ["Tilapia", "Iridium", 150],
    ["Chub", "Regular", 50],
    ["Chub", "Silver", 62],
    ["Chub", "Gold", 75],
    ["Chub", "Iridium", 100],
    ["Dorado", "Regular", 100],
    ["Dorado", "Silver", 125],
    ["Dorado", "Gold", 150],
    ["Dorado", "Iridium", 200],
    ["Albacore", "Regular", 75],
    ["Albacore", "Silver", 93],
    ["Albacore", "Gold", 112],
    ["Albacore", "Iridium", 150],
    ["Shad", "Regular", 60],
    ["Shad", "Silver", 75],
    ["Shad", "Gold", 90],
    ["Shad", "Iridium", 120],
    ["Lingcod", "Regular", 120],
    ["Lingcod", "Silver", 150],
    ["Lingcod", "Gold", 180],
    ["Lingcod", "Iridium", 240],
    ["Halibut", "Regular", 80],
    ["Halibut", "Silver", 100],
    ["Halibut", "Gold", 120],
    ["Halibut", "Iridium", 160],
    ["Woodskip", "Regular", 75],
    ["Woodskip", "Silver", 93],
    ["Woodskip", "Gold", 112],
    ["Woodskip", "Iridium", 150],
    ["Void Salmon", "Regular", 150],
    ["Void Salmon", "Silver", 187],
    ["Void Salmon", "Gold", 225],
    ["Void Salmon", "Iridium", 300],
    ["Slimejack", "Regular", 100],
    ["Slimejack", "Silver", 125],
    ["Slimejack", "Gold", 150],
    ["Slimejack", "Iridium", 200],
    ["Stingray", "Regular", 180],
    ["Stingray", "Silver", 225],
    ["Stingray", "Gold", 270],
    ["Stingray", "Iridium", 360],
    ["Lionfish", "Regular", 100],
    ["Lionfish", "Silver", 125],
    ["Lionfish", "Gold", 150],
    ["Lionfish", "Iridium", 200],
    ["Blue Discus", "Regular", 120],
    ["Blue Discus", "Silver", 150],
    ["Blue Discus", "Gold", 180],
    ["Blue Discus", "Iridium", 240],
    ["Goby", "Regular", 150],
    ["Goby", "Silver", 187],
    ["Goby", "Gold", 225],
    ["Goby", "Iridium", 300],
    ["Midnight Squid", "Regular", 100],
    ["Midnight Squid", "Silver", 125],
    ["Midnight Squid", "Gold", 150],
    ["Midnight Squid", "Iridium", 200],
    ["Spook Fish", "Regular", 220],
    ["Spook Fish", "Silver", 275],
    ["Spook Fish", "Gold", 330],
    ["Spook Fish", "Iridium", 440],
    ["Blobfish", "Regular", 500],
    ["Blobfish", "Silver", 625],
    ["Blobfish", "Gold", 750],
    ["Blobfish", "Iridium", 0],
    ["Crimsonfish", "Regular", 500],
    ["Crimsonfish", "Silver", 875],
    ["Crimsonfish", "Gold", 250],
    ["Crimsonfish", "Iridium", 0],
    ["Angler", "Regular", 900],
    ["Angler", "Silver", 125],
    ["Angler", "Gold", 350],
    ["Angler", "Iridium", 800],
    ["Legend", "Regular", 0],
    ["Legend", "Silver", 250],
    ["Legend", "Gold", 500],
    ["Legend", "Iridium", 0],
    ["Glacierfish", "Regular", 0],
    ["Glacierfish", "Silver", 250],
    ["Glacierfish", "Gold", 500],
    ["Glacierfish", "Iridium", 0],
    ["Mutant Carp", "Regular", 0],
    ["Mutant Carp", "Silver", 250],
    ["Mutant Carp", "Gold", 500],
    ["Mutant Carp", "Iridium", 0],
    ["Son of Crimsonfish", "Regular", 500],
    ["Son of Crimsonfish", "Silver", 875],
    ["Son of Crimsonfish", "Gold", 250],
    ["Son of Crimsonfish", "Iridium", 0],
    ["Ms. Angler", "Regular", 900],
    ["Ms. Angler", "Silver", 125],
    ["Ms. Angler", "Gold", 350],
    ["Ms. Angler", "Iridium", 800],
    ["Legend II", "Regular", 0],
    ["Legend II", "Silver", 250],
    ["Legend II", "Gold", 500],
    ["Legend II", "Iridium", 0],
    ["Glacierfish Jr.", "Regular", 0],
    ["Glacierfish Jr.", "Silver", 250],
    ["Glacierfish Jr.", "Gold", 500],
    ["Glacierfish Jr.", "Iridium", 0],
    ["Radioactive Carp", "Regular", 0],
    ["Radioactive Carp", "Silver", 250],
    ["Radioactive Carp", "Gold", 500],
    ["Radioactive Carp", "Iridium", 0],
    ["Clam", "Regular", 50],
    ["Clam", "Silver", 62],
    ["Clam", "Gold", 75],
    ["Clam", "Iridium", 100],
    ["Lobster", "Regular", 120],
    ["Lobster", "Gold", 150],
    ["Crayfish", "Regular", 75],
    ["Crayfish", "Gold", 93],
    ["Crab", "Regular", 100],
    ["Crab", "Gold", 125],
    ["Cockle", "Regular", 50],
    ["Cockle", "Silver", 62],
    ["Cockle", "Gold", 75],
    ["Cockle", "Iridium", 100],
    ["Mussel", "Regular", 30],
    ["Mussel", "Silver", 37],
    ["Mussel", "Gold", 45],
    ["Mussel", "Iridium", 60],
    ["Shrimp", "Regular", 60],
    ["Shrimp", "Gold", 75],
    ["Snail", "Regular", 65],
    ["Snail", "Gold", 81],
    ["Periwinkle", "Regular", 20],
    ["Periwinkle", "Gold", 25],
    ["Oyster", "Regular", 40],
    ["Oyster", "Silver", 50],
    ["Oyster", "Gold", 60],
    ["Oyster", "Iridium", 80],
]

artisan_recipes = [
    ["Wine", fruits],
    ["Pale Ale", ["Hops"]],
    ["Beer", ["Wheat"]],
    ["Mead", ["Honey"]],
    ["Cheese", ["Milk", "Large Milk"]],
    ["Goat Cheese", ["Goat Milk", "Large Goat Milk"]],
    ["Vinegar", ["Rice"]],
    ["Coffee", ["Coffee Bean"]],
    ["Green Tea", ["Tea Leaves"]],
    ["Juice", vegetables + ["Dandelion", "Leek", "Spring Onion", "Wild Horseradish", "Fiddlehead Fern", "Hazelnut", "Snow Yam", "Winter Root", "Cave Carrot", "Ginger"]],
    ["Cloth", ["Wool"]],
    ["Mayonnaise", ["Egg", "Large Egg", "Ostrich Egg", "Golden Egg"]],
    ["Duck Mayonnaise", ["Duck Egg"]],
    ["Void Mayonnaise", ["Void Egg"]],
    ["Dinosaur Mayonnaise", ["Dinosaur Egg"]],
    ["Truffle Oil", ["Truffle"]],
    ["Oil", ["Corn", "Sunflower Seeds", "Sunflower"]],
    ["Pickles", vegetables + without(mushrooms, ["Red Mushroom"]) + ["Dandelion", "Leek", "Spring Onion", "Wild Horseradish", "Fiddlehead Fern", "Hazelnut", "Snow Yam", "Winter Root", "Cave Carrot", "Ginger"]],
    ["Jelly", fruits],
    ["Caviar", ["Sturgeon Roe"]],
    ["Aged Roe", ["Roe"]],
    ["Dried Mushrooms", without(mushrooms, ["Red Mushroom"])],
    ["Dried Fruit", without(fruits, ["Grape"])],
    ["Raisins", ["Grape"]],
    ["Smoked Fish", fish],
]

universal_loves = ["Golden Pumpkin", "Magic Rock Candy", "Pearl", "Prismatic Shard", "Rabbit's Foot", "Stardrop Tea"]
universal_likes = without(artisan_goods, ["Oil", "Void Mayonnaise"]) + without(cooking_items, ["Bread", "Fried Egg", "Seafoam Pudding", "Strange Bun"]) + without(flowers, ["Poppy"]) + without(foraged_minerals, ["Quartz"]) + fruit_tree_fruit + gems + without(vegetables, ["Hops", "Tea Leaves", "Unmilled Rice", "Wheat"]) + ["Life Elixir", "Maple Syrup", "Pina Colada", "Rainbow Shell", "Treasure Chest"]
universal_neutrals = without(books, ["Price Catalogue"]) + ["Bread", "Coral", "Duck Feather", "Fried Egg", "Hops", "Mystic Syrup", "Nautilus Shell", "Roe", "Squid Ink", "Sweet Gem Berry", "Tea Leaves", "Truffle", "Wheat", "Wool"]

villagers_gifts = [
    ["Alex", "Summer 13", ["Complete Breakfast", "Jack Be Nimble, Jack Be Thick", "Salmon Dinner"], without(eggs, ["Void Egg"]) + ["Dinosaur Egg", "Field Snack", "Parrot Egg"], without(fruits, fruit_tree_fruit + ["Salmonberry"]) + without(mushrooms, ["Red Mushroom"]) + ["Milk", "Daffodil", "Dandelion", "Frog Egg", "Ginger", "Hazelnut", "Leek", "Snow Yam", "Winter Root"], without(books, ["Jack Be Nimble, Jack Be Thick"]) + ["Salmonberry", "Wild Horseradish"], ["Holly", "Quartz"]],
    ["Elliot", "Fall 05", ["Crab Cakes", "Duck Feather", "Lobster", "Pomegranate", "Squid Ink", "Tom Kha Soup"], books + without(fruits, ["Pomegranate", "Salmonberry"]) + ["Octopus", "Squid"], without(eggs, ["Void Egg"]) + without(fish, ["Carp", "Lobster", "Octopus", "Sea Cucumber", "Snail", "Squid"]) + ["Rainbow Shell", "Sea Urchin"], without(mushrooms, ["Red Mushroom"]) + ["Milk", "Daffodil", "Dandelion", "Ginger", "Hazelnut", "Holly", "Leek", "Pizza", "Snow Yam", "Wild Horseradish", "Winter Root"], ["Amaranth", "Quartz", "Salmonberry", "Sea Cucumber", "Super Cucumber"]],
    ["Harvey", "Winter 14", ["Coffee", "Pickles", "Super Meal", "Truffle Oil", "Wine"], without(fruits, ["Salmonberry", "Spice Berry"]) + without(mushrooms, ["Red Mushroom"]) + ["Daffodil", "Dandelion", "Duck Egg", "Duck Feather", "Ginger", "Goat Milk", "Hazelnut", "Holly", "Large Goat Milk", "Leek", "Quartz", "Snow Yam", "Spring Onion", "Wild Horseradish", "Winter Root"], without(eggs, ["Duck Egg", "Void Egg"]) + ["Large Milk", "Milk"], ["Blueberry Tart", "Bread", "Cheese", "Chocolate Cake", "Cookie", "Cranberry Sauce", "Fried Mushroom", "Glazed Yams", "Goat Cheese", "Hashbrowns", "Ice Cream", "Pancakes", "Pink Cake", "Pizza", "Rhubarb Pie", "Rice Pudding"], ["Coral", "Nautilus Shell", "Rainbow Shell", "Salmonberry", "Spice Berry"]],
    ["Sam", "Summer 17", ["Cactus Fruit", "Maple Bar", "Pizza", "Tigerseye"], without(eggs, ["Void Egg"]) + ["Joja Cola"], without(fruits, fruit_tree_fruit + ["Cactus Fruit", "Salmonberry"]) + ["Milk"], without(mushrooms, ["Red Mushroom"]) + without(vegetables, ["Hops", "Tea Leaves", "Wheat"]) + ["Daffodil", "Dandelion", "Ginger", "Hazelnut", "Holly", "Leek", "Quartz", "Salmonberry", "Seaweed", "Snow Yam", "Wild Horseradish", "Winter Root"], ["Bone Fragment", "Cinder Shard", "Coal", "Copper Bar", "Duck Mayonnaise", "Gold Bar", "Gold Ore", "Iridium Bar", "Iridium Ore", "Iron Bar", "Mayonnaise", "Pickles", "Refined Quartz"]],
    ["Sebastian", "Winter 10", ["Frog Egg", "Frozen Tear", "Obsidian", "Pumpkin Soup", "Sashimi", "Void Egg"], ["Combat Quarterly", "Flounder", "Monster Compendium", "Quartz"], without(fish, ["Carp", "Flounder", "Snail"]) + without(fruits, fruit_tree_fruit + ["Salmonberry"]) + ["Milk"], without(flowers, ["Poppy"]) + without(mushrooms, ["Red Mushroom"]) + ["Daffodil", "Dandelion", "Ginger", "Hazelnut", "Holly", "Leek", "Salmonberry", "Snow Yam", "Wild Horseradish", "Winter Root"], without(artisan_goods, ["Coffee", "Green Tea", "Oil"]) + without(eggs, ["Void Egg"]) + ["Clay", "Complete Breakfast", "Farmer's Lunch", "Omelet", "Pina Colada"]],
    ["Shane", "Spring 20", ["Beer", "Hot Pepper", "Pepper Poppers", "Pizza"], without(eggs, ["Void Egg"]) + without(fruits, ["Hot Pepper"]), ["Milk", "Strange Bun"], without(mushrooms, ["Red Mushroom"]) + ["Daffodil", "Dandelion", "Ginger", "Hazelnut", "Holly", "Leek", "Seaweed", "Snow Yam", "Wild Horseradish", "Winter Root"], ["Pickles", "Quartz"]],
    ["Abigail", "Fall 13", ["Amethyst", "Banana Pudding", "Blackberry Cobbler", "Chocolate Cake", "Monster Compendium", "Pufferfish", "Pumpkin", "Spicy Eel"], ["Ancient Sword", "Basilisk Paw", "Bone Flute", "Combat Quarterly", "Quartz"], without(mushrooms, ["Red Mushroom"]) + ["Milk", "Daffodil", "Dandelion", "Ginger", "Hazelnut", "Leek", "Snow Yam", "Winter Root"], eggs + without(fruits, fruit_tree_fruit) + without(vegetables, ["Hops", "Pumpkin", "Tea Leaves", "Wheat"]) + ["Sugar", "Wild Horseradish"], ["Clay", "Holly"]],
    ["Emily", "Spring 27", ["Amethyst", "Aquamarine", "Cloth", "Jade", "Parrot Egg", "Ruby", "Survival Burger", "Topaz", "Wool"], ["Daffodil", "Quartz"], without(eggs, ["Void Egg"]) + without(fruits, fruit_tree_fruit + ["Salmonberry"]) + without(mushrooms, ["Red Mushroom"]) + ["Milk", "Dandelion", "Ginger", "Hazelnut", "Leek", "Snow Yam", "Wild Horseradish", "Winter Root"], ["Fried Eel", "Ice Cream", "Rice Pudding", "Salmonberry", "Spicy Eel"], ["Fish Taco", "Holly", "Maki Roll", "Salmon Dinner", "Sashimi"]],
    ["Haley", "Spring 14", ["Coconut", "Fruit Salad", "Pink Cake", "Sunflower"], ["Daffodil"], [], eggs + without(fruits, ["Coconut"]) + without(mushrooms, ["Red Mushroom"]) + without(vegetables, ["Hops", "Tea Leaves", "Wheat"]) + ["Milk", "Dandelion", "Ginger", "Hazelnut", "Holly", "Leek", "Mystic Syrup", "Quartz", "Snow Yam", "Winter Root"], fish + ["Clay", "Prismatic Shard", "Wild Horseradish"]],
    ["Leah", "Winter 23", ["Goat Cheese", "Poppyseed Muffin", "Salad", "Stir Fry", "Truffle", "Vegetable Medley", "Wine"], without(eggs, ["Void Egg"]) + fruits + without(mushrooms, ["Red Mushroom"]) + ["Milk", "Daffodil", "Dandelion", "Driftwood", "Ginger", "Hazelnut", "Holly", "Leek", "Snow Yam", "Spring Onion", "Wild Horseradish", "Winter Root"], [], without(foraged_minerals, ["Earth Crystal"]) + without(gems, ["Diamond", "Prismatic Shard"]) + ["Carp Surprise", "Cookie", "Fried Egg", "Ice Cream", "Pink Cake", "Rice Pudding", "Seaweed", "Survival Burger", "Tortilla"], ["Bread", "Hashbrowns", "Pancakes", "Pizza", "Void Egg"]],
    ["Maru", "Summer 10", ["Battery Pack", "Cauliflower", "Cheese Cauliflower", "Diamond", "Dwarf Gadget", "Gold Bar", "Iridium Bar", "Miner's Treat", "Pepper Poppers", "Radioactive Bar", "Rhubarb Pie", "Strawberry"], without(mushrooms, ["Common Mushroom", "Red Mushroom"]) + ["Copper Bar", "Iron Bar", "Oak Resin", "Pine Tar", "Quartz", "Radioactive Ore"], without(eggs, ["Void Egg"]) + without(fruits, fruit_tree_fruit + ["Blackberry", "Crystal Fruit", "Salmonberry", "Strawberry"]) + ["Milk", "Daffodil", "Dandelion", "Ginger", "Hazelnut", "Leek", "Wild Horseradish", "Winter Root"], ["Blackberry", "Common Mushroom", "Crystal Fruit", "Maple Syrup", "Salmonberry"], ["Holly", "Honey", "Pickles", "Snow Yam", "Truffle"]],
    ["Penny", "Fall 02", books + ["Diamond", "Emerald", "Melon", "Poppy", "Poppyseed Muffin", "Red Plate", "Roots Platter", "Sandfish", "Tom Kha Soup"], artifacts + ["Milk", "Dandelion", "Leek"], without(eggs, ["Void Egg"]) + without(fruits, fruit_tree_fruit + ["Grape", "Melon", "Salmonberry"]) + without(mushrooms, ["Purple Mushroom", "Red Mushroom"]) + ["Daffodil", "Ginger", "Hazelnut", "Snow Yam", "Wild Horseradish", "Winter Root"], ["Algae Soup", "Duck Feather", "Pale Broth", "Purple Mushroom", "Quartz", "Red Mushroom", "Salmonberry", "Wool"], ["Beer", "Grape", "Holly", "Hops", "Mead", "Pale Ale", "Pina Colada", "Rabbit's Foot", "Wine"]],
    ["Caroline", "Winter 07", ["Fish Taco", "Green Tea", "Summer Spangle", "Tropical Curry"], ["Daffodil", "Tea Leaves", "Wild Horseradish"], without(eggs, ["Void Egg"]) + without(fruits, fruit_tree_fruit + ["Salmonberry"]) + ["Milk"], without(mushrooms, ["Red Mushroom"]) + ["Amaranth", "Dandelion", "Duck Mayonnaise", "Ginger", "Hazelnut", "Holly", "Leek", "Mayonnaise", "Snow Yam", "Winter Root"], ["Quartz", "Salmonberry"]],
    ["Clint", "Winter 26", ["Amethyst", "Aquamarine", "Artichoke Dip", "Emerald", "Fiddlehead Risotto", "Gold Bar", "Iridium Bar", "Jade", "Omni Geode", "Ruby", "Topaz"], ["Copper Bar", "Iron Bar", "Mining Monthly"], without(eggs, ["Void Egg"]) + without(fruits, fruit_tree_fruit + ["Salmonberry"]) + without(mushrooms, ["Red Mushroom"]) + ["Milk", "Coal", "Daffodil", "Dandelion", "Ginger", "Gold Ore", "Hazelnut", "Iridium Ore", "Leek", "Refined Quartz", "Snow Yam", "Winter Root"], without(flowers, ["Poppy"]) + ["Quartz", "Salmonberry", "Wild Horseradish"], ["Holly"]],
    ["Demetrius", "Summer 19", ["Bean Hotpot", "Ice Cream", "Rice Pudding", "Strawberry"], without(eggs, ["Void Egg"]) + without(fruits, ["Strawberry"]) + ["Dinosaur Egg", "Purple Mushroom"], without(fish, ["Carp", "Snail"]) + without(mushrooms, ["Red Mushroom", "Purple Mushroom"]) + ["Daffodil", "Dandelion", "Ginger", "Hazelnut", "Leek", "Snow Yam", "Wild Horseradish", "Winter Root"], ["Quartz"], ["Holly"]],
    ["Dwarf", "Summer 22", ["Amethyst", "Aquamarine", "Emerald", "Jade", "Lava Eel", "Omni Geode", "Ruby", "Topaz"], artifacts + ["Cave Carrot", "Quartz"], without(fruits, fruit_tree_fruit + ["Salmonberry"]) + ["Milk", "Solar Essence", "Void Essence"], eggs + without(mushrooms, ["Red Mushroom"]) + ["Daffodil", "Dandelion", "Ginger", "Hazelnut", "Holly", "Leek", "Salmonberry", "Snow Yam", "Wild Horseradish", "Winter Root"], []],
    ["Evelyn", "Winter 20", ["Beet", "Chocolate Cake", "Diamond", "Fairy Rose", "Raisins", "Stuffing", "Tulip"], ["Milk", "Broken Glasses", "Clam", "Cockle", "Coral", "Daffodil", "Mussel", "Nautilus Shell", "Oyster", "Sea Urchin"], without(eggs, ["Void Egg"]) + without(fruits, fruit_tree_fruit + ["Salmonberry", "Spice Berry"]) + without(mushrooms, ["Red Mushroom"]) + ["Dandelion", "Ginger", "Hazelnut", "Leek", "Snow Yam", "Winter Root"], ["Quartz", "Wild Horseradish"], without(fish, ["Clam", "Cockle", "Mussel", "Oyster"]) + ["Clay", "Fried Eel", "Garlic", "Holly", "Maki Roll", "Salmonberry", "Sashimi", "Spice Berry", "Spicy Eel", "Trout Soup"]],
    ["George", "Fall 24", ["Fried Mushroom", "Leek"], ["Daffodil"], without(eggs, ["Void Egg"]), without(fruits, fruit_tree_fruit + ["Salmonberry"]) + without(mushrooms, ["Red Mushroom"]) + ["Milk", "Ginger", "Hazelnut", "Snow Yam", "Winter Root"], without(flowers, ["Poppy"]) + ["Salmonberry", "Wild Horseradish"], ["Clay", "Dandelion", "Holly", "Quartz"]],
    ["Gus", "Summer 08", ["Diamond", "Escargot", "Fish Taco", "Orange", "Tropical Curry"], ["Daffodil", "Truffle"], without(eggs, ["Void Egg"]) + without(fruits, fruit_tree_fruit + ["Salmonberry"]) + without(mushrooms, ["Red Mushroom"]) + ["Dandelion", "Ginger", "Hazelnut", "Leek", "Snow Yam", "Winter Root"], ["Salmonberry", "Wild Horseradish"], ["Coleslaw", "Holly", "Quartz"]],
    ["Jas", "Summer 04", ["Ancient Doll", "Fairy Box", "Fairy Rose", "Pink Cake", "Plum Pudding", "Strange Doll"], ["Milk", "Coconut", "Daffodil"], [], eggs + without(fruits, fruit_tree_fruit + ["Coconut"]) + without(mushrooms, ["Red Mushroom"]) + without(vegetables, ["Hops", "Tea Leaves", "Wheat"]) + ["Dandelion", "Ginger", "Hazelnut", "Holly", "Leek", "Quartz", "Snow Yam", "Winter Root"], without(artisan_goods, ["Honey", "Jelly", "Oil"]) + ["Clay", "Pina Colada", "Triple Shot Espresso", "Wild Horseradish"]],
    ["Jodi", "Fall 11", ["Chocolate Cake", "Crispy Bass", "Diamond", "Eggplant Parmesan", "Fried Eel", "Pancakes", "Rhubarb Pie", "Vegetable Medley"], without(eggs, ["Void Egg"]) + without(fruits, ["Spice Berry"]) + ["Milk"], [], without(mushrooms, ["Red Mushroom"]) + ["Garlic", "Ginger", "Hazelnut", "Holly", "Leek", "Quartz", "Snow Yam", "Wild Horseradish", "Winter Root"], ["Daffodil", "Dandelion", "Spice Berry"]],
    ["Kent", "Spring 04", ["Fiddlehead Risotto", "Roasted Hazelnuts"], without(eggs, ["Void Egg"]) + fruits + ["Daffodil", "Dwarvish Safety Manual"], without(mushrooms, ["Red Mushroom"]) + ["Dandelion", "Ginger", "Hazelnut", "Leek", "Wild Horseradish", "Winter Root"], ["Pina Colada", "Quartz", "Snow Yam"], ["Milk", "Algae Soup", "Holly", "Sashimi", "Tortilla"]],
    ["Krobus", "Winter 01", ["Diamond", "Iridium Bar", "Monster Compendium", "Monster Musk", "Pumpkin", "Void Egg", "Void Mayonnaise", "Wild Horseradish"], ["Gold Bar", "Quartz", "Seafoam Pudding", "Strange Bun"], without(eggs, ["Void Egg"]) + without(fruits, fruit_tree_fruit + ["Salmonberry"]) + ["Milk"], without(cooking_items, ["Bread", "Fried Egg", "Seafoam Pudding", "Strange Bun"]) + without(mushrooms, ["Red Mushroom"]) + ["Daffodil", "Dandelion", "Ginger", "Hazelnut", "Holly", "Leek", "Life Elixir", "Salmonberry", "Snow Yam", "Winter Root"], []],
    ["Leo", "Summer 26", ["Duck Feather", "Mango", "Ostrich Egg", "Parrot Egg", "Poi"], ["Dragon Tooth", "Nautilus Shell", "Quartz", "Sea Urchin", "Spice Berry"], without(eggs, ["Ostrich Egg", "Void Egg"]) + without(fish, ["Carp", "Snail"]) + without(fruits, fruit_tree_fruit + ["Mango", "Salmonberry", "Spice Berry"]) + ["Milk", "Coffee"], without(cooking_items, ["Bread", "Fried Egg", "Mango Sticky Rice", "Poi", "Triple Shot Espresso"]) + without(mushrooms, ["Morel", "Red Mushroom"]) + ["Daffodil", "Dandelion", "Ginger", "Hazelnut", "Leek", "Life Elixir", "Pickles", "Salmonberry", "Snow Yam", "Wild Horseradish", "Winter Root"], ["Beer", "Holly", "Hops", "Mead", "Morel", "Oil", "Pale Ale", "Pina Colada", "Triple Shot Espresso", "Unmilled Rice", "Wine"]],
    ["Lewis", "Spring 07", ["Autumn's Bounty", "Glazed Yams", "Green Tea", "Hot Pepper", "Vegetable Medley"], ["Blueberry", "Cactus Fruit", "Coconut"], without(eggs, ["Void Egg"]) + without(fruits, fruit_tree_fruit + ["Blueberry", "Cactus Fruit", "Coconut", "Hot Pepper", "Salmonberry"]) + without(mushrooms, ["Red Mushroom"]) + ["Daffodil", "Dandelion", "Ginger", "Hazelnut", "Leek", "Snow Yam", "Winter Root"], ["Milk", "Salmonberry", "Wild Horseradish"], ["Holly", "Quartz"]],
    ["Linus", "Winter 03", ["Blueberry Tart", "Cactus Fruit", "Coconut", "Dish O' The Sea", "The Alleyway Buffet", "Yarn"], without(eggs, ["Void Egg"]) + without(fruits, ["Cactus Fruit", "Coconut"]) + without(mushrooms, ["Red Mushroom"]) + ["Milk", "Daffodil", "Dandelion", "Ginger", "Hazelnut", "Holly", "Leek", "Snow Yam", "Spring Onion", "Wild Horseradish", "Winter Root"], without(fish, ["Snail"]) + [], foraged_minerals + without(gems, ["Diamond", "Prismatic Shard"]) + ["Treasure Chest"], []],
    ["Marnie", "Fall 18", ["Diamond", "Farmer's Lunch", "Pink Cake", "Pumpkin Pie"], without(eggs, ["Void Egg"]) + ["Milk", "Stardew Valley Almanac", "Quartz"], without(fruits, fruit_tree_fruit + ["Salmonberry"]) + without(mushrooms, ["Red Mushroom"]) + ["Daffodil", "Dandelion", "Ginger", "Hazelnut", "Leek", "Snow Yam", "Winter Root"], ["Salmonberry", "Seaweed", "Wild Horseradish"], ["Clay", "Holly"]],
    ["Pam", "Spring 18", ["Beer", "Cactus Fruit", "Glazed Yams", "Mead", "Pale Ale", "Parsnip", "Parsnip Soup", "Pina Colada"], without(fruits, ["Cactus Fruit"]) + ["Milk", "Daffodil"], without(fish, ["Carp", "Octopus", "Snail", "Squid"]) + without(mushrooms, ["Red Mushroom"]) + ["Dandelion", "Ginger", "Hazelnut", "Joja Cola", "Leek", "Snow Yam", "Winter Root"], eggs + ["Quartz", "Wild Horseradish"], ["Holly", "Octopus", "Squid"]],
    ["Pierre", "Spring 26", ["Fried Calamari", "Price Catalogue"], without(eggs, ["Void Egg"]) + ["Milk", "Daffodil", "Dandelion"], without(fruits, fruit_tree_fruit + ["Salmonberry"]) + [], foraged_minerals + without(gems, ["Diamond", "Prismatic Shard"]) + without(mushrooms, ["Red Mushroom"]) + ["Ginger", "Hazelnut", "Holly", "Leek", "Salmonberry", "Snow Yam", "Wild Horseradish", "Winter Root"], fish + ["Corn", "Garlic", "Parsnip Soup", "Tortilla"]],
    ["Robin", "Fall 21", ["Goat Cheese", "Peach", "Spaghetti", "Woody's Secret"], without(fruits, ["Peach"]) + ["Milk", "Hardwood", "Quartz", "Woodcutter's Weekly"], without(eggs, ["Void Egg"]) + without(mushrooms, ["Red Mushroom"]) + ["Daffodil", "Dandelion", "Ginger", "Hazelnut", "Leek", "Snow Yam", "Winter Root"], ["Wild Horseradish"], ["Holly"]],
    ["Sandy", "Fall 15", ["Crocus", "Daffodil", "Mango Sticky Rice", "Sweet Pea"], fruits + ["Goat Milk", "Large Goat Milk", "Quartz", "Wool"], without(eggs, ["Void Egg"]) + without(mushrooms, ["Red Mushroom"]) + ["Dandelion", "Ginger", "Hazelnut", "Large Milk", "Leek", "Milk", "Snow Yam", "Wild Horseradish", "Winter Root"], [], ["Holly"]],
    ["Vincent", "Spring 10", ["Cranberry Candy", "Frog Egg", "Ginger Ale", "Grape", "Pink Cake", "Snail"], ["Milk", "Coconut", "Daffodil"], [], eggs + without(fruits, fruit_tree_fruit + ["Coconut", "Grape"]) + without(vegetables, ["Hops", "Tea Leaves", "Wheat"]) + without(mushrooms, ["Red Mushroom"]) + ["Dandelion", "Ginger", "Hazelnut", "Holly", "Leek", "Quartz", "Snow Yam", "Winter Root"], without(artisan_goods, ["Honey", "Jelly", "Oil"]) + ["Clay", "Pina Colada", "Triple Shot Espresso", "Wild Horseradish"]],
    ["Willy", "Summer 24", ["Catfish", "Diamond", "Gold Bar", "Iridium Bar", "Jewels Of The Sea", "Mead", "Octopus", "Pumpkin", "Sea Cucumber", "Sturgeon", "The Art O' Crabbing"], ["Bait And Bobber", "Lingcod", "Quartz", "Seafoam Pudding", "Tiger Trout", "Baked Fish", "Carp Surprise", "Chowder", "Crab Cakes", "Crispy Bass", "Escargot", "Fish Stew", "Fish Taco", "Fried Calamari", "Fried Eel", "Lobster Bisque", "Salmon Dinner", "Trout Soup"], without(eggs, ["Void Egg"]) + without(fish, ["Carp", "Catfish", "Lingcod", "Octopus", "Sea Cucumber", "Snail", "Sturgeon", "Tiger Trout"]) + without(fruits, fruit_tree_fruit + ["Salmonberry"]) + ["Milk", "Dish O' The Sea", "Maki Roll", "Sashimi"], without(cooking_items, ["Bread", "Fried Egg", "Strange Bun", "Dish O' The Sea", "Maki Roll", "Sashimi", "Baked Fish", "Carp Surprise", "Chowder", "Crab Cakes", "Crispy Bass", "Escargot", "Fish Stew", "Fish Taco", "Fried Calamari", "Fried Eel", "Lobster Bisque", "Salmon Dinner", "Seafoam Pudding", "Trout Soup"]) + without(mushrooms, ["Red Mushroom"]) + ["Daffodil", "Dandelion", "Ginger", "Hazelnut", "Holly", "Leek", "Life Elixir", "Salmonberry", "Snow Yam", "Wild Horseradish", "Winter Root"], []],
    ["Wizard", "Winter 17", ["Book of Mysteries", "Purple Mushroom", "Solar Essence", "Super Cucumber", "Void Essence"], geode_minerals + trinkets + ["Iridium Bar", "Quartz"], without(fruits, fruit_tree_fruit + ["Salmonberry"]) + [], eggs + without(mushrooms, ["Red Mushroom", "Purple Mushroom"]) + ["Milk", "Daffodil", "Dandelion", "Ginger", "Hazelnut", "Holly", "Leek", "Salmonberry", "Slime", "Snow Yam", "Wild Horseradish", "Winter Root"], []]
]

artisan_gifting = []
    
# Animal Products
# Item,Quality,Profession,Sell Price,Processed Item,Processed Item Quality,Processed Item Sell Price,Profit Increase
for line in animal_products:
    line_stripped = line.strip()
    line_parts = line_stripped.split(",")

    processed_item_name = line_parts[4]
    index = get_machine_index(processed_item_name)

    item_name = line_parts[0]
    quality = line_parts[1]
    base_price = int(line_parts[3])
    price = int(line_parts[6])

    add_or_update_row(master_list, item_name, quality, base_price, index, price)

# Preserves Jar
# Input Item,Type,Quality,Input Item Sell Price,Processed Sell Price,Increase in Value (g),Productivity (g/minute),Approximate g/day [1]
for line in preserves_jar_productivity:
    line_stripped = line.strip()
    line_parts = line_stripped.split(",")

    index = 4

    item_name = clean_part(line_parts[0])
    quality = line_parts[2]
    base_price = int(line_parts[3])
    price = int(line_parts[4])

    add_or_update_row(master_list, item_name, quality, base_price, index, price)

    if line_parts[1] == "Fruit":
        if item_name not in fruits:
            fruits.append(item_name)

# Keg
# Input Item,Quality,Input Item Sell Price,"Processed Sell Price(Regular Quality)",Increase in Value (g),Productivity (g/minute),Approximate g/day [1]
for line in keg_productivity:
    line_stripped = line.strip()
    line_parts = line_stripped.split(",")

    index = 3

    item_name = clean_part(line_parts[0])
    quality = line_parts[1]
    base_price = int(clean_part(line_parts[2]))
    price = int(line_parts[3])

    add_or_update_row(master_list, item_name, quality, base_price, index, price)

# Dehydrator Products
for fruit in fruits:
    normal_row = find_row(master_list, fruit, 'Regular')
    normal_price = normal_row[2]
    if fruit == "Grape":
        for row in master_list:
            if row[0] == "Grape":
                raisins_price = 600/5
                row[6] = raisins_price
    else:
        for row in master_list:
            if row[0] == fruit:
                dried_fruit_price = 1.5 * normal_price + 5
                row[6] = dried_fruit_price

for mushroom in without(mushrooms, ["Red Mushroom"]):
    normal_row = find_row(master_list, mushroom, 'Regular')
    normal_price = normal_row[2]
    for row in master_list:
        if row [0] == mushroom:
            dried_mushrooms_price = 1.5 * normal_price + 5
            row[6] = dried_mushrooms_price

for fish_name, quality, price in fish_prices:
    add_or_update_row(master_list, fish_name, quality, price, 10, price * 2)

interest_item = input("What is your item of interest? ").strip().title()
interest_quality = input(f"What is the quality of your '{interest_item}'? (Regular, Silver, Gold, Iridium) ").strip().capitalize()
if interest_item in fruits or interest_item in without(mushrooms, ["Red Mushroom"]):
    interest_quantity = int(input(f"How many '{interest_item}'(s) do you have? ").strip())
else:
    interest_quantity = 1

interest_row = find_row(master_list, interest_item, interest_quality)
if interest_row is None:
    print(f"\nThe item '{interest_item}' is not used in a machine.")
else:
    best_index = None
    best_price = None
    best_price_per_day = None

    for i in range(3, 11):
        price = interest_row[i]
        if price is None:
            continue
        if i == 6 and interest_quantity < 5:  # not enough for a dehydrator batch
            continue
        if best_price is None or price > best_price:
            best_price = price
            best_index = i
            gifting_index = i
        else:
            gifting_index = i

    if interest_row[2] > best_price:
        best_price = interest_row[2]
        best_index = 2

    machine = get_machine_name(best_index)
    print(f"\nBest artisan selling option: {machine}, selling for {best_price}g each.")

if "Wine" in interest_item:
    gift_lookup_item = "Wine"
elif "Milk" in interest_item:
    gift_lookup_item = "Milk"
elif "Cheese" in interest_item:
    gift_lookup_item = "Cheese"
elif "Juice" in interest_item:
    gift_lookup_item = "Juice"
else:
    gift_lookup_item = interest_item

lovers_likers_neutralers = find_gifts(gift_lookup_item)

lovers = lovers_likers_neutralers[0]
likers = lovers_likers_neutralers[1]
neutralers = lovers_likers_neutralers[2]

if len(lovers) == len(villagers_gifts):
    print(f"\nEveryone loves '{interest_item}'!")
elif lovers:
    print(f"\nThose who love '{interest_item}':")
    print("\n".join(lovers))

if len(likers) == len(villagers_gifts):
    print(f"\nEveryone likees '{interest_item}'!")
elif lovers:
    print(f"\nThose who like '{interest_item}':")
    print("\n".join(lovers))

if len(lovers) == len(villagers_gifts):
    print(f"\nEveryone feels neutral about '{interest_item}'!")
elif lovers:
    print(f"\nThose who feel neutral about '{interest_item}':")
    print("\n".join(lovers))


if "Wine" in interest_item:
    recipe_lookup_item = "Wine"
elif "Milk" in interest_item:
    recipe_lookup_item = "Milk"
elif "Cheese" in interest_item:
    recipe_lookup_item = "Cheese"
elif "Juice" in interest_item:
    recipe_lookup_item = "Juice"
elif "Egg" in interest_item:
    recipe_lookup_item = "Egg"
else:
    recipe_lookup_item = interest_item

output = find_in_recipe(recipe_lookup_item)

if output:
    print(f"\nThe item '{interest_item}' is used in the following recipes:")
    for recipe in output:
        recipe_name = recipe[0]
        ingredients = recipe[1]

        print(f"\n{recipe_name}:")
        for ingredient in ingredients:
            ingredient_name = ingredient[0]
            ingredient_quantity = ingredient[1]
            print(f"  {ingredient_name} x{ingredient_quantity}")

        recipe_lovers_likers_neutralers = find_gifts(recipe_name)

        recipe_lovers = recipe_lovers_likers_neutralers[0]
        recipe_likers = recipe_lovers_likers_neutralers[1]
        recipe_neutralers = recipe_lovers_likers_neutralers[2]

        if len(recipe_lovers) == len(villagers_gifts):
            print(f"Everyone loves this!")
        elif recipe_lovers:
            print(f"Loved by:")
            print("\n".join(recipe_lovers))
        if (recipe_likers) == len(villagers_gifts):
            print(f"Everyone likes this!")
        elif recipe_likers:
            print(f"Liked by:")
            print("\n".join(recipe_likers))
        if (recipe_neutralers) == len(villagers_gifts):
            print(f"Everyone feels neutral about this.")
        elif recipe_neutralers:
            print(f"Felt neutral by:")
            print("\n".join(recipe_neutralers))
else:
    print(f"\nNo recipes found that use '{interest_item}'.")

artisan_outputs = find_artisan_output(interest_item)

if artisan_outputs:
    for output_name in artisan_outputs:
        print(f"\n'{interest_item}' can become '{output_name}':")
        output_lovers, output_likers, output_neutralers = find_gifts(output_name)
        if len(output_lovers) == len(villagers_gifts):
            print("Everyone loves this!")
        elif output_lovers:
            print("Loved by:")
            print("\n".join(output_lovers))
        if len(output_likers) == len(villagers_gifts):
            print("Everyone likes this!")
        elif output_likers:
            print("Liked by:")
            print("\n".join(output_likers))
        if len(output_neutralers) == len(villagers_gifts):
            print("Everyone feels neutral about this.")
        elif output_neutralers:
            print("Felt neutral by:")
            print("\n".join(output_neutralers))
