import random
import time # Added for small delays to improve reading flow

# --- Global Game Variables ---

# Constants for formatting
GUIDE_PREFIX = "Guide: "
QUOTE = "''"
SPACE = " "
DIVIDER = "---" * 30  # A cleaner divider

# Inventory System (using a dictionary)
inventory = {}
player_name = ""
player_location = "Rookie Village Outskirts"

# --- Loot and Structure Definitions ---

# Define Item Drops
LOOT_TABLES = {
    "COMMON": {
        "Rusty 5.45mm Rounds": 10,
        "Field Dressing": 8,
        "Tourist's Delight Can": 15,
        "Vodka (Cure Radiation)": 5
    },
    "RARE": {
        "Anti-Radiation Drug": 15,
        "High-Grade 9x19mm Rounds": 10,
        "Basic Repair Kit": 5
    },
    "STRUCTURE_SPECIAL": {
        "Flash Artifact": 1,
        "Empty PDA": 3,
        "Broken Gas Mask": 5
    }
}

# Define Structures and their unique steps
STRUCTURES = {
    "Abandoned Research Post": {
        "description": "A low-profile, concrete building, partially buried and covered in thick vines. An ominous silence hangs over it.",
        "steps": {
            1: {"text": "Enter the main lab (requires a **key** which may be outside) or try the back service hatch.", "options": ["LAB", "HATCH"]},
            "LAB": {"text": "The lab is clean but ransacked. Do you check the **desks** or the **storage cabinets**?", "options": ["DESK", "CABINET"]},
            "HATCH": {"text": "The cramped service area smells strongly of ozone. A dead **Stalker** lies nearby. Do you **Loot** the Stalker or ignore them?", "options": ["LOOT", "IGNORE"]},
            "DESK": {"text": "You find a half-eaten snack and a rusty knife. (Minor find)", "loot": "COMMON"},
            "CABINET": {"text": "The cabinet is locked but yields to your knife. You find something important!", "loot": "RARE"},
            "LOOT": {"text": "The dead Stalker was carrying some supplies.", "loot": "COMMON"},
            "IGNORE": {"text": "You decide to respect the dead and move past quickly. (No loot, no danger)"}
        },
        "initial_step": 1
    },
    "Wrecked Train Depot": {
        "description": "An immense, rusted hangar containing the husks of several freight train cars. The interior is dark and cavernous.",
        "steps": {
            1: {"text": "Approach the **largest train car** or ascend the **observation platform**?", "options": ["CAR", "PLATFORM"]},
            "CAR": {"text": "The train car is dark. You hear skittering. Do you search the **passenger seats** or look beneath the **floorboards**?", "options": ["SEATS", "FLOOR"]},
            "PLATFORM": {"text": "The observation platform gives you a good view. You spot a **weapon crate** on the roof of the opposite hangar.", "options": ["CRATE"]},
            "SEATS": {"text": "Under a tattered cushion, you find a small dose of medicine.", "loot": "COMMON"},
            "FLOOR": {"text": "A flash of light leads you to a valuable, unique item!", "loot": "STRUCTURE_SPECIAL"},
            "CRATE": {"text": "Getting across is dangerous, but the crate is filled with useful items.", "loot": "RARE"}
        },
        "initial_step": 1
    }
}

# --- Utility Functions ---

def display_inventory():
    """Prints the current player inventory."""
    print(DIVIDER)
    print("🎒 **Inventory**")
    if inventory:
        for item, count in inventory.items():
            print(f"  * {item}: x{count}")
    else:
        print("  (Empty)")
    print(DIVIDER)

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
    if not loot_pool:
        print("[Loot system error: Invalid table name.]")
        return

    # Select an item based on weights (quantities)
    items = list(loot_pool.keys())
    weights = list(loot_pool.values())

    # Weighted random choice, select 1-3 items
    num_items = random.randint(1, 3) if loot_type != "STRUCTURE_SPECIAL" else 1

    for _ in range(num_items):
        chosen_item = random.choices(items, weights, k=1)[0]
        # Random quantity for common/rare items
        quantity = random.randint(1, 5) if loot_type == "COMMON" else 1
        add_item_to_inventory(chosen_item, quantity)

    display_inventory()


