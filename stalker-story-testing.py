import random
import json
import os
import tkinter as tk
from tkinter import scrolledtext, font, Menu, Toplevel

# --- Global Constants ---
GUIDE_PREFIX = "Guide: "
FOOD_ITEM = "Tourist's Delight Can"
SAVE_FILE = "stalker_save.json"

# --- Content Definitions ---

FACTIONS = {
    "Loners": {"slogan": "The Zone is our home and our prison.", "attitude": "Wary but generally helpful."},
    "Bandits": {"slogan": "Your wealth is my wealth.", "attitude": "Hostile, will rob or attack on sight if alone."},
    "Duty": {"slogan": "We must cleanse the Zone of its evil.", "attitude": "Lawful, often suspicious, willing to trade."},
    "Freedom": {"slogan": "The Zone is free for all!", "attitude": "Libertarian, distrustful of authority, focus on anomalies."},
    "Ecologists": {"slogan": "Knowledge is the only way to survive the Zone.", "attitude": "Non-combatants, keen traders for artifacts."}
}

MUTANTS = {
    "Blind Dog": {"health": 20, "damage": 5, "loot": "COMMON", "description": "A quick, snarling canine. Low health, low damage."},
    "Flesh": {"health": 40, "damage": 8, "loot": "RARE", "description": "A slow, bloated mutant. Moderate threat."},
    "Snork": {"health": 60, "damage": 12, "loot": "STRUCTURE_SPECIAL", "description": "A fast, deadly human-like creature. High damage."},
    "Bloodsucker": {"health": 80, "damage": 18, "loot": "RARE", "description": "A nearly invisible predator. Very high threat."}
}

# Loot tables remains the same, items are now defined with colors for the GUI
LOOT_TABLES = {
    "COMMON": {
        "Rusty 5.45mm Rounds": 10, "Field Dressing": 8, FOOD_ITEM: 15, "Vodka (Cure Radiation)": 5
    },
    "RARE": {
        "Anti-Radiation Drug": 15, "High-Grade 9x19mm Rounds": 10, "Basic Repair Kit": 5
    },
    "STRUCTURE_SPECIAL": {
        "Flash Artifact": 1, "Empty PDA": 3, "Broken Gas Mask": 5, "Advanced Toolkit": 2
    }
}

# Item properties used for inventory GUI rendering and logic
ITEM_PROPERTIES = {
    "Makarov PM Pistol": {"color": "#808080", "size": (2, 1), "type": "WEAPON", "display_name": "Makarov PM"},
    "9x18mm PM Rounds": {"color": "#a0a000", "size": (1, 1), "type": "AMMO", "display_name": "9x18mm PM"},
    "Rusty 5.45mm Rounds": {"color": "#606000", "size": (1, 1), "type": "AMMO", "display_name": "5.45mm Rusty"},
    "Field Dressing": {"color": "#ff6666", "size": (1, 1), "type": "HEAL", "display_name": "Dressing"},
    FOOD_ITEM: {"color": "#99cc00", "size": (1, 1), "type": "FOOD", "display_name": "Can of Food"},
    "Vodka (Cure Radiation)": {"color": "#00cccc", "size": (1, 1), "type": "ANTIRAD", "display_name": "Vodka"},
    "Anti-Radiation Drug": {"color": "#0099ff", "size": (1, 1), "type": "ANTIRAD", "display_name": "Anti-Rad"},
    "High-Grade 9x19mm Rounds": {"color": "#d0d000", "size": (1, 1), "type": "AMMO", "display_name": "9x19mm HighG"},
    "Basic Repair Kit": {"color": "#ff9900", "size": (1, 1), "type": "REPAIR", "display_name": "Repair Kit"},
    "Flash Artifact": {"color": "#ffcc00", "size": (1, 1), "type": "ARTIFACT", "display_name": "Flash Art."},
    "Empty PDA": {"color": "#606060", "size": (1, 1), "type": "JUNK", "display_name": "Empty PDA"},
    "Broken Gas Mask": {"color": "#505050", "size": (2, 2), "type": "ARMOR", "display_name": "Broken Mask"},
    "Advanced Toolkit": {"color": "#ffcc66", "size": (2, 1), "type": "REPAIR", "display_name": "Adv. Toolkit"},
}

USABLE_ITEMS = {
    "Field Dressing": {"heal": 20, "effect": "Restores 20 HP, stops bleeding.", "useable_in_combat": True, "type": "HEAL"},
    "Vodka (Cure Radiation)": {"rad_cure": 15, "effect": "Reduces radiation exposure.", "useable_in_combat": False, "type": "ANTIRAD"},
    FOOD_ITEM: {"heal": 5, "effect": "Small comfort, restores 5 HP.", "useable_in_combat": False, "type": "HEAL"},
    "Anti-Radiation Drug": {"rad_cure": 50, "effect": "Strongly reduces radiation exposure.", "useable_in_combat": False, "type": "ANTIRAD"}
}

ITEM_DESCRIPTIONS = {
    "Makarov PM Pistol": "A reliable, if outdated, Soviet sidearm. Good for emergencies. (2x1)",
    "9x18mm PM Rounds": "Standard ammunition for the Makarov.",
    "Rusty 5.45mm Rounds": "Low-quality rifle ammo, likely scavenged.",
    "Anti-Radiation Drug": "Chemical cocktail to purge harmful isotopes from the body.",
    "High-Grade 9x19mm Rounds": "Higher quality pistol ammunition. Better stopping power.",
    "Basic Repair Kit": "Contains tapes, glue, and a universal tool. Can fix low-grade armor.",
    "Flash Artifact": "A strange, smooth stone found near a Burner Anomaly. Sells well to Ecologists.",
    "Empty PDA": "A non-functional personal digital assistant. Maybe a tech can extract data.",
    "Broken Gas Mask": "A relic. Provides no protection but is a grim reminder of the Zone's dangers. (2x2)",
    "Advanced Toolkit": "Specialized tools used for deep maintenance and complex field repairs.",
    "Field Dressing": "Quick-use bandage and antiseptic.",
    FOOD_ITEM: "A can of preserved meat. Standard ration."
}

LOCATIONS = [
    "A **small, abandoned military checkpoint**.",
    "The air is thick with the scent of damp earth and rust. You are standing in a **collapsed tunnel**.",
    "An open **field of yellowed grass** stretches out.",
    "A **small, deserted town square**. The buildings are eerily intact.",
    "A cluster of **dense, mutated bushes** surrounds you.",
    "A **massive, broken communications tower** leans precariously.",
]

# Additional locations for more variety
LOCATIONS += [
    "A ruined **fuel depot**, half-swallowed by ash and weeds.",
    "The smell of ozone hangs over a nearby **anomaly field**.",
    "A half-collapsed **bridge** crosses a dried up riverbed.",
    "You find an old **train carriage** turned on its side, windows long gone.",
    "A line of scorched trees marks where something burned through the earth.",
    "A quiet **abandoned campsite** — a burnt campfire, a scattering of tins.",
]

# Structure Exploration Data (Same as before)
STRUCTURES = {
    "Abandoned Research Post": {
        "description": "A low-profile, concrete building, partially buried and covered in thick vines. It promises great, but dangerous, finds.",
        "steps": {
            "initial": {"text": "You stand at the entrance. Enter the main lab or try the back service **hatch**.", "options": ["LAB", "HATCH"]},
            "LAB": {"text": "The lab is ransacked. Check the **desks** or the **storage cabinets**?", "options": ["DESK", "CABINET"]},
            "DESK": {"text": "A quick look through the broken computer desks yields a minor find.", "loot": "COMMON", "end": True},
            "CABINET": {"text": "The metal cabinet is sealed shut but you manage to pry it open! This was worth the effort.", "loot": "RARE", "end": True},
            "HATCH": {"text": "A dead Stalker lies nearby. **Loot** the Stalker or **ignore** them?", "options": ["LOOT_STALKER", "IGNORE"]},
            "LOOT_STALKER": {"text": "The dead Stalker was carrying some basic survival supplies.", "loot": "COMMON", "end": True},
            "IGNORE": {"text": "You decide to respect the dead and head back.", "end": True}
        }, "initial_step": "initial"
    },
    "Old Factory Warehouse": {
        "description": "A cavernous, echoing warehouse. The air hums faintly—a sign of weak but persistent anomalies.",
        "steps": {
            "initial": {"text": "Navigate the main floor or climb to the rusty **office** area?", "options": ["FLOOR", "OFFICE"]},
            "FLOOR": {"text": "The floor is littered with machinery. You spot a small **cache** hidden beneath a tarp.", "loot": "RARE", "end": True},
            "OFFICE": {"text": "The office is structurally unsound. You risk checking the metal **safe** behind the manager's desk.", "options": ["SAFE", "BAILOUT"]},
            "SAFE": {"text": "Success! The safe was not locked correctly and contained some valuable items.", "loot": "STRUCTURE_SPECIAL", "end": True},
            "BAILOUT": {"text": "You realize the risk is too high and climb down quickly.", "end": True}
        }, "initial_step": "initial"
    }
}

