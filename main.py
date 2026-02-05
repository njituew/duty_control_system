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
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 20

    # Загрузка данных из JSON
    vehicles = []
    personnel = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            vehicles = data.get("vehicles", [])
            personnel = data.get("personnel", [])

    # Состояния для автомобилей и персонала (не сохраняются)
    vehicle_states = {
        veh: {
            "arrived": False,
            "arrival_time": None,
            "departure_time": None,
            "text_control": ft.Text(""),
        }
        for veh in vehicles
    }
    personnel_states = {
        pers: {
            "arrived": False,
            "arrival_time": None,
            "departure_time": None,
            "text_control": ft.Text(""),
        }
        for pers in personnel
    }

    # Функция для сохранения списков в JSON
    def save_data():
        data = {"vehicles": vehicles, "personnel": personnel}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # Функция для обработки нажатия кнопки (общая для авто и персонала)
    def toggle_state(e, key, states):
        state = states[key]
        if not state["arrived"]:
            state["arrived"] = True
            state["arrival_time"] = datetime.datetime.now().strftime("%H:%M:%S")
            e.control.bgcolor = ft.Colors.GREEN_500
            state["text_control"].value = f"Прибыла в {state['arrival_time']}"
        else:
            state["arrived"] = False
            state["departure_time"] = datetime.datetime.now().strftime("%H:%M:%S")
            e.control.bgcolor = ft.Colors.GREY_800
            state["text_control"].value = f"Убыла в {state['departure_time']}"
        page.update()

    # Функция для создания ряда с кнопкой и текстом
    def create_item_row(text, states):
        button = ft.ElevatedButton(
            text,
            bgcolor=ft.Colors.GREY_800,
            color=ft.Colors.WHITE,
            on_click=lambda e: toggle_state(e, text, states),
            width=150,
            height=50,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )
        text_control = states[text]["text_control"]
        return ft.Row(
            [button, text_control],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # Контейнеры для таблиц
    vehicles_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    personnel_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

    # Обновление таблиц
    def update_tables():
        vehicles_container.controls = [
            create_item_row(veh, vehicle_states) for veh in vehicles
        ]
        personnel_container.controls = [
            create_item_row(pers, personnel_states) for pers in personnel
        ]
        page.update()

    # Инициализация таблиц
    update_tables()

    # UI для добавления/удаления
    new_vehicle_field = ft.TextField(
        label="Новый номер авто",
        width=200,
        border_color=ft.Colors.GREEN_700,
        focused_border_color=ft.Colors.GREEN_400,
    )
    add_vehicle_btn = ft.ElevatedButton(
        "Добавить авто",
        on_click=lambda e: add_item(new_vehicle_field, vehicles, vehicle_states),
    )
    remove_vehicle_field = ft.TextField(
        label="Удалить номер авто",
        width=200,
        border_color=ft.Colors.GREEN_700,
        focused_border_color=ft.Colors.GREEN_400,
    )
    remove_vehicle_btn = ft.ElevatedButton(
        "Удалить авто",
        on_click=lambda e: remove_item(remove_vehicle_field, vehicles, vehicle_states),
    )

    new_personnel_field = ft.TextField(
        label="Новое ФИО",
        width=200,
        border_color=ft.Colors.GREEN_700,
        focused_border_color=ft.Colors.GREEN_400,
    )
    add_personnel_btn = ft.ElevatedButton(
        "Добавить ФИО",
        on_click=lambda e: add_item(new_personnel_field, personnel, personnel_states),
    )
    remove_personnel_field = ft.TextField(
        label="Удалить ФИО",
        width=200,
        border_color=ft.Colors.GREEN_700,
        focused_border_color=ft.Colors.GREEN_400,
    )
    remove_personnel_btn = ft.ElevatedButton(
        "Удалить ФИО",
        on_click=lambda e: remove_item(
            remove_personnel_field, personnel, personnel_states
        ),
    )

    # Функции добавления/удаления
    def add_item(field, list_, states):
        value = field.value.strip()
        if value and value not in list_:
            list_.append(value)
            states[value] = {
                "arrived": False,
                "arrival_time": None,
                "departure_time": None,
                "text_control": ft.Text(""),
            }
            save_data()
            update_tables()
            field.value = ""
            page.update()

    def remove_item(field, list_, states):
        value = field.value.strip()
        if value in list_:
            list_.remove(value)
            del states[value]
            save_data()
            update_tables()
            field.value = ""
            page.update()

    # Основной layout
    main_row = ft.Row(
        [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Транспортные средства",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        vehicles_container,
                        ft.Row([new_vehicle_field, add_vehicle_btn]),
                        ft.Row([remove_vehicle_field, remove_vehicle_btn]),
                    ],
                    spacing=20,
                ),
                border=ft.border.all(1, ft.Colors.GREEN_900),
                border_radius=8,
                padding=10,
                width=400,
                bgcolor=ft.Colors.GREY_900,
            ),
            ft.Container(width=50),  # Разделитель
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Командование организации",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        personnel_container,
                        ft.Row([new_personnel_field, add_personnel_btn]),
                        ft.Row([remove_personnel_field, remove_personnel_btn]),
                    ],
                    spacing=20,
                ),
                border=ft.border.all(1, ft.Colors.GREEN_900),
                border_radius=8,
                padding=10,
                width=400,
                bgcolor=ft.Colors.GREY_900,
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=20,
    )

    page.add(main_row)


ft.app(target=main)
