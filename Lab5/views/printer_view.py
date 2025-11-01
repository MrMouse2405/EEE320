"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

"""

from typing import override
from tkinter import Button, Canvas, Frame, Scrollbar
from constants import SERVER_VIEW_HEIGHT, SERVER_VIEW_WIDTH
from models import Printer
from controllers import PrinterController
from mvc import View


class PrinterView(View[PrinterController, Printer]):
    def __init__(self, root: Frame, model: Printer) -> None:
        super().__init__(root, model)
        self._canvas: Canvas
        self._vsb: Scrollbar
        self._list_frame: Frame
        self._list_win_id: int

    @override
    def create_ui(self) -> None:
        print("create printer ui")
        _ = self.grid_rowconfigure(0, weight=1)
        _ = self.grid_columnconfigure(0, weight=1)

        # Scrollable area
        self._canvas = Canvas(
            self,
            width=SERVER_VIEW_WIDTH,
            height=SERVER_VIEW_HEIGHT,
            borderwidth=0,
            highlightthickness=0,
        )
        self._vsb = Scrollbar(self, orient="vertical", command=self._canvas.yview)
        _ = self._canvas.configure(yscrollcommand=self._vsb.set)

        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._vsb.grid(row=0, column=1, sticky="ns")

        # Inner frame that will hold the bill buttons
        self._list_frame = Frame(self._canvas)
        self._list_win_id = self._canvas.create_window(
            (0, 0), window=self._list_frame, anchor="nw"
        )

        # Keep scrollregion and inner frame width in sync
        def _on_frame_config(_):
            assert self._canvas is not None
            _ = self._canvas.configure(scrollregion=self._canvas.bbox("all"))

        def _on_canvas_config(event):
            assert self._canvas is not None and self._list_win_id is not None
            _ = self._canvas.itemconfigure(self._list_win_id, width=event.width)

        _ = self._list_frame.bind("<Configure>", _on_frame_config)
        _ = self._canvas.bind("<Configure>", _on_canvas_config)
        _ = self._canvas.bind_all(
            "<MouseWheel>",
            lambda e: self._canvas.yview_scroll(-1 if e.delta > 0 else 1, "units"),
        )

        self.refresh()

    @override
    def refresh(self) -> None:
        print("refresh printer view")
        if not self._list_frame:
            return

        # Clear old buttons
        for w in self._list_frame.winfo_children():
            w.destroy()

        # IMPORTANT: materialize the generator once
        bills = list(self.model.bills)

        # Add one button per bill
        for bill in bills:
            btn = Button(
                self._list_frame,
                text=f"Bill #{bill.id}",
                command=lambda b_id=bill.id: self.controller.on_bill_touched(b_id),
            )
            btn.pack(fill="x", padx=12, pady=6)
