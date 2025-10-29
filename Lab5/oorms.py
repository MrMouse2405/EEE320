from tkinter import Tk

from controllers import ServerController
from models import Restaurant
from repositories import TableRepository
from repositories.MenuItemRepository import MenuItemRepository
from views import ServerView


class App(Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("oorms lab 5")

        table_repository = TableRepository()
        menu_item_repository = MenuItemRepository()

        restaurant = Restaurant(
            table_repository.get_all(), menu_item_repository.get_all()
        )
        server_view: ServerView = ServerView(self, restaurant)
        server_controller: ServerController = ServerController(server_view, restaurant)
        server_view.controller = server_controller


if __name__ == "__main__":
    App().mainloop()
