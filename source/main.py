import tkinter
import threading
import warnings
import time
import win32gui
from mod.sprites import Animation
from mod.actions import Actions, AutoActions


class AppUI(tkinter.Tk):
    def __init__(self):
        super().__init__()

        IMAGE_PATH = [
            "./assets/miku_sprite_sheet_1.png",
            "./assets/miku_sprite_sheet_2.png",
            "./assets/miku_sprite_sheet_3.png",
            "./assets/miku_sprite_sheet_4.png",
            "./assets/miku_sprite_sheet_5.png",
            "./assets/miku_sprite_sheet_6.png",
            "./assets/miku_sprite_sheet_7.png",
            "./assets/miku_sprite_sheet_8.png",
        ]

        SPRITE_NUMBER_OF_FRAMES = [20, 8, 8, 8, 5, 3, 12, 9]

        self.sprite = Animation(IMAGE_PATH, SPRITE_NUMBER_OF_FRAMES)
        self.actions = Actions(self.sprite.canvas, self)
        self.auto_actions = AutoActions(self.sprite.canvas, self)

        # Configure window
        self.resizable(False, False)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.config(bg=self.sprite.BACKGROUND_COLOR)
        self.wm_attributes("-transparentcolor", self.sprite.BACKGROUND_COLOR)

        # Start sprite animations
        self.sprite.animation()
        self.auto_actions.gravity()
        self.auto_actions.move_in_x()

        # Smooth vertical follow
        self.target_y = None
        threading.Thread(target=self.update_target_position, daemon=True).start()
        self.smooth_follow_loop()

    def update_target_position(self):
        """Continuously track bottom of active window as target Y, but ignore self window."""
        while True:
            try:
                hwnd = win32gui.GetForegroundWindow()
                # Ignore if the active window is Miku herself
                if hwnd != 0 and hwnd != self.winfo_id():
                    rect = win32gui.GetWindowRect(hwnd)
                    bottom_y = rect[3]  # bottom of active window
                    self.target_y = bottom_y - self.winfo_height() - 10  # small offset
                else:
                    self.target_y = None
            except Exception:
                self.target_y = None
            time.sleep(0.1)

    def smooth_follow_loop(self):
        """Move window smoothly toward target Y without snapping."""
        if self.target_y is not None:
            current_y = self.winfo_y()
            if current_y < self.target_y:
                new_y = min(current_y + 2, self.target_y)
                self.geometry(f"+{self.winfo_x()}+{new_y}")
            elif current_y > self.target_y:
                new_y = max(current_y - 2, self.target_y)
                self.geometry(f"+{self.winfo_x()}+{new_y}")
        self.after(15, self.smooth_follow_loop)  # 60 FPS-ish

    def stop(self):
        self.quit()

    def change_animation(self, animation: int = 0):
        self.sprite.animation_list = animation


class AppBroadcast(AppUI):
    def __init__(self):
        super().__init__()
        self.running = True
        self.user_name = "human"  # optional memory
        threading.Thread(target=self.listen_to_console, daemon=True).start()
        self.mainloop()

    def listen_to_console(self):
        while self.running:
            try:
                command = input().lower()

                # Exit commands
                if command in ['miku bye', 'bye', 'exit', 'quit']:
                    self.running = False
                    self.broadcast(f"Goodbye~!! 💕👋. Come back soon, {self.user_name}~")
                    self.stop()

                # Greetings
                elif command in ['miku hello', 'hello', 'hi', 'hey']:
                    self.broadcast(f"Hello~!! 💕 How are you feeling today, {self.user_name}?")

                # How are you
                elif command in ['how are you', 'how are you?', 'miku how are you']:
                    self.broadcast("I am fine, thank you~!! 💕 Wanna play a game or chat?")

                # Mood / emotions
                elif command in ['i am sad', 'sad', 'i feel bad', 'upset']:
                    self.broadcast("Aww~ 🥺 Don’t be sad! Here’s a virtual hug 🤗💖")
                elif command in ['i am happy', 'happy', 'excited', 'yay']:
                    self.broadcast("Yayyy!! 💕 I’m so happy with you!! Let’s celebrate~ 🎉")

                # Fun / random
                elif command in ['tell me a joke', 'joke', 'make me laugh']:
                    self.broadcast("Why did the anime character bring a ladder? To reach new heights! 😏✨")
                elif command in ['dance', 'show me dance', 'miku dance']:
                    self.broadcast("Hehe~ 💃 Watch me boogie!!")
                    self.change_animation(2)  # example dance animation index

                # Favorites / quirky questions
                elif command in ['what is your favorite food', 'favorite food']:
                    self.broadcast("I looove digital cupcakes~ 🍰✨ What about you?")
                elif command in ['do you like me', 'miku like me']:
                    self.broadcast(f"Of course~ 💖 You’re my favorite human, {self.user_name}!!")

                # Fallback
                else:
                    self.broadcast("I do not understand you~ 🥺 Try asking something else!")

            except EOFError as e:
                warnings.warn(f"Error: {e}")
                break

    def broadcast(self, text: str):
        print(f"Miku: {text}")


if __name__ == "__main__":
    AppBroadcast()
