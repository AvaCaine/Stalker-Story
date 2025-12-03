import random
import json
import os
import tkinter as tk
from tkinter import scrolledtext, font

# --- Global Constants ---
GUIDE_PREFIX = "Guide: "
FOOD_ITEM = "Tourist's Delight Can"
SAVE_FILE = "stalker_save.json"

# --- Content Definitions (Same as original, slightly simplified for GUI) ---

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

USABLE_ITEMS = {
    "Field Dressing": {"heal": 20, "effect": "restores HP"},
    "Vodka (Cure Radiation)": {"rad_cure": 15, "effect": "Reduces radiation (placeholder)"}
}

LOCATIONS = [
    "A **small, abandoned military checkpoint**.",
    "The air is thick with the scent of damp earth and rust. You are standing in a **collapsed tunnel**.",
    "An open **field of yellowed grass** stretches out.",
    "A **small, deserted town square**. The buildings are eerily intact.",
    "A cluster of **dense, mutated bushes** surrounds you.",
    "A **massive, broken communications tower** leans precariously.",
]

# --- Structure and Combat definitions are handled internally via state ---


class StalkerGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("S.T.A.L.K.E.R.: Story")
        self.geometry("1200x800")
        self.configure(bg="#1c1c1c")

        # Game State Variables (Default values)
        self.inventory = {}
        self.player_name = ""
        self.player_health = 100 
        self.player_x = 0
        self.player_y = 0
        self.player_location_name = "Rookie Village Outskirts"
        self.reputation = { 
            "Loners": 50, "Bandits": -25, "Duty": 10,     
            "Freedom": -10, "Ecologists": 75 
        }

        # Game Flow Control
        self.current_state = 'MAIN_MENU'
        self.next_state_on_submit = None
        self.current_prompt_type = None # e.g., 'intro_name', 'dialogue_choice', 'exploration_menu'
        self.current_combat_target = None

        # UI Setup
        self.setup_ui()
        self.start_game()

    def setup_ui(self):
        # 1. Main Frames
        self.map_frame = tk.Frame(self, bg="#2c2c2c")
        self.map_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)
        
        self.text_frame = tk.Frame(self, bg="#1c1c1c")
        self.text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 2. Map Canvas (Left Side)
        map_size = 500
        self.map_canvas = tk.Canvas(self.map_frame, width=map_size, height=map_size, bg="#0d0d0d", highlightthickness=0)
        self.map_canvas.pack(padx=5, pady=5)
        self.map_info = tk.Label(self.map_frame, text="MAP: Center is Rookie Village (0, 0)", fg="#888", bg="#2c2c2c")
        self.map_info.pack(pady=5)
        self.map_scale = 20 # Pixels per grid unit

        # 3. Text Log (Right Side - Top)
        log_font = font.Font(family="Consolas", size=11)
        self.log_text = scrolledtext.ScrolledText(self.text_frame, wrap=tk.WORD, state=tk.DISABLED, 
                                                  bg="#000000", fg="#00ff00", font=log_font, height=30)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 4. Input Panel (Right Side - Bottom)
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
        elif self.current_state == 'STRUCTURE_EXPLORATION':
            self.handle_structure_input(user_input)

    # --- Map Drawing ---

    def draw_map(self):
        """Draws the top-down grid and player location."""
        self.map_canvas.delete("all")
        map_center = self.map_canvas.winfo_width() / 2
        map_limit = 10 # Map shows +/- 10 grid units
        
        # 1. Draw Grid
        for i in range(-map_limit, map_limit + 1):
            coord = map_center + i * self.map_scale
            # Vertical lines
            self.map_canvas.create_line(coord, 0, coord, self.map_canvas.winfo_height(), fill="#1a1a1a")
            # Horizontal lines
            self.map_canvas.create_line(0, coord, self.map_canvas.winfo_width(), coord, fill="#1a1a1a")

        # 2. Draw Center (Rookie Village)
        center_x = map_center
        center_y = map_center
        self.map_canvas.create_oval(center_x-4, center_y-4, center_x+4, center_y+4, fill="#008000")
        
        # 3. Draw Player Position
        # Convert game coords (x, y) to canvas coords
        canvas_x = center_x + self.player_x * self.map_scale
        canvas_y = center_y - self.player_y * self.map_scale # Y is inverted on canvas
        
        r = 6 # Player dot radius
        self.map_canvas.create_oval(canvas_x - r, canvas_y - r, canvas_x + r, canvas_y + r, fill="#ff0000", tags="player")

        self.map_info.config(text=f"Location: {self.player_location_name} | Coords: ({self.player_x}, {self.player_y})")


    # --- Game Flow Scenes and Handlers ---

    def start_game(self):
        """Initial display of the main menu."""
        self.write_to_log("--- S.T.A.L.K.E.R. PDA ---", 'guide')
        self.write_to_log("1) Start New Game")
        self.write_to_log("2) Load Saved Game")
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
        """Prompts for the player's name."""
        self.write_to_log(f"{GUIDE_PREFIX} 'Hello STALKER, I'll be your guide to getting started here, though, I must ask, what should I call you?'", 'guide')
        self.current_state = 'INTRO_NAME'
        self.current_prompt_type = 'name'

    def handle_intro_name_input(self, name):
        if name:
            self.player_name = name.capitalize()
            self.write_to_log(f"{GUIDE_PREFIX} 'Pleasure to meet you, {self.player_name}.'")
            self.scene_intro_dialogue()
        else:
            self.write_to_log("[SYSTEM] You must enter a name, stalker.", 'warning')

    def scene_intro_dialogue(self):
        """Handles the first dialogue choice."""
        self.write_to_log("\n--- Respond: ---")
        self.write_to_log("1) Nice to meet you as well.")
        self.write_to_log("2) Let's just get going.")
        self.write_to_log("3) Enough pleasantry, I don't need the chit-chat.")
        self.write_to_log("4) *Remain silent...*")
        self.write_to_log("-" * 30)
        self.current_state = 'INTRO_DIALOGUE'
        self.current_prompt_type = 'dialogue_choice'

    def handle_intro_dialogue_input(self, choice):
        if choice == "1":
            self.write_to_log(f"{GUIDE_PREFIX} 'Alright then, we'd best get a move on. I appreciate the manners.'", 'guide')
        elif choice == "2":
            self.write_to_log(f"{GUIDE_PREFIX} 'Alright, fair enough I guess, we do need to get going.'", 'guide')
        elif choice == "3":
            self.write_to_log(f"{GUIDE_PREFIX} 'Damn, well screw you I guess, now let's get going.'", 'guide')
        elif choice == "4":
            self.write_to_log(f"{GUIDE_PREFIX} 'Not a talker stalker huh, well, we better get going.'", 'guide')
        else:
            self.write_to_log("[SYSTEM] Invalid choice. Select 1-4.", 'warning')
            return # Stay in current state

        self.after(500, self.scene_weapons_crate) # Move to next scene after brief pause

    def scene_weapons_crate(self):
        """Handles the initial weapons crate interaction."""
        self.write_to_log("\n" + "="*50)
        self.write_to_log(f"{GUIDE_PREFIX} 'Hey, hold up. There is an old weapons crate here. Why don't you open it up and see what is in there?'", 'guide')
        self.write_to_log("\n📦 **Old Wooden Crate**")
        self.write_to_log("1) Open the crate and look inside.")
        self.write_to_log("2) Leave it.")
        self.write_to_log("-" * 30)
        self.current_state = 'CRATE_SCENE'
        self.current_prompt_type = 'crate_choice'

    def handle_crate_input(self, choice):
        if choice == "1":
            self.write_to_log(f"{GUIDE_PREFIX} 'Nice! A trusty sidearm. Take care of it, stalker.'", 'guide')
            self.add_item_to_inventory("Makarov PM Pistol")
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
        self.write_to_log("\n**ACTIONS**")
        self.write_to_log(f"[STATUS] {status_text}")
        self.write_to_log("1) Move **(N)orth, (E)ast, (W)est, (S)outh**")
        self.write_to_log("2) Check **INVENTORY**")
        self.write_to_log("3) Check **REPUTATION**")
        self.write_to_log("4) **SAVE** Game")
        self.write_to_log("5) **EXIT** Game (Save & Quit)")
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
            self.display_inventory()
            self.display_exploration_menu()
            
        elif action == "3":
            self.display_reputation()
            self.display_exploration_menu()
            
        elif action == "4":
            self.save_game()
            self.display_exploration_menu()
            
        elif action == "5":
            self.save_game()
            self.write_to_log(f"\n{GUIDE_PREFIX} 'Ending your run, {self.player_name}? Farewell for now.'", 'guide')
            self.after(1000, self.destroy)
            
        else:
            self.write_to_log("[SYSTEM] Invalid command. Choose 1-5, or a direction (N/E/W/S).", 'warning')

    # --- Game Mechanics ---

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
        self.write_to_log(f"**Moving {direction}...**")
        self.write_to_log(f"{GUIDE_PREFIX} 'We've moved to coordinates ({self.player_x}, {self.player_y}). Let's check the area.'", 'guide')
        self.write_to_log("-" * 30)
        self.draw_map()
        
        self.generate_new_area()

    def generate_new_area(self):
        """Generates a new area description and triggers encounters."""
        
        if self.player_health <= 0:
            self.handle_knockout()
            
        self.write_to_log(f"🧭 **CURRENT LOCATION: {self.player_location_name} ({self.player_x}, {self.player_y})**")
        self.write_to_log("-" * 30)
        
        # Weighted Event Roll (10% Mutant, 10% NPC, 80% Standard)
        event_roll = random.choices(["MUTANT", "NPC", "STANDARD"], weights=[10, 10, 80], k=1)[0]
        
        if event_roll == "MUTANT":
            mutant_name = random.choice(list(MUTANTS.keys()))
            self.start_combat(mutant_name)
            
        # Structure encounter disabled for now to simplify state management
        # elif event_roll == "STRUCTURE":
        #     structure_name = random.choice(list(STRUCTURES.keys()))
        #     self.handle_structure_encounter(structure_name)
        
        elif event_roll == "NPC":
            self.handle_npc_encounter_start()
            
        elif event_roll == "STANDARD":
            self.write_to_log(random.choice(LOCATIONS))
            if random.random() < 0.15: 
                 self.write_to_log("\n[Small Find] You find a lone item on the ground.")
                 self.determine_loot("COMMON")
            
            self.after(500, self.display_exploration_menu) # Return to menu

    # --- Combat Logic (Simplified for GUI) ---

    def calculate_player_damage(self):
        """Determines player damage based on equipped weapon (simplified)."""
        if self.inventory.get("Makarov PM Pistol", 0) > 0 and self.inventory.get("9x18mm PM Rounds", 0) > 0:
            return random.randint(10, 20)
        else:
            return random.randint(2, 5) 

    def start_combat(self, mutant_name):
        self.current_combat_target = {"name": mutant_name, **MUTANTS[mutant_name]}
        self.current_combat_target["health"] = MUTANTS[mutant_name]["health"]

        self.write_to_log("\n🚨 **COMBAT START: {} ATTACKS!**".format(mutant_name), 'combat')
        self.write_to_log(self.current_combat_target['description'])
        self.current_state = 'COMBAT'
        self.display_combat_menu()

    def display_combat_menu(self):
        m_name = self.current_combat_target['name']
        m_health = self.current_combat_target['health']
        
        self.write_to_log("\n**YOUR TURN**")
        self.write_to_log(f"Mutant Health: {m_health} | Your Health: {self.player_health}/100")
        self.write_to_log("A) **SHOOT** (Makarov PM)")
        self.write_to_log(f"B) **HEAL** (Field Dressing: {self.inventory.get('Field Dressing', 0)})")
        self.write_to_log("C) **FLEE** (50% chance of escape)")
        self.write_to_log("-" * 30)
        
    def handle_combat_input(self, choice):
        choice = choice.upper()
        if self.player_health <= 0:
            self.handle_knockout()
            return
            
        if choice == "A":
            self.combat_attack_action()
        elif choice == "B":
            if self.use_item("Field Dressing"):
                self.after(500, self.combat_mutant_turn)
            else:
                self.display_combat_menu()
                return # Give player another choice
        elif choice == "C":
            if random.random() < 0.5:
                self.write_to_log("\n💨 **SUCCESS!** You manage to lose the mutant in the undergrowth.")
                self.current_combat_target = None
                self.current_state = 'EXPLORATION_MENU'
                self.after(500, self.display_exploration_menu)
                return
            else:
                self.write_to_log("\n❌ **FAILURE!** The mutant is too fast and blocks your retreat!")
                self.after(500, self.combat_mutant_turn)
        else:
            self.write_to_log("[SYSTEM] Invalid choice.", 'warning')
            self.display_combat_menu()
            return
            
        # If attack was chosen, check victory and proceed to mutant turn
        if choice == "A":
            if self.current_combat_target['health'] <= 0:
                self.combat_end(True)
                return
            self.after(500, self.combat_mutant_turn)

    def combat_attack_action(self):
        p_damage = self.calculate_player_damage()
        m_name = self.current_combat_target['name']
        
        if self.inventory.get("Makarov PM Pistol", 0) > 0 and self.inventory.get("9x18mm PM Rounds", 0) > 0:
            self.inventory["9x18mm PM Rounds"] -= 1
            self.current_combat_target['health'] -= p_damage
            self.write_to_log(f" > You fire your pistol, hitting the {m_name} for **{p_damage}** damage.")
        elif self.inventory.get("Makarov PM Pistol", 0) > 0 and self.inventory.get("9x18mm PM Rounds", 0) == 0:
             self.write_to_log("You are out of 9x18mm ammo! You resort to striking the mutant with your pistol.")
             self.current_combat_target['health'] -= p_damage
        else:
            self.current_combat_target['health'] -= p_damage
            self.write_to_log(f" > You strike with your knife/fists, hitting for **{p_damage}** damage.")

    def combat_mutant_turn(self):
        m_name = self.current_combat_target['name']
        m_damage = self.current_combat_target['damage']
        
        p_damage_taken = m_damage
        self.player_health = max(0, self.player_health - p_damage_taken)
        
        self.write_to_log(f"\n < The {m_name} attacks you for **{p_damage_taken}** damage.", 'combat')
        self.write_to_log(f"  * Your Health: {self.player_health}/100 | Mutant Health: {self.current_combat_target['health']}")
        
        if self.player_health <= 0:
            self.combat_end(False)
        else:
            self.after(500, self.display_combat_menu)

    def combat_end(self, player_won):
        if player_won:
            self.write_to_log(f"\n✅ **VICTORY!** The {self.current_combat_target['name']} is defeated.")
            self.determine_loot(self.current_combat_target["loot"])
        else:
            self.write_to_log("\n❌ **DEFEAT!** You collapse from your wounds.")
            self.handle_knockout()
        
        self.current_combat_target = None
        self.current_state = 'EXPLORATION_MENU'
        self.after(500, self.display_exploration_menu)


    def handle_knockout(self):
        """Handles the player being knocked out."""
        
        self.write_to_log("\n🤕 **KNOCKED OUT**")
        self.write_to_log(f"{GUIDE_PREFIX} 'I'm applying a field dressing now. This is going to cost you!'", 'guide')
        
        if self.inventory.get("Field Dressing", 0) > 0:
            self.inventory["Field Dressing"] -= 1
            self.player_health = 10 
            self.write_to_log("🩹 Used Field Dressing. You are stabilized at 10 HP.")
        else:
            self.player_health = 5 
            self.write_to_log("⚠️ No Field Dressings left! Stabilized at 5 HP.", 'warning')

        valuable_items = [i for i in self.inventory if i not in ["Rusty 5.45mm Rounds", FOOD_ITEM]]
        if valuable_items:
            lost_item = random.choice(valuable_items)
            if self.inventory[lost_item] > 0:
                self.inventory[lost_item] -= 1
                if self.inventory[lost_item] == 0: del self.inventory[lost_item]
                self.write_to_log(f"[LOST: -1 {lost_item}] The attackers escaped with your **{lost_item}**!")

        self.player_health = max(1, self.player_health)
        self.write_to_log("-" * 30)

    # --- NPC Encounter Logic ---

    def handle_npc_encounter_start(self):
        faction_name = random.choice(list(FACTIONS.keys()))
        self.current_npc_faction = faction_name
        rep_score = self.reputation.get(faction_name, 0)
        
        self.write_to_log("-" * 30)
        self.write_to_log(f"👥 **ENCOUNTER: {faction_name} Stalkers**")
        self.write_to_log("-" * 30)

        if faction_name == "Bandits" and rep_score < 0:
            self.write_to_log("A group of Bandits steps out, demanding everything you have. What do you do?")
            self.write_to_log("1) **FIGHT** (Risk damage, -10 Bandits Rep)")
            self.write_to_log("2) **SURRENDER** (Lose 1 item, +5 Bandits Rep)")
            food_count = self.inventory.get(FOOD_ITEM, 0)
            self.write_to_log(f"3) **BRIBE** (Offer 1 food, +10 Bandits Rep, Food: {food_count})")
            self.write_to_log("-" * 30)
            self.current_state = 'NPC_ENCOUNTER'
        elif rep_score >= 40:
            self.write_to_log(f"The {faction_name} group is friendly. They **trade** supplies.")
            self.add_item_to_inventory("9x18mm PM Rounds", 5)
            self.update_reputation(faction_name, 5)
            self.after(500, self.display_exploration_menu)
        else: 
            self.write_to_log(f"The {faction_name} group is neutral. You **part ways** peacefully.")
            self.after(500, self.display_exploration_menu)

    def handle_npc_input(self, choice):
        faction_name = self.current_npc_faction
        
        if choice == "1":
            self.write_to_log("You draw your weapon. Conflict is inevitable, but you manage to scare them off.")
            self.update_reputation(faction_name, -10)
        elif choice == "2":
            self.write_to_log("You drop your bag and raise your hands.")
            if self.inventory:
                stolen_item = random.choice(list(self.inventory.keys()))
                self.inventory[stolen_item] = max(0, self.inventory[stolen_item] - 1)
                if self.inventory[stolen_item] == 0: del self.inventory[stolen_item]
                self.write_to_log(f"[STOLEN: -1 {stolen_item}] You lost an item, but the Bandits leave quickly.")
            self.update_reputation(faction_name, 5) 
        elif choice == "3":
            if self.inventory.get(FOOD_ITEM, 0) > 0:
                self.inventory[FOOD_ITEM] -= 1
                self.write_to_log("You toss them a can of food. They begrudgingly accept and move on.")
                self.update_reputation(faction_name, 10)
            else:
                self.write_to_log("You have no food to offer! They get angry and leave in frustration.")
                self.update_reputation(faction_name, -5)
        else:
            self.write_to_log("[SYSTEM] Invalid choice.", 'warning')
            return # Stay in NPC_ENCOUNTER

        self.current_state = 'EXPLORATION_MENU'
        self.current_npc_faction = None
        self.after(500, self.display_exploration_menu)

    # --- Utility and Menu Functions ---

    def display_inventory(self):
        """Prints the current inventory."""
        self.write_to_log("\n🎒 **INVENTORY**")
        self.write_to_log(f"  * Health: {self.player_health}/100")
        
        if not self.inventory:
            self.write_to_log("  (Empty)")
        else:
            for item, count in self.inventory.items():
                self.write_to_log(f"  * {item}: x{count}")
        self.write_to_log("-" * 30)

    def display_reputation(self):
        """Prints the current player reputation."""
        self.write_to_log("\n🤝 **FACTION STANDING**")
        for faction, rep_score in self.reputation.items():
            status = "Ally" if rep_score >= 70 else \
                     "Friendly" if rep_score >= 40 else \
                     "Neutral" if rep_score >= 0 else \
                     "Wary" if rep_score >= -40 else \
                     "Hostile"
            self.write_to_log(f"  * {faction}: {rep_score} ({status})")
        self.write_to_log("-" * 30)

    def update_reputation(self, faction, amount):
        """Updates player reputation and prints a notification."""
        self.reputation[faction] = max(-100, min(100, self.reputation.get(faction, 0) + amount))
        self.write_to_log(f"[Reputation Change: {faction} {amount:+} | New Standing: {self.reputation[faction]}]")

    def add_item_to_inventory(self, item_name, quantity=1):
        """Adds a specified item and quantity to the inventory."""
        if item_name in self.inventory:
            self.inventory[item_name] += quantity
        else:
            self.inventory[item_name] = quantity
        self.write_to_log(f"[Acquired: +{quantity} {item_name}]")

    def determine_loot(self, loot_type):
        """Randomly selects and returns loot from the specified table."""
        loot_pool = LOOT_TABLES.get(loot_type, {})
        if not loot_pool: return

        items = list(loot_pool.keys())
        weights = list(loot_pool.values())
        
        num_items = random.randint(1, 3) if loot_type != "STRUCTURE_SPECIAL" else 1
        
        self.write_to_log("\n[RESULT] You found something!")
        for _ in range(num_items):
            chosen_item = random.choices(items, weights, k=1)[0]
            quantity = random.randint(1, 5) if loot_type == "COMMON" else 1
            self.add_item_to_inventory(chosen_item, quantity)

    def use_item(self, item_name):
        """Consumes an item from inventory and applies its effect (simplified)."""
        if item_name in USABLE_ITEMS:
            if self.inventory.get(item_name, 0) > 0:
                self.inventory[item_name] -= 1
                effect = USABLE_ITEMS[item_name]
                
                if "heal" in effect:
                    heal_amount = effect["heal"]
                    self.player_health = min(100, self.player_health + heal_amount)
                    self.write_to_log(f"🩹 You use a **{item_name}** and recover {heal_amount} HP. Health: {self.player_health}/100.")
                    return True
                if "rad_cure" in effect:
                    self.write_to_log(f"You chug the {item_name}. You feel momentarily worse...")
                    return True
            else:
                self.write_to_log(f"You don't have any **{item_name}**!", 'warning')
                return False
        else:
            self.write_to_log(f"You cannot use **{item_name}** right now.", 'warning')
            return False

    # --- Save/Load Functions ---

    def save_game(self):
        """Saves the current game state to a JSON file."""
        state = {
            'name': self.player_name, 'health': self.player_health, 'inventory': self.inventory,
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
                self.inventory = state['inventory']
                self.reputation = state['reputation']
                self.player_x = state['x']
                self.player_y = state['y']
            self.clear_log()
            self.write_to_log(f"[SYSTEM] Game loaded. Welcome back, {self.player_name}!", 'guide')
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