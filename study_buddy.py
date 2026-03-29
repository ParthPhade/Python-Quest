import os
import sys
import subprocess
import time
import json

BASE_DIR = "python_quest_workspace"
STUDENT_DIR = os.path.join(BASE_DIR, "student_projects")
STATS_FILE = os.path.join(BASE_DIR, "player_stats.json")

for d in [BASE_DIR, STUDENT_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class Colors:
    C = '\033[96m'
    G = '\033[92m'
    Y = '\033[93m'
    R = '\033[91m'
    M = '\033[95m'
    B = '\033[94m'
    W = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class Profile:
    def __init__(self):
        self.data = self.load()

    def load(self):
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, "r") as f: return json.load(f)
            except: pass
        return {"name": None, "xp": 0, "level": 1, "completed": []}

    def save(self):
        with open(STATS_FILE, "w") as f: json.dump(self.data, f)

    def gain_xp(self, amount):
        self.data["xp"] += amount
        new_lvl = (self.data["xp"] // 100) + 1
        if new_lvl > self.data["level"]:
            self.data["level"] = new_lvl
            UI.box(f"LEVEL UP: {new_lvl}", Colors.Y)
        self.save()

class Engine:
    @staticmethod
    def run(filename, code):
        path = os.path.join(STUDENT_DIR, filename)
        with open(path, "w") as f: f.write(code)
        try:
            res = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=5)
            return res.stdout.strip(), res.stderr.strip()
        except subprocess.TimeoutExpired:
            return "", "Error: Timeout"
        except Exception as e:
            return "", str(e)

    @staticmethod
    def editor(mission, is_sandbox=False):
        UI.box(f"MISSION: {mission}\nRUN | UNDO | CLEAR | EXIT", Colors.W)
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

class Lesson:
    def __init__(self, id, title, concept, example, task, validator):
        self.id, self.title = id, title
        self.concept = concept
        self.example = example
        self.task = task
        self.validator = validator

    def play(self, profile):
        clear_screen()
        UI.header(f"LESSON {self.id}: {self.title}")
        UI.box(f"{self.concept}", Colors.W)
        UI.box(f"{self.example}", Colors.M)
        input("Press Enter to Start...")
        
        while True:
            clear_screen()
            code = Engine.editor(self.task)
            if code == "EXIT": break
            if not code.strip(): continue

            stdout, stderr = Engine.run(f"L{self.id}.py", code)
            UI.box(f"{stdout if stdout else '(No Output)'}", Colors.G)
            if stderr: UI.box(f"{stderr}", Colors.R)

            success, feedback = self.validator(code, stdout)
            if success:
                UI.box(f"DONE: {feedback}", Colors.G)
                profile.gain_xp(50)
                if self.id not in profile.data["completed"]: profile.data["completed"].append(self.id)
                profile.save()
                input("\nPress Enter..."); break
            else:
                UI.box(f"RETRY: {feedback}", Colors.R)
                input("\nPress Enter...")

class UI:
    @staticmethod
    def header(title):
        print(f"{Colors.C}╔" + "═" * 64 + f"╗{Colors.END}")
        print(f"{Colors.C}║ {Colors.W}{Colors.BOLD}{title.center(62)}{Colors.C} ║{Colors.END}")
        print(f"{Colors.C}╚" + "═" * 64 + f"╝{Colors.END}")

    @staticmethod
    def box(text, color=Colors.W):
        width = 66
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

def v_out(c, o, key): return (key.lower() in o.lower()), f"Output found: {key}"
def v_code(c, o, key): return (key in c), f"Code valid: {key}"

