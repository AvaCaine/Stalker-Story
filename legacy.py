import random
import time
import json
import os

# --- Global Game Variables ---

# Constants for formatting
GUIDE_PREFIX = "Guide: "
QUOTE = "''"
SPACE = " "
DIVIDER = "---" * 30
SAVE_FILE = "stalker_save.json"
FOOD_ITEM = "Tourist's Delight Can" # Defined for easy reference/syntax fixing

# State Variables
inventory = {}
player_name = ""
player_health = 100 
player_x = 0
player_y = 0
player_location_name = "Rookie Village Outskirts" 

# Reputation Variables
reputation = { 
    "Loners": 50, "Bandits": -25, "Duty": 10,     
    "Freedom": -10, "Ecologists": 75 
}

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

# Define what items can be used and their effects
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

STRUCTURES = {
    "Abandoned Research Post": {
        "description": "A low-profile, concrete building, partially buried and covered in thick vines.",
        "steps": {
            1: {"text": "Enter the main lab or try the back service **hatch**.", "options": ["LAB", "HATCH"]},
            "LAB": {"text": "The lab is ransacked. Check the **desks** or the **storage cabinets**?", "options": ["DESK", "CABINET"]},
            "DESK": {"text": "A minor find.", "loot": "COMMON"},
            "CABINET": {"text": "The cabinet is locked but yields a major find!", "loot": "RARE"},
            "HATCH": {"text": "A dead Stalker lies nearby. **Loot** the Stalker or **ignore** them?", "options": ["LOOT", "IGNORE"]},
            "LOOT": {"text": "The dead Stalker was carrying some supplies.", "loot": "COMMON"},
            "IGNORE": {"text": "You decide to respect the dead."}
        }, "initial_step": 1
    },
    # ... (other structures remain the same) ...
}


# --- System Functions: Save/Load ---

def save_game():
    """Saves the current game state to a JSON file."""
    state = {
        'name': player_name, 'health': player_health, 'inventory': inventory,
        'reputation': reputation, 'x': player_x, 'y': player_y
    }
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(state, f, indent=4)
        print(f"\n[SYSTEM] Game state saved successfully to {SAVE_FILE}.")
    except Exception as e:
        print(f"\n[SYSTEM] Error saving game: {e}")

def load_game():
    """Loads the game state from the JSON file."""
    global player_name, player_health, inventory, reputation, player_x, player_y
    try:
        with open(SAVE_FILE, 'r') as f:
            state = json.load(f)
            player_name = state['name']
            player_health = state['health']
            inventory = state['inventory']
            reputation = state['reputation']
            player_x = state['x']
            player_y = state['y']
        print(f"\n[SYSTEM] Game loaded. Welcome back, {player_name}!")
        return True
    except FileNotFoundError:
        print("\n[SYSTEM] No saved game found. Starting new game.")
        return False
    except Exception as e:
        print(f"\n[SYSTEM] Error loading game: {e}")
        return False


# --- Utility Functions ---

def drop_item(item_name, quantity=1):
    """Removes an item from the inventory."""
    if inventory.get(item_name, 0) >= quantity:
        inventory[item_name] -= quantity
        if inventory[item_name] == 0:
            del inventory[item_name]
        print(f"🗑️ You dropped {quantity}x **{item_name}**.")
    else:
        print(f"Error: You tried to drop {quantity} {item_name}, but only have {inventory.get(item_name, 0)}.")

def use_item(item_name):
    """Consumes an item from inventory and applies its effect."""
    global player_health
    
    if item_name in USABLE_ITEMS:
        if inventory.get(item_name, 0) > 0:
            inventory[item_name] -= 1
            effect = USABLE_ITEMS[item_name]
            
            if "heal" in effect:
                heal_amount = effect["heal"]
                player_health = min(100, player_health + heal_amount)
                print(f"🩹 You use a **{item_name}** and recover {heal_amount} HP. Health: {player_health}/100.")
                return True
            if "rad_cure" in effect:
                print(f"You chug the {item_name}. You feel momentarily worse, but your Geiger counter stops clicking as fast.")
                # This would integrate with a future radiation mechanic
                return True
        else:
            print(f"You don't have any **{item_name}**!")
            return False
    else:
        print(f"You cannot use **{item_name}** right now.")
        return False

def display_reputation():
    """Prints the current player reputation with all factions."""
    print(DIVIDER)
    print("🤝 **FACTION STANDING**")
    for faction, rep_score in reputation.items():
        status = "Ally" if rep_score >= 70 else \
                 "Friendly" if rep_score >= 40 else \
                 "Neutral" if rep_score >= 0 else \
                 "Wary" if rep_score >= -40 else \
                 "Hostile"
        print(f"  * {faction}: {rep_score} ({status})")
    print(DIVIDER)
    input("Press Enter to continue...")

