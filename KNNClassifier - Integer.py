import heapq
import csv
import random
import itertools
from multiprocessing import Process, Queue

import sys
import pdb
import traceback

class KNNClassifier:
    'k-NN Classifier using Hamming Distance'

    def __init__(self, train_data, test_data):
        train_header_row, self.train_set = self.loadDataset(train_data)
        test_header_row, self.test_set = self.loadDataset(test_data)

        # Check if training and test set are from the same dataset
        if set(train_header_row) != set(test_header_row):
            raise ValueError("Header row for test set does not match header for train. Please make sure test and train are from the same dataset.")
        else:
            self.header_row = train_header_row

        self.total_players = len(self.test_set)
        self.players_per_game_test = self.countPlayers()
        self.classify_output = []

        # Print some statistics about the test and training data
        print "Total examples: " + str(len(self.train_set) + len(self.test_set))
        print "Number training players: " + str(len(self.train_set))
        print "Number testing players: " + str(len(self.test_set))
        print "Number of games: " + str(len(self.header_row))
        print 

    def nthBit(self, i, n):
        """Get the nth bit of the integer i"""
        return "0" if not i & (1 << n) else "1"

    def countPlayers(self):
        """Count number of players for each game"""
        header_length = len(self.header_row)
        player_game_count = [0 for x in range(header_length)]
        for i in range(len(self.test_set)):
            for j in range(header_length):
                player_game_count[j] += int(self.nthBit(self.test_set[i], header_length - j - 1))
        return player_game_count

    def loadDataset(self, filename):
        """Loads data from a csv file"""
        # Open the file
        with open(filename, 'rb') as f:
            # Read the header line so it is not used in data
            header = f.next()
            header = ''.join(header.splitlines()).split(",")
            data = [int(row.translate(None, ","), 2) for row in f]

            return header, data

    def classifyGame(self, k, game_index, game_name, out_queue):
        """Runs kNN classificaion on each game in the inputted gamelist"""
        game_id = self.header_row[game_index]
        algorithm_name = "kNN (k = " + str(k) + ")"
        g_index = len(self.header_row) - self.header_row.index(game_id) - 1
        true_labels = []
        classification = []

        print "Testing game " + str(game_name) + " with " + str(k) + " nearest neighbors"

        for i in range(len(self.test_set)):
            t = self.test_set[i]
            true_labels.append(self.nthBit(t, g_index))
            classification.append(self.getClassification(self.findClosest(t, k, g_index), g_index))

        print "Testing game " + str(game_name) + " with " + str(k) + " nearest neighbors completed. Accuracy results below."
        confusion_matrix = self.confusion(true_labels, classification)
        result = [
            game_name,
            game_id,
            algorithm_name,
            self.players_per_game_test[game_index],
            self.players_per_game_test[game_index]/float(self.total_players)
        ]
        result += self.generateStatistics(confusion_matrix)
        out_queue.put(result) # for multithreading
    
    def generateStatistics(self, confusion_matrix):
        """Print out accuracy statistics"""
        EPSILON = sys.float_info.epsilon # add to avoid division by 0
        tp_0 = confusion_matrix["0"]["0"] + EPSILON
        tn_0 = confusion_matrix["1"]["1"] + EPSILON
        fp_0 = confusion_matrix["0"]["1"] + EPSILON
        fn_0 = confusion_matrix["1"]["0"] + EPSILON

        tp_1 = confusion_matrix["1"]["1"] + EPSILON
        tn_1 = confusion_matrix["0"]["0"] + EPSILON
        fp_1 = confusion_matrix["1"]["0"] + EPSILON
        fn_1 = confusion_matrix["0"]["1"] + EPSILON

        accuracy = self.accuracy(tp_0, tn_0, fn_0, fp_0)
        precision_0 = self.precision(tp_0, fp_0)
        recall_0 = self.recall(tp_0, fn_0)
        f_measure_0 = self.f_measure(precision_0, recall_0)
        precision_1 = self.precision(tp_1, fp_1)
        recall_1 = self.recall(tp_1, fn_1)
        f_measure_1 = self.f_measure(precision_1, recall_1)

        output = [
            accuracy,
            precision_0,
            recall_0,
            f_measure_0,
            precision_1,
            recall_1,
            f_measure_1
        ]

        print "Accuracy: " + str(100.0 * accuracy) + "%"
        print "Precision (0): " + str(precision_0)
        print "Recall (0): " + str(recall_0)
        print "F1 (0): " + str(f_measure_0)
        print "Precision (1): " + str(precision_1)
        print "Recall (1): " + str(recall_1)
        print "F1 (1): " + str(f_measure_1)

        print "a    b"
        print str(confusion_matrix["0"]["0"]) + " | " + str(confusion_matrix["0"]["1"]) + "   a = 0"
        print "-----"
        print str(confusion_matrix["1"]["0"]) + " | " + str(confusion_matrix["1"]["1"])  +  "   b = 1\n"

        return output 

    def confusion(self, trueLabels, classifications):
        """Generates confusion matrix"""
        confusion_matrix = {"0": {"0": 0, "1": 0}, "1": {"0": 0, "1": 0}}

        true_length = len(trueLabels)
        class_length = len(classifications)
        if true_length == class_length:
            for i in range(true_length):
                confusion_matrix[trueLabels[i]][classifications[i]] += 1
        return confusion_matrix

    def precision(self, tp, fp):
      """Calculates the precision using true positive and false positive metrics"""
      return float(tp)/float(tp + fp)

    def recall(self, tp, fn):
      """Calculates the recall using true positive and false negative metrics"""
      return float(tp)/float(tp + fn)

    def f_measure(self, precision, recall):
      """Calculates the f-measure using precision and recall metrics"""
      return float(2.0 * precision * recall)/float(precision + recall)

    def accuracy(self, tp, tn, fn, fp):
      """Calculates the accuracy using true positive, true negative, false positive, and false negative metrics"""
      return (float(tp + tn)/float(tp + tn + fn + fp))

    def hammingDistance(self, instance1, instance2, ignore_index):
        """Calculates hamming distance between two instances ignoring the classification column"""

        # xor the two numbers, convert it a string representation of the binary number, then count the number of 1s
        # If the classification index of the two instances will cause a difference in distance, subtract 1
        return bin(instance1 ^ instance2).count("1") - (self.nthBit(instance1, ignore_index) != self.nthBit(instance2, ignore_index))

    def findClosest(self, target, k, ignore_index):
        """Finds the closest k instances in training data to a target in testing data"""

        return heapq.nsmallest(k, self.train_set, key=lambda n: self.hammingDistance(target, n, ignore_index))

    def getClassification(self, closest, classification_index):
        """Returns classification of a testing instance based on majority vote by k-neighbors"""
        class_one = len([c for c in closest if self.nthBit(c, classification_index) == "1"])
        class_zero = len(closest) - class_one

        return "1" if class_one > class_zero else "0"