lessons = [
    Lesson("1", "Digital Voice", "print() shows text. Use quotes.", "print('Hello')", "Output: ACCESS GRANTED", lambda c,o: v_out(c,o,"ACCESS")),
    Lesson("2", "Memory Boxes", "x = 10 stores data.", "health = 100", "Set hp = 100", lambda c,o: v_code(c,o,"hp =")),
    Lesson("3", "Arithmetic", "Use + - * /.", "print(10 * 5)", "Print 10 * 5", lambda c,o: v_out(c,o,"50")),
    Lesson("4", "String Power", ".upper() makes text big.", "print('hi'.upper())", "Print 'hacker' in CAPS", lambda c,o: v_out(c,o,"HACKER")),
    Lesson("5", "Backpack", "Lists use [ ] and commas.", "items = ['a', 'b']", "Create list tools = ['pc', 'usb']", lambda c,o: v_code(c,o,"tools = [")),
    Lesson("6", "Tuples", "Tuples are immutable lists in ( ).", "t = (1, 2)", "Create t = (5, 6)", lambda c,o: v_code(c,o,"(")),
    Lesson("7", "Sets", "Sets only keep unique items.", "s = {1, 2}", "Create s = {1, 2}", lambda c,o: v_code(c,o,"{")),
    Lesson("8", "Dictionaries", "Dicts use Key:Value pairs.", "d = {'x': 1}", "Create d = {'id': 1}", lambda c,o: v_code(c,o,":")),
    Lesson("9", "If Statements", "If x > 5: happens if true.", "if 10 > 5:", "Check if 10 > 5", lambda c,o: v_code(c,o,"if ")),
    Lesson("10", "Else", "Else runs when if is false.", "else:", "Add else to an if", lambda c,o: v_code(c,o,"else")),
    Lesson("11", "For Loops", "For repeats for each item.", "for i in range(3):", "Loop range(3)", lambda c,o: v_code(c,o,"for ")),
    Lesson("12", "While Loops", "While repeats while true.", "while x < 3:", "Loop until x is 3", lambda c,o: v_code(c,o,"while ")),
    Lesson("13", "Try Except", "Try catches errors safely.", "try:\n  pass", "Use try/except", lambda c,o: v_code(c,o,"try")),
    Lesson("14", "Input", "input() gets data from user.", "x = input()", "Ask for name", lambda c,o: v_code(c,o,"input")),
    Lesson("15", "Functions", "def name(): creates a tool.", "def hi():", "Create def greet()", lambda c,o: v_code(c,o,"def ")),
    Lesson("16", "Arguments", "Functions take data in ( ).", "def hi(x):", "Function with (x)", lambda c,o: v_code(c,o,"(x)")),
    Lesson("17", "Read File", "open(f, 'r') opens for reading.", "open('f', 'r')", "Open file for 'r'", lambda c,o: v_code(c,o,"'r'")),
    Lesson("18", "Write File", "open(f, 'w') opens for writing.", "open('f', 'w')", "Open file for 'w'", lambda c,o: v_code(c,o,"'w'")),
    Lesson("19", "Classes", "class is a blueprint for objects.", "class Hero:", "Create class Player", lambda c,o: v_code(c,o,"class ")),
    Lesson("20", "Inheritance", "Take powers from other classes.", "class A(B):", "Inherit from A", lambda c,o: v_code(c,o,"(A)"))
]

def main():
    clear_screen()
    p = Profile()
    if not p.data["name"]:
        UI.header("LOGIN")
        p.data["name"] = input("\nNAME ❯ "); p.save()

    while True:
        clear_screen()
        UI.header(f"{p.data['name']} | LVL {p.data['level']} | XP {p.data['xp']}")
        
        sagas = [("BASICS", 0, 4), ("DATA", 4, 8), ("LOGIC", 8, 12), ("TOOLS", 12, 16), ("PRO", 16, 20)]
        for name, start, end in sagas:
            done = sum(1 for i in range(start, end) if lessons[i].id in p.data["completed"])
            print(f"\n {Colors.M}{name.ljust(12)}{Colors.END} {UI.progress_bar(done, 4)}")
            for i in range(start, end):
                status = f"{Colors.G}OK{Colors.END}" if lessons[i].id in p.data["completed"] else ".."
                print(f"   {status} {lessons[i].id}. {lessons[i].title}")

        print(f"\n {Colors.Y}[S] SANDBOX{Colors.END}  {Colors.R}[R] RESET{Colors.END}  {Colors.R}[Q] QUIT{Colors.END}")
        cmd = input("\n❯ ").lower()
        
        if cmd == 'q': break
        if cmd == 'r':
            if input("WIPE? (y/n): ").lower() == 'y':
                if os.path.exists(STATS_FILE): os.remove(STATS_FILE)
                return main()
        if cmd == 's':
            clear_screen()
            UI.header("SANDBOX")
            code = Engine.editor("FREEHAND", is_sandbox=True)
            if code != "EXIT":
                out, err = Engine.run("sandbox.py", code)
                UI.box(f"{out if out else '(No Output)'}", Colors.G)
                if err: UI.box(err, Colors.R)
                input("\nEnter to return...")
        elif cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < 20: lessons[idx].play(p)

if __name__ == "__main__":
    try: main()
    except Exception as e: print(f"Error: {e}"); input()
