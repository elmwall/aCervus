import secrets
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
        self.fields = rec.initial_fields_data
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
        self.editor = None
        self.inspect = False
        self.shield = ft.Container(
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.0, ft.Colors.BLACK),
            visible=False
        )
        self.controlled_elements = []
        self.hovered_field = None
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
            self.fields = cond.relocate_field(self.fields, field_id, self.field_selection)
            cond.arrange_editor(self.rebuild, self.fields, self.write_temp, self.controlled_elements, self.identify_field, self.select_fields, self.inspect)
            self.field_selection = None

    def add_field(self):
        "Manages info for selected field and collects Flet object."
        field_id = cond.generate_id(self.dropdown_selection.key, self.fields)
        index = len(self.fields_column.controls)
        self.fields[field_id] = rec.field_data(
            self.dropdown_selection.key, "", rec.field_definitions[self.dropdown_selection.key]["settings"], index
        )
        self.fields_column.controls.insert(
            index, cond.define_field(field_id, self.fields, self.fields, self.write_temp, self.controlled_elements, self.identify_field, self.select_fields, self.inspect)
        )
        self.fields_column.update()
    
    def selector(self):
        "Add new field to editor via dropdown selector and confirmation."
        self.dropdown = cond.define_dropdown(rec.field_definitions, self.dropdown_selection)
        return cond.define_options_field(self.dropdown, self.add_field, self.switch_interaction)

    def rebuild(self, new_controls):
        self.fields_column.controls.clear()
        self.fields_column.controls = new_controls

    def build(self):
        "Generate editor view with user input."
        cond.arrange_editor(self.rebuild, self.fields, self.write_temp, self.controlled_elements, self.identify_field, self.select_fields, self.inspect)
        self.editor = ft.Stack([
            ft.Container(self.fields_column),
            self.shield
        ], expand=True)
        return ft.Container(
            content=cond.arrange_build(self.editor, self.selector()), 
            expand=True
        )

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