# --- Encounters and Exploration ---

def handle_structure_encounter(structure_name):
    """Handles the multi-step exploration within a found structure."""

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
            return # Exit the structure encounter

        print(GUIDE_PREFIX, QUOTE, step["text"], QUOTE)
        time.sleep(0.5)

        # 1. Handle Options (Decision Point)
        if "options" in step:
            options_list = step["options"]

            # Format options for display
            options_map = {str(i + 1): opt for i, opt in enumerate(options_list)}

            print("\n**Choose your next action:**")
            for i, option_key in enumerate(options_list):
                print(f"{i + 1}) {option_key}")
            print(DIVIDER)

            while True:
                choice = input(f"Your Choice (1-{len(options_list)}): ").strip()
                if choice in options_map:
                    # Set the next step key to the chosen option's key (e.g., '1' maps to 'LAB')
                    current_step_key = options_map[choice]
                    time.sleep(0.5)
                    break
                else:
                    print("Invalid input. Try again.")

        # 2. Handle Loot (End Point)
        elif "loot" in step:
            print("\n[RESULT] You found something!")
            determine_loot(step["loot"])
            time.sleep(1)
            return # Exit the structure after looting

        # 3. Handle Narrative (Simple End Point)
        else:
            print("\n[RESULT] Nothing left to do here.")
            time.sleep(1)
            return # Exit the structure

def generate_new_area():
    """Generates a new, random location description and may trigger a structure encounter."""
    global player_location

    # Simple location name update
    player_location = random.choice([
        "Ruined Factory", "Abandoned Swamp", "Old Camp Site",
        "Mutated Forest", "Fallen Bridge", "Anomaly Field"
    ])

    print(DIVIDER)
    print(f"🧭 **LOCATION: {player_location}**")
    print(DIVIDER)

    # 70% chance of standard exploration, 30% chance of structure
    if random.random() < 0.3:
        # Structure Encounter Triggered
        structure_name = random.choice(list(STRUCTURES.keys()))
        handle_structure_encounter(structure_name)
    else:
        # Standard Exploration
        print("The air is thick with the scent of damp earth and rust. The area is quiet, perhaps too quiet.")
        print(f"\n{GUIDE_PREFIX} {QUOTE}Just an open field, stalker. Nothing of note here. Let's keep moving.{QUOTE}")
        # Add a small chance for a random minor loot find
        if random.random() < 0.2:
             print("\nYou found a lone item on the ground.")
             determine_loot("COMMON")

    print(SPACE)


# --- Initial Setup/Story Scenes (Kept from previous version) ---

def scene_intro():
    # ... (code for scene_intro remains unchanged, except for adding 'global player_name' if not present) ...
    global player_name

    print(GUIDE_PREFIX, QUOTE, "Hello STALKER, I'll be your guide to getting started here, though, I must ask, what should I call you?", QUOTE, SPACE)

    while True:
        player_name = input("My name's... ").strip()
        if player_name:
            break
        print("You must enter a name, stalker.")

    print(SPACE)
    print(GUIDE_PREFIX, QUOTE, "Pleasure to meet you,", player_name, QUOTE, SPACE)

    # Interaction
    print(DIVIDER)
    print("Respond to the Guide:")
    print("1) Nice to meet you as well. (Polite)")
    print("2) Let's just get going. (Impatient)")
    print("3) Enough pleasantry, I don't need the chit-chat. (Rude)")
    print("4) *Remain silent...* (Reserved)")
    print(DIVIDER)

    while True:
        respond1 = input("Your Reply (1/2/3/4): ").strip()
        print(DIVIDER)
        if respond1 == "1":
            print(GUIDE_PREFIX, QUOTE, "Alright then, we'd best get a move on. I appreciate the manners.", QUOTE)
            break
        elif respond1 == "2":
            print(GUIDE_PREFIX, QUOTE, "Alright, fair enough I guess, we do need to get going. Time is money out here.", QUOTE)
            break
        elif respond1 == "3":
            print(GUIDE_PREFIX, QUOTE, "Damn, well screw you I guess, now let's get going. Don't worry, the Zone's got a nice way of fixing attitudes.", QUOTE)
            break
        elif respond1 == "4":
            print(GUIDE_PREFIX, QUOTE, "Not a talker, stalker, huh? Well, we better get going. Keep your eyes open, silence can be deadly.", QUOTE)
            break
        else:
            print("Invalid input. Please choose 1, 2, 3, or 4.")

    print(SPACE)
    input("Press Enter to continue...")
    print(SPACE)