# Expand the structures pool with many generated variants (placeholders).
for i in range(1, 101):
    name = f"Ruined Outpost #{i}"
    if name not in STRUCTURES:
        STRUCTURES[name] = {
            "description": f"A crumbling outpost with faded markings (variant {i}). May have hidden rooms or tunnels.",
            "steps": {"initial": {"text": "The outpost entrance yawns open.", "options": ["INVESTIGATE", "LEAVE"]}},
            "initial_step": "initial"
        }


class StalkerGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("S.T.A.L.K.E.R.: Story")
        self.geometry("1200x800")
        self.configure(bg="#1c1c1c")

        # Inventory Grid Dimensions (8 columns x 6 rows)
        self.GRID_COLS = 8
        self.GRID_ROWS = 6
        self.SLOT_SIZE = 60
        self.INV_WIDTH = self.GRID_COLS * self.SLOT_SIZE
        self.INV_HEIGHT = self.GRID_ROWS * self.SLOT_SIZE

        # Game State Variables (Default values)
        self.player_name = ""
        self.player_health = 100 
        self.player_x = 0
        self.player_y = 0
        self.player_location_name = "Rookie Village Outskirts"
        self.reputation = { 
            "Loners": 50, "Bandits": -25, "Duty": 10,     
            "Freedom": -10, "Ecologists": 75 
        }

        # Map markers (structures, camps, points of interest)
        self.map_markers = []  # each: {'type': 'STRUCTURE'|'CAMP'|'ANOMALY', 'x':int, 'y':int, 'name':str}

        # Inventory State (The inventory is now a list of lists representing the grid)
        # Each cell contains a tuple: (item_name, quantity) or None
        self.inventory_grid = [[None for _ in range(self.GRID_COLS)] for _ in range(self.GRID_ROWS)]
        self.selected_slot = None  # (row, col) of the currently selected item for movement
        
        # Game Flow Control
        self.current_state = 'MAIN_MENU'
        self.current_combat_target = None
        self.current_structure = None 
        self.current_step_key = None 
        
        # UI Setup
        self.setup_ui()
        self.start_game()

    def setup_ui(self):
        # 1. Main Frames
        self.map_frame = tk.Frame(self, bg="#2c2c2c")
        self.map_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=10, pady=10)
        
        self.text_frame = tk.Frame(self, bg="#1c1c1c")
        self.text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 2. Map Canvas (Left Side - Top)
        map_size = 350
        self.map_canvas = tk.Canvas(self.map_frame, width=map_size, height=map_size, bg="#0d0d0d", highlightthickness=0)
        self.map_canvas.pack(padx=5, pady=5)
        self.map_scale = 20 # Pixels per grid unit
        self.map_info = tk.Label(self.map_frame, text="MAP: Rookie Village (0, 0)", fg="#888", bg="#2c2c2c")
        self.map_info.pack(pady=5)

        # 3. Inventory GUI Frame (Left Side - Bottom)
        self.inventory_gui_label = tk.Label(self.map_frame, text="STALKER BACKPACK", fg="#00ff88", bg="#2c2c2c", font=("Consolas", 12))
        self.inventory_gui_label.pack(pady=(10, 0))

        self.inventory_canvas = tk.Canvas(self.map_frame, width=self.INV_WIDTH, height=self.INV_HEIGHT, bg="#0d0d0d", highlightthickness=1, highlightbackground="#444")
        self.inventory_canvas.pack(padx=5, pady=5)
        
        # Bind mouse events to the inventory canvas
        self.inventory_canvas.bind("<Button-1>", self.on_grid_click_lmb)
        self.inventory_canvas.bind("<Button-3>", self.on_grid_click_rmb)
        
        # Legend under inventory: simple colored key
        # Legend under inventory: vertical colored key to avoid overlap
        self.legend_canvas = tk.Canvas(self.map_frame, width=self.INV_WIDTH, height=120, bg="#1c1c1c", highlightthickness=0)
        self.legend_canvas.pack(padx=5, pady=(4,0))
        # draw legend circles and labels vertically
        def legend_entry(y, color, label):
            x = 12
            r = 8
            self.legend_canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="#000")
            self.legend_canvas.create_text(x+24, y, text=label, fill="#fff", anchor="w", font=("Consolas", 10))

        legend_entry(18, "#ff0000", "Player")
        legend_entry(42, "#ffff00", "Structure")
        legend_entry(66, "#008000", "Camp / Friendly")
        legend_entry(90, "#ff66ff", "Anomaly")
        
        # 4. Text Log (Right Side - Top)
        log_font = font.Font(family="Consolas", size=11)
        self.log_text = scrolledtext.ScrolledText(self.text_frame, wrap=tk.WORD, state=tk.DISABLED, 
                                                  bg="#000000", fg="#00ff00", font=log_font, height=30)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 5. Input Panel (Right Side - Bottom)
        self.input_label = tk.Label(self.text_frame, text="Input:", fg="#00ff00", bg="#1c1c1c", anchor="w")
        self.input_label.pack(fill=tk.X, pady=(10, 2))
        
        self.input_entry = tk.Entry(self.text_frame, bg="#333333", fg="#ffffff", insertbackground="#ffffff")
        self.input_entry.bind('<Return>', lambda event: self.submit_input())
        self.input_entry.pack(fill=tk.X)
        self.input_entry.focus_set()

        self.submit_button = tk.Button(self.text_frame, text="Submit", command=self.submit_input, bg="#444", fg="#fff")
        self.submit_button.pack(fill=tk.X, pady=(5, 0))
        
        # Configure tags for log formatting
        self.log_text.tag_config('guide', foreground='#00ffff')
        self.log_text.tag_config('warning', foreground='#ffcc00')
        self.log_text.tag_config('combat', foreground='#ff0000')
        self.log_text.tag_config('structure', foreground='#ffff00')
        self.log_text.tag_config('structure_spotted', foreground='#cc99ff')
        self.log_text.tag_config('inventory', foreground='#00ff88')
        self.log_text.tag_config('system_info', foreground='#ffffff') # New Tag for system info/status
        
        # Initial draw of the grid
        self.draw_inventory_grid()

    # --- Core UI Writing and Logic ---

    def write_to_log(self, text, tag=None):
        """Appends text to the log window."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text + "\n", tag)
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END) # Scroll to bottom

    def clear_log(self):
        """Clears the log window."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state=tk.DISABLED)

    def submit_input(self):
        """Processes the input from the entry field based on the current game state."""
        user_input = self.input_entry.get().strip()
        self.input_entry.delete(0, tk.END)
        
        if not user_input:
            self.write_to_log("[SYSTEM] Enter a command or choice.", 'warning')
            return

        self.write_to_log(f"> {user_input}\n")

        # Delegate input handling based on current state
        if self.current_state == 'MAIN_MENU':
            self.handle_main_menu_input(user_input)
        elif self.current_state == 'INTRO_NAME':
            self.handle_intro_name_input(user_input)
        elif self.current_state == 'INTRO_DIALOGUE':
            self.handle_intro_dialogue_input(user_input)
        elif self.current_state == 'CRATE_SCENE':
            self.handle_crate_input(user_input)
        elif self.current_state == 'EXPLORATION_MENU':
            self.handle_exploration_menu_input(user_input)
        elif self.current_state == 'COMBAT':
            self.handle_combat_input(user_input)
        elif self.current_state == 'NPC_ENCOUNTER':
            self.handle_npc_input(user_input)
        elif self.current_state == 'NPC_TRADE':
            self.handle_npc_trade_input(user_input)
        elif self.current_state == 'STRUCTURE_EXPLORATION':
            self.handle_structure_input(user_input)
        elif self.current_state == 'STRUCTURE_SELECTION':
            self.handle_structure_selection_input(user_input)

    # --- Game Flow Scenes and Handlers ---
    # (Intro, Combat, NPC, Structure logic remains largely the same, relying on add_item_to_inventory)

    def start_game(self):
        """Initial display of the main menu."""
        self.write_to_log("--- STALKER PDA ---", 'guide')
        self.write_to_log("1) Start New Game", 'system_info')
        self.write_to_log("2) Load Saved Game", 'system_info')
        self.write_to_log("-" * 30)
        self.draw_map()
        self.current_state = 'MAIN_MENU'

    def handle_main_menu_input(self, choice):
        if choice == "1":
            self.clear_log()
            self.scene_intro_name()
        elif choice == "2":
            if self.load_game():
                self.write_to_log("[SYSTEM] Game loaded. Proceeding to exploration.", 'guide')
                self.enter_exploration_menu()
            else:
                self.write_to_log("[SYSTEM] Load failed. Starting new game instead.", 'warning')
                self.scene_intro_name()
        else:
            self.write_to_log("[SYSTEM] Invalid choice. Select 1 or 2.", 'warning')

    def scene_intro_name(self):
        self.write_to_log(f"{GUIDE_PREFIX} 'Hello STALKER, I'll be your guide to getting started here, though, I must ask, what should I call you?'", 'guide')
        self.current_state = 'INTRO_NAME'

    def handle_intro_name_input(self, name):
        if name:
            self.player_name = name.capitalize()
            self.write_to_log(f"{GUIDE_PREFIX} 'Pleasure to meet you, {self.player_name}.'")
            self.scene_intro_dialogue()
        else:
            self.write_to_log("[SYSTEM] You must enter a name, stalker.", 'warning')

    def scene_intro_dialogue(self):
        self.write_to_log("\n--- Respond: ---")
        self.write_to_log("1) Nice to meet you as well.", 'system_info')
        self.write_to_log("2) Let's just get going.", 'system_info')
        self.write_to_log("3) Enough pleasantry, I don't need the chit-chat.", 'system_info')
        self.write_to_log("4) *Remain silent...*", 'system_info')
        self.write_to_log("-" * 30)
        self.current_state = 'INTRO_DIALOGUE'

    def handle_intro_dialogue_input(self, choice):
        if choice in ["1", "2", "3", "4"]:
            if choice == "1": self.write_to_log(f"{GUIDE_PREFIX} 'Alright then, we'd best get a move on. I appreciate the manners.'", 'guide')
            elif choice == "2": self.write_to_log(f"{GUIDE_PREFIX} 'Alright, fair enough I guess, we do need to get going.'", 'guide')
            elif choice == "3": self.write_to_log(f"{GUIDE_PREFIX} 'Damn, well screw you I guess, now let's get going.'", 'guide')
            elif choice == "4": self.write_to_log(f"{GUIDE_PREFIX} 'Not a talker stalker huh, well, we better get going.'", 'guide')
            self.after(500, self.scene_weapons_crate)
        else:
            self.write_to_log("[SYSTEM] Invalid choice. Select 1-4.", 'warning')
            return

    def scene_weapons_crate(self):
        self.write_to_log("\n" + "="*50)
        self.write_to_log(f"{GUIDE_PREFIX} 'Hey, hold up. There is an old weapons crate here. Why don't you open it up and see what is in there?'", 'guide')
        self.write_to_log("\n📦 **Old Wooden Crate**")
        self.write_to_log("1) Open the crate and look inside.", 'system_info')
        self.write_to_log("2) Leave it.", 'system_info')
        self.write_to_log("-" * 30)
        self.current_state = 'CRATE_SCENE'

    def handle_crate_input(self, choice):
        if choice == "1":
            self.write_to_log(f"{GUIDE_PREFIX} 'Nice! A trusty sidearm. Take care of it, stalker.'", 'guide')
            # Add items directly to the grid
            self.add_item_to_inventory("Makarov PM Pistol", 1)
            self.add_item_to_inventory("9x18mm PM Rounds", 12)
            self.add_item_to_inventory("Field Dressing", 1) 
        elif choice == "2":
            self.write_to_log(f"{GUIDE_PREFIX} 'Suit yourself. Let's move.'", 'guide')
        else:
            self.write_to_log("[SYSTEM] Invalid choice. Select 1 or 2.", 'warning')
            return

        self.after(500, self.enter_exploration_menu)

    def enter_exploration_menu(self):
        """Sets the state to the main game loop."""
        self.write_to_log("\n" + "="*50)
        self.write_to_log(f"{GUIDE_PREFIX} 'The Zone awaits. What do you do?'", 'guide')
        self.display_exploration_menu()

    def display_exploration_menu(self):
        """Writes the main menu options to the log."""
        self.current_state = 'EXPLORATION_MENU'
        
        status_text = f"Health: {self.player_health}/100 | Location: {self.player_location_name} @ {self.player_x},{self.player_y}"
        self.write_to_log("\n**ACTIONS**", 'system_info')
        self.write_to_log(f"[STATUS] {status_text}", 'system_info')
        self.write_to_log("1) Move **(N)orth, (E)ast, (W)est, (S)outh**", 'system_info')
        self.write_to_log("2) Check **REPUTATION**", 'system_info')
        self.write_to_log("3) **SAVE** Game", 'system_info')
        self.write_to_log("4) **EXIT** Game (Save & Quit)", 'system_info')
        # If there are structure markers at the player's current coords, allow interaction
        markers_here = [m for m in getattr(self, 'map_markers', []) if m.get('x') == self.player_x and m.get('y') == self.player_y and m.get('type') == 'STRUCTURE']
        if markers_here:
            names = ", ".join(m['name'] for m in markers_here)
            self.write_to_log(f"5) Interact with structure(s): {names}", 'system_info')
        self.write_to_log("\nUse the **STALKER BACKPACK** panel on the left to manage your inventory.")
        self.write_to_log("-" * 30)
        self.map_info.config(text=status_text)
        self.draw_map()

    def handle_exploration_menu_input(self, action):
        action = action.upper()
        
        if action in ("N", "E", "W", "S", "1"):
            if action == "1":
                self.write_to_log("[SYSTEM] Please specify direction (N/E/W/S).", 'warning')
                return
            direction = action if action != "1" else input("Which direction? (N/E/W/S): ").strip().upper()
            if direction in ("N", "E", "W", "S"):
                self.move_player(direction)
            else:
                self.write_to_log("[SYSTEM] Invalid direction.", 'warning')
                self.display_exploration_menu()
                
        elif action == "2":
            self.display_reputation()
            self.display_exploration_menu()
            
        elif action == "3":
            self.save_game()
            self.display_exploration_menu()
            
        elif action == "4":
            self.save_game()
            self.write_to_log(f"\n{GUIDE_PREFIX} 'Ending your run, {self.player_name}? Farewell for now.'", 'guide')
            self.after(1000, self.destroy)
        elif action == "5":
            # Interact with structure(s) at current position
            markers_here = [m for m in getattr(self, 'map_markers', []) if m.get('x') == self.player_x and m.get('y') == self.player_y and m.get('type') == 'STRUCTURE']
            if not markers_here:
                self.write_to_log("[SYSTEM] No structure to interact with here.", 'warning')
                self.display_exploration_menu()
                return

            if len(markers_here) == 1:
                self.start_structure_encounter(markers_here[0]['name'])
            else:
                # Let player select which structure
                self.pending_structure_options = [m['name'] for m in markers_here]
                self.write_to_log("Multiple structures found here. Choose one:" , 'system_info')
                for i, name in enumerate(self.pending_structure_options):
                    self.write_to_log(f"{i+1}) {name}", 'system_info')
                self.write_to_log("0) Cancel", 'system_info')
                self.current_state = 'STRUCTURE_SELECTION'
            return
        
        # Removed the INVENTORY_MENU state and corresponding '2' and 'B' input handlers.
        
        else:
            # Note: Options 2, 3, 4 are now Rep, Save, Exit, respectively.
            self.write_to_log("[SYSTEM] Invalid command. Choose 1, 2, 3, 4, or a direction (N/E/W/S).", 'warning')

    # --- Inventory GUI & Grid Logic (No changes in functionality) ---

    def coords_to_slot(self, x, y):
        """Converts canvas coordinates to grid (row, col) indices."""
        col = int(x // self.SLOT_SIZE)
        row = int(y // self.SLOT_SIZE)
        if 0 <= row < self.GRID_ROWS and 0 <= col < self.GRID_COLS:
            return row, col
        return None

    def slot_is_empty(self, r, c, size_w, size_h):
        """Checks if a multi-slot area is empty."""
        for row in range(r, r + size_h):
            for col in range(c, c + size_w):
                if row >= self.GRID_ROWS or col >= self.GRID_COLS or self.inventory_grid[row][col] is not None:
                    return False
        return True

    def find_empty_slot(self, size_w, size_h):
        """Finds the first available top-left (r, c) for an item of size (w, h)."""
        for r in range(self.GRID_ROWS):
            for c in range(self.GRID_COLS):
                if self.slot_is_empty(r, c, size_w, size_h):
                    return r, c
        return None

    def on_grid_click_lmb(self, event):
        """Handles left-click for item selection and movement."""
        slot = self.coords_to_slot(event.x, event.y)
        if not slot: return
        r, c = slot
        
        # We need to find the top-left corner of the item clicked, not just the slot
        item_data = None
        item_r, item_c = r, c
        
        # Traverse the grid backwards/upwards to find the item's origin slot
        for r_search in range(r + 1):
            for c_search in range(c + 1):
                cell_data = self.inventory_grid[r_search][c_search]
                if cell_data is not None and cell_data[0] == "ITEM_ORIGIN":
                    item_name, quantity, size_w, size_h = cell_data[1:]
                    if r_search <= r < r_search + size_h and c_search <= c < c_search + size_w:
                        item_data = (item_name, quantity, size_w, size_h)
                        item_r, item_c = r_search, c_search
                        break
            if item_data: break
        
        if item_data:
            # 1. Clicked an item (origin found at item_r, item_c)
            if self.selected_slot and self.selected_slot == (item_r, item_c):
                # Deselect if clicked twice
                self.selected_slot = None
                self.write_to_log(f"⚡ Item deselected: {item_data[0]}.")
            else:
                # Select the item
                self.selected_slot = (item_r, item_c)
                self.write_to_log(f"🖱️ Item selected: {item_data[0]} (x{item_data[1]}) at ({item_r}, {item_c}). Click an empty spot to move.", 'inventory')
        
        elif self.selected_slot:
            # 2. Clicked an empty slot, attempt to move selected item
            
            # Find the actual item data based on selected_slot
            selected_r, selected_c = self.selected_slot
            selected_data = self.inventory_grid[selected_r][selected_c]
            if selected_data and selected_data[0] == "ITEM_ORIGIN":
                item_name, quantity, size_w, size_h = selected_data[1:]
                
                # Check the new area for placement
                if self.slot_is_empty(r, c, size_w, size_h):
                    # Clear old slot
                    self.clear_item_area(selected_r, selected_c, size_w, size_h)
                    
                    # Place in new slot
                    self.place_item_in_grid(item_name, quantity, r, c)
                    
                    self.write_to_log(f"📦 Moved {item_name} from ({selected_r}, {selected_c}) to ({r}, {c}).", 'inventory')
                    self.selected_slot = None
                else:
                    self.write_to_log("[SYSTEM] Destination slot is blocked or too small.", 'warning')
            
        self.draw_inventory_grid()

    def on_grid_click_rmb(self, event):
        """Handles right-click to show context menu."""
        slot = self.coords_to_slot(event.x, event.y)
        if not slot: return
        r, c = slot

        item_data = None
        item_r, item_c = r, c
        
        # Find the item's origin slot, similar to LMB
        for r_search in range(r + 1):
            for c_search in range(c + 1):
                cell_data = self.inventory_grid[r_search][c_search]
                if cell_data is not None and cell_data[0] == "ITEM_ORIGIN":
                    item_name, quantity, size_w, size_h = cell_data[1:]
                    if r_search <= r < r_search + size_h and c_search <= c < c_search + size_w:
                        item_data = (item_name, quantity, size_w, size_h)
                        item_r, item_c = r_search, c_search
                        break
            if item_data: break
            
        if item_data:
            item_name, quantity, _, _ = item_data
            self.show_context_menu(event.x_root, event.y_root, item_name, item_r, item_c)
        else:
            self.write_to_log("[SYSTEM] Nothing found in this slot.", 'warning')

    def show_context_menu(self, x_root, y_root, item_name, r, c):
        """Displays the right-click context menu."""
        menu = Menu(self, tearoff=0)
        
        # 1. Examine
        menu.add_command(label="Examine", command=lambda: self.examine_item_gui(item_name))

        # 2. Use (for consumables)
        if item_name in USABLE_ITEMS:
            menu.add_command(label="Use", command=lambda: self.use_item_gui(item_name, r, c))
        # 3. Equip (not implemented, placeholder)
        elif ITEM_PROPERTIES.get(item_name, {}).get("type") in ["WEAPON", "ARMOR"]:
            menu.add_command(label="Equip (WIP)")

        # 4. Drop
        menu.add_command(label="Drop (All)", command=lambda: self.drop_item_gui(item_name, r, c))
        
        menu.add_separator()
        menu.add_command(label="Cancel")

        try:
            menu.tk_popup(x_root, y_root)
        finally:
            menu.grab_release()

    def examine_item_gui(self, item_name):
        """Prints item description to the log."""
        desc = ITEM_DESCRIPTIONS.get(item_name, "A generic item with no specific description.")
        if item_name in USABLE_ITEMS:
            desc += f" [Effect: {USABLE_ITEMS[item_name]['effect']}]"
        self.write_to_log(f"\n[EXAMINE] **{item_name}**: {desc}", 'inventory')
        self.after(500, self.draw_inventory_grid) # Redraw to clear selection highlight if any

    def use_item_gui(self, item_name, r, c):
        """Consumes an item from the grid."""
        item_data = USABLE_ITEMS.get(item_name)
        
        # Check if the item can be used
        if not item_data or item_name not in self.get_total_inventory_counts():
            self.write_to_log(f"You cannot use **{item_name}**.", 'warning')
            return

        # Apply effect
        if item_data["type"] == "HEAL":
            heal_amount = item_data["heal"]
            self.player_health = min(100, self.player_health + heal_amount)
            self.write_to_log(f"🩹 Used **{item_name}** and recovered {heal_amount} HP. Health: {self.player_health}/100.", 'inventory')
        elif item_data["type"] == "ANTIRAD":
            self.write_to_log(f"🧪 Consumed **{item_name}**. Zone influence reduced.", 'inventory')
        
        # Remove item from grid (This logic assumes consumables are 1x1 stackable items)
        cell_data = self.inventory_grid[r][c]
        if cell_data and cell_data[0] == "ITEM_ORIGIN" and cell_data[1] == item_name:
            # Reduce quantity
            new_quantity = cell_data[2] - 1
            if new_quantity > 0:
                # Update quantity in place
                # Note: cell_data[3] and cell_data[4] are size_w and size_h
                self.inventory_grid[r][c] = ("ITEM_ORIGIN", item_name, new_quantity, cell_data[3], cell_data[4])
            else:
                # Item consumed, clear the area
                self.clear_item_area(r, c, ITEM_PROPERTIES[item_name]["size"][0], ITEM_PROPERTIES[item_name]["size"][1])
        
        self.draw_inventory_grid()


    def drop_item_gui(self, item_name, r, c):
        """Removes all stack of an item from its origin slot and clears the grid area."""
        selected_data = self.inventory_grid[r][c]

        if selected_data and selected_data[0] == "ITEM_ORIGIN" and selected_data[1] == item_name:
            quantity = selected_data[2]
            size_w, size_h = selected_data[3], selected_data[4]
            
            self.clear_item_area(r, c, size_w, size_h)
            
            self.write_to_log(f"🗑️ Permanently discarded {quantity} unit(s) of **{item_name}**.", 'inventory')
        
        self.draw_inventory_grid()

    def clear_item_area(self, r, c, size_w, size_h):
        """Clears the grid slots occupied by an item starting at (r, c)."""
        for row in range(r, r + size_h):
            for col in range(c, c + size_w):
                if 0 <= row < self.GRID_ROWS and 0 <= col < self.GRID_COLS:
                    self.inventory_grid[row][col] = None
    
    # --- Inventory and Item Utilities ---
    
    def get_total_inventory_counts(self):
        """Calculates total counts based on the grid for external game logic (e.g., combat, use_item)."""
        counts = {}
        for r in range(self.GRID_ROWS):
            for c in range(self.GRID_COLS):
                cell_data = self.inventory_grid[r][c]
                if cell_data and cell_data[0] == "ITEM_ORIGIN":
                    item_name, quantity = cell_data[1], cell_data[2]
                    counts[item_name] = counts.get(item_name, 0) + quantity
        return counts

    def add_item_to_inventory(self, item_name, quantity=1):
        """Adds a specified item and quantity to the inventory grid."""
        
        size_w, size_h = ITEM_PROPERTIES.get(item_name, {}).get("size", (1, 1))

        # 1. Try to stack
        if size_w == 1 and size_h == 1:
            for r in range(self.GRID_ROWS):
                for c in range(self.GRID_COLS):
                    cell_data = self.inventory_grid[r][c]
                    if cell_data and cell_data[0] == "ITEM_ORIGIN" and cell_data[1] == item_name:
                        # Stack: Update quantity
                        new_quantity = cell_data[2] + quantity
                        self.inventory_grid[r][c] = ("ITEM_ORIGIN", item_name, new_quantity, size_w, size_h)
                        self.write_to_log(f"[Acquired: +{quantity} {item_name} (Stacked)]", 'inventory')
                        self.draw_inventory_grid()
                        return

        # 2. Find new slot (for new items or unstackable items)
        r, c = self.find_empty_slot(size_w, size_h)
        if r is not None:
            self.place_item_in_grid(item_name, quantity, r, c)
            self.write_to_log(f"[Acquired: +{quantity} {item_name} (New Slot)]", 'inventory')
            self.draw_inventory_grid()
        else:
            self.write_to_log(f"[SYSTEM] Inventory is full! Dropped {item_name}.", 'warning')


    def place_item_in_grid(self, item_name, quantity, r, c):
        """Marks the grid cells for a new item starting at (r, c)."""
        size_w, size_h = ITEM_PROPERTIES.get(item_name, {}).get("size", (1, 1))
        
        # 1. Mark the origin cell with full data
        self.inventory_grid[r][c] = ("ITEM_ORIGIN", item_name, quantity, size_w, size_h)
        
        # 2. Mark subsequent cells as occupied placeholders
        for row in range(r, r + size_h):
            for col in range(c, c + size_w):
                if row == r and col == c: continue # Skip origin cell
                if 0 <= row < self.GRID_ROWS and 0 <= col < self.GRID_COLS:
                    self.inventory_grid[row][col] = ("ITEM_OCCUPIED", item_name)
                    
    def draw_inventory_grid(self):
        """Redraws the entire inventory canvas based on the grid state."""
        self.inventory_canvas.delete("all")
        
        # 1. Draw grid lines
        for r in range(self.GRID_ROWS):
            for c in range(self.GRID_COLS):
                x1 = c * self.SLOT_SIZE
                y1 = r * self.SLOT_SIZE
                x2 = x1 + self.SLOT_SIZE
                y2 = y1 + self.SLOT_SIZE
                
                # Draw the slot
                self.inventory_canvas.create_rectangle(x1, y1, x2, y2, outline="#444", fill="#1a1a1a")

        # 2. Draw items
        for r in range(self.GRID_ROWS):
            for c in range(self.GRID_COLS):
                cell_data = self.inventory_grid[r][c]
                
                if cell_data and cell_data[0] == "ITEM_ORIGIN":
                    item_name, quantity, size_w, size_h = cell_data[1:]
                    item_props = ITEM_PROPERTIES.get(item_name, {})
                    color = item_props.get("color", "#fff")
                    display_name = item_props.get("display_name", item_name) # Use the defined display name

                    x1 = c * self.SLOT_SIZE
                    y1 = r * self.SLOT_SIZE
                    x2 = x1 + size_w * self.SLOT_SIZE
                    y2 = y1 + size_h * self.SLOT_SIZE
                    
                    # Draw item rectangle
                    rect_id = self.inventory_canvas.create_rectangle(x1 + 3, y1 + 3, x2 - 3, y2 - 3, 
                                                                     fill=color, outline="#eee", width=2, tags=("item", f"item_{r}_{c}"))

                    # Draw selection highlight
                    if self.selected_slot == (r, c):
                        self.inventory_canvas.create_rectangle(x1 + 1, y1 + 1, x2 - 1, y2 - 1, 
                                                               outline="#00ff00", width=3, tags="selection")

                    # Draw item name text
                    # Use a slightly smaller font for Field Dressing so it fits
                    font_size = 8
                    if item_name == "Field Dressing":
                        font_size = 6
                    self.inventory_canvas.create_text(
                        x1 + (size_w * self.SLOT_SIZE) / 2, # Center X of the item
                        y1 + (size_h * self.SLOT_SIZE) / 2, # Center Y of the item
                        text=display_name, 
                        fill="#000000", 
                        font=("Consolas", font_size, "bold"), # Size can be adjusted per-item
                        width=(size_w * self.SLOT_SIZE) - 6 # Constrain width
                    )

                    # Draw quantity text (for stackable items) in the bottom right
                    if quantity > 1:
                        self.inventory_canvas.create_text(x2 - 8, y2 - 5, text=f"x{quantity}", 
                                                         fill="#000", font=("Consolas", 7, "bold"), anchor="se")
        
    # --- Combat Logic (Requires total counts for ammo/healing) ---

    def calculate_player_damage(self):
        """Determines player damage based on equipped weapon (simplified)."""
        counts = self.get_total_inventory_counts()
        if counts.get("Makarov PM Pistol", 0) > 0 and counts.get("9x18mm PM Rounds", 0) > 0:
            return random.randint(10, 20)
        else:
            return random.randint(2, 5) 

    def combat_attack_action(self):
        p_damage = self.calculate_player_damage()
        m_name = self.current_combat_target['name']
        
        counts = self.get_total_inventory_counts()
        
        if counts.get("Makarov PM Pistol", 0) > 0 and counts.get("9x18mm PM Rounds", 0) > 0:
            # Consume 1 round: Find and update the first stack of 9x18mm PM Rounds
            found = False
            for r in range(self.GRID_ROWS):
                for c in range(self.GRID_COLS):
                    cell_data = self.inventory_grid[r][c]
                    if cell_data and cell_data[0] == "ITEM_ORIGIN" and cell_data[1] == "9x18mm PM Rounds":
                        new_quantity = cell_data[2] - 1
                        if new_quantity > 0:
                             self.inventory_grid[r][c] = ("ITEM_ORIGIN", "9x18mm PM Rounds", new_quantity, cell_data[3], cell_data[4])
                        else:
                             self.clear_item_area(r, c, 1, 1)
                        found = True
                        break
                if found: break
                
            self.current_combat_target['health'] -= p_damage
            self.write_to_log(f" > You fire your pistol, hitting the {m_name} for **{p_damage}** damage. (Ammo -1)")
        else:
            self.current_combat_target['health'] -= p_damage
            self.write_to_log(f" > You strike with your knife/fists, hitting for **{p_damage}** damage.")
        
        self.draw_inventory_grid() # Update inventory display after ammo use
        
    def combat_heal_action(self):
        """Heals in combat using a field dressing."""
        counts = self.get_total_inventory_counts()
        if counts.get("Field Dressing", 0) > 0:
            # Apply effect
            heal_amount = USABLE_ITEMS["Field Dressing"]["heal"]
            self.player_health = min(100, self.player_health + heal_amount)
            self.write_to_log(f"🩹 Used **Field Dressing** and recovered {heal_amount} HP. Health: {self.player_health}/100.", 'inventory')

            # Consume 1 dressing: Find and update the first stack
            found = False
            for r in range(self.GRID_ROWS):
                for c in range(self.GRID_COLS):
                    cell_data = self.inventory_grid[r][c]
                    if cell_data and cell_data[0] == "ITEM_ORIGIN" and cell_data[1] == "Field Dressing":
                        new_quantity = cell_data[2] - 1
                        if new_quantity > 0:
                             self.inventory_grid[r][c] = ("ITEM_ORIGIN", "Field Dressing", new_quantity, cell_data[3], cell_data[4])
                        else:
                             self.clear_item_area(r, c, 1, 1)
                        found = True
                        break
                if found: break
                
            self.draw_inventory_grid()
            return True
        else:
            self.write_to_log("You don't have any Field Dressing to use!", 'warning')
            return False

    def handle_combat_input(self, choice):
        choice = choice.upper()
        if self.player_health <= 0:
            self.handle_knockout()
            return
            
        if choice == "A":
            self.combat_attack_action()
        elif choice == "B":
            if self.combat_heal_action(): # Use specific combat heal logic
                self.after(500, self.combat_mutant_turn)
            else:
                self.display_combat_menu()
                return
        elif choice == "C":
            if random.random() < 0.5:
                self.write_to_log("\n💨 **SUCCESS!** You manage to lose the mutant in the undergrowth.")
                self.combat_end(True, escaped=True)
                return
            else:
                self.write_to_log("\n❌ **FAILURE!** The mutant is too fast and blocks your retreat!")
                self.after(500, self.combat_mutant_turn)
        else:
            self.write_to_log("[SYSTEM] Invalid choice.", 'warning')
            self.display_combat_menu()
            return
            
        if choice == "A":
            if self.current_combat_target['health'] <= 0:
                self.combat_end(True)
                return
            self.after(500, self.combat_mutant_turn)

    def handle_knockout(self):
        """Handles the player being knocked out."""
        
        self.write_to_log("\n🤕 **KNOCKED OUT**")
        self.write_to_log(f"{GUIDE_PREFIX} 'I'm applying a field dressing now. This is going to cost you!'", 'guide')
        
        # Use Field Dressing from grid
        counts = self.get_total_inventory_counts()
        if counts.get("Field Dressing", 0) > 0:
            # Find and consume the first Field Dressing stack
            for r in range(self.GRID_ROWS):
                for c in range(self.GRID_COLS):
                    cell_data = self.inventory_grid[r][c]
                    if cell_data and cell_data[0] == "ITEM_ORIGIN" and cell_data[1] == "Field Dressing":
                        # Note: cell_data[3] and cell_data[4] are size_w and size_h
                        new_quantity = cell_data[2] - 1
                        if new_quantity > 0:
                             self.inventory_grid[r][c] = ("ITEM_ORIGIN", "Field Dressing", new_quantity, cell_data[3], cell_data[4])
                        else:
                             self.clear_item_area(r, c, 1, 1)
                        break
                        
            self.player_health = 10 
            self.write_to_log("🩹 Used Field Dressing. You are stabilized at 10 HP.")
            self.draw_inventory_grid()
        else:
            self.player_health = 5 
            self.write_to_log("⚠️ No Field Dressings left! Stabilized at 5 HP.", 'warning')

        # Simplified loss logic - just check for Makarov existence
        if counts.get("Makarov PM Pistol", 0) > 0:
             # Find and clear the pistol
            for r in range(self.GRID_ROWS):
                for c in range(self.GRID_COLS):
                    cell_data = self.inventory_grid[r][c]
                    if cell_data and cell_data[0] == "ITEM_ORIGIN" and cell_data[1] == "Makarov PM Pistol":
                        self.clear_item_area(r, c, 2, 1)
                        self.write_to_log(f"[LOST: -1 Makarov PM Pistol] The attackers escaped with your pistol!")
                        break
            self.draw_inventory_grid()
            
        self.player_health = max(1, self.player_health)
        self.write_to_log("-" * 30)
        self.combat_end(False) # End combat/move back to exploration

    # --- Utility and Menu Functions ---
    
    # Rep, Loot, Move, Structure logic omitted for brevity as they remain unchanged

    def move_player(self, direction):
        """Updates player coordinates and triggers an area generation."""
        
        if direction == "N": self.player_y += 1
        elif direction == "S": self.player_y -= 1
        elif direction == "E": self.player_x += 1
        elif direction == "W": self.player_x -= 1
        
        distance = abs(self.player_x) + abs(self.player_y)
        if distance == 0: self.player_location_name = "Rookie Village Outskirts"
        elif distance < 5: self.player_location_name = "Near Zone Edge"
        elif distance < 15: self.player_location_name = "Outer Zone Territories"
        else: self.player_location_name = "Deep Zone Sector"
            
        self.write_to_log("-" * 30)
        self.write_to_log(f"**Moving {direction}...**", 'system_info')
        self.write_to_log(f"{GUIDE_PREFIX} 'We've moved to coordinates ({self.player_x}, {self.player_y}). Let's check the area.'", 'guide')
        self.write_to_log("-" * 30)
        self.draw_map()
        
        self.generate_new_area()

    def generate_new_area(self):
        """Generates a new area description and triggers encounters."""
        
        if self.player_health <= 0:
            self.handle_knockout()
            
        self.write_to_log(f"🧭 **CURRENT LOCATION: {self.player_location_name} ({self.player_x}, {self.player_y})**", 'system_info')
        self.write_to_log("-" * 30)
        
        # Make structures and varied locations more common
        event_roll = random.choices(["MUTANT", "NPC", "STRUCTURE", "STANDARD"], weights=[12, 12, 30, 46], k=1)[0]
        
        if event_roll == "MUTANT":
            mutant_name = random.choice(list(MUTANTS.keys()))
            self.start_combat(mutant_name)
        elif event_roll == "STRUCTURE":
            # Instead of auto-starting structure exploration, place a marker (with a generated instance)
            structure_name = random.choice(list(STRUCTURES.keys()))
            # add marker at current coords if not exists; if new, attach a generated instance so it's persistent
            exists = None
            for m in self.map_markers:
                if m.get('type') == 'STRUCTURE' and m.get('x') == self.player_x and m.get('y') == self.player_y and m.get('name') == structure_name:
                    exists = m
                    break
            if not exists:
                try:
                    inst = self.generate_structure_instance(structure_name)
                except Exception:
                    inst = None
                marker = {'type': 'STRUCTURE', 'x': self.player_x, 'y': self.player_y, 'name': structure_name, 'instance': inst}
                self.map_markers.append(marker)
            else:
                # ensure marker has an instance (create if missing)
                if 'instance' not in exists or not exists.get('instance'):
                    try:
                        exists['instance'] = self.generate_structure_instance(structure_name)
                    except Exception:
                        exists['instance'] = None
            # notify player with violet tag and do not auto-open
            self.write_to_log(f"💜 Structure detected nearby: {structure_name}. Use the exploration menu to interact.", 'structure_spotted')
            self.after(500, self.display_exploration_menu)
            return
        elif event_roll == "NPC":
            self.handle_npc_encounter_start()
        elif event_roll == "STANDARD":
            self.write_to_log(random.choice(LOCATIONS))
            self.after(500, self.display_exploration_menu)
            
    def start_structure_encounter(self, structure_name):
        # Initialize structure exploration with a stack-based menu so the player can
        # explore multiple parts and return to explore others.
        self.current_structure_name = structure_name

        # Try to use an existing marker's stored instance (so revisits persist)
        self.current_structure = None
        self.current_structure_marker = None
        for m in self.map_markers:
            if m.get('type') == 'STRUCTURE' and m.get('x') == self.player_x and m.get('y') == self.player_y and m.get('name') == structure_name:
                # Use stored instance if present, otherwise generate and attach
                if m.get('instance'):
                    self.current_structure = m['instance']
                else:
                    inst = self.generate_structure_instance(structure_name)
                    m['instance'] = inst
                    self.current_structure = inst
                self.current_structure_marker = m
                break

        # If not found, create a marker and attach a generated instance
        if not self.current_structure:
            inst = self.generate_structure_instance(structure_name)
            marker = {'type': 'STRUCTURE', 'x': self.player_x, 'y': self.player_y, 'name': structure_name, 'instance': inst}
            self.map_markers.append(marker)
            self.current_structure_marker = marker
            self.current_structure = inst

        # Restore visited steps (persisted on the instance) so loot/encounters don't reset
        stored_visited = self.current_structure.get('visited', [])
        self.current_structure_visited = set(stored_visited if isinstance(stored_visited, (list, tuple, set)) else [])

        self.structure_menu_stack = [self.current_structure["initial_step"]]

        self.write_to_log("-" * 30)
        self.write_to_log(f"🛑 **STRUCTURE FOUND: {structure_name}**", 'structure')
        self.write_to_log(self.current_structure["description"])
        self.write_to_log("-" * 30)

        self.current_state = 'STRUCTURE_EXPLORATION'
        self.display_structure_menu()

    def display_structure_menu(self):
        if not self.current_structure or not self.structure_menu_stack:
            self.end_structure_encounter()
            return

        top_key = self.structure_menu_stack[-1]
        step = self.current_structure["steps"].get(top_key)
        if not step:
            self.write_to_log("[SYSTEM] Structure data corrupted.", 'warning')
            self.end_structure_encounter()
            return

        # Show prompt for this menu level
        self.write_to_log(f"{GUIDE_PREFIX} '{step['text']}'", 'guide')

        options_list = step.get('options', [])
        self.write_to_log("\n**Structure Options:**", 'system_info')
        for i, option_key in enumerate(options_list):
            visited_mark = ' (explored)' if option_key in self.current_structure_visited else ''
            self.write_to_log(f"{i + 1}) {option_key}{visited_mark}", 'system_info')

        # Back option if we are nested
        extra_index = len(options_list) + 1
        self.write_to_log(f"{extra_index}) Leave Structure", 'system_info')
        if len(self.structure_menu_stack) > 1:
            self.write_to_log("B) Back", 'system_info')

        self.write_to_log("-" * 30)

    def handle_structure_input(self, choice):
        if not self.current_structure or not self.structure_menu_stack:
            self.end_structure_encounter()
            return

        top_key = self.structure_menu_stack[-1]
        step = self.current_structure['steps'].get(top_key)
        if not step:
            self.end_structure_encounter()
            return

        options_list = step.get('options', [])

        choice_str = str(choice).strip()

        # Letter-based Back option
        if choice_str.lower() == 'b':
            if len(self.structure_menu_stack) > 1:
                self.structure_menu_stack.pop()
                self.display_structure_menu()
            else:
                self.write_to_log("[SYSTEM] No previous area to go back to.", 'warning')
            return

        # Attempt numeric selection
        try:
            choice_index = int(choice_str)
        except ValueError:
            self.write_to_log("[SYSTEM] Invalid choice. Enter a number or 'B' to go back.", 'warning')
            return

        # Leave
        if choice_index == len(options_list) + 1:
            self.write_to_log("You step away from the structure.", 'system_info')
            self.end_structure_encounter()
            return

        # Back numeric (kept for compatibility if steps include explicit back-option keys)
        if choice_index == 0 and len(self.structure_menu_stack) > 1:
            self.structure_menu_stack.pop()
            self.display_structure_menu()
            return

        # Select an option
        if 1 <= choice_index <= len(options_list):
            next_key = options_list[choice_index - 1]
            next_step = self.current_structure['steps'].get(next_key)
            if not next_step:
                self.write_to_log("[SYSTEM] That option seems broken.", 'warning')
                return

            # Show the step text
            self.write_to_log(f"{GUIDE_PREFIX} '{next_step['text']}'", 'guide')

            # If this is a defined back-step (generated with a back flag), go back one level
            if next_step.get('back') or (isinstance(next_key, str) and next_key.endswith('_BACK')):
                if len(self.structure_menu_stack) > 1:
                    self.structure_menu_stack.pop()
                    self.display_structure_menu()
                else:
                    self.end_structure_encounter()
                return

            # If this step triggers a combat encounter
            # Prevent re-processing of already-visited actionable steps
            actionable = next_step.get('encounter') or ('loot' in next_step) or next_step.get('end')
            if next_key in self.current_structure_visited and actionable:
                self.write_to_log("[SYSTEM] This area has already been searched. There's nothing new.", 'system_info')
                self.display_structure_menu()
                return

            if next_step.get('encounter'):
                mutant_type = next_step.get('mutant_type')
                # Mark visited so it can't be spammed
                self.current_structure_visited.add(next_key)
                # Persist visited on the stored instance (if any)
                if getattr(self, 'current_structure_marker', None):
                    inst = self.current_structure_marker.get('instance')
                    if inst is not None:
                        if not isinstance(inst.get('visited'), set):
                            inst['visited'] = set(inst.get('visited', []))
                        inst['visited'].add(next_key)
                # Start combat against that mutant
                if mutant_type in MUTANTS:
                    self.start_combat(mutant_type)
                else:
                    # If an arbitrary mutant name was provided, start as a dict
                    self.start_combat_from_dict({'name': mutant_type, 'health': 40, 'damage': 8, 'loot': 'COMMON'})
                return

            # If there's loot, give it and mark visited, but do not force exit
            if 'loot' in next_step:
                self.determine_loot(next_step['loot'])
                self.current_structure_visited.add(next_key)
                # Persist visited on the stored instance (if any)
                if getattr(self, 'current_structure_marker', None):
                    inst = self.current_structure_marker.get('instance')
                    if inst is not None:
                        if not isinstance(inst.get('visited'), set):
                            inst['visited'] = set(inst.get('visited', []))
                        inst['visited'].add(next_key)
                self.write_to_log("\n[You may continue exploring other parts of the structure.]", 'system_info')
                self.display_structure_menu()
                return

            # If the step has further options, dive into them by pushing onto stack
            if 'options' in next_step:
                self.structure_menu_stack.append(next_key)
                self.display_structure_menu()
                return

            # No loot and no options — just flavor text; return to menu
            self.display_structure_menu()
            return

        self.write_to_log("[SYSTEM] Invalid choice. Select a listed number.", 'warning')

    def handle_structure_selection_input(self, choice):
        """Handles selection when multiple structures exist at the same grid point."""
        try:
            idx = int(choice)
        except ValueError:
            self.write_to_log("[SYSTEM] Invalid selection.", 'warning')
            return

        if idx == 0:
            self.write_to_log("Selection cancelled.", 'system_info')
            self.after(200, self.display_exploration_menu)
            return

        options = getattr(self, 'pending_structure_options', [])
        if 1 <= idx <= len(options):
            name = options[idx-1]
            # Start encounter for chosen structure
            self.start_structure_encounter(name)
            # clear pending options
            self.pending_structure_options = []
            return

        self.write_to_log("[SYSTEM] Invalid selection.", 'warning')

    def determine_loot(self, loot_type):
        """Randomly selects and adds loot from the specified table to the grid."""
        loot_pool = LOOT_TABLES.get(loot_type, {})
        if not loot_pool: return

        items = list(loot_pool.keys())
        weights = list(loot_pool.values())
        
        num_items = random.randint(1, 3) if loot_type == "COMMON" else 1
        
        self.write_to_log("\n[RESULT] You found something!", 'system_info')
        for _ in range(num_items):
            chosen_item = random.choices(items, weights, k=1)[0]
            quantity = random.randint(1, 5) if loot_type == "COMMON" else 1
            self.add_item_to_inventory(chosen_item, quantity)

    def generate_structure_instance(self, base_name):
        """Creates a randomized structure instance (description + steps) from a base name.
        The returned dict has keys: description, steps, initial_step.
        """
        desc_variants = [
            "A partially collapsed building with rusted metal and shattered glass.",
            "An old industrial shell with dark corridors and an acrid smell.",
            "A buried outpost with collapsed roofing and strange scorch marks.",
            "A quiet research annex, its equipment covered in dust and webbing."
        ]
        description = f"{random.choice(desc_variants)} (Source: {base_name})"

        steps = {}
        # Entrance
        entrance_key = 'ENTRANCE'

        # Decide number of main rooms and whether an underground section exists
        room_count = random.randint(1, 4)
        has_underground = random.random() < 0.3

        # Entrance options lead to room keys and possibly basement
        main_options = [f'ROOM_{i+1}' for i in range(room_count)]
        if has_underground:
            main_options.append('UNDERGROUND')

        steps[entrance_key] = {"text": "You stand at the entrance. Which direction do you explore?", "options": main_options}

        # Build rooms
        for i in range(room_count):
            key = f'ROOM_{i+1}'
            # Each room gives options to 'SEARCH' or 'LEAVE'
            steps[key] = {"text": f"You enter a dim room labeled #{i+1}. Search thoroughly or move on?", "options": [f'{key}_SEARCH', f'{key}_BACK']}

            # Search result: random loot or encounter or nothing
            roll = random.random()
            if roll < 0.55:
                loot_type = 'COMMON' if random.random() < 0.8 else 'RARE'
                steps[f'{key}_SEARCH'] = {"text": "You rummage through debris and find something.", "loot": loot_type, "end": True}
            elif roll < 0.8:
                # Encounter: start combat if chosen
                mutant = random.choice(list(MUTANTS.keys()))
                steps[f'{key}_SEARCH'] = {"text": f"Something moves in the shadows... a {mutant}!", "encounter": True, "mutant_type": mutant}
            else:
                steps[f'{key}_SEARCH'] = {"text": "You find nothing of value.", "end": True}

            steps[f'{key}_BACK'] = {"text": "You back out to the previous area.", "end": False}
            # mark this as a back-step so UI can treat it specially
            steps[f'{key}_BACK']['back'] = True

        # Underground section: a small tunnel with possible branching
        if has_underground:
            steps['UNDERGROUND'] = {"text": "A hatch opens to a narrow tunnel descending underground.", "options": ['TUNNEL_1', 'TUNNEL_2']}
            for ti in range(1, 3):
                tkey = f'TUNNEL_{ti}'
                # Tunnels more dangerous: higher chance of mutant or artifact
                r = random.random()
                if r < 0.5:
                    mutant = random.choice(list(MUTANTS.keys()))
                    steps[tkey] = {"text": f"The tunnel echoes with a skittering sound... a {mutant} appears!", "encounter": True, "mutant_type": mutant}
                else:
                    steps[tkey] = {"text": "A small alcove contains a curious object.", "loot": 'STRUCTURE_SPECIAL', "end": True}

        # Finalize
        instance = {"description": description, "steps": steps, "initial_step": entrance_key}
        return instance

    # Simplified or stubbed functions (NPC/Combat)

    def combat_mutant_turn(self):
        # Placeholder for Mutant turn logic
        m_name = self.current_combat_target['name']
        m_damage = self.current_combat_target['damage']
        
        self.player_health -= m_damage
        self.write_to_log(f" > The {m_name} attacks, hitting you for **{m_damage}** damage.", 'combat')
        
        if self.player_health <= 0:
            self.handle_knockout()
            return

        self.display_combat_menu()

    def start_combat(self, mutant_name):
        self.current_combat_target = MUTANTS[mutant_name].copy()
        self.current_combat_target['name'] = mutant_name # Store name explicitly
        
        self.write_to_log("-" * 30)
        self.write_to_log(f"💥 **CONTACT!** A **{mutant_name}** attacks!", 'combat')
        self.write_to_log(f"Mutant Health: {self.current_combat_target['health']}. {self.current_combat_target['description']}")
        self.write_to_log("-" * 30)
        
        self.current_state = 'COMBAT'
        self.display_combat_menu()

    def display_combat_menu(self):
        m_name = self.current_combat_target['name']
        self.write_to_log(f"\n[COMBAT] You: {self.player_health}/100 | {m_name}: {self.current_combat_target['health']}", 'combat')
        self.write_to_log("A) Attack", 'system_info')
        self.write_to_log("B) Use Field Dressing (If available)", 'system_info')
        self.write_to_log("C) Retreat (50% chance)", 'system_info')
        self.write_to_log("-" * 30)

    def combat_end(self, victory, escaped=False):
        if victory and not escaped:
            self.write_to_log(f"🎉 **VICTORY!** The {self.current_combat_target['name']} is dead.", 'combat')
            self.determine_loot(self.current_combat_target['loot'])
        elif escaped:
            self.write_to_log(f"🏃 You managed to evade the {self.current_combat_target['name']}.", 'combat')
        else:
             self.write_to_log(f"💔 **DEFEAT!** You were knocked out.", 'combat')
        
        self.current_combat_target = None
        self.after(500, self.enter_exploration_menu)

    def handle_npc_encounter_start(self):
        # NPC interaction with trade/info/attack options
        faction = random.choice(list(FACTIONS.keys()))
        self.npc_faction = faction
        self.npc_name = f"{faction} Stalker"
        self.write_to_log("-" * 30)
        self.write_to_log(f"🤝 **NPC ENCOUNTER:** You meet a STALKER from the **{faction}** faction.", 'guide')
        self.write_to_log(f"Attitude: {FACTIONS[faction]['attitude']}")
        self.current_state = 'NPC_ENCOUNTER'
        self.display_npc_menu()

    def display_npc_menu(self):
        """Prints the NPC action menu for the current NPC without re-rolling faction."""
        self.write_to_log("1) Trade  2) Ask for info  3) Leave  4) Attack", 'system_info')
        self.write_to_log("-" * 30)

    def handle_npc_input(self, choice):
        # NPC interaction handling: Trade, Info, Leave, Attack
        if choice == "1":
            # Start trade
            self.npc_offers = self.generate_npc_offers(self.npc_faction)
            if not self.npc_offers:
                self.write_to_log("[SYSTEM] This NPC has nothing to trade.", 'warning')
                self.current_state = 'NPC_ENCOUNTER'
                return
            self.write_to_log("\n**Trading Offers:**", 'system_info')
            for i, offer in enumerate(self.npc_offers):
                give_item, give_qty, ask_item, ask_qty = offer
                self.write_to_log(f"{i+1}) NPC offers {give_qty} x {give_item} for {ask_qty} x {ask_item}", 'system_info')
            self.write_to_log("0) Cancel", 'system_info')
            self.write_to_log("-" * 30)
            self.current_state = 'NPC_TRADE'

        elif choice == "2":
            # Ask for info: give a rumor/tip and maybe small reward
            tips = [
                "There's a stash hidden near the broken communications tower.",
                "A trader was seen moving goods toward the old factory.",
                "Watch out near the riverbed — anomalies are stronger there.",
                "The Ecologists pay well for artifacts found near old labs."
            ]
            tip = random.choice(tips)
            self.write_to_log(f"\n[INFO] '{tip}'", 'system_info')
            # small chance to receive a minor item
            if random.random() < 0.25:
                self.add_item_to_inventory(FOOD_ITEM, 1)
                self.write_to_log("[NPC] 'Here, take this. Might help you.'", 'guide')
            self.write_to_log("-" * 30)
            # Redisplay NPC menu so the interaction doesn't get stuck
            self.display_npc_menu()

        elif choice == "3":
            self.write_to_log("You bid farewell and move on.", 'system_info')
            self.after(500, self.enter_exploration_menu)

        elif choice == "4":
            # Attack the NPC — generate a combat target and start combat
            enemy = {
                'name': f"{self.npc_faction} Stalker",
                'health': random.randint(30, 70),
                'damage': random.randint(6, 14),
                'loot': 'COMMON',
                'description': 'A wary but capable human opponent.'
            }
            self.start_combat_from_dict(enemy)

        else:
            self.write_to_log("[SYSTEM] Invalid choice.", 'warning')

    def generate_npc_offers(self, faction):
        # Simple barter offers: list of tuples (give_item, give_qty, ask_item, ask_qty)
        base_offers = [
            ("Field Dressing", 1, FOOD_ITEM, 1),
            ("High-Grade 9x19mm Rounds", 2, "9x18mm PM Rounds", 4),
            ("Vodka (Cure Radiation)", 1, FOOD_ITEM, 1),
            ("Basic Repair Kit", 1, "Empty PDA", 1)
        ]
        # Adjust offers slightly by faction temperament
        if faction == 'Bandits':
            # Bandits often ask for more
            base_offers = [(g, gn, a, max(1, an+1)) for (g,gn,a,an) in base_offers]
        elif faction == 'Ecologists':
            # Ecologists more likely to offer artifacts
            base_offers.insert(0, ("Flash Artifact", 1, FOOD_ITEM, 1))

        return base_offers

    def handle_npc_trade_input(self, choice):
        # Expect numeric choice corresponding to offers
        try:
            idx = int(choice)
        except ValueError:
            self.write_to_log("[SYSTEM] Invalid selection.", 'warning')
            return

        if idx == 0:
            self.write_to_log("Trade cancelled.", 'system_info')
            self.current_state = 'NPC_ENCOUNTER'
            # Redisplay the same NPC menu (do not re-roll)
            self.display_npc_menu()
            return

        if 1 <= idx <= len(self.npc_offers):
            give_item, give_qty, ask_item, ask_qty = self.npc_offers[idx-1]
            counts = self.get_total_inventory_counts()
            if counts.get(ask_item, 0) >= ask_qty:
                # Remove asked items (naive removal from first stacks)
                remaining = ask_qty
                for r in range(self.GRID_ROWS):
                    for c in range(self.GRID_COLS):
                        cell = self.inventory_grid[r][c]
                        if cell and cell[0] == 'ITEM_ORIGIN' and cell[1] == ask_item and remaining > 0:
                            take = min(remaining, cell[2])
                            newq = cell[2] - take
                            if newq > 0:
                                self.inventory_grid[r][c] = ("ITEM_ORIGIN", ask_item, newq, cell[3], cell[4])
                            else:
                                self.clear_item_area(r, c, cell[3], cell[4])
                            remaining -= take
                            if remaining == 0:
                                break
                    if remaining == 0:
                        break

                # Give the player the offered item
                self.add_item_to_inventory(give_item, give_qty)
                self.write_to_log(f"Trade complete. You gave {ask_qty} x {ask_item} and received {give_qty} x {give_item}.", 'system_info')
            else:
                self.write_to_log("You don't have the items required for that trade.", 'warning')

            # Return to NPC encounter menu without re-rolling the NPC
            self.current_state = 'NPC_ENCOUNTER'
            self.display_npc_menu()
            return

        self.write_to_log("[SYSTEM] Invalid trade selection.", 'warning')

    def start_combat_from_dict(self, target_dict):
        # Start combat using an explicitly provided target dict (used for NPCs)
        self.current_combat_target = target_dict.copy()
        self.write_to_log("-" * 30)
        self.write_to_log(f"💥 **CONTACT!** A **{self.current_combat_target['name']}** attacks!", 'combat')
        self.write_to_log(f"Target Health: {self.current_combat_target['health']}. {self.current_combat_target.get('description','')}")
        self.write_to_log("-" * 30)
        self.current_state = 'COMBAT'
        self.display_combat_menu()

    def end_structure_encounter(self):
        # Clear structure exploration state but keep map markers so player can revisit
        self.current_structure = None
        self.current_structure_name = None
        self.current_step_key = None
        self.structure_menu_stack = []
        self.current_structure_visited = set()
        self.after(500, self.enter_exploration_menu)

    def display_reputation(self):
        self.write_to_log("\n**FACTION REPUTATION**", 'system_info')
        for faction, rep in self.reputation.items():
            level = "Loved" if rep >= 75 else "Friendly" if rep >= 50 else "Neutral" if rep >= 0 else "Hostile"
            self.write_to_log(f"- {faction}: {rep} ({level})", 'system_info')
        self.write_to_log("-" * 30, 'system_info')

    # --- Map Drawing ---

    def draw_map(self):
        """Draws the top-down grid and player location."""
        self.map_canvas.delete("all")
        map_width = self.map_canvas.winfo_width()
        map_height = self.map_canvas.winfo_height()
        map_center_x = map_width / 2
        map_center_y = map_height / 2
        map_limit = 8 # Map shows +/- 8 grid units (since canvas is 350 wide)
        
        # 1. Draw Grid
        for i in range(-map_limit, map_limit + 1):
            coord_x = map_center_x + i * self.map_scale
            coord_y = map_center_y + i * self.map_scale
            # Vertical lines
            self.map_canvas.create_line(coord_x, 0, coord_x, map_height, fill="#1a1a1a")
            # Horizontal lines
            self.map_canvas.create_line(0, coord_y, map_width, coord_y, fill="#1a1a1a")

        # 2. Draw Center (Rookie Village)
        self.map_canvas.create_oval(map_center_x-4, map_center_y-4, map_center_x+4, map_center_y+4, fill="#008000")
        
        # 3. Draw Player Position
        # Convert game coords (x, y) to canvas coords
        canvas_x = map_center_x + self.player_x * self.map_scale
        canvas_y = map_center_y - self.player_y * self.map_scale # Y is inverted on canvas
        
        r = 6 # Player dot radius
        # Draw markers (structures, camps, anomalies)
        try:
            for marker in getattr(self, 'map_markers', []):
                mx = map_center_x + marker['x'] * self.map_scale
                my = map_center_y - marker['y'] * self.map_scale
                mcolor = '#ffff00' if marker.get('type') == 'STRUCTURE' else '#008000' if marker.get('type') == 'CAMP' else '#ff66ff'
                mr = 5
                self.map_canvas.create_oval(mx - mr, my - mr, mx + mr, my + mr, fill=mcolor, outline="#000")
        except Exception:
            pass

        self.map_canvas.create_oval(canvas_x - r, canvas_y - r, canvas_x + r, canvas_y + r, fill="#ff0000", tags="player")

        status_text = f"Location: {self.player_location_name} | Coords: ({self.player_x}, {self.player_y})"
        self.map_info.config(text=status_text)

    # --- Save/Load Functions (Updated for grid) ---

    def save_game(self):
        """Saves the current game state to a JSON file."""
        state = {
            'name': self.player_name, 'health': self.player_health, 'inventory_grid': self.inventory_grid,
            'reputation': self.reputation, 'x': self.player_x, 'y': self.player_y
        }
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(state, f, indent=4)
            self.write_to_log(f"\n[SYSTEM] Game state saved successfully to {SAVE_FILE}.", 'guide')
        except Exception as e:
            self.write_to_log(f"\n[SYSTEM] Error saving game: {e}", 'warning')

    def load_game(self):
        """Loads the game state from the JSON file."""
        try:
            with open(SAVE_FILE, 'r') as f:
                state = json.load(f)
                self.player_name = state['name']
                self.player_health = state['health']
                # Check for old/new inventory format
                if 'inventory_grid' in state:
                    self.inventory_grid = state['inventory_grid']
                else: # Fallback/Compatibility: if only old inventory dict exists
                    self.inventory_grid = [[None for _ in range(self.GRID_COLS)] for _ in range(self.GRID_ROWS)]
                    self.write_to_log("[SYSTEM] Legacy inventory detected. Items must be manually re-acquired.", 'warning')
                    
                self.reputation = state['reputation']
                self.player_x = state['x']
                self.player_y = state['y']
            
            self.clear_log()
            self.write_to_log(f"[SYSTEM] Game loaded. Welcome back, {self.player_name}!", 'guide')
            self.draw_inventory_grid()
            return True
        except FileNotFoundError:
            self.write_to_log("[SYSTEM] No saved game found.", 'warning')
            return False
        except Exception as e:
            self.write_to_log(f"[SYSTEM] Error loading game: {e}", 'warning')
            return False

if __name__ == "__main__":
    app = StalkerGame()
    app.mainloop()