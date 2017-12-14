# Provides information needed for main to run TravianBot

world = "http://ts1.travian.com/" # URL to the server
field = world + "dorf1.php"
village = world + "dorf2.php"

username = "username" # Enter username
password = "password" # Enter password

# Following variables decide if each action should be done
heroAdventure = False # Put true only if hero is in home village and is ready for adventure
checkForAttack = False
build = False
raidFarms = False

# Name of villages must be accurate and is case-sensitive
numberOfVillages = 4
villageNames = ["abc 1", "abc 2", "abc 3", "abc 4"]
heroCurrentVillage = 1 # Zero-based index

# Names of buildings must be spelled correctly
# Buildings must already exist, i.e. cannot build a new building
# Fields to be upgraded is given by their URL index number
upgradeQueues = [None]*numberOfVillages
upgradeQueues[0] = ["grain mill"] * 2 + ["marketplace"]
upgradeQueues[1] = ["marketplace", "stable"]
upgradeQueues[2] = ["3"]
upgradeQueues[3] = []

# Village at given coordinates will be raided by all troops in village
dodgeAttackCoor = [None]*numberOfVillages
dodgeAttackCoor[0] = ["-27","-159"]
dodgeAttackCoor[1] = ["-27","-159"]
dodgeAttackCoor[2] = ["-27","-159"]
dodgeAttackCoor[3] = ["-27","-159"]

# String must be in the format "village name - time"
# String must be unique
# Time specified (in minutes) * 2 will be the time when the farm list is raided again
# In game, the 'village name' section must not be included as the farm list name. The 'time' should be the name.
# (This is because the village name will always be included by the game)
farmLists = [None]*numberOfVillages
farmLists[0] = ["abc 1 - 30"]
farmLists[1] = ["abc 2 - 30", "abc 2 - 60"]
farmLists[2] = []
farmLists[3] = []
