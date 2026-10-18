import secrets
import time
from threading import Thread
import json

import flet as ft

from ui.field_recepes import field_definitions
from ui.components import (ControlLayer,
                           EditorContainer,
                           EditorText,
                           MenuTooltip,
                           OptionsIcon)


class Editor:
    "Managing editor area and connected data input."
    def __init__(self):
        self.temp_directory = "../temp_data/"
        self.timer = False
        self.fields = _initial_fields_data()
        # self.field_definitions = _field_definitions()
        self.status = _status()
        INITIAL_SELCTION_KEY = "text"
        self.dropdown_selection = ft.Text(
            value=field_definitions[INITIAL_SELCTION_KEY]["display"], 
            key=INITIAL_SELCTION_KEY
        )
        self.fields_column = ft.Column(
            controls=[],
            expand=True,
            width=600,
            scroll=ft.ScrollMode.ADAPTIVE,
            alignment=ft.MainAxisAlignment.START
        )
        self.editor = None
        self.inspect = False
        self.shield = ft.Container(
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.0, ft.Colors.BLACK),
            visible=False
        )
        self.controlled_elements = []
        self.hovered_field = ""
        self.field_selection = None

    def switch_interaction(self):
        if self.inspect: 
            self.field_selection = None
            self.inspect = False 
        else: 
            self.inspect = True
        for x in self.controlled_elements:
            print(x, x.ignore_interactions)
            x.ignore_interactions = self.inspect
        self.editor.update()

    def identify_field(self, field_id):
        self.hovered_field = field_id

    def select_fields(self, field_id):
        if self.field_selection is None:
            self.field_selection = field_id
        else:
            origin = self.fields[self.field_selection]["position"]
            self.fields[self.field_selection]["position"] = self.fields[field_id]["position"]
            for x, y in self.fields.items():
                if x == self.field_selection:
                    continue
                elif origin > self.fields[self.field_selection]["position"]:
                    if y["position"] in range(self.fields[self.field_selection]["position"], origin):
                        y["position"] += 1
                elif origin < self.fields[self.field_selection]["position"]:
                    print(range(origin, self.fields[self.field_selection]["position"]))
                    if y["position"] in range(origin, self.fields[self.field_selection]["position"] + 1):
                        y["position"] -= 1
            _arrange_editor(self.rebuild, self.fields, self.write_temp, self.controlled_elements, self.identify_field, self.select_fields, self.inspect)
            self.field_selection = None

    def add_field(self):
        "Manages info for selected field and collects Flet object."
        field_id = _generate_id(self.dropdown_selection.key, self.fields)
        index = len(self.fields_column.controls)
        self.fields[field_id] = _field_data(
            self.dropdown_selection.key, "", field_definitions[self.dropdown_selection.key]["settings"], index
        )
        self.fields_column.controls.insert(
            index, _define_field(field_id, self.fields, self.fields, self.write_temp, self.controlled_elements, self.identify_field, self.select_fields, self.inspect)
        )
        self.fields_column.update()
    
    def selector(self):
        "Add new field to editor via dropdown selector and confirmation."
        self.dropdown = _define_selector(field_definitions, self.dropdown_selection)
        return _define_options_field(self.dropdown, self.add_field, self.switch_interaction)

    def rebuild(self, new_controls):
        self.fields_column.controls.clear()
        self.fields_column.controls = new_controls

    def build(self):
        "Generate editor view with user input."
        _arrange_editor(self.rebuild, self.fields, self.write_temp, self.controlled_elements, self.identify_field, self.select_fields, self.inspect)
        self.editor = ft.Stack([
            ft.Container(self.fields_column),
            self.shield
        ], expand=True)
        return ft.Container(
            content=_arrange_build(self.editor, self.selector()), 
            expand=True
        )

    def write_temp(self):
        "Auto-saves document after delay. Uses separate thread to avoid interruptions."
        # TODO: 
        # - (system settings) adjustable interval
        self.status["saved"] = False
        print("last hovered", self.hovered_field)
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


