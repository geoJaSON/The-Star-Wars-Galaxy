import random, time, os, copy

class Weapon:
    def __init__(self, name, damage, effect=None, cooldown=0):
        self.name = name
        self.damage = damage
        self.effect = effect
        self.cooldown = cooldown
        self.current_cooldown = cooldown

    def __str__(self):
        return f"{self.name} (Damage: {self.damage}, Effect: {self.effect if self.effect else 'None'}, Cooldown: {self.cooldown}, Current Cooldown: {self.current_cooldown})"

    def apply_effect(self, attacker, defender):
        if self.effect == "ion_cannon":
            if not defender.captain or not defender.captain.negate_ion_cannon():
                defender.turn_gauge = defender.turn_gauge/2
        elif self.effect == "missile_barrage":
            for _ in range(5):
                hit = random.randint(0, 100) < attacker.accuracy - defender.maneuverability
                if hit:
                    damage = self.damage
                    defender.take_damage(damage)
                    print(f"{attacker.name} attacks {defender.name} with {self.name} for {damage} damage.")
            print(f"{attacker.name} barrages {defender.name} with {self.name}.")
        elif self.effect == "tractor_beam":
            defender.maneuverability = 0
            defender.tractor_beam_turns = 2
            print(f"{defender.name}'s evasion is reduced to 0% for the next 2 turns due to the Tractor Beam.")

    def decrement_cooldown(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def is_available(self):
        return self.current_cooldown == 0
    
class Captain:
    def __init__(self, name, ability, ability_message, reference, trigger_condition=None):
        self.name = name
        self.ability = ability
        self.ability_message = ability_message
        self.reference = reference
        self.trigger_condition = trigger_condition
        self.turn_counter = 0
        self.effects = ["always_hit", "evade_hit", "extra_attack", "fill_turn_gauge", "negate_ion_cannon", "critical_hit", "shield_overload", "emp_blast", "cloaking_device"]
        self.current_effect = None
        if self.ability == "random_effect":
            self.current_effect = random.choice(self.effects)

    def use_ability(self, attacker=None, ship=None, defender=None, is_attacking=False, is_defending=False):
        self.turn_counter += 1
        if self.ability == "random_effect" and self.turn_counter % 2 == 0:
            self.current_effect = random.choice(self.effects)
            print(f"{self.name} rolls the dice! Gets {self.current_effect} effect!")

        effective_ability = self.current_effect if self.ability == "random_effect" else self.ability

        if self.trigger_condition == "attacking" and not is_attacking:
            return None
        if self.trigger_condition == "defending" and not is_defending:
            return None

        if effective_ability == "always_hit" and attacker and random.random() < 0.3:
            print(self.ability_message)
            return True
        elif effective_ability == "evade_hit" and defender and random.random() < 0.3:
            print(f"{self.ability_message}")
            return False
        elif effective_ability == "extra_attack" and attacker and random.random() < 0.3:
            print(self.ability_message)
            if defender:
                defender.take_damage(attacker.attack_power * 0.5)
        elif effective_ability == "fill_turn_gauge" and random.random() < 0.3:
            attacker.turn_gauge = 10
            print(self.ability_message)
        elif effective_ability == "negate_ion_cannon" and defender and random.random() < 0.3:
            print(self.ability_message)
            return True
        elif effective_ability == "critical_hit" and attacker and random.random() < 0.3:
            print(self.ability_message)
            return True
        elif effective_ability == "armor_drain":
            defender.armor_drain_turns = 3  # Drain armor for 3 turns
            print(f"{self.name} uses {self.ability_message} on {defender.name}!")
        elif effective_ability == "energy_drain":
            defender.energy_drain_turns = 3  # Drain energy for 3 turns
            print(f"{self.name} uses {self.ability_message} on {defender.name}!")
        elif effective_ability == "berserk" and attacker and random.random() < 0.1:
            attacker.activate_berserk()
        elif effective_ability == "shield_overload":
            ship.shields *= 2
            ship.overloaded_shields_turns = 3
            print(f"{self.ability_message} {ship.name}'s shields are overloaded!")
        elif effective_ability == "emp_blast" and defender:
            defender.emp_blast_turns = 1
            print(f"{self.name} uses {self.ability_message} on {defender.name}!")
        elif effective_ability == "cloaking_device" and random.random() < 0.3:
            ship.cloaking_device_turns = 1
            print(f"{self.ability_message} {ship.name} is cloaked and evades all attacks!")
        return None

    def negate_ion_cannon(self):
        effective_ability = self.current_effect if self.ability == "random_effect" else self.ability
        return effective_ability == "negate_ion_cannon" and random.random() < 0.3


class Ship:
    def __init__(self, name, shields, armor, attack_power, weapons, accuracy, maneuverability, speed, energy, shield_recharge_rate, critical_hit_chance, captain=None, wingman=None):
        self.name = name
        self.shields = shields
        self.armor = armor
        self.attack_power = attack_power
        self.weapons = copy.deepcopy(weapons)
        self.accuracy = accuracy
        self.maneuverability = maneuverability
        self.speed = speed
        self.energy = energy
        self.max_energy = energy
        self.shield_recharge_rate = shield_recharge_rate
        self.critical_hit_chance = critical_hit_chance
        self.turn_gauge = 0
        self.skip_turn = False
        self.captain = captain
        self.wingman = wingman
        self.tractor_beam_turns = 0
        self.armor_drain_turns = 0
        self.energy_drain_turns = 0
        self.berserk_turns = 0
        self.overloaded_shields_turns = 0
        self.emp_blast_turns = 0
        self.cloaking_device_turns = 0
        
    def take_damage(self, damage):
        if self.shields >= damage:
            self.shields -= damage
        else:
            remaining_damage = damage - self.shields
            self.shields = 0
            self.armor -= remaining_damage

    def is_destroyed(self):
        return self.armor <= 0

    def recharge_shields(self):
        if self.overloaded_shields_turns > 0:
            self.overloaded_shields_turns -= 1
            if self.overloaded_shields_turns == 0:
                self.shields /= 2
        else:
            self.shields = min(self.shields + self.shield_recharge_rate * self.shields, self.shields)

    def drain_armor(self):
        if self.armor_drain_turns > 0:
            drain_amount = self.armor * 0.01
            self.armor -= drain_amount
            self.armor_drain_turns -= 1
            print(f"{self.name} suffers {drain_amount:.2f} armor drain due to the effect.")

    def drain_energy(self):
        if self.energy_drain_turns > 0:
            drain_amount = self.energy * 0.05  # Drains 5% of current energy
            self.energy -= drain_amount
            self.energy_drain_turns -= 1
            print(f"{self.name} suffers {drain_amount:.2f} energy drain due to the effect.")

    def repair(self):
        energy_cost = 20
        repair_amount = 10
        if self.energy >= energy_cost:
            self.energy -= energy_cost
            self.armor += repair_amount
            print(f"{self.name} repairs {repair_amount} armor, costing {energy_cost} energy.")
        else:
            print(f"{self.name} does not have enough energy to repair.")

    def activate_berserk(self):
        self.berserk_turns = 3
        print(f"{self.name} enters berserk mode! Increased attack power but reduced accuracy and defense.")

    def apply_berserk_effects(self):
        if self.berserk_turns > 0:
            self.attack_power *= 1.5
            self.accuracy *= 0.75
            self.maneuverability *= 0.75
            self.berserk_turns -= 1
            print(f"{self.name} is in berserk mode! Attack power: {self.attack_power}, Accuracy: {self.accuracy}, Maneuverability: {self.maneuverability}")

    def reset_berserk_effects(self):
        if self.berserk_turns == 0:
            self.attack_power /= 1.5
            self.accuracy /= 0.75
            self.maneuverability /= 0.75

    def boost_shields(self):
        energy_cost = 15
        shield_boost = 20
        if self.energy >= energy_cost:
            self.energy -= energy_cost
            self.shields += shield_boost
            print(f"{self.name} boosts shields by {shield_boost}, costing {energy_cost} energy.")
        else:
            print(f"{self.name} does not have enough energy to boost shields.")

    def skip_next_turn(self):
        self.skip_turn = True

    def update_turn_gauge(self):
        self.turn_gauge += self.speed
        if self.turn_gauge >= 10:
            self.turn_gauge = 10

    def emp_blast(self):
        self.emp_blast_turns = 1
        print(f"{self.name} uses EMP Blast! The target ship's weapons are disabled for a turn.")

    def cloaking_device(self):
        self.cloaking_device_turns = 1
        print(f"{self.name} activates Cloaking Device! The ship evades all attacks for a turn.")

    def get_conditions(self):
        conditions = []
        if self.tractor_beam_turns > 0:
            conditions.append(f"Tractor Beam")
        if self.armor_drain_turns > 0:
            conditions.append(f"Armor Drain")
        if self.energy_drain_turns > 0:
            conditions.append(f"Energy Drain")
        if self.berserk_turns > 0:
            conditions.append(f"Berserk")
        if self.overloaded_shields_turns > 0:
            conditions.append(f"Overloaded Shields")
        if self.emp_blast_turns > 0:
            conditions.append(f"EMP Blast")
        if self.cloaking_device_turns > 0:
            conditions.append(f"Cloaked")
        if self.skip_turn:
            conditions.append("Skip Turn")
        return ", ".join(conditions) if conditions else "No Conditions"

    def __str__(self):
        return f"{self.name} - Shields: {self.shields}, Armor: {self.armor}, {self.get_conditions()}"
class Team:
    def __init__(self, name):
        self.name = name
        self.ships = []

    def add_ship(self, ship):
        self.ships.append(ship)

    def is_defeated(self):
        return all(ship.is_destroyed() for ship in self.ships)

    def __str__(self):
        return f"Team {self.name}:\n" + "\n".join(str(ship) for ship in self.ships)

def choose_option(options, prompt):
    while True:
        print(prompt)
        for idx, option in enumerate(options, 1):
            print(f"{idx}. {option}")
        try:
            choice = int(input("Choose an option: ")) - 1
            if 0 <= choice < len(options):
                return options[choice]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def battle(attacker_ship, defender_ship, weapon):
    hit_chance = (attacker_ship.accuracy - defender_ship.maneuverability)+30
    hit = random.randint(0, 100) < hit_chance

    if defender_ship.captain:
        evade = defender_ship.captain.use_ability(attacker=attacker_ship, ship=defender_ship, is_defending=True)
        if evade is False:
            print(f"{attacker_ship.name}'s attack on {defender_ship.name} is evaded!")
            return

    if hit:
        critical_hit = random.randint(0, 100) < attacker_ship.critical_hit_chance
        base_damage = weapon.damage * (2 if critical_hit else 1)
        if weapon.effect == "concussion_missile":
            damage_to_shields = base_damage * 0.5
            damage_to_armor = base_damage * 1.5
            if defender_ship.shields >= damage_to_shields:
                defender_ship.shields -= damage_to_shields
            else:
                remaining_damage = damage_to_shields - defender_ship.shields
                defender_ship.shields = 0
                defender_ship.armor -= remaining_damage * 1.5
            defender_ship.armor -= damage_to_armor
            print(f"{attacker_ship.name} attacks {defender_ship.name} with {weapon.name}, dealing {damage_to_shields} damage to shields and {damage_to_armor} damage to armor.")
        else:
            damage = base_damage
            defender_ship.take_damage(damage)
            print(f"{attacker_ship.name} attacks {defender_ship.name} with {weapon.name} for {damage} damage.")
        
        if critical_hit:
            print("It's a critical hit!")
        if weapon.effect and weapon.effect != "concussion_missile":
            weapon.apply_effect(attacker_ship, defender_ship)
            print(f"{defender_ship.name} is affected by {weapon.name}.")
        if defender_ship.is_destroyed():
            print(f"{defender_ship.name} is destroyed!")
    else:
        print(f"{attacker_ship.name} misses the attack on {defender_ship.name}.")
    if attacker_ship.captain:
        attacker_ship.captain.use_ability(attacker=attacker_ship, ship=attacker_ship, defender=defender_ship, is_attacking=True)

    weapon.current_cooldown = weapon.cooldown

def clear_screen():
    # For Windows
    if os.name == 'nt':
        os.system('cls')
    # For Unix/Linux/MacOS/BSD/etc
    else:
        os.system('clear')

def print_progress_bar(ship):
    bar_length = 20
    progress = min(int((ship.turn_gauge / 10) * bar_length), bar_length)
    bar = "|" + "-" * progress + " " * (bar_length - progress) + "|"
    print(f"{bar} {ship.turn_gauge:.2f} {ship.name} ")

def update_turn_gauge(ships):
    for ship in ships:
        if not ship.is_destroyed():
            ship.turn_gauge += ship.speed / 10
            ship.recharge_shields()
            if ship.tractor_beam_turns > 0:
                ship.tractor_beam_turns -= 1
                if ship.tractor_beam_turns == 0:
                    ship.maneuverability = original_maneuverability[ship.name]
                    print(f"{ship.name}'s evasion returns to normal.")
            ship.drain_armor()
            ship.drain_energy()


def game_loop(team1, team2):
    turn = 0
    original_maneuverability = {ship.name: ship.maneuverability for ship in team1.ships}
    original_maneuverability.update({ship.name: ship.maneuverability for ship in team2.ships})

    while not team1.is_defeated() and not team2.is_defeated():
        clear_screen()
        
        update_turn_gauge(team1.ships + team2.ships)

        for team in [team1, team2]:
            for ship in team.ships:
                if not ship.is_destroyed():
                    print_progress_bar(ship)

        ready_ships = [(ship, team) for team in [team1, team2] for ship in team.ships if ship.turn_gauge >= 10 and not ship.is_destroyed() and not ship.skip_turn]

        if ready_ships:
            print(f"{team1.name}- {team1.ships[0]}") # Display conditions for team 1 ships
            print(f"{team2.name}- {team2.ships[0]}") # Display conditions for team 2 ships
            ready_ships.sort(key=lambda x: x[0].turn_gauge, reverse=True)
            attacker_ship, attacker_team = ready_ships[0]
            attacker_ship.turn_gauge -= 10
            
            defender_team = team1 if attacker_team == team2 else team2
            defender_ship = random.choice([ship for ship in defender_team.ships if not ship.is_destroyed()])
            
            print(f"\n{attacker_team.name}'s turn")
            
            options = [weapon.name for weapon in attacker_ship.weapons if weapon.is_available()] + ["Repair", "Boost Shields"]
            choice = choose_option(options, f"Choose an action for {attacker_ship.name}:")

            for weapon in attacker_ship.weapons:
                weapon.decrement_cooldown()

            if choice == "Repair":
                attacker_ship.repair()
            elif choice == "Boost Shields":
                attacker_ship.boost_shields()
            else:
                if attacker_ship.emp_blast_turns > 0:
                    print(f"{attacker_ship.name}'s weapons are disabled due to EMP Blast.")
                    attacker_ship.emp_blast_turns -= 1
                else:
                    weapon = next(weapon for weapon in attacker_ship.weapons if weapon.name == choice)
                    battle(attacker_ship, defender_ship, weapon)
                    input("Press Enter to continue...")
            if attacker_ship.skip_turn:
                attacker_ship.skip_turn = False
            
        else:
            time.sleep(0.1)  # Add a small delay for readability

        turn += 1

    if team1.is_defeated():
        print(f"{team2.name} wins!")
        input("Press Enter to continue...")
    else:
        print(f"{team1.name} wins!")
        input("Press Enter to continue...")

def choose_team():
    print("Choose your team:")
    team_names = list(teams.keys())
    for idx, team_name in enumerate(team_names, 1):
        print(f"{idx}. {team_name}")
    choice = int(input("Choose an option: ")) - 1
    return team_names[choice]

def display_references():
    for team_name, team_info in teams.items():
        print(f"\nTeam: {team_name}")
        print("Captains:")
        for captain_name, captain in team_info["captains"].items():
            print(f"  - {captain_name}: {captain.reference}")
        print("Ships:")
        for ship_name, ship in team_info["ships"].items():
            print(f"  - {ship_name}: Shields: {ship.shields}, Armor: {ship.armor}, Attack: {ship.attack_power}, Speed: {ship.speed}, Shield Recharge Rate: {ship.shield_recharge_rate}, Critical Hit Chance: {ship.critical_hit_chance}")

def how_to_play():
    print("\nHow to Play:")
    print("1. Choose your team, captain, wingman, and ship. Your wingman will provide a passive bonus.")
    print("2. During your turn, choose an action: attack, repair, or boost shields.")
    print("3. Different ships have different weapons, some with special effects.")
    print("4. The goal is to destroy the ship of the opposing team.")

def choose_option(options, prompt):
    while True:
        print(prompt)
        for idx, option in enumerate(options, 1):
            print(f"{idx}. {option}")
        try:
            choice = int(input("Choose an option: ")) - 1
            if 0 <= choice < len(options):
                return options[choice]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def display_selections(team1, team2, step):
    clear_screen()
    print("******************************************")
    print("*          Star Wars Tactics:            *")
    print("*           Captain's Duel!              *")
    print("******************************************\n")
    
    print("Current Selections:")
    print(f"Player 1 - Team: {team1['name'] if 'name' in team1 else 'Not selected'}")
    print(f"Player 1 - Captain: {team1['captain'] if 'captain' in team1 else 'Not selected'}")
    print(f"Player 1 - Wingman: {team1['wingman'] if 'wingman' in team1 else 'Not selected'}")
    print(f"Player 1 - Ship: {team1['ship'] if 'ship' in team1 else 'Not selected'}")
    
    print(f"\nPlayer 2 - Team: {team2['name'] if 'name' in team2 else 'Not selected'}")
    print(f"Player 2 - Captain: {team2['captain'] if 'captain' in team2 else 'Not selected'}")
    print(f"Player 2 - Wingman: {team2['wingman'] if 'wingman' in team2 else 'Not selected'}")
    print(f"Player 2 - Ship: {team2['ship'] if 'ship' in team2 else 'Not selected'}\n")
    
    print(f"Step: {step}\n")

def pre_game_setup():
    team1 = {}
    team2 = {}

    print("******************************************")
    print("*          Star Wars Tactics:            *")
    print("*           Captain's Duel!              *")
    print("******************************************\n")

    while True:
        options = ["How to Play", "Reference", "Start"]
        choice = choose_option(options, "Choose an option:")
        
        if choice == "How to Play":
            how_to_play()
        elif choice == "Reference":
            display_references()
        elif choice == "Start":
            break

    # Player 1 selections
    step = "Player 1 Team Selection"
    display_selections(team1, team2, step)
    team1_name = choose_team()
    team1['name'] = team1_name
    team1_captains = teams[team1_name]["captains"]
    team1_ships = teams[team1_name]["ships"]

    step = "Player 1 Captain Selection"
    display_selections(team1, team2, step)
    captain1_name = choose_option(list(team1_captains.keys()), "Available Captains:")
    team1['captain'] = captain1_name

    step = "Player 1 Wingman Selection"
    display_selections(team1, team2, step)
    wingman1_name = choose_option(list(team1_captains.keys()), "Available Wingmen:")
    team1['wingman'] = wingman1_name

    step = "Player 1 Ship Selection"
    display_selections(team1, team2, step)
    ship1_name = choose_option(list(team1_ships.keys()), "Available Ships:")
    team1['ship'] = ship1_name

    # Player 2 selections
    step = "Player 2 Team Selection"
    display_selections(team1, team2, step)
    team2_name = choose_team()
    team2['name'] = team2_name
    team2_captains = teams[team2_name]["captains"]
    team2_ships = teams[team2_name]["ships"]

    step = "Player 2 Captain Selection"
    display_selections(team1, team2, step)
    captain2_name = choose_option(list(team2_captains.keys()), "Available Captains:")
    team2['captain'] = captain2_name

    step = "Player 2 Wingman Selection"
    display_selections(team1, team2, step)
    wingman2_name = choose_option(list(team2_captains.keys()), "Available Wingmen:")
    team2['wingman'] = wingman2_name

    step = "Player 2 Ship Selection"
    display_selections(team1, team2, step)
    ship2_name = choose_option(list(team2_ships.keys()), "Available Ships:")
    team2['ship'] = ship2_name

    # Assign captain and wingman to ships
    team1_ship = teams[team1_name]["ships"][team1['ship']]
    team1_ship.captain = teams[team1_name]["captains"][team1['captain']]
    team1_ship.wingman = teams[team1_name]["captains"][team1['wingman']]

    team2_ship = teams[team2_name]["ships"][team2['ship']]
    team2_ship.captain = teams[team2_name]["captains"][team2['captain']]
    team2_ship.wingman = teams[team2_name]["captains"][team2['wingman']]

    # Add ships to teams
    team1_final = Team(team1_name)
    team2_final = Team(team2_name)
    team1_final.add_ship(team1_ship)
    team2_final.add_ship(team2_ship)

    return team1_final, team2_final




if __name__ == "__main__":
    settings = {
        'music': False
    }
    # Define weapons with specific cooldown periods
    blasters = Weapon("Blasters", 10, cooldown=0)
    ion_cannon = Weapon("Ion Cannon", 5, effect="ion_cannon", cooldown=3)
    torpedos = Weapon("Proton Torpedos", 15, cooldown=2)
    tractor_beam = Weapon("Tractor Beam", 0, effect="tractor_beam", cooldown=3)
    concussion_missile = Weapon("Concussion Missile", 20, effect="concussion_missile", cooldown=4)
    turbolasers = Weapon("Turbolasers", 25, cooldown=5)
    missile_barrage = Weapon("Missile Barrage", 3, effect="missile_barrage", cooldown=6)

    # Define teams
    teams = {
    "Rebel Alliance": {
        "captains": {
            "Luke Skywalker": Captain("Luke Skywalker", "always_hit", "Luke Skywalker used the Force! Bonus accuracy!", 'Force Guidance- chance to turn a missed attack into a hit.', trigger_condition="attacking"),
            "Han Solo": Captain("Han Solo", "evade_hit", "Han Solo used some maneuvers! Bonus evasion!", 'Few Surprises Left- chance to turn a hit into a miss.', trigger_condition="defending"),
            "Wedge Antilles": Captain("Wedge Antilles", "fill_turn_gauge", "Wedge Antilles accelerates to attack speed! Bonus turn!", 'Attack Speed! - Chance to fill his turn gauge.'),
            "Admiral Ackbar": Captain("Admiral Ackbar", "negate_ion_cannon", "Admiral Ackbar senses a trap! Ion cannon evaded!", 'It\'s a trap! -chance to evade the ion cannon.'),
            "Lando Calrissian": Captain("Lando Calrissian", "random_effect", "Lando Calrissian rolls the dice!", 'Lady Luck- will occasionally roll the dice to gain a random effect for 2 turns.'),
        },
        "ships": {
            "X-Wing": Ship("X-Wing", 35, 25, 10, [blasters, torpedos], accuracy=85, maneuverability=70, speed=9, energy=100, shield_recharge_rate=0.08, critical_hit_chance=10),
            "Y-Wing": Ship("Y-Wing", 30, 40, 15, [blasters,ion_cannon ], accuracy=70, maneuverability=60, speed=7, energy=100, shield_recharge_rate=0.05, critical_hit_chance=5),
            "Corellian Corvette": Ship("Corellian Corvette", 50, 45, 20, [blasters, ion_cannon, torpedos], accuracy=75, maneuverability=55, speed=6, energy=100, shield_recharge_rate=0.07, critical_hit_chance=8),
            "Millennium Falcon": Ship("Millennium Falcon", 40, 40, 25, [blasters, concussion_missile], accuracy=90, maneuverability=70, speed=8, energy=100, shield_recharge_rate=0.1, critical_hit_chance=12),
            "Nebulon-B Frigate": Ship("Nebulon-B Frigate", 35, 30, 10, [blasters, ion_cannon], accuracy=80, maneuverability=60, speed=7, energy=100, shield_recharge_rate=0.08, critical_hit_chance=10),
            "MC80 Star Cruiser": Ship("MC80 Star Cruiser", 45, 35, 15, [blasters, ion_cannon], accuracy=75, maneuverability=55, speed=6, energy=100, shield_recharge_rate=0.07, critical_hit_chance=8),
        }
    },
    "Galactic Empire": {
        "captains": {
            "Emperor's Hand Mara Jade": Captain("Emperor's Hand Mara Jade", "extra_attack", "Mara Jade hears the Emperor's voice! Bonus blaster shots!", 'The Last Command- chance for a bonus attack.'),
            "Darth Vader": Captain("Darth Vader", "critical_hit", "Darth Vader has you now! Bonus Critical hit!", 'Ruthless Pursuit- chance for a critical hit.'),
            "Maarek Stele": Captain("Maarek Stele", "always_evade", "Maarek Stele's piloting skills evade the attack! Bonus evasion!", 'Hero of the Empire- chance to evade an attack.'),
            "Admiral Piett": Captain("Admiral Piett", "fill_turn_gauge", "Admiral Piett's orders earn a bonus turn!", 'Imperial Admiralty- chance to fill his turn gauge.'),
            "Admiral Zaarin": Captain("Admiral Zaarin", "random_effect", "Admiral Zaarin experiments with new technology!", 'R&D- experiments with new tech to gain a random effect for 2 turns.'),
        },
        "ships": {
            "TIE Fighter": Ship("TIE Fighter", 0, 25, 10, [blasters], accuracy=85, maneuverability=80, speed=15, energy=100, shield_recharge_rate=0.0, critical_hit_chance=10),
            "TIE Bomber": Ship("TIE Bomber", 15, 35, 15, [blasters, concussion_missile], accuracy=70, maneuverability=50, speed=7, energy=100, shield_recharge_rate=0.05, critical_hit_chance=5),
            "Imperial-I Star Destroyer": Ship("Imperial-I Star Destroyer", 45, 50, 20, [blasters, ion_cannon, torpedos, tractor_beam], accuracy=75, maneuverability=55, speed=6, energy=100, shield_recharge_rate=0.07, critical_hit_chance=8),
            "TIE Interceptor": Ship("TIE Interceptor", 35, 40, 25, [blasters], accuracy=85, maneuverability=70, speed=8, energy=100, shield_recharge_rate=0.1, critical_hit_chance=12),
        }
    },
    "Bounty Hunters": {
        "captains": {
            "Boba Fett": Captain("Boba Fett", "fill_turn_gauge", "Boba Fett's Slave I is ready to attack! Bonus turn!", ''),
            "IG-88": Captain("IG-88", "negate_ion_cannon", "IG-88's droid brain negates the ion cannon!", ''),
            "Bossk": Captain("Bossk", "critical_hit", "Bossk's Trandoshan instincts lead to a critical hit!", ''),
            "Dengar": Captain("Dengar", "always_hit", "Dengar's precision ensures a hit!", ''),
            'Greedo': Captain("Greedo", "random_effect", "Greedo rolls the dice!", '')
        },
        "ships": {
            "Slave I": Ship("Slave I", 35, 40, 15, [blasters, ion_cannon], accuracy=75, maneuverability=55, speed=6, energy=100, shield_recharge_rate=0.08, critical_hit_chance=5),
            "IG-2000": Ship("IG-2000", 40, 30, 10, [blasters, torpedos], accuracy=80, maneuverability=60, speed=7, energy=100, shield_recharge_rate=0.1, critical_hit_chance=10),
            "Hound's Tooth": Ship("Hound's Tooth", 45, 45, 20, [blasters, ion_cannon, torpedos], accuracy=75, maneuverability=55, speed=6, energy=100, shield_recharge_rate=0.07, critical_hit_chance=8),
            "Manka Hunter": Ship("Manka Hunter", 50, 50, 25, [blasters, concussion_missile], accuracy=85, maneuverability=70, speed=8, energy=100, shield_recharge_rate=0.1, critical_hit_chance=12),
            "Punishing One": Ship("Punishing One", 40, 35, 15, [blasters, ion_cannon], accuracy=80, maneuverability=60, speed=7, energy=100, shield_recharge_rate=0.08, critical_hit_chance=10)
        }
    },
    "Smugglers": {
        "captains": {
            "Mara Jade": Captain("Mara Jade", "extra_attack", "Mara Jade sneak attacks! Bonus blaster shots!", 'Surprise and Improvise- chance for a bonus attack.'),
            "Dash Rendar": Captain("Dash Rendar", "always_hit", "Dash Rendar's luck is with you! Bonus accuracy!", ''),
            "Talon Karrde": Captain("Talon Karrde", "evade_hit", "Talon Karrde's roar distracts the enemy! Bonus evasion!", ''),
            "Booster Terrick": Captain("Booster Terrick", "fill_turn_gauge", "Jabba the Hutt's bounty hunters are ready to attack! Bonus turn!", ''),
        },
        "ships": {
            "Z-95 Headhunter": Ship("Z-95 Headhunter", 15, 15, 10, [blasters, ion_cannon], accuracy=80, maneuverability=70, speed=9, energy=100, shield_recharge_rate=0.08, critical_hit_chance=10),
            "Jade Fire": Ship("Jade Fire", 30, 25, 10, [blasters, ion_cannon], accuracy=80, maneuverability=60, speed=7, energy=100, shield_recharge_rate=0.08, critical_hit_chance=10),
            "Wild Karrde": Ship("Wild Karrde", 40, 35, 25, [blasters, turbolasers], accuracy=85, maneuverability=60, speed=6, energy=100, shield_recharge_rate=0.1, critical_hit_chance=12),
            "Outrider": Ship("Outrider", 35, 40, 15, [blasters, ion_cannon], accuracy=70, maneuverability=50, speed=5, energy=100, shield_recharge_rate=0.07, critical_hit_chance=5),
            "Errant Venture": Ship("Errant Venture", 40, 30, 10, [torpedos, blasters, tractor_beam], accuracy=80, maneuverability=60, speed=6, energy=100, shield_recharge_rate=0.08, critical_hit_chance=10),
        }
    },
    "New Republic": {
        "captains": {
            "Jedi Master Luke Skywalker": Captain("Jedi Master Luke Skywalker", "always_hit", "Jedi Master Luke Skywalker uses the Force! Bonus accuracy!", ''),
            "Leia Organa Solo": Captain("Leia Organa Solo", "evade_hit", "Leia Organa Solo uses her diplomatic skills! Bonus evasion!", 'New Republic Diplomacy - chance to evade an attack.'),
            "Jedi Knight Mara Jade": Captain("Jedi Knight Mara Jade", "fill_turn_gauge", "Jedi Knight Mara Jade accelerates to attack speed! Bonus turn!", ''),
            "Kyle Katarn": Captain("Kyle Katarn", "fill_turn_gauge", "Kyle Katarn takes advantage of Jedi training! Bonus turn!", 'Jedi Inititave - chance to fill his turn gauge.'),
            "Garm bel Iblis": Captain("Garm bel Iblis", "negate_ion_cannon", "Garm bel Iblis's cunning avoids the ion cannon!", 'Original Rebel - chance to negate the ion cannon.'),
            "Corran Horn": Captain("Corran Horn", "always_hit", "Corran Horn's concentration ensures a hit!", 'Rogue Squadron Training - chance to always hit.'),
            "Commander Wedge Antilles": Captain("Commander Wedge Antilles", "extra_attack", "Commander Wedge Antilles's calls on Rogue Squadron!", 'Rogue Squadron - chance for a bonus attack.'),
        },
        "ships": {
            "E-Wing": Ship("E-Wing", 35, 25, 10, [blasters, ion_cannon], accuracy=80, maneuverability=60, speed=7, energy=100, shield_recharge_rate=0.08, critical_hit_chance=10),
            "V-Wing": Ship("V-Wing", 30, 35, 15, [torpedos, blasters], accuracy=70, maneuverability=50, speed=5, energy=100, shield_recharge_rate=0.05, critical_hit_chance=5),
            "Dreadnaught Heavy Cruiser": Ship("Dreadnaught Heavy Cruiser", 40, 40, 25, [blasters, concussion_missile], accuracy=85, maneuverability=65, speed=6, energy=100, shield_recharge_rate=0.07, critical_hit_chance=12),
            "Nebula Star Destroyer": Ship("Nebula Star Destroyer", 50, 45, 20, [blasters, missile_barrage, torpedos], accuracy=75, maneuverability=55, speed=6, energy=100, shield_recharge_rate=0.07, critical_hit_chance=8),
        }
    },
    "Imperial Remnant": {
        "captains": {
            "Captain Gilad Pellaeon": Captain("Gilad Pellaeon", "fill_turn_gauge", "Gilad Pellaeon's tactical genius earns a bonus turn!", 'Nobl'),
            "Grand Admiral Thrawn": Captain("Grand Admiral Thrawn", "fill_turn_gauge", "Grand Admiral Thrawn's a tactical genius! Bonus turn!", 'Five Steps Ahead - chance to fill his turn gauge.'),
            "Baron Soontir Fel": Captain("Baron Soontir Fel", "always_hit", "Baron Soontir Fel's piloting skills cements the attack!", 'Feared Ace - chance to always hit.'),
        },
        "ships": {
            "Imperial-II Star Destroyer": Ship("Imperial-II Imperial Star Destroyer", 45, 50, 20, [blasters, ion_cannon, torpedos, tractor_beam], accuracy=75, maneuverability=55, speed=6, energy=100, shield_recharge_rate=0.07, critical_hit_chance=8),
            "TIE Defender": Ship("TIE Defender", 40, 40, 25, [blasters, ion_cannon], accuracy=85, maneuverability=70, speed=8, energy=100, shield_recharge_rate=0.1, critical_hit_chance=12), 
            "Immobilizer Cruiser": Ship("Immobilizer Cruiser", 35, 25, 10, [blasters, ion_cannon, tractor_beam], accuracy=80, maneuverability=60, speed=7, energy=100, shield_recharge_rate=0.08, critical_hit_chance=10), 
            'Eclipse': Ship("Eclipse", 50, 45, 20, [blasters, concussion_missile, turbolasers], accuracy=85, maneuverability=60, speed=6, energy=100, shield_recharge_rate=0.1, critical_hit_chance=12),
            'Chimaera': Ship("Chimaera", 40, 30, 15, [blasters, ion_cannon], accuracy=70, maneuverability=50, speed=5, energy=100, shield_recharge_rate=0.07, critical_hit_chance=5)
        },
    },
    "Warlords": {
        "captains": {
            "Zsinj": Captain("Zsinj", "fill_turn_gauge", "Warlord Zsinj's ambition earns a bonus turn!", 'Ruthless Ambition - chance to fill his turn gauge.'),
            "Ysanne Isard": Captain("Ysanne Isard", "armor_drain", "Ysanne Isard deploys the Krytos plague! Energy armor drain!", 'Krytos Plague - chance to drain opponent\'s armor for 3 turns.'),
            "Admiral Daala": Captain("Admiral Daala", "berserk", "Admiral Daala unleashes fury!", 'Mass Execution - chance to enter berserk mode.'),
        },
        "ships": {
            "TIE Interceptor": Ship("TIE Interceptor", 35, 25, 10, [blasters, ion_cannon], accuracy=80, maneuverability=60, speed=7, energy=100, shield_recharge_rate=0.08, critical_hit_chance=10),
            "Iron Fist": Ship("Iron Fist", 40, 35, 15, [blasters, torpedos], accuracy=75, maneuverability=55, speed=5, energy=100, shield_recharge_rate=0.07, critical_hit_chance=10),
            "Lusankya": Ship("Lusankya", 50, 50, 30, [blasters, concussion_missile, turbolasers], accuracy=60, maneuverability=50, speed=4, energy=100, shield_recharge_rate=0.05, critical_hit_chance=5), 
        }
    }
}


    team1, team2 = pre_game_setup()
    game_loop(team1, team2)
