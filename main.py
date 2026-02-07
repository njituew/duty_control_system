import flet as ft
import json
import datetime
import os

DATA_FILE = "data.json"


def main(page: ft.Page):
    page.title = "Расход"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.BLACK
    page.padding = 24

    vehicles, personnel = [], []

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            vehicles = data.get("vehicles", [])
            personnel = data.get("personnel", [])

    def save_data():
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"vehicles": vehicles, "personnel": personnel},
                f,
                ensure_ascii=False,
                indent=2,
            )

    def init_states(items, is_vehicle):
        return {
            item: {
                "arrived": False,
                "text": ft.Text("", size=13, color=ft.Colors.GREY_300),
                "is_vehicle": is_vehicle,
            }
            for item in items
        }

    vehicle_states = init_states(vehicles, True)
    personnel_states = init_states(personnel, False)

    # ---------------- dialogs & overlays ----------------

    def show_dialog(dialog: ft.AlertDialog):
        page.overlay.clear()
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def close_dialog(e=None):
        if page.overlay:
            page.overlay[0].open = False
            page.update()

    def show_snackbar(text, undo=None):
        page.snack_bar = ft.SnackBar(
            ft.Row(
                [
                    ft.Text(text),
                    (
                        ft.TextButton("Отменить", on_click=undo)
                        if undo
                        else ft.Container()
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
        )
        page.snack_bar.open = True
        page.update()

    # ---------------- add / delete ----------------

    def open_add_dialog(title, lst, states, is_vehicle):
        field = ft.TextField(label="ФИО / номер ТС", autofocus=True)

        def confirm(e):
            val = field.value.strip()
            if val and val not in lst:
                lst.append(val)
                states[val] = {
                    "arrived": False,
                    "text": ft.Text("", size=13, color=ft.Colors.GREY_300),
                    "is_vehicle": is_vehicle,
                }
                save_data()
                refresh_layout()
                show_snackbar(f"Добавлено: {val}")
            close_dialog()

        show_dialog(
            ft.AlertDialog(
                title=ft.Text(title),
                content=field,
                actions=[
                    ft.TextButton("Отмена", on_click=close_dialog),
                    ft.FilledButton("Добавить", on_click=confirm),
                ],
            )
        )

    def open_delete_dialog(name, states):
        lst = vehicles if states[name]["is_vehicle"] else personnel
        removed = states[name]

        def confirm(e):
            lst.remove(name)
            states.pop(name)
            save_data()
            refresh_layout()

            def undo(e):
                lst.append(name)
                states[name] = {
                    "arrived": removed["arrived"],
                    "text": ft.Text("", size=13, color=ft.Colors.GREY_300),
                    "is_vehicle": removed["is_vehicle"],
                }
                save_data()
                refresh_layout()

            show_snackbar(f"Удалено: {name}", undo)
            close_dialog()

        show_dialog(
            ft.AlertDialog(
                title=ft.Text("Удалить"),
                content=ft.Text(f"Удалить «{name}»?"),
                actions=[
                    ft.TextButton("Отмена", on_click=close_dialog),
                    ft.FilledButton(
                        "Удалить",
                        bgcolor=ft.Colors.RED_600,
                        on_click=confirm,
                    ),
                ],
            )
        )

    # ---------------- logic ----------------

    def toggle_state(e, name, states):
        state = states[name]
        now = datetime.datetime.now().strftime("%H:%M")

        if not state["arrived"]:
            state["arrived"] = True
            state["text"].value = (
                f"прибыло {now}" if state["is_vehicle"] else f"прибыл {now}"
            )
            state["text"].color = ft.Colors.GREEN_300
            e.control.bgcolor = ft.Colors.GREEN_600
        else:
            state["arrived"] = False
            state["text"].value = (
                f"убыло {now}" if state["is_vehicle"] else f"убыл {now}"
            )
            state["text"].color = ft.Colors.RED_300
            e.control.bgcolor = ft.Colors.GREY_700

        page.update()

    def create_item(name, states):
        delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED_300,
            on_click=lambda e: open_delete_dialog(name, states),
            tooltip="Удалить",
        )

        return ft.Column(
            [
                ft.FilledButton(
                    name,
                    width=160,
                    height=48,
                    bgcolor=ft.Colors.GREY_800,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: toggle_state(e, name, states),
                ),
                states[name]["text"],
                delete_btn,
            ],
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def build_grid(items, states, columns):
        if not items:
            return ft.Text("Список пуст", color=ft.Colors.GREY_500)

        return ft.GridView(
            controls=[create_item(item, states) for item in items],
            runs_count=columns,
            max_extent=180,
            spacing=16,
            run_spacing=16,
            expand=True,
        )

    def section_header(title, on_add):
        return ft.Container(
            width=420,
            content=ft.Row(
                [
                    ft.Text(
                        title,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_300,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ADD_CIRCLE,
                        icon_color=ft.Colors.GREEN_400,
                        on_click=on_add,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

    vehicles_container = ft.Container(
        padding=16,
        border=ft.Border.all(1, ft.Colors.GREEN_900),
        border_radius=10,
        expand=True,
    )

    personnel_container = ft.Container(
        padding=16,
        border=ft.Border.all(1, ft.Colors.GREEN_900),
        border_radius=10,
        expand=True,
    )

    main_container = ft.Container(expand=True)

    def refresh_layout():
        width = page.width
        columns = 2 if width < 700 else 3

        vehicles_container.content = build_grid(vehicles, vehicle_states, columns)
        personnel_container.content = build_grid(personnel, personnel_states, columns)

        if width < 880:
            main_container.content = ft.Column(
                [
                    section_header(
                        "Транспортные средства",
                        lambda e: open_add_dialog(
                            "Добавить ТС", vehicles, vehicle_states, True
                        ),
                    ),
                    vehicles_container,
                    ft.Divider(),
                    section_header(
                        "Командование",
                        lambda e: open_add_dialog(
                            "Добавить", personnel, personnel_states, False
                        ),
                    ),
                    personnel_container,
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            )
        else:
            main_container.content = ft.Row(
                [
                    ft.Column(
                        [
                            section_header(
                                "Транспортные средства",
                                lambda e: open_add_dialog(
                                    "Добавить ТС", vehicles, vehicle_states, True
                                ),
                            ),
                            vehicles_container,
                        ],
                        expand=True,
                        spacing=16,
                    ),
                    ft.VerticalDivider(width=60),
                    ft.Column(
                        [
                            section_header(
                                "Командование",
                                lambda e: open_add_dialog(
                                    "Добавить", personnel, personnel_states, False
                                ),
                            ),
                            personnel_container,
                        ],
                        expand=True,
                        spacing=16,
                    ),
                ],
                expand=True,
            )

        page.update()

    page.on_resize = lambda e: refresh_layout()
    page.add(main_container)
    refresh_layout()


if __name__ == "__main__":
    ft.app(target=main)
