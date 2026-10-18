import flet as ft



def field_data(key, value, settings, position):
    return {
        "type": key,
        "value": value,
        "settings": settings,
        "position": position,
    }


field_definitions = {
    "h1": {
        "key": "h1",
        "display": "Title",
        "settings": None
    },
    "h2": {
        "key": "h2",
        "display": "Heading 1",
        "settings": None
    },
    "h3": {
        "key": "h3",
        "display": "Heading 2",
        "settings": None
    },
    "text": {
        "key": "text",
        "display": "Text",
        "settings": None
    },
    "table": {
        "key": "table",
        "display": "Table",
        "settings": [4, 3]
    },
    "list": {
        "key": "list",
        "display": "List",
        "settings": None
    },
    "image": {
        "key": "image",
        "display": "Image",
        "settings": None
    },
    "link": {
        "key": "link",
        "display": "Link",
        "settings": None
    },
    "separator": {
        "key": "separator",
        "display": "Separator",
        "settings": None
    }
}


initial_fields_data = {
    "h1_1": field_data("h1", "", field_definitions["h1"]["settings"], 0),
    "text_1": field_data("text", "", field_definitions["text"]["settings"], 1),
}


# def initial_fields_data():
#     return {
#         "h1_1": field_data("h1", "", field_definitions["h1"]["settings"], 0),
#         "text_1": field_data("text", "", field_definitions["text"]["settings"], 1),
#     }
