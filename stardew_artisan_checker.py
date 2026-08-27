"""
Stardew Valley Artisan Best Value Checker

Author: Katie Viola
Start Date: 8/26/26
End Date:
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

def find_row(master_list, item, quality):
    # Search through every row we've made so far
    for row in master_list:
        if row[0] == item and row[1] == quality:
            return row  # found it - hand back the actual row (not a copy)
    return None  # looped through everything, never found a match

def add_or_update_row(master_list, item, quality, base_price, index, price):
    row = find_row(master_list, item, quality)

    if row is None:
        new_row = [item, quality, base_price, None, None, None, None, None, None, None]
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
        return None  # unrecognized - good spot to print a warning while debugging

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
        9: "Loom"
    }
    return machine_names[i]

mushroom_items = ["Chanterelle", "Common Mushroom", "Magma Cap", "Morel", "Purple Mushroom"]
fruit_items = []
    
# Animal Products
# Item,Quality,Profession,Sell Price,Processed Item,Processed Item Quality,Processed Item Sell Price,Profit Increase
for line in animal_products:
    line_stripped = line.strip()
    line_parts = line_stripped.split(",")

    processed_item_name = line_parts[4]
    index = get_machine_index(processed_item_name)

    if index is None:
        print(f"Unrecognized processed item: {processed_item_name}")
        continue

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
        if item_name not in fruit_items:
            fruit_items.append(item_name)

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
for fruit in fruit_items:
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

for mushroom in mushroom_items:
    normal_row = find_row(master_list, mushroom, 'Regular')
    normal_price = normal_row[2]
    for row in master_list:
        if row [0] == mushroom:
            dried_mushrooms_price = 1.5 * normal_price + 5
            row[6] = dried_mushrooms_price

### Enter input of item, quality, and quanitity (if fruit or mushroom)
interest_item = input("What is your item of interest? ").strip().title()
interest_quality = input(f"What is the quality of your '{interest_item}'? (Regular, Silver, Gold, Iridium) ").strip().capitalize()
if interest_item in fruit_items or interest_item in mushroom_items:
    interest_quantity = int(input(f"How many '{interest_item}'(s) do you have? ").strip())
else:
    interest_quantity = 1

interest_row = find_row(master_list, interest_item, interest_quality)
if interest_row is None:
    print("Sorry, that item/quality combination wasn't found.")
else:
    best_index = None
    best_price = None
    best_price_per_day = None

    for i in range(3, 10):
        price = interest_row[i]
        if price is None:
            continue
        if i == 6 and interest_quantity < 5:  # not enough for a dehydrator batch
            continue
        if best_price is None or price > best_price:
            best_price = price
            best_index = i

    if interest_row[2] > best_price:
        best_price = interest_row[2]
        best_index = 2

    machine = get_machine_name(best_index)
    print(f"Best option: {machine}, selling for {best_price}g each.")

### Find what thing will be most profitable
