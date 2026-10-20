import secrets

import flet as ft

from ui.components import (ControlLayer,
                           EditorContainer,
                           EditorText,
                           MenuTooltip,
                           OptionsIcon)



class BuildTools:
    """
    Tools and information for updating editor build and inputs.

    Args:
        field_id (str | None): *local* id for field and key in editor_field_inputs  
        editor_field_inputs (dict): collected information on alls fields with settings and updated inputs  
        write_temp (function): call to write temporary info to file  
        controlled_elements (list): editor layer access point for blocking interaction  
        id_hovered_field (function): call to record hovered field globally  
        select_field (function): call to collect id for field adjustments  
        inspect (bool): switch for field input/adjustment modes

    Access stored arguments through `buildtools_instance.<attribute>`
    """
    field_data: dict | None
    def __init__(self, 
                 field_id: str | None, 
                 editor_field_inputs: dict, 
                 write_temp: callable, 
                 controlled_elements: list[ControlLayer], 
                 id_hovered_field: callable, 
                 select_field: callable, 
                 inspect: bool):


        self.field_id = field_id
        self.editor_field_inputs = editor_field_inputs
        self.write_temp = write_temp
        self.field_data = editor_field_inputs[field_id] if field_id else None
        self.controlled_elements = controlled_elements
        self.id_hovered_field = id_hovered_field
        self.select_field = select_field
        self.inspect = inspect

    def update_fields(self, field_id: str):
        "Adds new current id and "
        self.field_id = field_id
        self.field_data = self.editor_field_inputs[field_id] 


def define_field(tools: BuildTools):
    "Creates Flet object of requested type to document editor."
    field_id = tools.field_id
    info = tools.field_data
    field_type = info["type"]
    if field_type in ["h1", "h2", "h3", "text"]:
        # TODO 
        # - option to add right-side image #
        # base_on_change = EditorText.on_change
        control_layer = ControlLayer(EditorText.text_format(
            info["value"],
            text_type=field_type,
            # animate = ft.Animation(duration=300),
            on_change=lambda e: record_field(e.control.value, tools), 
        ))
    elif field_type == "table":
        # TODO
        # - add/remove column/line 
        columns = info["settings"][0]
        if "header" not in info["value"]:
            info["value"] = {"header": {}}
        control_layer = ControlLayer(ft.DataTable(
            columns = _table_columns(columns, tools),
            rows = _table_rows(info["settings"], tools),
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
        #     on_click=lambda e: record_field(e.control.value, tools)
        # )
    elif field_type == "link":
        # TODO 
        # - display text and link #
        pass
        # return ft.Row(controls=[
        #     ft.TextField(
        #         hint_text="Enter URL",
        #         on_submit=lambda e: record_field(e.control.value, tools)
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
        list_values = info["value"]
        print(tools.editor_field_inputs)
        list_tiles = _build_list([], list_values, tools)
        list_view = ft.ReorderableListView(
            controls=list_tiles,
            show_default_drag_handles=False,
            on_reorder=lambda e: _reorder_list(list_values, e.old_index, e.new_index, e, tools),
        )
        control_layer = ControlLayer(ft.Column(controls=[list_view, ft.Row(controls=[OptionsIcon(icon=ft.Icons.ADD), OptionsIcon(icon=ft.Icons.REMOVE)])]))
    elif field_type == "separator":
        control_layer = ft.Divider()
    control_layer.ignore_interactions = tools.inspect
    tools.controlled_elements.append(control_layer)
    def id_picked_up(select_field, field_id):
        print("picked up:", field_id)
        select_field(field_id, drag=True)
    def id_dropped(selected_fields, field_id):
        print(f"dropped in {field_id}")
        selected_fields(field_id, drop=True)
    drag_handle = ft.Draggable(
        OptionsIcon(icon=ft.Icons.MENU, radius=20), 
        on_drag_start=lambda e: id_picked_up(tools.select_field, field_id),
    )
    field_object = EditorContainer(
        content=ft.Row(controls=[control_layer, drag_handle]), 
        id_hovered_field=tools.id_hovered_field, 
        select_field=tools.select_field, 
        field_id=field_id
    )
    return ft.DragTarget(
        field_object,
        on_accept=lambda e: id_dropped(tools.select_field, field_id)
    )


def _table_columns(columns, tools):
    "Generates pre-defined table columns."
    table_header = tools.editor_field_inputs[tools.field_id]["value"]["header"]
    column_cells = []
    for x in range(columns):
        if x not in table_header:
            table_header[x] = ""
        column_cells.append(ft.DataColumn(label=EditorText.text_format(
            table_header[x],
            width={2: 230, 3: 160, 4: 130}[columns],
            text_type="inset",
            on_change=lambda e, x=x: record_field(
                e.control.value, tools, column=x
            )
        )))
    return column_cells


def _table_rows(settings, tools):
    "Generates pre-defined table rows with column cells."
    col_range, row_range = range(settings[0]), range(settings[1])
    table_data = tools.editor_field_inputs[tools.field_id]["value"]
    for y in row_range:
        if f"row_{y}" not in table_data:
            table_data[f"row_{y}"] = {}
        else:
            for x in col_range:
                if x not in table_data[f"row_{y}"]:
                    table_data[f"row_{y}"][x] = ""
    
    width = {2: 220, 3: 160, 4: 130}[settings[0]]
    rows = []
    for y in row_range:
        row_cells = [ft.DataCell(EditorText.text_format(
            table_data.get(f"row_{y}", {}).get(x, ""),
            width=width,
            text_type="inset",
            on_change=lambda e, x=x, y=y: record_field(
                e.control.value, tools, column=x, row=f"row_{y}"
            )
        )) for x in col_range]
        row = ft.DataRow(cells=row_cells)
        rows.append(row)
    return rows


def _edit_list(list_values, index, value, text):
    """
    Edit list function for stored values:
    - Updated point: removes/reinserts updated point
    """
    list_values[index] = [value, text]
    print(list_values)
    return list_values


def _reorder_list(list_values, old_index, new_index, e, tools):
    """
    Edit list function for ListTiles:
    - Reordering: removes index and inserts value at new index
    - Rebuilds ListTiles
    """
    value = list_values.pop(old_index)
    list_values.insert(new_index, value)
    print(list_values)
    _build_list(e.control.controls, list_values, tools)
    e.control.update()
    return list_values


def _build_list(list_tiles, list_values, tools):
    info = tools.field_data
    length = info["settings"]["length"]
    list_tiles.clear()
    for x in range(0, length):
        if info["settings"]["use_checkbox"]:
            indicator = ft.Checkbox(
                value=list_values[x][0], 
                scale=0.75,
                margin=ft.Margin(top=-9),
                on_change=lambda e, x=x: record_field(
                    _edit_list(list_values, x, e.control.value, list_values[x][1]), tools
                )
            )
        else:
            indicator = ft.Text("–")
        text_object = EditorText.text_format(
            value=list_values[x][1],
            text_type="inset",
            on_change=lambda e, x=x: record_field(
                _edit_list(list_values, x, list_values[x][0], e.control.value), tools
            ),
        )
        list_tiles.append(ft.ListTile(
            title=ft.Row(controls=[ft.ReorderableDragHandle(indicator), text_object], vertical_alignment=ft.CrossAxisAlignment.START), 
            dense=True, 
            visual_density=ft.VisualDensity.COMPACT)
        )
    return list_tiles


def define_dropdown(field_definitions, dropdown_selection):
    "Generates PopupMenuButton as a dropdown selector field for editor options."
    dropdown_options = []
    def _selection(e):
        dropdown_selection.key = e.control.data
        dropdown_selection.value = e.control.content
    for key in field_definitions.keys():
        dropdown_options.append(ft.PopupMenuItem(
            content=field_definitions[key]["display"], 
            data=key,
            height=30,
            on_click=_selection
        ))

    return ft.PopupMenuButton(
        items=dropdown_options,
        menu_position=ft.PopupMenuPosition.OVER,
        tooltip=MenuTooltip(message="Select field"),
        margin=ft.Margin(left=5, right=5),
        content=ft.Container(
            width=110,
            height=30,
            bgcolor="#444444",
            padding=ft.Padding(left=8),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[dropdown_selection, 
                          ft.Icon(ft.Icons.ARROW_DROP_UP, size=20)],
            ),
        ),
    )


# def _switch_interaction(interaction):
#     # print(interaction)
#     if interaction:
#         interaction = False
#     else:
#         print("no change")
#     print(interaction)


def define_options_field(dropdown, add_field, switch_interaction, inspect):
    "Generates and arranges Flet objects for editor options field."
    # TODO 
    # add option for direct save 
    # add position selector 
    # - #
    def switch(e, is_active):
        e.control.selected = False if switch_interaction(check=True) else True
        e.control.bgcolor = "#5F4444" if is_active else "#333333"
        e.control.update()

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
                    bgcolor="#333333",
                    selected=False,
                    on_click=lambda e: (switch_interaction(), switch(e, switch_interaction(check=True))),
                    tooltip=MenuTooltip(message="Move field"),
                ),
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        ),
        bgcolor="#333333",
    )