def scene_weapons_crate():
    # ... (code for scene_weapons_crate remains unchanged) ...
    print(DIVIDER)
    print(GUIDE_PREFIX, QUOTE, "Hey, hold up. There is an old weapons crate here, looks like it hasn't been looted yet. Why don't you open it up and see what is in there!", QUOTE)
    print(DIVIDER)
    print("\n📦 **Old Wooden Crate**")
    print("1) Open the crate and look inside.")
    print("2) Leave it. It might be a trap or empty.")
    print("3) Check inventory.")
    print(SPACE)

    while True:
        open_input = input("- (1/2/3) ").strip()
        print(DIVIDER)

        if open_input == "1":
            print(GUIDE_PREFIX, QUOTE, "Nice! A trusty sidearm. And some rounds to go with it. Take care of it, stalker.", QUOTE)
            add_item_to_inventory("Makarov PM Pistol")
            add_item_to_inventory("9x18mm PM Rounds", 12)
            break

        elif open_input == "2":
            print(GUIDE_PREFIX, QUOTE, "Suit yourself. A brave man takes risks, but a wise man knows which ones to avoid. Let's move.", QUOTE)
            break

        elif open_input == "3":
            display_inventory()
            print("\nWhat do you do now?")

        else:
            print("Invalid input. Please choose 1, 2, or 3.")
            print(DIVIDER)

# --- Main Game Loop for Exploration ---

def exploration_loop():
    """The endless loop for movement and exploration."""

    # Initial location description after the setup scenes
    print(DIVIDER)
    print(GUIDE_PREFIX, QUOTE, "Alright, stalker, the path is clear now. Time to start moving deeper into the Zone. You're currently near the safety of the **Rookie Village Outskirts**.", QUOTE)
    print(DIVIDER)
    print("🧭 **CURRENT LOCATION: Rookie Village Outskirts**")
    print("The familiar buzz of the settlement's perimeter fence is barely audible behind you. The path ahead is overgrown and leads into dense, shadowy woods.")
    print(DIVIDER)

    while True:
        print("\n**What will you do?**")
        print(f"1) Move **DEEPER** into the Zone (Current Location: {player_location})")
        print("2) Check **INVENTORY**")
        print("3) **ASK** the Guide for advice")
        print("4) **EXIT** Game (End current session)")
        print(DIVIDER)

        action = input(f"Enter your choice (1/2/3/4): ").strip()
        print(DIVIDER)

        if action == "1":
            print(f"\n{GUIDE_PREFIX} {QUOTE}Heading into the unknown, I see. Keep your gun ready, {player_name}.{QUOTE}\n")
            generate_new_area()
            input("\nPress Enter to search for the next path...")

        elif action == "2":
            display_inventory()

        elif action == "3":
            print(GUIDE_PREFIX, QUOTE, "Advice? Trust no one, shoot first, and never run straight through a shimmering patch of air. Now, let's move.", QUOTE)

        elif action == "4":
            print(f"\n{GUIDE_PREFIX} {QUOTE}Ending your run, {player_name}? Come back when you're ready to face the Zone again. Farewell for now.{QUOTE}")
            break

        else:
            print("Invalid command. Choose 1, 2, 3, or 4.")
            print(DIVIDER)

# --- Game Execution ---

def main_game():
    """The main function to run the game flow."""
    print(DIVIDER)
    print("--- **THE ZONE: STALKER EXPLORATION** ---")
    print(DIVIDER)

    scene_intro()
    scene_weapons_crate()
    exploration_loop()

    print("\n--- GAME OVER ---")


# Execute the game
if __name__ == "__main__":
    main_game()
