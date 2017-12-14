from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import TravianInfo
import threading

class Village():
    def __init__(self, villageNumber, driver):
        self.villageNumber = villageNumber
        self.upgradeQueue = TravianInfo.upgradeQueues[villageNumber]
        self.driver = driver
        
    def convert_time_to_seconds(self, timeOriginal):
        time = timeOriginal.split(":")
        timeSec = int(time[0])*3600 + int(time[1])*60 + int(time[2])
        return timeSec
    
    # Check if there is enough resources for upgrading the given field or building
    def check_resources_for_upgrade(self):
        resNeeded = []
        resBig = []
        
        resNeeded.append(int(self.driver.find_element_by_class_name("r1").text))
        resNeeded.append(int(self.driver.find_element_by_class_name("r2").text))
        resNeeded.append(int(self.driver.find_element_by_class_name("r3").text))
        resNeeded.append(int(self.driver.find_element_by_class_name("r4").text))
        
        location = self.driver.find_element_by_id("stockBarResource1")
        resources = location.find_element_by_xpath(".//span[@class='value']").get_attribute('innerHTML')
        resBig.append(int(resources.replace(',','')))
        location = self.driver.find_element_by_id("stockBarResource2")
        resources = location.find_element_by_xpath(".//span[@class='value']").get_attribute('innerHTML')
        resBig.append(int(resources.replace(',','')))
        location = self.driver.find_element_by_id("stockBarResource3")
        resources = location.find_element_by_xpath(".//span[@class='value']").get_attribute('innerHTML')
        resBig.append(int(resources.replace(',','')))
        location = self.driver.find_element_by_id("stockBarResource4")
        resources = location.find_element_by_xpath(".//span[@class='value']").get_attribute('innerHTML')
        resBig.append(int(resources.replace(',','')))
        
        if (resBig[0]>=resNeeded[0] and resBig[1]>=resNeeded[1] and resBig[2]>=resNeeded[2] and resBig[3]>=resNeeded[3]):
            return True
        else:
            return False
    
    # Helper function for build()
    # Attempt to upgrade the field tile given by val
    def upgrade_tiles(self, val):
        try:
            self.driver.get(TravianInfo.field)
            tileNum = 'build.php?id=' + str(val)
            path = ".//area[@href='"+tileNum+"']"
            allTiles = self.driver.find_element_by_name("rx")
            tile = allTiles.find_element_by_xpath(path)
            tile.click()
            if self.check_resources_for_upgrade():
                temp = self.driver.find_element_by_class_name("clocks").text
                timeVal = self.convert_time_to_seconds(temp)
                button = self.driver.find_element_by_xpath("//*[@class='green build']")
                button.click()
                return True, timeVal
            return False, 300
        except NoSuchElementException:
            print ("Incorrect value given, please check that the names are spelled correctly.")
            return False, 300

    # Helper function for build()
    # Attempt to upgrade the building given by val
    def upgrade_buildings(self, val):
        try:
            self.driver.get(TravianInfo.village)
            villageMap = self.driver.find_element_by_id("village_map")
            villageBuildings = villageMap.find_elements_by_tag_name("area")
        
            for element in villageBuildings:
                buildingName = element.get_attribute("alt").split('<',1)[0].strip()
                if buildingName.lower() == val.lower():
                    element.click()
                    if self.check_resources_for_upgrade():
                        temp = self.driver.find_element_by_class_name("clocks").text
                        timeVal = self.convert_time_to_seconds(temp)
                        button = self.driver.find_element_by_xpath("//*[@class='green build']")
                        button.click()
                        return True, timeVal
                    else:
                        self.driver.get(TravianInfo.village)            
                        return False, 300
            print ("Incorrect value given, please check that the names are spelled correctly.")
            return False, 300        
        except NoSuchElementException:
            return False, 300
            
    # Build the fields or buildings according to upgradeQueue[] (in TravianInfo)
    def build(self):
        try:
            buildDuration = self.driver.find_element_by_class_name("buildDuration")
            currentlyBuilding = True
        except NoSuchElementException:
            currentlyBuilding = False
        if currentlyBuilding:    
            timerElement = buildDuration.find_element_by_xpath(".//span[@class='timer']")
            timer = timerElement.get_attribute("value")
            print (TravianInfo.villageNames[self.villageNumber], "is currently building. Time before completion:", timer)
            return int(timer)
        else:
            timeVal = 300
            for i in range(len(self.upgradeQueue)):
                val = self.upgradeQueue[i]
                if val.isdigit():
                    currentlyBuildingUpdated, timeVal = self.upgrade_tiles(val)
                    if currentlyBuildingUpdated:
                        del self.upgradeQueue[i]
                        print (TravianInfo.villageNames[self.villageNumber], "is building", val)
                        print ("Building Queue lefts:", self.upgradeQueue)
                        return timeVal
                else:
                    currentlyBuildingUpdated, timeVal = self.upgrade_buildings(val)
                    if currentlyBuildingUpdated:
                        del self.upgradeQueue[i]
                        print (TravianInfo.villageNames[self.villageNumber], "is building", val)
                        print ("Building Queue lefts:", self.upgradeQueue)
                        return timeVal
            return timeVal
        
    # Send the hero out on adventure
    def adventure(self):
        adventureButton = self.driver.find_element_by_xpath('.//button[@class="layoutButton adventureWhite green  "]')
        adventureButton.click()
        try:
            isAdventure = self.driver.find_element_by_xpath('.//div[@class="boxes boxesColor gray adventureStatusMessage"]')
            adventureTime = isAdventure.find_element_by_class_name("timer").get_attribute("value")
            print ("Hero is already on an adventure")
            return adventureTime
        except NoSuchElementException:
            try:
                adventureList = self.driver.find_element_by_id("adventureListForm")
                adventureList.find_element_by_link_text("To the adventure").click()
                self.driver.execute_script("window.scrollTo(0, 250)")
                self.driver.find_element_by_class_name("adventureSendButton").click()
                isAdventure = self.driver.find_element_by_xpath('.//div[@class="heroStatusMessage "]')
                adventureTime = isAdventure.find_element_by_class_name("timer").get_attribute("value")
                return adventureTime
            except NoSuchElementException:
                print ("No adventures at the moment")
                return 300
                
    # Check if there are any incoming attacks or raids
    # If there is an attack, start a timer thread to sleep and dodge the attack only 30 seconds before landing time
    # If not, start a timer thread to sleep and check for attacks again 5 minutes later
    def check_for_attacks(self, otherQueue, dodgeQueue):
        try:
            self.driver.find_element_by_class_name("a1")
            self.driver.find_element_by_id("n2").click()
            villageMap = self.driver.find_element_by_id("village_map")
            villageMap.find_element_by_xpath('.//area[contains(@alt,"Rally")]').click()
            self.driver.find_element_by_link_text("Overview").click()
            table = self.driver.find_element_by_class_name("data")
            try:
                tableList1 = table.find_elements_by_xpath('.//table[@class="troop_details inRaid"]')
                thread = [None]*len(tableList1)
                for i in range(len(tableList1)):
                    time = int(tableList1[i].find_element_by_class_name("timer").get_attribute("value"))
                    print (TravianInfo.villageNames[self.villageNumber], "incoming raid in:", time)
                    if time < 660:
                        thread[i] = threading.Thread(target=self.attack_sleep,args=(time, dodgeQueue))
                        thread[i].start()
            except NoSuchElementException:
                pass
            try:
                tableList2 = table.find_elements_by_xpath('.//table[@class="troop_details inAttack"]')
                thread = [None]*len(tableList2)
                for i in range(len(tableList2)):
                    time = int(tableList2[i].find_element_by_class_name("timer").get_attribute("value"))
                    print (TravianInfo.villageNames[self.villageNumber], "incoming attack in:", time)
                    if time < 660:
                        thread[i] = threading.Thread(target=self.attack_sleep,args=(time, dodgeQueue))
                        thread[i].start() 
            except NoSuchElementException:
                pass
        except NoSuchElementException:
            print ("There are no incoming attacks on", TravianInfo.villageNames[self.villageNumber])
        thread = threading.Thread(target=self.sleep,args=(600, "checkatk", otherQueue))
        thread.start()
             
    # Send all troops out to raid village in dodgeAttackCoor[] (in TravianInfo) when dodging       
    def dodge_attack(self, villageLink):
        villageLink.click()    
        self.driver.find_element_by_id("n2").click()
        villageMap = self.driver.find_element_by_id("village_map")
        villageMap.find_element_by_xpath('.//area[contains(@alt,"Rally")]').click()
        self.driver.find_element_by_link_text("Send troops").click()
        troopCount = self.driver.find_element_by_xpath('.//table[@id="troops"]')
        allTroops = troopCount.find_elements_by_tag_name("a")
        for element in allTroops:
            element.click()
        xCoor = self.driver.find_element_by_name("x")
        xCoor.clear()
        xCoor.send_keys(TravianInfo.dodgeAttackCoor[self.villageNumber][0])
        yCoor = self.driver.find_element_by_name("y")
        yCoor.clear()
        yCoor.send_keys(TravianInfo.dodgeAttackCoor[self.villageNumber][1])
        option = self.driver.find_element_by_class_name("option")
        option.find_element_by_xpath('.//input[@value="3"]').click()
        print (TravianInfo.villageNames[self.villageNumber], "- Sending all troops for attack / dodge attack")
        self.driver.find_element_by_id("btn_ok").click()
        self.driver.find_element_by_id("btn_ok").click()
        
    # Send troops out for raiding according to farmlist given by farmLists[] (in TravianInfo)
    def raid_farms(self, name):
        self.driver.find_element_by_id("n2").click()
        villageMap = self.driver.find_element_by_id("village_map")
        villageMap.find_element_by_xpath('.//area[contains(@alt,"Rally")]').click()
        self.driver.find_element_by_link_text("Farm List").click()
        allFarmLists = self.driver.find_elements_by_class_name("listTitleText")
        allMarkAlls = self.driver.find_elements_by_xpath('.//div[@class="markAll"]')
        allStartRaid = self.driver.find_elements_by_xpath('.//button[@value="start raid"]')
        for i in range(len(allFarmLists)):
            if allFarmLists[i].text == name:
                boxChecked = False
                while True:
                    try:
                        if not boxChecked:
                            allMarkAlls[i].click()
                            boxChecked = True
                            time.sleep(3)
                        allStartRaid[i].click()
                        print ("Sending raid for farm list:", name)
                        break
                    except:
                        self.driver.execute_script("window.scrollBy(0, 250)")
                break
        timeToWait = name.split("-")[-1].strip()
        return timeToWait
        
    # Depending on the given job's task name, execute the corresponding functions
    def jobs(self, task, otherQueue, villageLink, dodgeQueue):
        villageLink.click()
        if task == "build":
            buildTimer = self.build()
            self.driver.find_element_by_id("n1").click()
            threadBuild = threading.Thread(target=self.sleep,args=(buildTimer, task, otherQueue))
            threadBuild.start()
        if task == "checkatk":
            self.check_for_attacks(otherQueue, dodgeQueue)
            self.driver.find_element_by_id("n1").click()
        if task == "adventure":
            adventureTimer = int(self.adventure()) * 2
            self.driver.find_element_by_id("n1").click()
            threadAdventure = threading.Thread(target=self.sleep,args=(adventureTimer, task, otherQueue))
            threadAdventure.start()
        if "farm" in task:
            nameOfFarmList = task.split(",")[1].strip()
            farmTimer = int(self.raid_farms(nameOfFarmList)) * 60 * 2
            time.sleep(5)
            self.driver.execute_script("window.scrollTo(0, 0)")
            self.driver.find_element_by_id("n1").click()
            threadFarm = threading.Thread(target=self.sleep,args=(farmTimer, task, otherQueue))
            threadFarm.start()
        time.sleep(5)
    
    # Sleep for a given time, for threading use
    def sleep(self, timeVal, task, otherQueue):
        print ("Thread sleeping:", TravianInfo.villageNames[self.villageNumber], ", Task:", task, ", Time:", timeVal)
        time.sleep(int(timeVal))
        print ("Adding into otherQueue:", self.villageNumber, task)
        otherQueue.append(Job(self.villageNumber, task))

    # Sleep for a given time when attempting to dodge an attack, for threading use
    def attack_sleep(self, timeVal, dodgeQueue):       
        if not (timeVal-30) < 0: 
            timeVal = timeVal - 30
            print ("Thread sleeping:", TravianInfo.villageNames[self.villageNumber], ", Task: DodgeAttack", ", Time:", timeVal)
            time.sleep(timeVal)
        print ("Adding into dodgeQueue:", self.villageNumber)
        dodgeQueue.append(self.villageNumber)
        