def update_reputation(faction, amount):
    """Updates player reputation and prints a notification."""
    global reputation
    reputation[faction] = max(-100, min(100, reputation.get(faction, 0) + amount))
    time.sleep(0.5)
    print(f"\n[Reputation Change: {faction} {amount:+} | New Standing: {reputation[faction]}]")
    time.sleep(0.5)

def add_item_to_inventory(item_name, quantity=1):
    """Adds a specified item and quantity to the inventory."""
    if item_name in inventory:
        inventory[item_name] += quantity
    else:
        inventory[item_name] = quantity
    print(f"\n[Acquired: +{quantity} {item_name} x{quantity}]")

def determine_loot(loot_type):
    """Randomly selects and returns loot from the specified table."""
    loot_pool = LOOT_TABLES.get(loot_type, {})
    if not loot_pool: return

    items = list(loot_pool.keys())
    weights = list(loot_pool.values())
    
    num_items = random.randint(1, 3) if loot_type != "STRUCTURE_SPECIAL" else 1
    
    print("\n[RESULT] You found something!")
    for _ in range(num_items):
        chosen_item = random.choices(items, weights, k=1)[0]
        quantity = random.randint(1, 5) if loot_type == "COMMON" else 1
        add_item_to_inventory(chosen_item, quantity)

# --- Inventory Menu System ---

def handle_item_actions(item_name):
    """Sub-menu for item actions (Use, Drop, Cancel)."""
    
    while True:
        is_usable = item_name in USABLE_ITEMS
        
        print(DIVIDER)
        print(f"Selected: **{item_name}** (x{inventory.get(item_name, 0)})")
        print(f"A) Use Item (Usable: {'Yes' if is_usable else 'No'})")
        print("B) Drop Item")
        print("C) Cancel")
        print(DIVIDER)
        
        action = input("Action (A/B/C): ").strip().upper()
        
        if action == 'A':
            if is_usable:
                use_item(item_name)
                return # Exit item submenu after use attempt
            else:
                print("Cannot use that item right now.")
        elif action == 'B':
            drop_item(item_name)
            return # Exit item submenu after drop
        elif action == 'C':
            return # Back to main inventory list
        else:
            print("Invalid action.")

def inventory_menu():
    """Interactive inventory display and item selection."""
    while True:
        print(DIVIDER)
        print("🎒 **INVENTORY**")
        print(f"  * Health: {player_health}/100")
        
        items_list = list(inventory.keys())
        if not items_list:
            print("  (Empty)")
            print(DIVIDER)
            input("Press Enter to close inventory...")
            return

        item_map = {}
        print("\nItems:")
        for i, item in enumerate(items_list):
            item_map[str(i + 1)] = item
            print(f"{i + 1}) {item}: x{inventory[item]}")
        
        print("\nX) Close Inventory")
        print(DIVIDER)
        
        choice = input("Select item number or X: ").strip().upper()
        
        if choice == 'X':
            return
        
        if choice in item_map:
            selected_item = item_map[choice]
            handle_item_actions(selected_item)
        else:
            print("Invalid input.")

# --- Tactical Combat System ---

def calculate_player_damage():
    """Determines player damage based on equipped weapon (simplified)."""
    if inventory.get("Makarov PM Pistol", 0) > 0 and inventory.get("9x18mm PM Rounds", 0) > 0:
        return random.randint(10, 20)
    else:
        return random.randint(2, 5) 

