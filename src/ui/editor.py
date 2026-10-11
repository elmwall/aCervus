import flet as ft


class TextEditor(ft.TextField):
    def __init__(self):
        super().__init__()
        self.textfield = ft.TextField(multiline=True,
                                      autofocus=True,
                                      on_change=self.save_text)

    def heading(self):
        pass
        # super().

    def save_text(self) -> None:
        with open("save.txt", "w") as f:
            f.write(self.textfield)


class Editor(ft.Container):
    def __init__(self):
        # pass
        super().__init__()

    def text_field(self, page):
        # pass
        field: ft.TextField = ft.TextField(value="test")
        page.add(
            field
        )