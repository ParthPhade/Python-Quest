import os
import sys
import subprocess
import time
import json

# ==============================================================================
# 🛠️ SYSTEM CONFIGURATION
# ==============================================================================
# We define where the player's data and projects will be stored.
BASE_DIR = "python_quest_workspace"
STUDENT_DIR = os.path.join(BASE_DIR, "student_projects")
STATS_FILE = os.path.join(BASE_DIR, "player_stats.json")

# Ensure the folders exist before we start the game.
for d in [BASE_DIR, STUDENT_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def clear_screen():
    """Clears the terminal window for a clean UI experience."""
    os.system('cls' if os.name == 'nt' else 'clear')

# 🎨 COLOR SCHEME: We use ANSI escape codes to make the terminal look like a high-tech console.
class Colors:
    C = '\033[96m' # Cyan (Borders & System)
    G = '\033[92m' # Green (Success & Input)
    Y = '\033[93m' # Yellow (Missions & Level Up)
    R = '\033[91m' # Red (Errors & Warnings)
    M = '\033[95m' # Magenta (Syntax Examples)
    B = '\033[94m' # Blue (Progress Bars)
    W = '\033[97m' # White (Text)
    BOLD = '\033[1m'
    END = '\033[0m'

# ==============================================================================
# 📊 PROGRESS & STATS SYSTEM
# ==============================================================================
class Profile:
    """Handles loading, saving, and updating the player's experience and progress."""
    def __init__(self):
        self.data = self.load()

    def load(self):
        """Tries to read player_stats.json. If it doesn't exist, starts a fresh profile."""
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, "r") as f: return json.load(f)
            except: pass
        return {"name": None, "xp": 0, "level": 1, "completed": []}

    def save(self):
        """Saves current progress to the hard drive."""
        with open(STATS_FILE, "w") as f: json.dump(self.data, f)

    def gain_xp(self, amount):
        """Adds XP and checks if the player should Level Up."""
        self.data["xp"] += amount
        new_lvl = (self.data["xp"] // 100) + 1
        if new_lvl > self.data["level"]:
            self.data["level"] = new_lvl
            UI.box(f"🎉 LEVEL UP! YOU ARE NOW LEVEL {new_lvl}! 🎉", Colors.Y)
        self.save()

# ==============================================================================
# ⚙️ THE CODING ENGINE
# ==============================================================================
class Engine:
    """The 'Brain' that runs the code you write and prevents the app from crashing."""
    @staticmethod
    def run(filename, code):
        """Writes your code to a file and runs it through the Python interpreter."""
        path = os.path.join(STUDENT_DIR, filename)
        with open(path, "w") as f: f.write(code)
        try:
            # We run the code as a separate process. If it crashes, the game stays open!
            res = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=5)
            return res.stdout.strip(), res.stderr.strip()
        except subprocess.TimeoutExpired:
            return "", "⚠️ ERROR: Infinite Loop! (Code was forced to stop after 5s)"
        except Exception as e:
            return "", str(e)

    @staticmethod
    def editor(mission, is_sandbox=False):
        """The interactive line-by-line code editor."""
        UI.box(f"MISSION: {mission}\nCOMMANDS: RUN | UNDO | CLEAR | EXIT", Colors.W, title="CODE TERMINAL")
        lines = []
        while True:
            try:
                line = input(f"{Colors.G}{len(lines)+1}{Colors.END} ❯ ")
                cmd = line.strip().upper()
                if cmd == "RUN": break
                if cmd == "EXIT": return "EXIT"
                if cmd == "UNDO" and lines: lines.pop(); continue
                if cmd == "CLEAR": lines = []; continue
                lines.append(line)
            except EOFError: break
        return "\n".join(lines)

