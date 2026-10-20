import time
from threading import Thread
import json

import flet as ft

import ui.field_recepes as rec
import ui.conductor as cond



class Editor:
    "Managing editor area and connected data input."
    def __init__(self):
        self.temp_directory = "../temp_data/"
        self.timer = False
        self.fields_data = rec.initial_fields_data
        self.status = _status()
        INITIAL_SELCTION_KEY = "text"
        self.dropdown_selection = ft.Text(
            value=rec.field_definitions[INITIAL_SELCTION_KEY]["display"], 
            key=INITIAL_SELCTION_KEY
        )
        self.fields_column = ft.Column(
            controls=[],
            expand=True,
            width=600,
            scroll=ft.ScrollMode.ADAPTIVE,
            alignment=ft.MainAxisAlignment.START
        )
        self.editor = ft.GestureDetector(mouse_cursor=ft.MouseCursor.BASIC)
        self.inspect = False
        self.shield = ft.Container(
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.0, ft.Colors.BLACK),
            visible=False
        )
        self.controlled_elements = []
        self.hovered_field = None
        self.field_selection = None
        self.initial_seleciton = True

    def switch_interaction(self, check = False):
        if check: return self.inspect
        if self.inspect: 
            self.field_selection = None
            self.inspect = False 
            self.editor.mouse_cursor = ft.MouseCursor.BASIC
        else: 
            self.inspect = True
            self.initial_seleciton = True
            self.editor.mouse_cursor = ft.MouseCursor.CLICK
        for x in self.controlled_elements:
            print(x, x.ignore_interactions)
            x.ignore_interactions = self.inspect
        self.editor.update()

    def id_hovered_field(self, field_id):
        self.hovered_field = field_id

    def select_fields(self, field_id, drag = False, drop = False):
        print("select_fields:", field_id)
        if not field_id:
            raise ValueError("field_id could not be accessed for selection.")
            
        if self.inspect and self.initial_seleciton:
            self.field_selection = field_id
            self.initial_seleciton = False
            print("select_fields: define init")
        elif drag:
            print("select_fields: drag")
            self.field_selection = field_id
            self.initial_seleciton = False
        elif self.inspect or drop:
            print("success:", self.field_selection, field_id)
            self.fields_data = cond.relocate_field(self.fields_data, field_id, self.field_selection)
            tools = cond.BuildTools(None, self.fields_data, self.write_temp, self.controlled_elements, self.id_hovered_field, self.select_fields, self.inspect)
            cond.arrange_editor(self.rebuild, tools)
            self.field_selection = None

    def add_field(self):
        "Manages info for selected field and collects Flet object."
        field_id = cond.generate_id(self.dropdown_selection.key, self.fields_data)
        index = len(self.fields_column.controls)
        type_settings = rec.field_definitions[self.dropdown_selection.key]
        self.fields_data[field_id] = rec.field_data(
            self.dropdown_selection.key, type_settings["initial_value"], type_settings["settings"], index
        )
        tools = cond.BuildTools(field_id, self.fields_data, self.write_temp, self.controlled_elements, self.id_hovered_field, self.select_fields, self.inspect)
        self.fields_column.controls.insert(
            index, cond.define_field(tools)
        )
        self.fields_column.update()
    
    def selector(self):
        "Add new field to editor via dropdown selector and confirmation."
        self.dropdown = cond.define_dropdown(rec.field_definitions, self.dropdown_selection)
        return cond.define_options_field(self.dropdown, self.add_field, self.switch_interaction, self.inspect)

    def rebuild(self, new_controls):
        self.fields_column.controls.clear()
        self.fields_column.controls = new_controls

    def build(self):
        "Generate editor view with user input."
        tools = cond.BuildTools(None, self.fields_data, self.write_temp, self.controlled_elements, self.id_hovered_field, self.select_fields, self.inspect)
        cond.arrange_editor(self.rebuild, tools)
        self.editor = ft.GestureDetector(
            ft.Stack([
                    ft.Container(self.fields_column),
                    self.shield
                ], expand=True),
            mouse_cursor=ft.MouseCursor.BASIC,
            expand=True,
        )
        return ft.Container(
            content=cond.arrange_build(self.editor, self.selector()), 
            expand=True,
        )
    
    def write_temp(self):
        "Auto-saves document after delay. Uses separate thread to avoid interruptions."
        # TODO: 
        # - (system settings) adjustable interval
        self.status["saved"] = False
        if not self.status["queued"]:
            self.status["queued"] = True
            thread = Thread(target=_thread, args=(self.fields_data, self.status))
            thread.start()
        else:
            print("already queued")

        # Diagnostics
        print("last hovered", self.hovered_field)
        
        # TODO:
        # - export/import editing format with format tags
        # - repositioning field 
        # - remove field 
        # - naming and sync to formatted file
        # - (file options) export to md/txt/html? #


def _status():
    return {
        "saved": True,
        "queued": False
    }

        
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