def _initial_fields_data():
    return {
        "h1_1": _field_data("h1", "", field_definitions["h1"]["settings"], 0),
        "text_1": _field_data("text", "", field_definitions["text"]["settings"], 1),
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


# def check_empty(e):
#     # print("test", value)
#     e.control.bgcolor = "#221818" if not e.control.value else "#111111"
#     # e.control.update()

def _define_field(field_id, data, fields, write_temp, controlled_elements, identify_field, select_fields, inspect):
    "Creates Flet object of requested type to document editor."
    info = data[field_id]
    field_type = info["type"]
    # match info["type"]:
    if field_type in ["h1", "h2", "h3", "text"]:
        # TODO 
        # - option to add right-side image #
        # base_on_change = EditorText.on_change
        control_layer = ControlLayer(EditorText.text_format(
            info["value"],
            text_type=field_type,
            # animate = ft.Animation(duration=300),
            on_change=lambda e: _update_field(e.control.value, field_id, data, fields, write_temp), 
        ))
    elif field_type == "table":
        # TODO
        # - add/remove column/line 
        columns = info["settings"][0]
        if "header" not in data[field_id]["value"]:
            data[field_id]["value"] = {"header": {}}
        control_layer = ControlLayer(ft.DataTable(
            columns = _table_columns(columns, field_id, data, fields, write_temp),
            rows = _table_rows(info["settings"], field_id, data, fields, write_temp),
            column_spacing=10,
            horizontal_margin=10,
            width={2: 500, 3: 550, 4: 600}[columns],
        ))
    elif field_type == "image":
        # TODO
        # - settings to add row of 1, 2, 3 #
        pass
        # return ft.Button(
        #     "Select image file",
        #     on_click=lambda e: _update_field(e.control.value, field_id, data, fields, write_temp)
        # )
    elif field_type == "link":
        # TODO 
        # - display text and link #
        pass
        # return ft.Row(controls=[
        #     ft.TextField(
        #         hint_text="Enter URL",
        #         on_submit=lambda e: _update_field(e.control.value, field_id, data, fields, write_temp)
        #     ),
        #     ft.Button(
        #         content="Press Enter to confirm",
        #     ),
        #     ft.Button(icon=ft.Icon(ft.Icons.MENU)),
        # ])
    elif field_type == "list":
        # TODO
        # - basic function
        # - checkbox and textfield
        # - subtext field? #
        pass
    elif field_type == "separator":
        control_layer = ft.Divider()
    control_layer.ignore_interactions = inspect
    controlled_elements.append(control_layer)
    return EditorContainer(control_layer, identify_field=identify_field, select_fields=select_fields, field_id=field_id)


def _table_columns(columns, field_id, data, fields, write_temp):
    "Generates pre-defined table columns."
    column_cells = []
    for x in range(columns):
        if x not in data[field_id]["value"]["header"]:
            data[field_id]["value"]["header"][x] = ""
        column_cells.append(ft.DataColumn(
            label=EditorText.text_format(
                data[field_id]["value"]["header"][x],
                width={2: 230, 3: 160, 4: 130}[columns],
                text_type="inset",
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
    for y in row_range:
        if f"row_{y}" not in data[field_id]["value"]:
            data[field_id]["value"][f"row_{y}"] = {}
        else:
            for x in col_range:
                if x not in data[field_id]["value"][f"row_{y}"]:
                    data[field_id]["value"][f"row_{y}"][x] = ""
    rows = [
        ft.DataRow(cells=[
            ft.DataCell(EditorText.text_format(
                data[field_id]["value"].get(f"row_{y}", {}).get(x, ""),
                width={2: 220, 3: 160, 4: 130}[settings[0]],
                text_type="inset",
                on_change=lambda e, x=x, y=y: _update_field(
                    e.control.value, field_id, data, fields, write_temp, column=x, row=f"row_{y}"
                )
            )) for x in col_range
        ]) for y in row_range
    ]
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
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
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

# def _switch_interaction(interaction):
#     # print(interaction)
#     if interaction:
#         interaction = False
#     else:
#         print("no change")
#     print(interaction)

def _define_options_field(dropdown, add_field, switch_interaction):
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
                    on_click=switch_interaction,
                    tooltip=MenuTooltip(message="Move field"),
                ),
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        ),
        bgcolor="#333333",
    )


def _arrange_editor(rebuild, fields, write_temp, controlled_elements, identify_field, select_fields, inspect):
    "Arranges the finished document editor fields into Flet column."
    column_controls = []
    print(fields)
    orded_fields = {k: v for k, v in sorted(fields.items(), key=lambda x: x[1]["position"])}
    for field_id in orded_fields.keys():
        column_controls.append(
            _define_field(field_id, fields, fields, write_temp, controlled_elements, identify_field, select_fields, inspect),
        )
        # column_controls.append(ft.Divider())
    rebuild(column_controls)
    # return ft.Column(
    #     controls=column_controls,
    #     expand=True,
    #     width=600,
    #     scroll=ft.ScrollMode.ADAPTIVE,
    #     alignment=ft.MainAxisAlignment.START
    # )


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