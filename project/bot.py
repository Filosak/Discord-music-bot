import json
import os
from PIL import Image

pad_left = 0
pad_up = 0

def merge(im1, im2, pl, pu):
    w = im1.size[0] + im2.size[0] + 20 + pl
    h = max(im1.size[1], im2.size[1]) + pu
    im = Image.new("RGBA", (w, h))

    im.paste(im1)
    im.paste(im2, (im1.size[0] + 20 + pl, pu))

    return im

curr_type = "minecraft:crafting_shaped"

with open("project/MC_recipe_data.json", "r") as jsonFile:
    try: 
        MC_data = json.load(jsonFile)
    except Exception as e:
        MC_data = {}

item = "tnt"
image = Image.new("RGBA", (60, 60))




for row in MC_data[item]["pattern"]:
    for slot in row:
        if (slot != " "):
            im = Image.open(slot)
            image.paste(im, (pad_left, pad_up))
        pad_left += 20
    pad_left = 0
    pad_up += 20

image.show()









# for recipe in os.listdir("MC/recipes"):
#     with open(f"MC/recipes/{recipe}") as file:
#         loaded = json.load(file)

#         if (loaded["type"] != "minecraft:crafting_shaped"):
#             continue
        
#         items = {}
#         file_basename = os.path.basename(file.name)[:-5].replace("_", "").lower()
#         pattern = loaded["pattern"]

#         for k in loaded["key"]:
#             if (type(loaded["key"][k]) == list):
#                 items[k] = loaded["key"][k][0]
#             else:
#                 items[k] = loaded["key"][k]
        
#         MC_data[f"{file_basename}"] = {
#             "pattern": [
#                 [],
#                 [],
#                 []
#             ],
#             "reuslt": loaded["result"]
#         } 
        
        

#         for i, row in enumerate(pattern):
#             for slot in row:
#                 try:
#                     if (slot == " "):
#                         MC_data[f"{file_basename}"]["pattern"][i].append(" ")

#                     elif (list(items[slot].keys())[0] == "tag"):
#                         with open(f"MC/tags/items/{items[slot]['tag'][10:]}.json") as temp_file:
#                             temp_loaded = json.load(temp_file)

#                             if (os.path.isfile(f"MC/textures/block/{temp_loaded['values'][0][10:]}.png")):
#                                 MC_data[f"{file_basename}"]["pattern"][i].append(f"MC/textures/block/{temp_loaded['values'][0][10:]}.png")
#                             else:
#                                 MC_data[f"{file_basename}"]["pattern"][i].append(f"MC/textures/item/{temp_loaded['values'][0][10:]}.png")
                    
#                     else:
#                         if (os.path.isfile(f"MC/textures/block/{items[slot]['item'][10:]}.png")):
#                             MC_data[f"{file_basename}"]["pattern"][i].append(f"MC/textures/block/{items[slot]['item'][10:]}.png")
#                         else:
#                             MC_data[f"{file_basename}"]["pattern"][i].append(f"MC/textures/item/{items[slot]['item'][10:]}.png")

#                 except Exception as e:
#                     print(e)

#         for i, row in enumerate(MC_data[f"{file_basename}"]):
#             if (not row):
#                 MC_data[f"{file_basename}"]["pattern"][i] = [" ", " ", " "]

#         with open("project/MC_recipe_data.json", "w") as json_file:
#             json.dump(MC_data, json_file, indent=4, sort_keys=True)