def handle_combat(mutant_name):
    """Handles turn-based combat with a single mutant."""
    global player_health
    mutant = MUTANTS[mutant_name]
    m_health = mutant["health"]
    m_damage = mutant["damage"]

    print(DIVIDER)
    print(f"🚨 **COMBAT START: {mutant_name} ATTACKS!**")
    print(mutant['description'])
    print(DIVIDER)

    while m_health > 0:
        if player_health <= 0:
            handle_knockout()
            return True 

        print("\n**YOUR TURN**")
        print(f"Mutant Health: {m_health} | Your Health: {player_health}/100")
        print("A) **SHOOT** (Makarov PM)")
        print(f"B) **HEAL** (Field Dressing: {inventory.get('Field Dressing', 0)})")
        print("C) **FLEE** (50% chance of escape)")
        
        choice = input("Action (A/B/C): ").strip().upper()
        
        # Player Action Phase
        if choice == "A":
            p_damage = calculate_player_damage()
            if inventory.get("Makarov PM Pistol", 0) > 0 and inventory.get("9x18mm PM Rounds", 0) > 0:
                inventory["9x18mm PM Rounds"] -= 1
                m_health -= p_damage
                print(f" > You fire your pistol, hitting the {mutant_name} for **{p_damage}** damage.")
            elif inventory.get("Makarov PM Pistol", 0) > 0 and inventory.get("9x18mm PM Rounds", 0) == 0:
                 print("You are out of 9x18mm ammo! You resort to striking the mutant with your pistol.")
                 m_health -= p_damage
            else:
                m_health -= p_damage
                print(f" > You strike with your knife/fists, hitting the {p_damage} damage.")

        elif choice == "B":
            if use_item("Field Dressing"):
                pass
            else:
                continue 

        elif choice == "C":
            if random.random() < 0.5:
                print("\n💨 **SUCCESS!** You manage to lose the mutant in the undergrowth.")
                return True 
            else:
                print("\n❌ **FAILURE!** The mutant is too fast and blocks your retreat!")

        else:
            print("Invalid choice. You hesitate!")
            
        # Check for Victory
        if m_health <= 0:
            print(f"\n✅ **VICTORY!** The {mutant_name} is defeated.")
            determine_loot(mutant["loot"])
            return True

        # Mutant Attack Phase
        p_damage_taken = m_damage
        player_health -= p_damage_taken
        print(f"\n < The {mutant_name} attacks you for **{p_damage_taken}** damage.")
        print(f"  * Your Health: {player_health}/100 | Mutant Health: {m_health}")
        time.sleep(1)

def handle_knockout():
    """Handles the player being knocked out (Health <= 0)."""
    global player_health
    
    print(DIVIDER)
    print("🤕 **KNOCKED OUT**")
    print(GUIDE_PREFIX, QUOTE, f"{player_name}, you're down! I'm applying a field dressing now. This is going to cost you!", QUOTE)
    
    if inventory.get("Field Dressing", 0) > 0:
        inventory["Field Dressing"] -= 1
        player_health = 10 
        print("🩹 Used Field Dressing. You are stabilized at 10 HP.")
    else:
        player_health = 5 
        print("⚠️ No Field Dressings left! Stabilized at 5 HP.")

    valuable_items = [i for i in inventory if i not in ["Rusty 5.45mm Rounds", FOOD_ITEM]]
    if valuable_items:
        lost_item = random.choice(valuable_items)
        if inventory[lost_item] > 0:
            inventory[lost_item] -= 1
            if inventory[lost_item] == 0: del inventory[lost_item]
            print(f"[-1 {lost_item}] The mutant escaped with your **{lost_item}**!")
    
    print(DIVIDER)
    input("Press Enter to wake up and continue...")
    print(SPACE)

# --- Encounter Logic (Fixed NPC Print) ---

def handle_npc_encounter():
    """Triggers and handles an encounter with a Stalker or group."""
    
    faction_name = random.choice(list(FACTIONS.keys()))
    
    print(DIVIDER)
    print(f"👥 **ENCOUNTER: {faction_name} Stalkers**")
    print(DIVIDER)

    rep_score = reputation.get(faction_name, 0)
    
    # 1. BANDIT INTERACTION (Fixed SyntaxError)
    if faction_name == "Bandits" and rep_score < 0:
        print("A group of Bandits steps out, demanding everything you have. What do you do?")
        print("1) **FIGHT** (Risk damage, -10 Bandits Rep)")
        print("2) **SURRENDER** (Lose 1 item, +5 Bandits Rep)")
        
        # FIX: Calculate the inventory count outside of the f-string's curly braces.
        food_count = inventory.get(FOOD_ITEM, 0)
        print(f"3) **BRIBE** (Offer 1 food, +10 Bandits Rep, Food: {food_count})")
        
        print(DIVIDER)
        
        while True:
            choice = input("Your choice (1/2/3): ").strip()
            if choice == "1":
                print("You draw your weapon. Conflict is inevitable, but you manage to scare them off.")
                update_reputation(faction_name, -10)
                break
            elif choice == "2":
                print("You drop your bag and raise your hands.")
                if inventory:
                    stolen_item = random.choice(list(inventory.keys()))
                    inventory[stolen_item] = max(0, inventory[stolen_item] - 1)
                    if inventory[stolen_item] == 0: del inventory[stolen_item]
                    print(f"[STOLEN: -1 {stolen_item}] You lost an item, but the Bandits leave quickly.")
                update_reputation(faction_name, 5) 
                break
            elif choice == "3":
                if inventory.get(FOOD_ITEM, 0) > 0:
                    inventory[FOOD_ITEM] -= 1
                    print("You toss them a can of food. They begrudgingly accept and move on.")
                    update_reputation(faction_name, 10)
                else:
                    print("You have no food to offer! They get angry and leave in frustration.")
                    update_reputation(faction_name, -5)
                break
            else:
                print("Invalid choice.")
        
    # 2. OTHER FACTIONS
    elif rep_score >= 40:
        print(f"The {faction_name} group is friendly. They **trade** supplies.")
        add_item_to_inventory("9x18mm PM Rounds", 5)
        update_reputation(faction_name, 5)
    else: 
        print(f"The {faction_name} group is neutral. You **part ways** peacefully.")

    time.sleep(1)
    print(DIVIDER)

