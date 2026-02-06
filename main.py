import flet as ft
import json
import datetime
import os


DATA_FILE = "data.json"


def main(page: ft.Page):
    page.title = "Расход"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN_700)
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 24
    page.bgcolor = ft.Colors.BLACK

    vehicles, personnel = [], []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            vehicles = data.get("vehicles", [])
            personnel = data.get("personnel", [])

    def create_state_dict(items):
        return {
            item: {
                "arrived": False,
                "arrival_time": None,
                "departure_time": None,
                "text": ft.Text("", size=13, color=ft.Colors.GREY_300),
            }
            for item in items
        }

    vehicle_states = create_state_dict(vehicles)
    personnel_states = create_state_dict(personnel)

    def save_data():
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"vehicles": vehicles, "personnel": personnel},
                f,
                ensure_ascii=False,
                indent=2,
            )

    def toggle_state(e, key, states):
        state = states[key]
        now = datetime.datetime.now().strftime("%H:%M")

        if not state["arrived"]:
            state.update({"arrived": True, "arrival_time": now, "departure_time": None})
            e.control.bgcolor = ft.Colors.GREEN_600
            state["text"].value = f"прибыл  {now}"
            state["text"].color = ft.Colors.GREEN_300
        else:
            state.update({"arrived": False, "departure_time": now})
            e.control.bgcolor = ft.Colors.GREY_800
            state["text"].value = f"убыл    {now}"
            state["text"].color = ft.Colors.RED_300

        e.control.color = ft.Colors.WHITE
        page.update()

    def create_button(text, states):
        return ft.FilledButton(
            text,
            width=160,
            height=48,
            on_click=lambda e: toggle_state(e, text, states),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            ),
        )

    def get_columns(width):
        return next(
            (
                col
                for limit, col in [(600, 2), (800, 3), (1000, 4), (float("inf"), 5)]
                if width < limit
            ),
            5,
        )

    def build_grid(items, states, columns):
        if not items:
            return ft.Text("Список пуст", color=ft.Colors.GREY_500, size=16)

        grid_items = [
            ft.Column(
                [create_button(item, states), states[item]["text"]],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                alignment=ft.MainAxisAlignment.CENTER,
            )
            for item in items
        ]

        return ft.GridView(
            controls=grid_items,
            runs_count=columns,
            max_extent=180,
            spacing=12,
            run_spacing=12,
            child_aspect_ratio=1.2,
            padding=0,
            expand=True,
        )

    def create_section_container():
        return ft.Container(
            border=ft.Border.all(1, ft.Colors.GREEN_900),
            border_radius=10,
            padding=16,
            bgcolor=ft.Colors.GREY_900,
            expand=True,
        )

    vehicles_container = create_section_container()
    personnel_container = create_section_container()
    main_container = ft.Container(expand=True)

    def create_input_row(label_text, button_text, on_click):
        field = ft.TextField(
            label=label_text,
            width=240,
            dense=True,
            border_color=ft.Colors.GREEN_800,
            focused_border_color=ft.Colors.GREEN_400,
        )
        button = ft.FilledButton(button_text, on_click=lambda e: on_click(field))
        return ft.Row(
            [field, button], spacing=12, alignment=ft.MainAxisAlignment.CENTER
        )

    def create_input_section(add_label, remove_label, lst, states):
        def add_item(field):
            if (val := field.value.strip()) and val not in lst:
                lst.append(val)
                states[val] = {
                    "arrived": False,
                    "arrival_time": None,
                    "departure_time": None,
                    "text": ft.Text("", size=13, color=ft.Colors.GREY_300),
                }
                save_data()
                refresh_layout()
                field.value = ""
            page.update()

        def remove_item(field):
            if (val := field.value.strip()) in lst:
                lst.remove(val)
                states.pop(val, None)
                save_data()
                refresh_layout()
                field.value = ""
            page.update()

        return ft.Column(
            [
                create_input_row(add_label, "Добавить", add_item),
                create_input_row(remove_label, "Удалить", remove_item),
            ],
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def refresh_layout(width=None):
        width = width or page.width
        columns = get_columns(width if width < 880 else (width - 160) // 2)

        vehicles_container.content = build_grid(vehicles, vehicle_states, columns)
        personnel_container.content = build_grid(personnel, personnel_states, columns)

        if width < 880:
            main_container.content = ft.Column(
                [
                    ft.Text(
                        "Транспортные средства",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_300,
                    ),
                    vehicles_container,
                    create_input_section(
                        "Добавить ТС", "Удалить ТС", vehicles, vehicle_states
                    ),
                    ft.Divider(height=30, color=ft.Colors.GREEN_900),
                    ft.Text(
                        "Командование",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_300,
                    ),
                    personnel_container,
                    create_input_section(
                        "Добавить", "Удалить", personnel, personnel_states
                    ),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )
        else:
            main_container.content = ft.Row(
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
                                "Добавить ТС", "Удалить ТС", vehicles, vehicle_states
                            ),
                        ],
                        spacing=16,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                    ),
                    ft.VerticalDivider(width=60, color=ft.Colors.GREEN_900),
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
                                "Добавить", "Удалить", personnel, personnel_states
                            ),
                        ],
                        spacing=16,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                    ),
                ],
                spacing=40,
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=True,
            )

        page.update()

    page.on_resize = lambda e: refresh_layout(page.width)
    page.add(main_container)
    refresh_layout()


if __name__ == "__main__":
    ft.app(target=main)