class Job():
    def __init__(self, villageNumber, task):
        self.villageNumber = villageNumber
        self.task = task
        
def initialize_all_jobs(otherQueue):
    print ("Initializing all jobs...")
    if TravianInfo.heroAdventure:
        otherQueue.append(Job(TravianInfo.heroCurrentVillage,"adventure"))
    for i in range(TravianInfo.numberOfVillages):
        if TravianInfo.checkForAttack:
            otherQueue.append(Job(i,"checkatk"))
        if TravianInfo.build:
            otherQueue.append(Job(i,"build"))
        if TravianInfo.raidFarms:
            for j in range(len(TravianInfo.farmLists[i])):
                task = "farm, " + TravianInfo.farmLists[i][j]
                otherQueue.append(Job(i, task))

# Get the link to the village given its villageNumber
def find_village_link(driver, villageNumber):
    allVillageLinks = driver.find_elements_by_class_name("name")
    for i in range(len(allVillageLinks)):
        if allVillageLinks[i].get_attribute("innerHTML")  == TravianInfo.villageNames[villageNumber]:
            return allVillageLinks[i]

# Logging in to the account (in TravianInfo)
def login(driver):
    print ("Logging in...")
    driver.get(TravianInfo.world)
    
    username = driver.find_element_by_name("name")
    username.clear()
    username.send_keys(TravianInfo.username)
    
    password = driver.find_element_by_name("password")
    password.clear()
    password.send_keys(TravianInfo.password)
    
    lowRes = driver.find_element_by_name("lowRes")
    lowRes.click()
    
    loggingIn = driver.find_element_by_name("s1")
    loggingIn.send_keys(Keys.RETURN)
    
# Main function    
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(executable_path="chromedriver.exe", chrome_options=options)
login(driver)

dodgeQueue = []
otherQueue = []
initialize_all_jobs(otherQueue)
village = [None]*TravianInfo.numberOfVillages
for i in range(TravianInfo.numberOfVillages):
    village[i] = Village(i,driver)

# Constantly check if there are events to be handled in dodgeQueue and otherQueue
while True:
    while dodgeQueue:
        time.sleep(2)
        villageToDodge = dodgeQueue.pop(0)
        villageLink = find_village_link(driver, villageToDodge)
        village[villageToDodge].dodge_attack(villageLink)
    while otherQueue and not dodgeQueue:
        time.sleep(2)
        currJob = otherQueue.pop(0)
        villageLink = find_village_link(driver, currJob.villageNumber)
        village[currJob.villageNumber].jobs(currJob.task, otherQueue, villageLink, dodgeQueue)
        