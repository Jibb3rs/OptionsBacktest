"""
Scroll Helper - Enables trackpad/mouse wheel scrolling on canvas
"""

def enable_scroll(canvas, frame):
    """
    Enable mouse wheel and trackpad scrolling for canvas
    
    Args:
        canvas: The tk.Canvas widget
        frame: The frame inside the canvas
    """
    
    def on_mouse_wheel(event):
        """Handle mouse wheel scroll"""
        # Mac trackpad and mouse wheel
        if event.num == 5 or event.delta < 0:
            canvas.yview_scroll(1, "units")
        if event.num == 4 or event.delta > 0:
            canvas.yview_scroll(-1, "units")
    
    def on_enter(event):
        """Bind scroll when mouse enters"""
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
        canvas.bind_all("<Button-4>", on_mouse_wheel)
        canvas.bind_all("<Button-5>", on_mouse_wheel)
    
    def on_leave(event):
        """Unbind scroll when mouse leaves"""
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")
    
    # Bind enter/leave events
    canvas.bind("<Enter>", on_enter)
    canvas.bind("<Leave>", on_leave)