def arrange_editor(rebuild, tools):
    "Arranges the finished document editor fields into Flet column."
    column_controls = []
    print(tools.editor_field_inputs)
    orded_fields = {k: v for k, v in sorted(tools.editor_field_inputs.items(), key=lambda x: x[1]["position"])}
    for field_id in orded_fields.keys():
        tools.update_fields(field_id)
        column_controls.append(
            define_field(tools),
        )
    rebuild(column_controls)


def arrange_build(editor_fields, selector):
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


def record_field(value, tools, column=None, row=None):
    "Syncronizes document changes to internal dict."
    field_data = tools.field_data
    if field_data["type"] == "table":
        if row is None:
            field_data["value"]["header"].update({column: value})
        else:
            field_data["value"][row][column] = value
    elif field_data["type"] == "list":
        field_data["value"] = value
    else:
        field_data["value"] = value
    print(tools.editor_field_inputs)
    tools.write_temp()


def generate_id(selected_type, existing_ids):
    "Creates unique IDs for new document editor fields."
    while True:
        suffix = secrets.token_hex(2)
        field_id = f"{selected_type}_{suffix}"
        if field_id not in existing_ids:
            return field_id


def relocate_field(editor_field_inputs, field_id, field_selection):
    origin = editor_field_inputs[field_selection]["position"]
    editor_field_inputs[field_selection]["position"] = editor_field_inputs[field_id]["position"]
    for x, y in editor_field_inputs.items():
        if x == field_selection:
            continue
        elif origin > editor_field_inputs[field_selection]["position"]:
            if y["position"] in range(editor_field_inputs[field_selection]["position"], origin):
                y["position"] += 1
        elif origin < editor_field_inputs[field_selection]["position"]:
            print(range(origin, editor_field_inputs[field_selection]["position"]))
            if y["position"] in range(origin, editor_field_inputs[field_selection]["position"] + 1):
                y["position"] -= 1
    return editor_field_inputs