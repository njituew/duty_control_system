import flet as ft

def main(page: ft.Page):
    page.title = "Тест Flet"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    page.add(
        ft.Text("✅ Flet успешно установлен!", size=30, weight="bold"),
        ft.Text("Версия: " + ft.__version__),
        ft.ElevatedButton("Нажми меня", on_click=lambda e: print("Кнопка нажата!"))
    )

ft.app(target=main)