# ==============================================================================
# 🎓 THE CURRICULUM ENGINE
# ==============================================================================
class Lesson:
    """A template for a Python lesson. Stores the 'Why', the 'How', and the 'Challenge'."""
    def __init__(self, id, title, concept, example, task, validator):
        self.id, self.title = id, title
        self.concept = concept   # The explanation (The Why)
        self.example = example   # The code sample (The How)
        self.task = task         # The mission (The Do)
        self.validator = validator # The function that checks if you did it right!

    def play(self, profile):
        """The sequence of a lesson: Explanation -> Example -> Coding."""
        clear_screen()
        UI.header(f"SAGA LESSON {self.id}: {self.title}")
        UI.box(f"{self.concept}", Colors.W, title="THE CONCEPT")
        UI.box(f"{self.example}", Colors.M, title="SYNTAX EXAMPLE")
        input(f"\n{Colors.BOLD}Ready to Code? Press Enter...{Colors.END}")
        
        while True:
            clear_screen()
            code = Engine.editor(self.task)
            if code == "EXIT": break
            if not code.strip(): continue

            stdout, stderr = Engine.run(f"L{self.id}.py", code)
            UI.box(f"{stdout if stdout else '(No Output)'}", Colors.G, title="TERMINAL OUTPUT")
            if stderr: UI.box(f"{stderr}", Colors.R, title="DEBUG LOG")

            # We use the 'validator' to check if the student solved the puzzle.
            success, feedback = self.validator(code, stdout)
            if success:
                UI.box(f"✅ SUCCESS: {feedback}", Colors.G)
                profile.gain_xp(50)
                if self.id not in profile.data["completed"]: profile.data["completed"].append(self.id)
                profile.save()
                input("\nLesson Mastered! Press Enter to return to Menu..."); break
            else:
                UI.box(f"❌ HINT: {feedback}", Colors.R, title="TUTOR HINT")
                input("\nPress Enter to try again...")

# ==============================================================================
# 🎨 UI & BOX DRAWING
# ==============================================================================
class UI:
    """Helper class to draw frames, headers, and progress bars."""
    @staticmethod
    def header(title):
        print(f"{Colors.C}╔" + "═" * 64 + f"╗{Colors.END}")
        print(f"{Colors.C}║ {Colors.W}{Colors.BOLD}{title.center(62)}{Colors.C} ║{Colors.END}")
        print(f"{Colors.C}╚" + "═" * 64 + f"╝{Colors.END}")

    @staticmethod
    def box(text, color=Colors.W, title=None):
        width = 66
        if title:
            print(f"{Colors.C}┌── {Colors.Y}{title} {Colors.C}" + "─" * (width - len(title) - 6) + f"┐{Colors.END}")
        else:
            print(f"{Colors.C}┌" + "─" * (width - 2) + f"┐{Colors.END}")
        for line in text.split('\n'):
            print(f"{Colors.C}│ {color}{line.ljust(width - 4)}{Colors.C} │{Colors.END}")
        print(f"{Colors.C}└" + "─" * (width - 2) + f"┘{Colors.END}")

    @staticmethod
    def progress_bar(current, total):
        pct = int((current / total) * 100)
        filled = int((current / total) * 10)
        bar = f"{Colors.G}█" * filled + f"{Colors.B}░" * (10 - filled)
        return f"{bar} {Colors.W}{pct}%{Colors.END}"

# ==============================================================================
# 📜 THE 20-LESSON CURRICULUM DATA
# ==============================================================================
# Here we define the actual content of the course. 
# You can edit these strings to change what the game teaches!

def v_out(c, o, key): return (key.lower() in o.lower()), f"The computer outputted '{key}'!"
def v_code(c, o, key): return (key in c), f"Keyword '{key}' used correctly."

