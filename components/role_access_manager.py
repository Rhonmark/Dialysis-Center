import tkinter as tk
import customtkinter as ctk

class RoleAccessManager:
    def __init__(self):
        self.current_user_role = None
        self.tooltip_windows = {}  
        self.get_current_user_role()
    
    def get_current_user_role(self):
        """Get the current logged-in user's role"""
        try:
            from components.state import login_shared_states
            username = login_shared_states.get('logged_username')
            
            if username:
                from backend.crud import get_login_credentials
                self.current_user_role = get_login_credentials(username, target_data="role")
                print(f"🔐 Current user role: {self.current_user_role}")
            else:
                print("❌ No logged username found")
                self.current_user_role = None
                
        except Exception as e:
            print(f"❌ Error getting user role: {e}")
            self.current_user_role = None
    
    def is_admin(self):
        """Check if current user is Admin"""
        return self.current_user_role == "Admin"
    
    def is_staff(self):
        """Check if current user is Staff"""
        return self.current_user_role == "Staff"
    
    def setup_admin_only_button(self, button, parent_widget, command_callback, tooltip_text="Only Admin can access this function"):
        """
        Setup a button for admin-only access with visual feedback and tooltips
        
        Args:
            button: The CTkButton widget
            parent_widget: The parent widget for tooltips
            command_callback: The original command function
            tooltip_text: Custom tooltip text
        """
        # Configure button appearance based on role
        if self.is_admin():
            button.configure(
                fg_color="#1A374D",
                hover_color="#16C79A",
                text_color="white",
                cursor="hand2"
            )
        else:
            button.configure(
                fg_color="#808080",
                hover_color="#808080",
                text_color="#CCCCCC",
                cursor="arrow"
            )
        
        # Store original command
        original_command = command_callback
        
        # Create wrapper command with access control
        def protected_command():
            if self.is_admin():
                return original_command()
            else:
                self.show_access_denied_message(parent_widget)
                return
        
        # Set the protected command
        button.configure(command=protected_command)
        
        # Bind hover events
        button_id = id(button)  # Use button's id as unique identifier
        
        def on_hover_enter(event):
            if not self.is_admin():
                self.show_tooltip(button_id, button, tooltip_text)
        
        def on_hover_leave(event):
            self.hide_tooltip(button_id)
        
        button.bind("<Enter>", on_hover_enter)
        button.bind("<Leave>", on_hover_leave)
        
        return button
    
    def show_tooltip(self, button_id, button_widget, text):
        """Show a tooltip with the given text"""
        # Hide existing tooltip for this button
        self.hide_tooltip(button_id)
        
        # Get button position
        x = button_widget.winfo_rootx()
        y = button_widget.winfo_rooty() + button_widget.winfo_height() + 5
        
        # Create tooltip window
        tooltip_window = tk.Toplevel(button_widget)
        tooltip_window.wm_overrideredirect(True)
        tooltip_window.wm_geometry(f"+{x}+{y}")
        tooltip_window.attributes('-topmost', True)
        
        # Style the tooltip
        tooltip_frame = ctk.CTkFrame(
            tooltip_window,
            fg_color="#2B2B2B",
            corner_radius=8,
            border_width=1,
            border_color="#555555"
        )
        tooltip_frame.pack(fill="both", expand=True)
        
        tooltip_label = ctk.CTkLabel(
            tooltip_frame,
            text=text,
            font=("Arial", 11),
            text_color="white",
            fg_color="transparent"
        )
        tooltip_label.pack(padx=10, pady=6)
        
        # Store tooltip window
        self.tooltip_windows[button_id] = tooltip_window
    
    def hide_tooltip(self, button_id):
        """Hide the tooltip for a specific button"""
        if button_id in self.tooltip_windows:
            try:
                self.tooltip_windows[button_id].destroy()
            except:
                pass  # Window might already be destroyed
            del self.tooltip_windows[button_id]
    
    def hide_all_tooltips(self):
        """Hide all active tooltips"""
        for button_id in list(self.tooltip_windows.keys()):
            self.hide_tooltip(button_id)
    
    def show_access_denied_message(self, parent_widget, message="⚠️ Access Denied: Admin Only"):
        """Show a prominent access denied message"""
        # Create a temporary message frame
        message_frame = ctk.CTkFrame(
            parent_widget,
            fg_color="#FF4444",
            corner_radius=10,
            width=300,
            height=60
        )
        message_frame.place(relx=0.5, rely=0.1, anchor="center")
        
        message_label = ctk.CTkLabel(
            message_frame,
            text=message,
            font=("Arial", 14, "bold"),
            text_color="white"
        )
        message_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Auto-hide after 3 seconds
        parent_widget.after(3000, lambda: self._safe_destroy(message_frame))
    
    def _safe_destroy(self, widget):
        """Safely destroy a widget"""
        try:
            widget.destroy()
        except:
            pass  # Widget might already be destroyed
    
    def check_admin_access(self, action_name="this action"):
        """
        Simple access check that returns True/False
        Can be used for conditional logic
        """
        if self.is_admin():
            return True
        else:
            print(f"🚫 Access denied: {action_name} requires Admin role")
            return False
    
    def refresh_user_role(self):
        """Refresh the current user role (useful after login changes)"""
        self.get_current_user_role()