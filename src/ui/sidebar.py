import flet as ft
# from flet import *
# from functools import partial

class NavBar:
    def __init__(self):
        super().__init__()
        self.width_base = 50
        self.width_expanded = 150
        self.height = 640

    def animate(self, e):
        e.control.width = self.width_expanded if e.data else self.width_base
        e.control.update()

    def options(self):
        return ft.Column(
            controls=[
                ft.Button(content="Editor"),
                ft.Button(content="Subjects"),
                ft.Button(content="History"),
                ft.Button(content="Tree"),
                ft.Divider(),
                ft.Text(value="Latest")
            ],
            expand=True,
        )

    def previous_files(self):
        pass

    def build(self):
        container = ft.Row(
            controls=[ft.Container(
                content=self.options(),
                width=self.width_base,
                # height=self.height,
                # expand=True,
                bgcolor="#222222",
                on_hover=self.animate,
                animate=ft.Animation(duration=300, curve=ft.AnimationCurve.EASE_OUT),
            )],
            width=150,
            spacing=0
        )
        # self.animate(container)

        return container