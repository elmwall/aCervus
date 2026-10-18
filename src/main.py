import flet as ft

# from ui.components import 
from ui.editor import Editor
from ui.sidebar import NavBar
from ui.file_options import Options

def run_editor():
    pass

def main(page: ft.Page):
    page.on_error = lambda e: print("Page error:", e.data)
    page.title = "aCervus"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 1000
    page.window.height = 700
    page.padding = 0
    # page.horizontal_alignment = ft.MainAxisAlignment.START
    # page.vertical_alignment = ft.CrossAxisAlignment.START

    editor = Editor()
    navbar = NavBar()
    options = Options()

    page.add(
        ft.Row(
            controls=[
                # ft.Button(content="test"),
                navbar.build(),
                editor.build(),
                options.build()
            ],
            # vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
            spacing=0,
            # padding=0
            # margin=ft.Margin.all(0),
        )
    )
    page.update()


    # editor = Editor()
    # editor.text_field(page)


if __name__ == "__main__":
    ft.run(main)



    