import flet as ft

from ui.field_recepes import field_definitions
        

class ControlLayer(ft.Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.padding = ft.Padding(left=5, top=5, right=5, bottom=5)


class EditorContainer(ft.Container):
    def __init__(self, *args, identify_field = None, select_fields = None, field_id = None, **kwargs):
        self.field_id = field_id
        self.identify_field = identify_field
        self.select_fields = select_fields
        super().__init__(*args, **kwargs)
        self.expand = True
        self.bgcolor = "#111111"
        self.padding = ft.Padding(10)
        self.border_radius = 10
        self.animate = ft.Animation(duration=300)
        self.on_hover = self.indicate_field
        self.on_click = self.set_field

    def indicate_field(self, e):
        e.control.bgcolor = "#272C29" if e.data else "#111111"
        if self.identify_field is not None:
            self.identify_field(self.field_id)
        print(self.field_id)

    def set_field(self):
        if self.select_fields is not None:
            self.select_fields(self.field_id)


class EditorText(ft.TextField):
    def __init__(self, *args, value="", **kwargs):
        super().__init__(*args, **kwargs)
        self.border = ft.NoInputBorder()
        self.expand = True
        # self.bgcolor = "#221818"
        # self.on_change = lambda e: self.check_empty
        # self.padding = ft.Margin(10)
        self.value = value
        # self.animate = ft.Animation(duration=3000)

    # def check_empty(self, e):
    #     print("test", e.control.value)
    #     e.control.bgcolor = "#381F1F" if len(e.control.value) == 0 else "#111111"

    @classmethod
    def text_format(cls, value, text_type = "text", width = None, **kwargs):
        default_args = {"value": value}
        if text_type == "text":
            default_args.update({
                "text_style": ft.TextStyle(
                    size=16,
                    weight=ft.FontWeight.W_400
                )
            })
        elif text_type == "h1":
            default_args.update({
                "hint_text": "Title",
                "text_style": ft.TextStyle(
                    size=36,
                    weight=ft.FontWeight.W_600
                )
            })
        elif text_type == "h2":
            default_args.update({
                "hint_text": "Heading",
                "text_style": ft.TextStyle(
                    size=26,
                    weight=ft.FontWeight.W_500
                )
            })
        elif text_type == "h3":
            default_args.update({
                "hint_text": "Heading",
                "text_style": ft.TextStyle(
                    size=22,
                    weight=ft.FontWeight.W_400
                )
            })
        elif text_type == "inset":
            default_args.update({
                "text_style": ft.TextStyle(
                    size=14,
                    weight=ft.FontWeight.W_400
                ),
                "width": width
            })
        default_args.update(**kwargs)
        return cls(**default_args)


class MenuTooltip(ft.Tooltip):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bgcolor = "#30343A"
        self.text_style = ft.TextStyle(size=12, color=ft.Colors.GREEN_400)


class OptionsIcon(ft.IconButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = ft.ButtonStyle(shape=ft.RoundedRectangleBorder())