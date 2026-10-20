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
        "initial_value": "",
        "settings": None
    },
    "h2": {
        "key": "h2",
        "display": "Heading 1",
        "initial_value": "",
        "settings": None
    },
    "h3": {
        "key": "h3",
        "display": "Heading 2",
        "initial_value": "",
        "settings": None
    },
    "text": {
        "key": "text",
        "display": "Text",
        "initial_value": "",
        "settings": None
    },
    "columns": {
        "key": "columns",
        "display": "Columns",
        "initial_value": "",
        "settings": 2
    },
    "table": {
        "key": "table",
        "display": "Table",
        "initial_value": "",
        "settings": [4, 3]
    },
    "list": {
        "key": "list",
        "display": "List",
        "initial_value": [[False, ""]]*6,
        "settings": {
            "length": 6,
            "use_checkbox": True
        }
    },
    "image": {
        "key": "image",
        "display": "Image",
        "initial_value": "",
        "settings": None
    },
    "link": {
        "key": "link",
        "display": "Link",
        "initial_value": "",
        "settings": None
    },
    "separator": {
        "key": "separator",
        "display": "Separator",
        "initial_value": "",
        "settings": None
    },
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
