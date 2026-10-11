import secrets
import time
from threading import Thread
import json

import flet as ft


class Editor:
    "Managing editor Flet fields and connected data input."
    def __init__(self):
        self.temp_directory = "../temp_data/"
        self.timer = False
        self.fields = _initial_fields_data()
        self.field_definitions = _field_definitions()
        self.status = _status()

    def add_field(self):
        "Manages info for selected field and collects Flet object."
        field_id = _generate_id(self.dropdown.value, self.fields)
        index = len(self.fields_column.controls) - 1
        self.fields[field_id] = _field_data(
            self.dropdown.value, "", self.field_definitions[self.dropdown.value]["settings"], index
        )
        self.fields_column.controls.insert(
            index, _define_field(field_id, self.fields, self.fields, self.write_temp)
        )
        self.fields_column.update()
    
    def selector(self):
        "Add new field to editor via dropdown selector and confirmation."
        self.dropdown = _define_selector(self.field_definitions)
        return _arrange_selector_field(self.dropdown, self.add_field)

    def build(self):
        "Generate editor view with user input."
        self.fields_column = _arrange_build(self.fields, self.selector(), self.write_temp)
        return self.fields_column

    def write_temp(self):
        "Auto-saves document after delay."
        # TODO: 
        # - create button for direct save
        # - adjustable interval
        self.status["saved"] = False
        if not self.status["queued"]:
            self.status["queued"] = True
            thread = Thread(target=_thread, args=(self.fields, self.status))
            thread.start()
        else:
            print("already queued")


def _initial_fields_data():
    return {
        "h1_1": _field_data("h1", "My title", None, 0),
        "text_1": _field_data("text", "My input text.\n\nIt has multiple rows.", None, 1),
    }


def _status():
    return {
        "saved": True,
        "queued": False
    }


def _field_data(key, value, settings, position):
    return {
        "type": key,
        "value": value,
        "settings": settings,
        "position": position,
    }


def _field_definitions():
    return {
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
            "display": "Text field",
            "settings": None
        },
        "table": {
            "key": "table",
            "display": "Table field",
            "settings": [4, 3]
        },
        "list": {
            "key": "list",
            "display": "List field",
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
    }


# @ft.control
class EditorTextField(ft.TextField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border = ft.NoInputBorder()

def _define_field(field_id, data, fields, write_temp):
    info = data[field_id]
    match info["type"]:
        case "h1":
            return EditorTextField(
                value=info["value"],
                hint_text="Title",
                # border=ft.NoInputBorder(),
                text_style=ft.TextStyle(
                    size=30,
                    weight=ft.FontWeight.W_600
                ),
                on_change=lambda e: _update_field(e.control.value, field_id, data, fields, write_temp)
            )
        case "text":
            return ft.Row(controls=[
                EditorTextField(
                    value=info["value"], 
                    multiline=True,
                    # border=ft.NoInputBorder(),
                    width=450,
                    on_change=lambda e: _update_field(e.control.value, field_id, data, fields, write_temp)
                ),
                ft.Button(icon=ft.Icon(ft.Icons.LOCK)),
                ft.Button(icon=ft.Icon(ft.Icons.MENU)),
            ])
        case "table":
            columns = info["settings"][0]
            data[field_id]["value"] = dict()
            return ft.DataTable(
                columns = _table_columns(columns, field_id, data, fields, write_temp),
                rows = _table_rows(info["settings"]),
                column_spacing=10,
                horizontal_margin=10,
                width={2: 500, 3: 550, 4: 600}[columns],
            )
        case "image":
            # return ft.Image(
            #     src="../assets/icon.png",
            #     height= 100
            # )
            return ft.Button(
                "Select image file",
                on_click=lambda e: _update_field(e.control.value, field_id, data, fields, write_temp)
            )
        case "link":
            return ft.Row(controls=[
                ft.TextField(
                    hint_text="Enter URL",
                    # multiline=True,
                    # border=ft.NoInputBorder(),
                    on_submit=lambda e: _update_field(e.control.value, field_id, data, fields, write_temp)
                ),
                ft.Button(
                    content="Press Enter to confirm",
                    # on_click=lambda e: _update_field(e.control.value, field_id, data, fields, write_temp)
                ),
                ft.Button(icon=ft.Icon(ft.Icons.MENU)),
            ])
        #"https://flet.dev"

# def _column_width(columns):
#     match columns:
#         case 2:
#             return 200
#         case 3:
#             return 180
#         case 4:
#             return 140

def _table_columns(columns, field_id, data, fields, write_temp):
    column_cells = []
    for x in range(columns):
        data[field_id]["value"][x] = ""
        column_cells.append(ft.DataColumn(
            label=EditorTextField(
                value=x,
                width={2: 230, 3: 160, 4: 130}[columns],
                on_change=lambda e: _update_field(
                    e.control.value, field_id, data, fields, write_temp, column=x
                )
            )))
    return column_cells

def _table_rows(settings):
    row_cells = [ft.DataCell(EditorTextField(width={2: 220, 3: 160, 4: 130}[settings[0]])) for x in range(settings[0])]
    rows = [ft.DataRow(cells = row_cells) for x in range(settings[1])]
    return rows


def _define_selector(field_definitions):
    dropdown_options = []
    for x in field_definitions:
        dropdown_options.append(
            ft.DropdownOption(key=field_definitions[x]["key"], 
                                text=field_definitions[x]["display"])
        )
    return ft.Dropdown(
        value="text",
        options=dropdown_options,
        width=200
    )


def _arrange_selector_field(dropdown, add_field):
    return ft.Row(
        controls=[
            dropdown,
            ft.Button(
                content="Add", 
                on_click=add_field
            )
        ],
    )


def _arrange_build(fields, selector, write_temp):
    column_controls = []
    print(fields)
    orded_fields = {k: v for k, v in sorted(fields.items(), key=lambda x: x[1]["position"])}
    for field_id in orded_fields.keys():
        column_controls.append(
            _define_field(field_id, fields, fields, write_temp)
        )

    column_controls.append(selector)

    return ft.Column(
        controls=column_controls,
        expand=True,
        height=600,
        width=600,
        scroll=ft.ScrollMode.ADAPTIVE,
    )


def _update_field(value, field_id, data, fields, write_temp, column=None):
    if data[field_id]["type"] == "table":
        data[field_id]["value"].update({column: value})
    # if data[field_id]["type"] == "table":
    #     if not "value" in data[field_id]:
    #         data[field_id]["value"] = dict()
    #     else:
    #         data[field_id]["value"].update(value)
        print(1)
    else:
        data[field_id]["value"] = value
    print(data)
    # timer = time.time()
    # time.sleep(10)
    # timer = True
    # if timer: 
    # status["saved"] = False
    write_temp()
        # timer = False


def _generate_id(selected_type, existing_ids):
    while True:
        suffix = secrets.token_hex(2)
        field_id = f"{selected_type}_{suffix}"
        if field_id not in existing_ids:
            return field_id



        
def _thread(fields, status):
    print("waiting")
    time.sleep(15)
    _save_temp(fields, status)

def _save_temp(fields, status):
    if not status["saved"]:
        print("writing")
        # with open("../../../temp_data/temp_file3.json", "w", encoding="utf-8") as f:
        #     json.dump(fields, f, indent=4, ensure_ascii=False)
        print("written")
        status["saved"] = True