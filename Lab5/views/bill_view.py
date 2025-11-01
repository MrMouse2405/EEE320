from __future__ import annotations
import sys
from tkinter import Button, Canvas, Frame, Scrollbar
from typing import override
from mvc import View
from controllers import BillController
from models import Bill
from constants import SERVER_VIEW_HEIGHT, SERVER_VIEW_WIDTH


class BillView(View[BillController, Bill]):
    def __init__(self, root: Frame, model: Bill) -> None:
        super().__init__(root, model)
        self.__canvas: Canvas
        self.__vsb: Scrollbar

    @override
    def create_ui(self) -> None:
        _ = self.grid_rowconfigure(0, weight=1)
        _ = self.grid_columnconfigure(0, weight=1)

        # Canvas + vertical scrollbar
        self.__canvas = Canvas(
            master=self,
            width=SERVER_VIEW_WIDTH,
            height=SERVER_VIEW_HEIGHT,
            borderwidth=0,
            highlightthickness=0,
        )
        self.__vsb = Scrollbar(self, orient="vertical", command=self.__canvas.yview)
        _ = self.__canvas.configure(yscrollcommand=self.__vsb.set)

        self.__canvas.grid(row=0, column=0, sticky="nsew")
        self.__vsb.grid(row=0, column=1, sticky="ns")

        # Mouse wheel scrolling (Windows/macOS/Linux)
        self.__bind_mousewheel(self.__canvas)

        # Initial paint
        self.create_bill_ui()

    @override
    def refresh(self) -> None:
        if not self.__canvas:
            return
        self.__canvas.delete("all")
        self.create_bill_ui()

    # ------------ rendering ------------
    def create_bill_ui(self) -> None:
        assert self.__canvas is not None
        c = self.__canvas
        m: Bill = self.model

        pad_x = 20
        lh = 22
        y = 20

        # Header
        bill_id = getattr(m, "id", None)
        header = f"Bill #{bill_id}" if bill_id else "Bill (unsaved)"
        _ = c.create_text(
            pad_x, y, text=header, anchor="nw", font=("TkDefaultFont", 16, "bold")
        )
        y += lh + 6

        # Table line (use first order set if present)
        order_sets = list(m.items)  # Sequence → list for safe reuse
        table_label = order_sets[0].table_number if order_sets else "—"
        _ = c.create_text(
            pad_x,
            y,
            text=f"Table: {table_label}",
            anchor="nw",
            font=("TkDefaultFont", 12),
        )
        y += lh

        # Seats & items
        for os in order_sets:
            if not os.items:
                continue

            _ = c.create_text(
                pad_x,
                y,
                text=f"Seat {os.seat_number}",
                anchor="nw",
                font=("TkDefaultFont", 12, "bold"),
            )
            y += lh

            items_seq = getattr(os, "items", None) or getattr(os, "item", [])
            for mi in items_seq:
                # left: name
                _ = c.create_text(pad_x + 16, y, text=mi.name, anchor="nw")
                # right: price
                _ = c.create_text(
                    SERVER_VIEW_WIDTH - pad_x, y, text=f"${mi.price:.2f}", anchor="ne"
                )
                y += lh
            y += 8  # spacing between seats

        # Total
        _ = c.create_line(pad_x, y, SERVER_VIEW_WIDTH - pad_x, y)
        y += 8
        _ = c.create_text(
            pad_x, y, text="Total", anchor="nw", font=("TkDefaultFont", 12, "bold")
        )
        _ = c.create_text(
            SERVER_VIEW_WIDTH - pad_x, y, text=f"${float(m.total):.2f}", anchor="ne"
        )
        y += lh + 12

        btn = Button(c, text="Done", command=lambda: self.controller.done())
        _ = c.create_window(SERVER_VIEW_WIDTH // 2, y, window=btn, anchor="n")
        y += 40

        _ = c.configure(
            scrollregion=(0, 0, SERVER_VIEW_WIDTH, max(y, SERVER_VIEW_HEIGHT))
        )

    # ------------ mouse wheel helpers ------------
    # thanks to stack overflow. Now I can develop on linux and
    # submit to instructor on windows
    def __bind_mousewheel(self, canvas: Canvas) -> None:
        # Scroll only when the mouse is over the canvas
        def _on_enter(_):  # bind platform-appropriate wheel
            if sys.platform == "darwin":
                _ = canvas.bind_all("<MouseWheel>", _on_wheel_mac)
            else:
                _ = canvas.bind_all("<MouseWheel>", _on_wheel_win)
                _ = canvas.bind_all("<Button-4>", _on_wheel_linux)
                _ = canvas.bind_all("<Button-5>", _on_wheel_linux)

        def _on_leave(_):
            if sys.platform == "darwin":
                canvas.unbind_all("<MouseWheel>")
            else:
                canvas.unbind_all("<MouseWheel>")
                canvas.unbind_all("<Button-4>")
                canvas.unbind_all("<Button-5>")

        def _on_wheel_win(event):
            canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

        def _on_wheel_mac(event):
            # On macOS, event.delta is smaller; negative = down
            canvas.yview_scroll(int(-event.delta), "units")

        def _on_wheel_linux(event):
            # Button-4 up, Button-5 down
            delta = -1 if event.num == 4 else 1
            canvas.yview_scroll(delta, "units")

        _ = canvas.bind("<Enter>", _on_enter)
        _ = canvas.bind("<Leave>", _on_leave)