# --- Main Game Loop ---

def exploration_loop():
    """The core endless loop for movement, encounters, and interaction."""
    
    print(DIVIDER)
    print(GUIDE_PREFIX, QUOTE, "The Zone awaits. What do you do?", QUOTE)
    
    if player_x == 0 and player_y == 0 and player_health > 0:
        generate_new_area()

    while True:
        if player_health <= 0:
            handle_knockout()
            
        print("\n**ACTIONS**")
        print(f"1) Move **(N)orth, (E)ast, (W)est, (S)outh** (Location: {player_location_name} @ {player_x},{player_y})")
        print("2) Check **INVENTORY** (Health/Items)")
        print("3) Check **REPUTATION** (Faction Standings)")
        print("4) **SAVE** Game")
        print("5) **EXIT** Game (Save & Quit)")
        print(DIVIDER)
        
        action = input(f"Enter your choice (1/2/3/4/5) or Direction (N/E/W/S): ").strip().upper()
        print(DIVIDER)

        if action in ("N", "E", "W", "S"):
            move_player(action)
                
        elif action == "1":
            direction_input = input("Which direction? (N/E/W/S): ").strip().upper()
            if direction_input in ("N", "E", "W", "S"):
                move_player(direction_input)
            else:
                print("Invalid direction input. Please use N, E, W, or S.")
                
        elif action == "2":
            inventory_menu()
            
        elif action == "3":
            display_reputation()
            
        elif action == "4":
            save_game()
            
        elif action == "5":
            save_game()
            print(f"\n{GUIDE_PREFIX} {QUOTE}Ending your run, {player_name}? Farewell for now.{QUOTE}")
            break
            
        else:
            print("Invalid command. Choose 1-5, or a direction (N/E/W/S).")

# --- Game Execution & Setup Scenes (Remaining code is the same) ---
def move_player(direction):
    """Updates the player's coordinates based on directional input."""
    global player_x, player_y, player_location_name
    
    if direction == "N": player_y += 1
    elif direction == "S": player_y -= 1
    elif direction == "E": player_x += 1
    elif direction == "W": player_x -= 1
    
    distance = abs(player_x) + abs(player_y)
    if distance == 0: player_location_name = "Rookie Village Outskirts"
    elif distance < 5: player_location_name = "Near Zone Edge"
    elif distance < 15: player_location_name = "Outer Zone Territories"
    else: player_location_name = "Deep Zone Sector"
        
    print(DIVIDER)
    print(f"**Moving {direction}...**")
    print(GUIDE_PREFIX, QUOTE, f"We've moved to coordinates ({player_x}, {player_y}). Let's check the area.", QUOTE)
    print(DIVIDER)
    
    return generate_new_area()

def generate_new_area():
    """Generates a new area description and may trigger a structure, NPC, or Mutant encounter."""
    
    if player_health <= 0:
        handle_knockout()
        
    print(f"🧭 **CURRENT LOCATION: {player_location_name} ({player_x}, {player_y})**")
    print(DIVIDER)
    
    # Weighted Event Roll (5% Mutant)
    event_roll = random.choices(["MUTANT", "STRUCTURE", "NPC", "STANDARD"], weights=[5, 20, 20, 55], k=1)[0]
    
    if event_roll == "MUTANT":
        mutant_name = random.choice(list(MUTANTS.keys()))
        handle_combat(mutant_name)
        
    elif event_roll == "STRUCTURE":
        structure_name = random.choice(list(STRUCTURES.keys()))
        handle_structure_encounter(structure_name)
    
    elif event_roll == "NPC":
        handle_npc_encounter()
        
    elif event_roll == "STANDARD":
        print(random.choice(LOCATIONS))
        if random.random() < 0.15: 
             print("\n[Small Find] You find a lone item on the ground.")
             determine_loot("COMMON")

    print(SPACE)
    return True

