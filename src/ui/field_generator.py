import secrets
import time
from threading import Thread
import json

import flet as ft


class Editor:
    "Managing editor area and connected data input."
    def __init__(self):
        self.temp_directory = "../temp_data/"
        self.timer = False
        self.fields = _initial_fields_data()
        self.field_definitions = _field_definitions()
        self.status = _status()
        INITIAL_SELCTION_KEY = "text"
        self.dropdown_selection = ft.Text(
            value=self.field_definitions[INITIAL_SELCTION_KEY]["display"], 
            key=INITIAL_SELCTION_KEY
        )

    def add_field(self):
        "Manages info for selected field and collects Flet object."
        field_id = _generate_id(self.dropdown_selection.key, self.fields)
        index = len(self.fields_column.controls)
        self.fields[field_id] = _field_data(
            self.dropdown_selection.key, "", self.field_definitions[self.dropdown_selection.key]["settings"], index
        )
        self.fields_column.controls.insert(
            index, _define_field(field_id, self.fields, self.fields, self.write_temp)
        )
        self.fields_column.update()
    
    def selector(self):
        "Add new field to editor via dropdown selector and confirmation."
        self.dropdown = _define_selector(self.field_definitions, self.dropdown_selection)
        return _define_options_field(self.dropdown, self.add_field)

    def build(self):
        "Generate editor view with user input."
        self.fields_column = _arrange_editor(self.fields, self.write_temp)
        return _arrange_build(self.fields_column, self.selector())

    def write_temp(self):
        "Auto-saves document after delay. Uses separate thread to avoid interruptions."
        # TODO: 
        # - (system settings) adjustable interval
        self.status["saved"] = False
        if not self.status["queued"]:
            self.status["queued"] = True
            thread = Thread(target=_thread, args=(self.fields, self.status))
            thread.start()
        else:
            print("already queued")

        # TODO:
        # - export/import editing format with format tags
        # - repositioning field 
        # - remove field 
        # - naming and sync to formatted file
        # - (file options) export to md/txt/html? #


