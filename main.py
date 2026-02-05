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
            width=160,
            height=48,
            on_click=lambda e: toggle_arrival(e, text, states),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            ),
        )

    # Адаптивные функции
    def get_columns_count(width: float) -> int:
        if width < 600:
            return 2
        elif width < 800:
            return 3
        elif width < 1000:
            return 4
        else:
            return 5

    def build_grid(items: list, states: dict, columns: int):
        if not items:
            return ft.Text("Список пуст", color=ft.Colors.GREY_500, size=16)

        grid_items = []
        for i, item in enumerate(items):
            grid_items.append(
                ft.Column(
                    [
                        create_item_button(item, states),
                        states[item]["text"],
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )

        return ft.GridView(
            controls=grid_items,
            runs_count=columns,
            max_extent=180,  # максимальная ширина колонки
            spacing=12,
            run_spacing=12,
            child_aspect_ratio=1.2,
            padding=0,
            expand=True,
        )

    def build_vertical_grid(items: list, states: dict):
        if not items:
            return ft.Text("Список пуст", color=ft.Colors.GREY_500, size=16)

        return ft.Column(
            [
                ft.Row(
                    [
                        create_item_button(item, states),
                        states[item]["text"],
                    ],
                    spacing=16,
                    alignment=ft.MainAxisAlignment.CENTER,
                )
                for item in items
            ],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    # Создание контейнеров
    vehicles_container = ft.Container(
        border=ft.Border.all(1, ft.Colors.GREEN_900),
        border_radius=10,
        padding=16,
        bgcolor=ft.Colors.GREY_900,
        expand=True,
    )

    personnel_container = ft.Container(
        border=ft.Border.all(1, ft.Colors.GREEN_900),
        border_radius=10,
        padding=16,
        bgcolor=ft.Colors.GREY_900,
        expand=True,
    )

    # Основной контейнер
    main_container = ft.Container(expand=True)

    def refresh_layout(width: float = None):
        if width is None:
            width = page.width

        # Определяем режим отображения
        if width < 880:
            # Вертикальный режим
            columns = get_columns_count(width)

            vehicles_container.content = build_grid(vehicles, vehicle_states, columns)
            personnel_container.content = build_grid(
                personnel, personnel_states, columns
            )

            main_container.content = ft.Column(
                [
                    # Секция ТС
                    ft.Text(
                        "Транспортные средства",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_300,
                    ),
                    vehicles_container,
                    create_input_section(
                        "Добавить ТС",
                        "Удалить ТС",
                        vehicles,
                        vehicle_states,
                    ),
                    ft.Divider(height=30, color=ft.Colors.GREEN_900),
                    # Секция командования
                    ft.Text(
                        "Командование",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_300,
                    ),
                    personnel_container,
                    create_input_section(
                        "Добавить",
                        "Удалить",
                        personnel,
                        personnel_states,
                    ),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )
        else:
            # Горизонтальный режим
            columns = get_columns_count((width - 160) // 2)

            vehicles_container.content = build_grid(vehicles, vehicle_states, columns)
            personnel_container.content = build_grid(
                personnel, personnel_states, columns
            )

            main_container.content = ft.Row(
                [
                    # Левая колонка - ТС
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
                                "Добавить ТС",
                                "Удалить ТС",
                                vehicles,
                                vehicle_states,
                            ),
                        ],
                        spacing=16,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                    ),
                    ft.VerticalDivider(width=60, color=ft.Colors.GREEN_900),
                    # Правая колонка - командование
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
                                "Добавить",
                                "Удалить",
                                personnel,
                                personnel_states,
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

    def on_resize(e):
        refresh_layout(page.width)

    page.on_resize = on_resize

    def create_input_section(label_add, label_remove, lst, states):
        new_field = ft.TextField(
            label=label_add,
            width=240,
            dense=True,
            border_color=ft.Colors.GREEN_800,
            focused_border_color=ft.Colors.GREEN_400,
        )
        add_btn = ft.FilledButton(
            "Добавить", on_click=lambda e: add(new_field, lst, states)
        )

        rem_field = ft.TextField(
            label=label_remove,
            width=240,
            dense=True,
            border_color=ft.Colors.GREEN_800,
            focused_border_color=ft.Colors.GREEN_400,
        )
        rem_btn = ft.OutlinedButton(
            "Удалить", on_click=lambda e: remove(rem_field, lst, states)
        )

        return ft.Column(
            [
                ft.Row(
                    [new_field, add_btn],
                    spacing=12,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [rem_field, rem_btn],
                    spacing=12,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
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
            refresh_layout()
            field.value = ""
        page.update()

    def remove(field: ft.TextField, lst: list, states: dict):
        val = field.value.strip()
        if val in lst:
            lst.remove(val)
            states.pop(val, None)
            save_data()
            refresh_layout()
            field.value = ""
        page.update()

    # Добавляем основной контейнер на страницу
    page.add(main_container)

    # Первоначальная настройка
    refresh_layout()


if __name__ == "__main__":
    ft.app(target=main)
