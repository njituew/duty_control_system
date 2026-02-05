import flet as ft
import json
import datetime
import os


DATA_FILE = "data.json"


def main(page: ft.Page):
    page.title = "Система контроля ТС и командования"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN_700)
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 24
    page.bgcolor = ft.Colors.BLACK

    vehicles = []
    personnel = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            vehicles = data.get("vehicles", [])
            personnel = data.get("personnel", [])

    vehicle_states = {
        v: {
            "arrived": False,
            "arrival_time": None,
            "departure_time": None,
            "text": ft.Text("", size=13, color=ft.Colors.GREY_300),
        }
        for v in vehicles
    }
    personnel_states = {
        p: {
            "arrived": False,
            "arrival_time": None,
            "departure_time": None,
            "text": ft.Text("", size=13, color=ft.Colors.GREY_300),
        }
        for p in personnel
    }

    def save_data():
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"vehicles": vehicles, "personnel": personnel},
                f,
                ensure_ascii=False,
                indent=2,
            )

    def toggle_arrival(e, key: str, states: dict):
        state = states[key]
        now = datetime.datetime.now().strftime("%H:%M")

        if not state["arrived"]:
            state["arrived"] = True
            state["arrival_time"] = now
            e.control.bgcolor = ft.Colors.GREEN_600
            e.control.color = ft.Colors.WHITE
            state["text"].value = f"прибыл  {now}"
            state["text"].color = ft.Colors.GREEN_300
        else:
            state["arrived"] = False
            state["departure_time"] = now
            e.control.bgcolor = ft.Colors.GREY_800
            e.control.color = ft.Colors.WHITE70
            state["text"].value = f"убыл    {now}"
            state["text"].color = ft.Colors.RED_300

        page.update()

    def create_item_button(text: str, states: dict):
        return ft.FilledButton(
            text,
            width=158,
            height=48,
            on_click=lambda e: toggle_arrival(e, text, states),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            ),
        )

    def build_grid(items: list, states: dict, columns: int = 3):
        controls = []
        row = []

        for item in items:
            col = ft.Column(
                [
                    create_item_button(item, states),
                    states[item]["text"],
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                tight=True,
            )
            row.append(col)

            if len(row) == columns:
                controls.append(
                    ft.Row(
                        row,
                        alignment=ft.MainAxisAlignment.START,
                        spacing=16,
                        run_spacing=12,
                    )
                )
                row = []

        if row:
            controls.append(
                ft.Row(
                    row,
                    alignment=ft.MainAxisAlignment.START,
                    spacing=16,
                    run_spacing=12,
                )
            )

        return ft.Column(
            controls,
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    vehicles_container = ft.Container(
        content=build_grid(vehicles, vehicle_states),
        height=480,
        width=540,
        border=ft.Border.all(1, ft.Colors.GREEN_900),
        border_radius=10,
        padding=16,
        bgcolor=ft.Colors.GREY_900,
    )

    personnel_container = ft.Container(
        content=build_grid(personnel, personnel_states),
        height=480,
        width=540,
        border=ft.Border.all(1, ft.Colors.GREEN_900),
        border_radius=10,
        padding=16,
        bgcolor=ft.Colors.GREY_900,
    )

    def refresh():
        vehicles_container.content = build_grid(vehicles, vehicle_states)
        personnel_container.content = build_grid(personnel, personnel_states)
        page.update()

    refresh()

    def create_input_section(
        label_new: str, label_remove: str, lst: list, states: dict
    ):
        new_field = ft.TextField(
            label=label_new,
            width=220,
            dense=True,
            border_color=ft.Colors.GREEN_800,
            focused_border_color=ft.Colors.GREEN_400,
        )
        add_btn = ft.FilledButton(
            "Добавить",
            on_click=lambda e: add(new_field, lst, states),
        )

        remove_field = ft.TextField(
            label=label_remove,
            width=220,
            dense=True,
            border_color=ft.Colors.GREEN_800,
            focused_border_color=ft.Colors.GREEN_400,
        )
        remove_btn = ft.OutlinedButton(
            "Удалить",
            on_click=lambda e: remove(remove_field, lst, states),
        )

        return ft.Column(
            [
                ft.Row([new_field, add_btn], spacing=12),
                ft.Row([remove_field, remove_btn], spacing=12),
            ],
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def add(field: ft.TextField, lst: list, states: dict):
        val = field.value.strip()
        if val and val not in lst:
            lst.append(val)
            states[val] = {
                "arrived": False,
                "arrival_time": None,
                "departure_time": None,
                "text": ft.Text("", size=13, color=ft.Colors.GREY_300),
            }
            save_data()
            refresh()
            field.value = ""
            page.update()

    def remove(field: ft.TextField, lst: list, states: dict):
        val = field.value.strip()
        if val in lst:
            lst.remove(val)
            states.pop(val, None)
            save_data()
            refresh()
            field.value = ""
            page.update()

    page.add(
        ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                "Транспортные средства",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREEN_300,
                            ),
                            vehicles_container,
                            create_input_section(
                                "Новый номер авто",
                                "Удалить номер",
                                vehicles,
                                vehicle_states,
                            ),
                        ],
                        spacing=16,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                    ),
                    ft.VerticalDivider(width=80, color=ft.Colors.GREEN_900),
                    ft.Column(
                        [
                            ft.Text(
                                "Командование",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREEN_300,
                            ),
                            personnel_container,
                            create_input_section(
                                "Новое ФИО", "Удалить ФИО", personnel, personnel_states
                            ),
                        ],
                        spacing=16,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=40,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            expand=True,
            padding=20,
        )
    )


if __name__ == "__main__":
    ft.app(main)