class OptionsIcon(ft.IconButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = ft.ButtonStyle(shape=ft.RoundedRectangleBorder())


class MenuTooltip(ft.Tooltip):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bgcolor = "#30343A"
        self.text_style = ft.TextStyle(size=12, color=ft.Colors.GREEN_400)


class EditorTextField(ft.TextField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border = ft.NoInputBorder()


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



def _define_field(field_id, data, fields, write_temp):
    "Creates Flet object of requested type to document editor."
    info = data[field_id]
    match info["type"]:
        case "h1":
            # TODO 
            # - option to add right-side image #
            return EditorTextField(
                value=info["value"],
                hint_text="Title",
                text_style=ft.TextStyle(
                    size=30,
                    weight=ft.FontWeight.W_600
                ),
                on_change=lambda e: _update_field(e.control.value, field_id, data, fields, write_temp)
            )
        case "text":
            # TODO 
            # - basic text style options? #
            return ft.Row(controls=[
                EditorTextField(
                    value=info["value"], 
                    multiline=True,
                    width=500,
                    on_change=lambda e: _update_field(e.control.value, field_id, data, fields, write_temp)
                ),
            ])
        case "table":
            # TODO
            # - add/remove column/line 
            columns = info["settings"][0]
            data[field_id]["value"] = {"header": {}}
            return ft.DataTable(
                columns = _table_columns(columns, field_id, data, fields, write_temp),
                rows = _table_rows(info["settings"], field_id, data, fields, write_temp),
                column_spacing=10,
                horizontal_margin=10,
                width={2: 500, 3: 550, 4: 600}[columns],
            )
        case "image":
            # TODO
            # - settings to add row of 1, 2, 3 #
            return ft.Button(
                "Select image file",
                on_click=lambda e: _update_field(e.control.value, field_id, data, fields, write_temp)
            )
        case "link":
            # TODO 
            # - display text and link #
            return ft.Row(controls=[
                ft.TextField(
                    hint_text="Enter URL",
                    on_submit=lambda e: _update_field(e.control.value, field_id, data, fields, write_temp)
                ),
                ft.Button(
                    content="Press Enter to confirm",
                ),
                ft.Button(icon=ft.Icon(ft.Icons.MENU)),
            ])
        case "list":
            # TODO
            # - basic function
            # - checkbox and textfield
            # - subtext field? #
            pass


def _table_columns(columns, field_id, data, fields, write_temp):
    "Generates pre-defined table columns."
    column_cells = []
    data[field_id]["value"]["header"] = dict()
    for x in range(columns):
        data[field_id]["value"]["header"][x] = ""
        column_cells.append(ft.DataColumn(
            label=EditorTextField(
                value="",
                width={2: 230, 3: 160, 4: 130}[columns],
                on_change=lambda e, x=x: _update_field(
                    e.control.value, field_id, data, fields, write_temp, column=x
                )
            )
        ))
    return column_cells


def _table_rows(settings, field_id, data, fields, write_temp):
    "Generates pre-defined table rows with column cells."
    rows = []
    col_range, row_range = range(settings[0]), range(settings[1])
    rows = [
        ft.DataRow(cells=[
            ft.DataCell(EditorTextField(
                value="",
                width={2: 220, 3: 160, 4: 130}[settings[0]],
                on_change=lambda e, x=x, y=y: _update_field(
                    e.control.value, field_id, data, fields, write_temp, column=x, row=f"row_{y}"
                )
            )) for x in col_range
        ]) for y in row_range
    ]
    data[field_id]["value"].update({
        f"row_{y}": {x: "" for x in col_range} for y in row_range
    })
    return rows


def _define_selector(field_definitions, dropdown_selection):
    "Generates PopupMenuButton as a dropdown selector field for editor options."
    dropdown_options = []
    def _selection(e):
        dropdown_selection.key = e.control.data
        dropdown_selection.value = e.control.content
    for key in field_definitions.keys():
        dropdown_options.append(
            ft.PopupMenuItem(
                content=field_definitions[key]["display"], 
                data=key,
                height=30,
                on_click=_selection
            )
        )
    return ft.PopupMenuButton(
        content=ft.Container(
            content=ft.Row(
                controls=[
                    dropdown_selection,
                    ft.Icon(ft.Icons.ARROW_DROP_UP, size=20)
                ],
            ),
            width=110,
            height=30,
            bgcolor="#444444",
            padding=ft.Padding(left=8),
        ),
        items=dropdown_options,
        menu_position=ft.PopupMenuPosition.OVER,
        tooltip=MenuTooltip(message="Select field"),
        margin=ft.Margin(left=5, right=5)
    )


def _define_options_field(dropdown, add_field):
    "Generates and arranges Flet objects for editor options field."
    # TODO 
    # add option for direct save 
    # add position selector 
    # - #
    return ft.Container(
        content=ft.Row(
            controls=[
                dropdown,
                OptionsIcon(
                    icon=ft.Icons.ADD,
                    on_click=add_field,
                    tooltip=MenuTooltip(message="Add new bottom field"),
                ),
                OptionsIcon(
                    icon=ft.Icons.REMOVE,
                    on_click=None,
                    tooltip=MenuTooltip(message="Remove field")
                ),
                OptionsIcon(
                    icon=ft.Icons.SWAP_VERT,
                    on_click=None,
                    tooltip=MenuTooltip(message="Move field")
                ),
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        ),
        bgcolor="#333333",
    )


def _arrange_editor(fields, write_temp):
    "Arranges the finished document editor fields into Flet column."
    column_controls = []
    print(fields)
    orded_fields = {k: v for k, v in sorted(fields.items(), key=lambda x: x[1]["position"])}
    for field_id in orded_fields.keys():
        column_controls.append(
            _define_field(field_id, fields, fields, write_temp)
        )

    return ft.Column(
        controls=column_controls,
        expand=True,
        width=600,
        scroll=ft.ScrollMode.ADAPTIVE,
        alignment=ft.MainAxisAlignment.START
    )


def _arrange_build(editor_fields, selector):
    "Arranges editor area with finished document editor and options "
    return ft.Column(
        controls=[
            editor_fields,
            selector
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        expand=True,
        margin=ft.Margin.all(0),
    )


def _update_field(value, field_id, data, fields, write_temp, column=None, row=None):
    "Syncronizes document changes to internal dict."
    if data[field_id]["type"] == "table":
        if row is None:
            data[field_id]["value"]["header"].update({column: value})
        else:
            data[field_id]["value"][row][column] = value
        print(1)
    else:
        data[field_id]["value"] = value
    print(data)
    write_temp()


def _generate_id(selected_type, existing_ids):
    "Creates unique IDs for new document editor fields."
    while True:
        suffix = secrets.token_hex(2)
        field_id = f"{selected_type}_{suffix}"
        if field_id not in existing_ids:
            return field_id

        
def _thread(fields, status):
    "Manages save-to-file thread."
    print("waiting")
    time.sleep(15)
    _save_temp(fields, status)


def _save_temp(fields, status):
    "Saves internal dict to file."
    if not status["saved"]:
        print("writing")
        # with open("../../../temp_data/temp_file3.json", "w", encoding="utf-8") as f:
        #     json.dump(fields, f, indent=4, ensure_ascii=False)
        print("written")
        status["saved"] = True