"""
Initialization and other data for the OORMS system.

Submitting lab group: Syed, Pabon
Submission date: Nov 5, 2025

Original code by EEE320 instructors.
"""

type SeatNumber = int
type NumberOfSeats = int
type TableLocation = tuple[int, int]
type TableData = tuple[NumberOfSeats, TableLocation]

type MenuItemName = str
type Cost = float
type FoodItem = tuple[MenuItemName, Cost]

"""
    Restaurant Data

"""
TABLES: list[TableData] = [
    (6, (20, 20)),
    (4, (20, 225)),
    (5, (20, 370)),
    (2, (270, 20)),
    (2, (270, 100)),
    (2, (270, 180)),
    (8, (270, 280)),
    (2, (270, 520)),
]

MENU_ITEMS: list[FoodItem] = [
    ("House burger", 16),
    ("Chicken club", 14.5),
    ("Crispy Pork Belly", 14.5),
    ("Fried Chicken", 14.5),
    ("Butter Chicken Tacos", 16),
    ("Roasted Squash", 14),
    ("Portabella Burger", 14),
    ("Striploin Sandwich", 16),
    ("Beef Cheek", 24),
    ("Cornish Rock Hen", 23),
    ("Grilled Local Trout", 19),
    ("Hunters Rabbit Stew", 19),
]

"""

    Button Styling

"""

BUTTON_SIZE = (100, 30)
BUTTON_MARGIN = (10, 10)

BUTTON_STYLE = {"fill": "#090", "outline": "#090"}
BUTTON_TEXT_STYLE = {"fill": "#fff"}


def GET_BUTTON_BOTTOM_RIGHT(view_width: int, view_height: int) -> tuple[int, int]:
    return (
        view_width - BUTTON_SIZE[0] - BUTTON_MARGIN[0],
        view_height - BUTTON_SIZE[1] - BUTTON_MARGIN[1],
    )


def GET_BUTTON_BOTTOM_LEFT(_: int, view_height: int) -> tuple[int, int]:
    return (BUTTON_MARGIN[0], view_height - BUTTON_SIZE[1] - BUTTON_MARGIN[1])


"""

    Server View Styling

"""

RESTAURANT_SCALE = 0.75

TABLE_FILL = "#ccc"
TABLE_OUTLINE = "#999"
TABLE_WIDTH = 80
SINGLE_TABLE_LOCATION = (30, 30)

SEAT_DIAM = 40
SEAT_SPACING = 10

EMPTY_SEAT_FILL = "#ccc"
EMPTY_SEAT_OUTLINE = "#999"

FULL_SEAT_FILL = "#090"
FULL_SEAT_OUTLINE = "#090"

SERVER_VIEW_WIDTH = 380
SERVER_VIEW_HEIGHT = 500


"""

    Printer View Styling

"""
TAPE_FONT = ("Consolas", "14")
TAPE_WIDTH = 40
VISIBLE_LINES = 40

"""

    Order View Styling

"""
MENU_ITEM_SIZE = (150, 20, 5)

ORDER_ITEM_LOCATION = (230, 20, 5)
DOT_SIZE = 15
DOT_MARGIN = 5
CANCEL_SIZE = (DOT_SIZE, DOT_SIZE)
CANCEL_STYLE = {"fill": "#900", "outline": "#900"}
NOT_YET_ORDERED_STYLE = {"fill": "#fff", "outline": "#090"}
ORDERED_STYLE = BUTTON_STYLE
