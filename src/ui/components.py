import flet as ft
        

class ControlLayer(ft.Container):
    "Access point for disabling interaction of editor function during field actions."
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.padding = ft.Padding(left=5, top=5, right=5, bottom=5)
        self.expand = True


class EditorContainer(ft.Container):
    "Frame for editor fields with shared style and functions."
    def __init__(self, *args, id_hovered_field = None, select_field = None, field_id = None, **kwargs):
        self.field_id = field_id
        self.id_hovered_field = id_hovered_field
        self.select_field = select_field
        super().__init__(*args, **kwargs)
        self.expand = True
        self.bgcolor = "#111111"
        self.padding = ft.Padding(10)
        self.border_radius = 10
        self.animate = ft.Animation(duration=300)
        self.on_hover = self.indicate_field
        self.on_click = self.set_field

    def indicate_field(self, e = None):
        "Color highlight upon hovering on editor field."
        if e: e.control.bgcolor = "#272C29" if e.data else "#111111"
        if callable(self.id_hovered_field):
            self.id_hovered_field(self.field_id)
        print("field:", self.field_id)
        return self.field_id

    def set_field(self):
        "Records the id of the field in question upon click."
        if callable(self.select_field):
            self.select_field(self.field_id)
        print("selected:", self.field_id)


class EditorText(ft.TextField):
    "Text field with adapted functions for specific types/levels of text."
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border = ft.NoInputBorder()
        self.expand = True
        # self.ma
    
    @classmethod
    def text_format(cls, value="", text_type = "text", width = None, **kwargs):
        default_args = {"value": value}
        if text_type == "text":
            default_args.update({
                # "text_style": ft.TextStyle(size=16, weight=ft.FontWeight.W_400, font_family="Consolas"),
                "text_style": ft.TextStyle(size=16, weight=ft.FontWeight.W_400),
                "multiline": True,
            })
        elif text_type == "h1":
            default_args.update({
                "hint_text": "Title",
                "text_style": ft.TextStyle(size=36, weight=ft.FontWeight.W_600)
            })
        elif text_type == "h2":
            default_args.update({
                "hint_text": "Heading",
                "text_style": ft.TextStyle(size=26, weight=ft.FontWeight.W_500)
            })
        elif text_type == "h3":
            default_args.update({
                "hint_text": "Heading",
                "text_style": ft.TextStyle(size=22, weight=ft.FontWeight.W_400)
            })
        elif text_type == "inset":
            default_args.update({
                "text_style": ft.TextStyle(size=14, weight=ft.FontWeight.W_400),
                "width": width,
                "dense": True,
                "multiline": True
            })
        default_args.update(**kwargs)
        return cls(**default_args)


class MenuTooltip(ft.Tooltip):
    "Style and settings for tool-tips on hover."
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bgcolor = "#30343A"
        self.text_style = ft.TextStyle(size=12, color=ft.Colors.GREEN_400)


class OptionsIcon(ft.IconButton):
    "Style and settings for icons in options bar."
    def __init__(self, *args, radius = 0, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=radius)
        )