def handle_structure_encounter(structure_name):
    structure = STRUCTURES[structure_name]
    print(DIVIDER)
    print(f"🛑 **STRUCTURE FOUND: {structure_name}**")
    print(structure["description"])
    print(DIVIDER)
    current_step_key = structure["initial_step"]
    
    while True:
        step = structure["steps"].get(current_step_key)
        
        if not step:
            print("\n[Exploration Complete: You have finished searching this area.]")
            return

        print(GUIDE_PREFIX, QUOTE, step["text"], QUOTE)
        time.sleep(0.5)

        if "options" in step:
            options_list = step["options"]
            options_map = {str(i + 1): opt for i, opt in enumerate(options_list)}
            
            print("\n**Choose your next action:**")
            for i, option_key in enumerate(options_list):
                print(f"{i + 1}) {option_key}")
            print(DIVIDER)

            while True:
                choice = input(f"Your Choice (1-{len(options_list)}): ").strip()
                if choice in options_map:
                    current_step_key = options_map[choice]
                    time.sleep(0.5)
                    break
                else:
                    print("Invalid input. Try again.")
                    
        elif "loot" in step:
            print(f"\n[NARRATIVE] {step['text']}")
            determine_loot(step["loot"])
            time.sleep(1)
            return
        else:
            print(f"\n[NARRATIVE] {step['text']}")
            time.sleep(1)
            return

def scene_intro():
    global player_name 
    print(GUIDE_PREFIX, QUOTE, "Hello STALKER, I'll be your guide to getting started here, though, I must ask, what should I call you?", QUOTE, SPACE)
    
    while True:
        player_name = input("My name's... ").strip()
        if player_name: break
        print("You must enter a name, stalker.")
    
    print(SPACE)
    print(GUIDE_PREFIX, QUOTE, "Pleasure to meet you,", player_name, QUOTE, SPACE)

    print(DIVIDER)
    print("Respond:")
    print("1) Nice to meet you as well.")
    print("2) Let's just get going.")
    print("3) Enough pleasantry, I don't need the chit-chat.")
    print("4) *Remain silent...*")
    print(DIVIDER)
    
    while True:
        respond1 = input("Your Reply (1/2/3/4): ").strip()
        print(DIVIDER)
        if respond1 == "1":
            print(GUIDE_PREFIX, QUOTE, "Alright then, we'd best get a move on. I appreciate the manners.", QUOTE); break
        elif respond1 == "2":
            print(GUIDE_PREFIX, QUOTE, "Alright, fair enough I guess, we do need to get going.", QUOTE); break
        elif respond1 == "3":
            print(GUIDE_PREFIX, QUOTE, "Damn, well screw you I guess, now let's get going.", QUOTE); break
        elif respond1 == "4":
            print(GUIDE_PREFIX, QUOTE, "Not a talker stalker huh, well, we better get going.", QUOTE); break
        else:
            print("Invalid input. Please choose 1, 2, 3, or 4.")
    
    print(SPACE)
    input("Press Enter to continue...")
    print(SPACE)

def scene_weapons_crate():
    print(DIVIDER)
    print(GUIDE_PREFIX, QUOTE, "Hey, hold up. There is an old weapons crate here.", QUOTE)
    print(DIVIDER)
    print("\n📦 **Old Wooden Crate**")
    print("1) Open the crate and look inside.")
    print("2) Leave it.")
    print(SPACE)

    while True:
        open_input = input("- (1/2) ").strip()
        print(DIVIDER)

        if open_input == "1":
            print(GUIDE_PREFIX, QUOTE, "Nice! A trusty sidearm. Take care of it, stalker.", QUOTE)
            add_item_to_inventory("Makarov PM Pistol")
            add_item_to_inventory("9x18mm PM Rounds", 12)
            add_item_to_inventory("Field Dressing", 1) 
            break
        elif open_input == "2":
            print(GUIDE_PREFIX, QUOTE, "Suit yourself. Let's move.", QUOTE)
            break
        else:
            print("Invalid input. Please choose 1 or 2.")
            print(DIVIDER)

def main_game():
    """The main function to run the game flow."""
    print(DIVIDER)
    print("--- **STALKER ZONE SIMULATOR** ---")
    print("1) Start New Game")
    print("2) Load Saved Game")
    print(DIVIDER)
    
    choice = input("Your Choice (1/2): ").strip()
    
    if choice == "2":
        if not load_game():
            scene_intro()
            scene_weapons_crate()
    else:
        scene_intro()
        scene_weapons_crate()

    exploration_loop()
    
    print("\n--- GAME SESSION ENDED ---")


# Execute the game
if __name__ == "__main__":
    main_game()