try:
    # Setup output
    random.seed("ML349")
    csv_header = [
                    "Game Name",
                    "SteamID",
                    "Algorithm",
                    "Number Players",
                    "% Players of Training Set",
                    "Accuracy",
                    "Precision (0)",
                    "Recall (0)",
                    "F1 (0)",
                    "Precision (1)",
                    "Recall (1)",
                    "F1 (1)"
    ]
    game_results = []
    with open("./data/games_by_username_all.csv", "r") as f:
        game_list = f.next().rstrip().split(",")

    games_to_pick = ["CounterStrike", "Team_Fortress_Classic", "Day_of_Defeat", "Deathmatch_Classic", "HalfLife_Opposing_Force", "Ricochet", "HalfLife", "CounterStrike_Condition_Zero", "CounterStrike_Condition_Zero_Deleted_Scenes", \
    "HalfLife_Blue_Shift", "HalfLife_2", "CounterStrike_Source", "HalfLife_Source", "Day_of_Defeat_Source", "HalfLife_2_Deathmatch", "HalfLife_2_Lost_Coast", "HalfLife_Deathmatch_Source", "HalfLife_2_Episode_One", "Portal", \
    "HalfLife_2_Episode_Two", "Left_4_Dead", "Left_4_Dead_2", "Portal_2", "CounterStrike_Global_Offensive", "Red_Orchestra_Ostfront_4145", "Mare_Nostrum", "Killing_Floor", "Darkest_Hour_Europe_4445", "SiN_Episodes_Emergence", \
    "SiN", "Darwinia", "Uplink", "DEFCON", "Multiwinia", "Earth_2160", "Two_Worlds_Epic_Edition", "Dark_Messiah_of_Might__Magic_Single_Player", "Dark_Messiah_of_Might__Magic_MultiPlayer", "Quake_III_Arena", "Quake_4", \
    "Wolfenstein_3D", "The_Ultimate_DOOM", "Final_DOOM", "DOOM_II_Hell_on_Earth", "Quake", "Quake_II", "Quake_III_Team_Arena", "Heretic_Shadow_of_the_Serpent_Riders", "The_Ship", "The_Ship_Single_Player", "Bloody_Good_Time",\
    "X3_Reunion", "X_Rebirth", "FlatOut_2", "BloodRayne", "Garrys_Mod", "Rome_Total_War__Alexander", "Star_Wars__Jedi_Knight_II_Jedi_Outcast", "Jade_Empire_Special_Edition", "XBlades", "XCOM_UFO_Defense", "Men_of_War", "Cryostasis",\
    "Tomb_Raider_Underworld", "Geometry_Wars_Retro_Evolved", "Sid_Meiers_Civilization_IV_Beyond_the_Sword", "BioShock_Infinite", "Borderlands", "Commander_Keen_Complete_Pack", "Warhammer_40000_Dawn_of_War__Winter_Assault",\
    "Star_Trek_Online", "Prototype", "Call_of_Duty_Modern_Warfare_2__Multiplayer", "Universe_at_War_Earth_Assault", "Empire_Total_War", "Aliens_vs_Predator", "Speedball_2_Tournament", "Shadowgrounds_Survivor",\
    "Penguins_Arena_Sednas_World", "Obulis", "Nikopol_Secrets_of_the_Immortals", "Grand_Theft_Auto_San_Andreas", "Midnight_Club_II", "Grand_Theft_Auto", "Grand_Theft_Auto_Vice_City", "Max_Payne_2_RU",\
    "Tom_Clancys_Ghost_Recon_Advanced_Warfighter_2", "Tom_Clancys_Splinter_Cell_Double_Agent", "Assassins_Creed", "Beyond_Good__Evil", "Harvest_Massive_Encounter", "AaAaAA__A_Reckless_Disregard_for_Gravity",\
    "1_2_3_KICK_IT_Drop_That_Beat_Like_an_Ugly_Baby", "Oddworld_Abes_Oddysee", "Oddworld_Abes_Exoddus", "Oddworld_Strangers_Wrath_HD", "Insecticide_Part_1", "Dragon_Age_Origins", "Pirates_Vikings__Knights_II", "Shattered_Horizon",\
    "Defense_Grid_The_Awakening", "And_Yet_It_Moves", "Tom_Clancys_Rainbow_Six_3_Gold_Edition", "Prince_of_Persia", "Warhammer_40000_Dawn_of_War_II__Chaos_Rising", "The_Witcher_Enhanced_Edition",\
    "The_Witcher_2_Assassins_of_Kings_Enhanced_Edition", "Lego_Harry_Potter", "Bionic_Commando", "Resident_Evil_5__Biohazard_5", "Penumbra_Black_Plague", "Penumbra_Overture", "Zeno_Clash", "Rock_of_Ages", "Rogue_Warrior",\
    "Tropico_3__Steam_Special_Edition", "Aquaria", "Burnout_Paradise_The_Ultimate_Box", "Crayon_Physics_Deluxe", "Blacklight_Tango_Down", "Dark_Sector", "Wallace__Gromit_Ep_1_Fright_of_the_Bumblebees",\
    "Tales_of_Monkey_Island_Chapter_1__Launch_of_the_Screaming_Narwhal", "Sam__Max_301_The_Penal_Zone", "The_Secret_of_Monkey_Island_Special_Edition", "Star_Wars_Dark_Forces", "Alien_Shooter_2_Reloaded", "Assassins_Creed_II",\
    "Arma_2", "SEGA_Genesis__Mega_Drive_Classics", "Mini_Ninjas", "Rising_StormRed_Orchestra_2_Multiplayer", "Time_Gentlemen_Please", "Ben_There_Dan_That", "Magnetis", "Section_8", "Fallout", "RUSH", "Moonbase_Alpha",\
    "Stronghold_Crusader_HD", "Serious_Sam_Classic_The_Second_Encounter", "Cargo__The_quest_for_gravity", "DogFighter", "Blur", "Call_of_Duty_Modern_Warfare_3", "Call_of_Duty_Modern_Warfare_3__Multiplayer", "GRID_2", "Fortix",\
    "Bob_Came_in_Pieces", "Star_Wolves_3_Civil_War", "Scratches_Directors_Cut", "Need_for_Speed_Hot_Pursuit", "The_SimsTM_3", "Shift_2_Unleashed", "LIMBO", "Tom_Clancys_HAWX_2", "Saira", "Beat_Hazard", "Spec_Ops_The_Line",\
    "Darksiders", "Darksiders_II", "Tactical_Intervention", "Puzzle_Dimension", "DUNGEONS__Steam_Special_Edition", "Tropico_4", "Fractal_Make_Blooms_Not_War", "Critter_Crunch", "Sniper_Elite_V2", "Men_of_War_Assault_Squad",\
    "Arma_Gold_Edition", "Dino_DDay", "Star_Ruler", "Crazy_Taxi", "Space_Channel_5_Part_2", "Closure", "Breach", "The_Elder_Scrolls_V_Skyrim", "Sengoku", "Fate_of_the_World", "Blackwell_Unbound", "Blackwell_Deception", "Dead_Island",\
    "Sanctum", "Hitogata_Happa", "GundeadliGne", "Xotic", "Jamestown", "Back_to_the_Future_Ep_4__Double_Visions", "Steel_Storm_Burning_Retribution", "Ravaged_Zombie_Apocalypse", "Nexuiz", "Section_8_Prejudice",\
    "Magic_The_Gathering__Duels_of_the_Planeswalkers_2013", "Toy_Soldiers", "Hard_Reset", "A_New_Beginning__Final_Cut", "Critical_Mass", "Arma_3", "War_Inc_Battlezone", "MicroVolts_Surge", "Neverwinter", "Astro_Tripper",\
    "Blocks_That_Matter", "Guardians_of_Middleearth", "Stacking", "Sideway", "Toki_Tori_2", "Flatout_3", "Cities_XL_2012", "Jurassic_Park_The_Game", "Magicka_Wizard_Wars", "Leviathan_Warships", "Titan_Attacks",\
    "Warlock__Master_of_the_Arcane", "QUBE", "Fable__The_Lost_Chapters", "The_Bridge", "BITTRIP_VOID", "Insanely_Twisted_Shadow_Planet", "Dota_2_Test", "Gunpoint", "War_of_the_Roses_Balance_Beta", "Bang_Bang_Racing",\
    "Legend_of_Grimrock", "eXceed__Gun_Bullet_Children", "eXceed_2nd__Vampire_REX", "Wizorb", "Rayman_Origins", "The_Walking_Dead", "Botanicula", "Loadout", "Drunken_Robot_Pornography", "Call_of_Duty_Ghosts__Multiplayer",\
    "Hero_Academy", "Max_Payne_RU", "Angry_Birds_Space", "Sanctum_2", "Rune_Classic", "Battle_vs_Chess", "The_Political_Machine_2012", "Deadlight", "Starbound", "Resonance", "C9", "The_Amazing_SpiderMan", "FTL_Faster_Than_Light",\
    "Transformers_Fall_of_Cybertron", "LEGO_Batman_2", "Dollar_Dash", "Tower_Wars", "Alien_Isolation", "Space_Rangers_HD_A_War_Apart", "Total_War_ROME_II__Emperor_Edition", "The_Book_of_Unwritten_Tales", "Home", "Worms_Armageddon",\
    "Frontline_Tactics", "Planets_Under_Attack", "Pid_", "Proteus", "Divinity_II_Developers_Cut", "King_Arthurs_Gold", "Edna__Harvey_Harveys_New_Eyes", "The_Walking_Dead_Survival_Instinct", "The_Journey_Down_Chapter_One",\
    "Kerbal_Space_Program", "Farming_Simulator_2013", "Cargo_Commander", "StarDrive", "DayZ", "Age_of_Empires_II_HD_Edition", "Puddle", "Resident_Evil_Revelations__Biohazard_Revelations_UE", "Wargame_AirLand_Battle", "Ys_I",\
    "Arma_Tactics", "Iron_Sky_Invasion", "Brothers__A_Tale_of_Two_Sons", "Weird_Worlds_Return_to_Infinite_Space", "Marvel_Heroes_2015", "Infestation_Survivor_Stories", "Kinetic_Void", "Kingdom_Wars", "SangFroid__Tales_of_Werewolves",\
    "10000000", "Retrovirus", "Company_of_Heroes_New_Steam_Version", "Teenage_Mutant_Ninja_Turtles_Out_of_the_Shadows", "Dream", "Incredipede", "Divinity_Dragon_Commander_Beta", "Divinity_Original_Sin", "Starseed_Pilgrim",\
    "Cities_XL_Platinum", "Leisure_Suit_Larry_in_the_Land_of_the_Lounge_Lizards_Reloaded", "SolForge", "Far_Cry_3_Blood_Dragon", "MURDERED_SOUL_SUSPECT", "Lunnye_Devitsy", "Surgeon_Simulator", "Organ_Trail_Directors_Cut",\
    "Unepic", "Receiver", "Teleglitch_Die_More_Edition", "Project_CARS", "Shadowrun_Returns", "Prime_World", "Tom_Clancys_Splinter_Cell_Blacklist", "Horizon", "Agricultural_Simulator_2013_Steam_Edition",\
    "Red_Orchestra_2_Heroes_of_Stalingrad__Single_Player", "Edge_of_Space", "BattleBlock_Theater", "Fist_Puncher", "Skyward_Collapse", "Papers_Please", "Bleed", "Rogue_Legacy", "Haunted_Memories", "Nuclear_Throne",\
    "GunZ_2_The_Second_Duel", "Cognition_An_Erica_Reed_Thriller", "Daikatana", "Gas_Guzzlers_Extreme", "Assetto_Corsa", "Face_Noir", "Foul_Play", "VelocityUltra", "ENSLAVED_Odyssey_to_the_West_Premium_Edition", "Paranormal",\
    "Viscera_Cleanup_Detail", "Giana_Sisters_Twisted_Dreams__Rise_of_the_Owlverlord", "InFlux", "Cook_Serve_Delicious", "Crypt_of_the_NecroDancer", "Hitman_Contracts", "Nether", "Knytt_Underground", "Freedom_Planet", "Marlow_Briggs",\
    "Scribblenauts_Unmasked", "FORCED", "Knockknock", "Escape_Goat", "Battle_Nations", "Sins_of_a_Dark_Age", "Slender_The_Arrival", "Depths_of_Fear__Knossos", "Nihilumbra", "Vox", "The_Cat_Lady", "Axis_Game_Factorys_AGFPRO_30",\
    "theHunter", "Gorky_17", "Enclave", "Abyss_Odyssey", "Edna__Harvey_The_Breakout", "Not_The_Robots", "Max_Gentlemen", "Bloody_Trapland", "Loren_The_Amazon_Princess", "99_Spirits", "Deus_Ex_The_Fall", "Dragon_Nest_Europe",\
    "Hero_of_the_Kingdom", "Nightmares_from_the_Deep_The_Cursed_Heart", "The_Last_Tinker_City_of_Colors", "Assassins_Creed_Liberation", "Blood_of_the_Werewolf", "Lethal_League", "Cloudbuilt", "Our_Darker_Purpose",\
    "BlazBlue_Calamity_Trigger", "Saturday_Morning_RPG", "3089__Futuristic_Action_RPG", "Driftmoon", "The_Stomping_Land", "Villagers_and_Heroes", "FootLOL_Epic_Fail_League", "EvilQuest", "Pixel_Piracy",\
    "Captain_Morgane_and_the_Golden_Turtle", "La_Tale", "Narcissu_1st__2nd", "Deadly_30", "Acceleration_of_Suguri_XEdition", "Alpha_Kimori_Episode_One_", "Tower_of_Guns", "Age_of_Mythology_Extended_Edition",\
    "Realms_of_Arkania_1__Blade_of_Destiny_Classic", "Ground_Pounders", "DARK_BLOOD_ONLINE", "Antisquad", "Meltdown", "Mechanic_Escape", "Doctor_Who_The_Adventure_Games", "Dethroned", "ARK", "Lambda_Wars_Beta",\
    "Reversion__The_Escape", "Super_Killer_Hornet_Resurrection", "Serena", "NARUTO_SHIPPUDEN_Ultimate_Ninja_STORM_Revolution", "FaceRig", "Z_Steel_Soldiers", "Z", "Shiny_The_Firefly", "Interplanetary", "Gigantic_Army",\
    "Grim_Legends_2_Song_of_the_Dark_Swan", "Pulstar", "RefleX", "Carmageddon_2_Carpocalypse_Now", "This_War_of_Mine", "Circuits", "100_Orange_Juice", "Strategic_War_in_Europe", "Majestic_Nights", "Dark_Arcana_The_Carnival",\
    "Pixel_Puzzles_UndeadZ", "Battleplan_American_Civil_War", "Thinking_with_Time_Machine", "QuestRun", "Harvester", "Metro_Last_Light_Redux", "The_Room", "Fable_Anniversary", "Endless_Legend", "Volt", "Project_Temporality",\
    "Flower_Shop_Summer_In_Fairbrook", "Planet_Stronghold", "Final_Slam_2", "FINAL_FANTASY_XIII2", "Racer_8", "Deponia_The_Complete_Journey", "Cinders", "Mind_Path_to_Thalamus", "Flashout_2", "Lovely_Planet",\
    "Woodle_Tree_Adventures", "Divine_Souls", "Night_Shift", "Frederic_Resurrection_of_Music", "Metal_Dead", "BlazeRush", "Heileen_1_Sail_Away", "Resident_Evil__biohazard_HD_REMASTER", "Echo_of_the_Wilds", "Shan_Gui", "Borealis",\
    "Nicole_otome_version", "I_Zombie", "Gold_Rush_Classic", "LogiGun", "Hatoful_Boyfriend", "The_Way_of_Life", "Fractured_Space", "Super_Trench_Attack", "Microsoft_Flight_Simulator_X_Steam_Edition", "Obludia", "Woah_Dave",\
    "Dizzel", "Strife_Veteran_Edition", "Double_Action_Boogaloo", "Time_Mysteries_3_The_Final_Enigma", "Five_Nights_at_Freddys", "Deadlings__Rotten_Edition", "Coffin_Dodgers", "Primal_Carnage_Extinction", "Schein", "Fat_Chicken",\
    "Clash_of_Puppets", "A_Bird_Story", "I_am_Bread", "Frozen_Synapse_Prime", "Tales_from_the_Borderlands", "Grass_Simulator", "Luna_Shattered_Hearts_Episode_1", "Ilamentia", "BrickForce_EU", "Cubicity", "CAFE_0_The_Drowned_Mermaid",\
    "Ostrich_Island", "Final_Dusk", "Bermuda", "FreeStyle2_Street_Basketball", "Hotline_Miami_2_Wrong_Number_Digital_Comic", "It_came_from_space_and_ate_our_brains", "Disillusions_Manga_Horror", "Deja_Vu_MacVenture_Series",\
    "Bloodbath_Kavkaz", "GunWorld", "Rustbucket_Rumble", "Sometimes_Success_Requires_Sacrifice", "Survarium", "Project_Explore", "Make_it_indie", "404Sight"]

    game_indices = [game_list.index(i) for i in games_to_pick]
    # Build kNN
    train_file = "./data/final_train.csv"
    test_file = "./data/final_test.csv"
    knn = KNNClassifier(train_file, test_file)

    # Classify test data for each game and get accuracy statistics
    q = Queue() # create queue to hold output as it finishes
    jobs = [] # list of jobs run
    
    for i in game_indices:
        # start a process for each iteration and store its output in the queue
        p = Process(target = knn.classifyGame, args = (5, i, game_list[i], q))
        jobs.append(p)
        p.start()
    
    # combine output into one list
    for i in range(len(jobs)):
        game_results.append(q.get())

    # wait until each job is finished
    for p in jobs:
        p.join()

    # export
    with open("./data/knn_5_results.csv", "wb") as f:
        csv_writer = csv.writer(f, delimiter=",")
        csv_writer.writerow(csv_header)
        for r in game_results:
            csv_writer.writerow(r)

except Exception as e:
    typ, value, tb = sys.exc_info()
    traceback.print_exc()
    pdb.post_mortem(tb)