lessons = [
    Lesson("1", "Digital Voice", 
           "In Python, print() is how we show text on the screen. \nText must ALWAYS be inside quotes like 'this' or \"this\".", 
           "print('Hello, Hacker')", 
           "Output exactly: ACCESS GRANTED", 
           lambda c,o: v_out(c,o,"ACCESS")),
    
    Lesson("2", "Memory Boxes", 
           "Variables are like boxes with labels. \nWe use the '=' sign to 'assign' a value to a name. \nExample: health = 100", 
           "player_name = 'Zero'", 
           "Create a variable called 'hp' and set it to 100", 
           lambda c,o: v_code(c,o,"hp =")),
    
    Lesson("3", "Arithmetic Ops", 
           "Python is a super calculator! You can use: \n+ (Add), - (Subtract), * (Multiply), / (Divide).", 
           "print(10 + 5)", 
           "Calculate and print 10 multiplied by 5", 
           lambda c,o: v_out(c,o,"50")),

    Lesson("4", "String Power", 
           "Strings (text) have built-in powers. \n.upper() makes text BIG, .lower() makes it small.", 
           "print('hi'.upper())", 
           "Print the word 'hacker' in all CAPITAL letters.", 
           lambda c,o: v_out(c,o,"HACKER")),

    Lesson("5", "The Backpack (Lists)", 
           "Lists store many items in order. \nThey use square brackets [ ] and commas , to separate items.", 
           "items = ['Sword', 'Shield']", 
           "Create a list named 'tools' with 'laptop' and 'usb' inside.", 
           lambda c,o: v_code(c,o,"tools = [")),

    # ... You can add all 20 lessons here with this same detailed format!
]

# ==============================================================================
# 🕹️ MAIN GAME LOOP
# ==============================================================================
def main():
    clear_screen()
    # Simple animated boot for style.
    for i in range(4):
        print(f"{Colors.C}[SYSTEM] Initializing Quest Engine" + "." * i, end="\r")
        time.sleep(0.3)
    
    p = Profile()
    if not p.data["name"]:
        UI.header("NEW PLAYER DETECTED")
        p.data["name"] = input(f"\n{Colors.BOLD}ENTER HACKER NAME ❯ {Colors.END}"); p.save()

    while True:
        clear_screen()
        UI.header(f"DASHBOARD: {p.data['name']} | LVL {p.data['level']} | XP {p.data['xp']}")
        
        # We group lessons into 'Sagas' for a professional feel.
        chapters = [("THE FUNDAMENTALS", 0, 5)] # Expand as you add lessons
        for name, start, end in chapters:
            done = sum(1 for i in range(start, end) if lessons[i].id in p.data["completed"])
            print(f"\n {Colors.M}{name.ljust(18)}{Colors.END} {UI.progress_bar(done, 5)}")
            for i in range(start, end):
                icon = f"{Colors.G}✅{Colors.END}" if lessons[i].id in p.data["completed"] else f"{Colors.W}..{Colors.END}"
                print(f"   {icon} {lessons[i].id}. {lessons[i].title}")

        print(f"\n {Colors.Y}[S] SANDBOX{Colors.END}  {Colors.R}[R] RESET{Colors.END}  {Colors.R}[Q] QUIT{Colors.END}")
        cmd = input("\nSELECT ACTION ❯ ").lower()
        
        if cmd == 'q': break
        if cmd == 'r':
            confirm = input(f"\n{Colors.R}⚠️ WIPE ALL MEMORY? (y/n): {Colors.END}").lower()
            if confirm == 'y':
                if os.path.exists(STATS_FILE): os.remove(STATS_FILE)
                return main()
        if cmd == 's':
            clear_screen()
            UI.header("FREEHAND SANDBOX MODE")
            code = Engine.editor("FREEHAND CODING", is_sandbox=True)
            if code != "EXIT":
                out, err = Engine.run("sandbox.py", code)
                UI.box(f"{out if out else '(No Output)'}", Colors.G, title="OUTPUT")
                if err: UI.box(err, Colors.R, title="ERRORS")
                input("\nEnter to return...")
        elif cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < len(lessons): lessons[idx].play(p)

if __name__ == "__main__":
    try: main()
    except Exception as e: print(f"\nCritical System Failure: {e}"); input()
