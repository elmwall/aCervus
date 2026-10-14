import flet as ft


class Options:
    def __init__(self):
        super().__init__()
        self.width_base = 200
        self.width_expanded = 150
        self.height = 640

    def animate(self, e):
        e.control.width = self.width_expanded if e.data else self.width_base
        e.control.update()

    def build(self):
        # return ft.Container(
        #     alignment=ft.Alignment.TOP_RIGHT,
        #     width=self.width_base,
        #     height=self.height,
        #     bgcolor="#222222",
        #     on_hover=self.animate,
        #     animate=ft.Animation(duration=300, curve=ft.AnimationCurve.EASE_OUT),
        # )
        container = ft.Row(
            controls=[ft.Container(
                content=ft.Button(content="test"),
                # alignment=ft.Alignment.CENTER_RIGHT,
                width=self.width_base,
                # height=self.height,
                bgcolor="#222222",
                expand=True,
                # on_hover=self.animate,
                # animate=ft.Animation(duration=300, curve=ft.AnimationCurve.EASE_OUT),
            )],
            # alignment=ft.MainAxisAlignment.END,
            width=200
        )
        # self.animate(container)

        return container