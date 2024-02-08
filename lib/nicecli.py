import json
import os

CONFIG = "config.json"

COLOROUT = ""
NC = ""
NG = ""
NCC = ""
SRC = ""


def main():
    init()

    while True:
        os.system("cls")
        print("\nMenu:")
        print("1. Add Color")
        print("2. Remove Color")
        print("3. Remove Category")
        print("4. Print Categories")
        print("5. Print Colors")
        print("6. Generate Dart Code")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            color_name = input("Enter color name: ")
            category_name = input("Enter category name: ")
            hex_value = input("Enter hex value: ")
            add_color(color_name, category_name, hex_value)
        elif choice == "2":
            color_name = input("Enter color name: ")
            category_name = input("Enter category name: ")
            remove_color(color_name, category_name)
        elif choice == "3":
            category_name = input("Enter category name: ")
            remove_category(category_name)
        elif choice == "4":
            print_categories()
        elif choice == "5":
            print_colors()
        elif choice == "6":
            generate_dart_code()
        elif choice == "7":
            break
        else:
            print("Invalid choice. Please try again.")

        input("\nBack to menu...")


def init():
    with open(CONFIG, 'w') as file:
        json.dump({
            "COLOROUT": "colors.json",
            "NC": "src/nice_colors",
            "NG": "src/nice_gradients",
            "NCC": "src/nice_colors/color",
            "SRC": "src",
        }, file, indent=2)
    with open(CONFIG, 'r') as config:
        config_data = json.load(config)

        global COLOROUT, NC, NG, NCC, SRC
        COLOROUT = config_data['COLOROUT']
        NC = config_data['NC']
        NG = config_data['NG']
        NCC = config_data['NCC']
        SRC = config_data['SRC']
    init_fss()


def init_fss():
    os.makedirs(NC, exist_ok=True)
    os.makedirs(NG, exist_ok=True)
    os.makedirs(NCC, exist_ok=True)


def dart_write(path, txt):
    data = dart_read(path)
    newline = f"""{txt}
  /*newline*/"""
    d = data.replace("/*newline*/", newline)
    write(path, d)


def write(path, data):
    with open(path, 'w') as file:
        file.write(data)


def dart_read(path):
    with open(path, 'r') as file:
        data = file.read()
        return data


def dart_make_library():
    with open("nice_colors.dart", 'w') as file:
        file.writelines([
            "library nice_colors;\n\n",
            "import 'dart:ui';\n\n",
            "//? COLORS\n\n"
            "part 'src/nice_colors/nice_colors.dart';\n\n",
            "/*newcolor*/"
        ])


def add_color_part(name):
    with open("nice_colors.dart", 'r') as lib:
        lib_data = lib.read()
        newcolor = f"part 'src/nice_colors/color/{name}.dart';\n/*newcolor*/"
        ld = lib_data.replace("/*newcolor*/", newcolor)
    with open("nice_colors.dart", 'w') as lib:
        lib.write(ld)


def dart_make_composite():
    with open(NC + "/nice_colors.dart", 'w') as file:
        file.writelines([
            "part of '../../nice_colors.dart';\n",
            "\n",
            "class NiceColors {\n",
            "  /*newline*/\n",
            "}\n"
        ])


def dart_make_color(name):
    with open(NCC + f"/{name}.dart", 'w') as file:
        classNameLine = f"class {name.title()}" + " {\n"
        file.writelines([
            "part of '../../../nice_colors.dart';\n",
            "\n",
            classNameLine,
            "  /*newline*/\n",
            "}\n",
        ])


def hex_to_rgb(hex_value):
    r = int(hex_value[0:2], 16)
    g = int(hex_value[2:4], 16)
    b = int(hex_value[4:6], 16)
    return f"{r}:{g}:{b}"


def load_colors():
    try:
        with open(COLOROUT, 'r') as file:
            colors = json.load(file)
    except FileNotFoundError:
        colors = {}
    return colors


def save_colors(colors):
    with open(COLOROUT, 'w') as file:
        json.dump(colors, file, indent=2)


def add_color(color, category, hex_value):
    rgb_value = hex_to_rgb(hex_value)
    colors = load_colors()
    if category in colors:
        colors[category][color] = {
            "hex": hex_value, "rgb": rgb_value}
    else:
        colors[category] = {color: {
            "hex": hex_value, "rgb": rgb_value}}
    save_colors(colors)
    print(f"Added color '{category}' to category '{color}'.")


def remove_color(color, category):
    colors = load_colors()
    if category in colors and color in colors[category]:
        del colors[category][color]
        print(f"Removed category '{color}' from color '{category}'.")
    else:
        print(f"Category '{color}' not found for color '{
              category}'.")


def add_category(category):
    colors = load_colors()
    if category not in colors:
        colors[category] = {}
        save_colors(colors)
        print(f"Added category '{category}'.")
    else:
        print(f"Category '{category}' already exists.")


def remove_category(category):
    colors = load_colors()
    if category in colors:
        del colors[category]
        save_colors(colors)
        print(f"Removed category '{category}'.")
    else:
        print(f"Category '{category}' not found.")


def print_categories():
    colors = load_colors()
    print("Categories:")
    for category in colors.keys():
        print(f"- {category}")


def print_colors():
    colors = load_colors()
    print("Colors:")
    for color, categories in colors.items():
        print(f"{color}:")
        for category, values in categories.items():
            print(f"  - Category: {category}")
            print(f"    Hex: {values['hex']}")
            print(f"    RGB: {values['rgb']}")


def generate_dart_code():
    with open(COLOROUT, 'r') as out:
        data = json.load(out)

    dart_make_library()
    dart_make_composite()

    for category, colors in data.items():
        title = category.title()
        newline = f"static get {category.lower()} => {category.title()}();"
        dart_write(NC + "/nice_colors.dart", newline)
        add_color_part(category)

        dart_make_color(category)
        for color, values in colors.items():
            hex = values['hex']
            # rgb = values['rgb]
            newline = f"Color {color} = const Color(0xff{hex});"
            dart_write(NCC + f"/{category}.dart", newline)


if __name__ == "__main__":
    main()
