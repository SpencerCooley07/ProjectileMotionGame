import csv, math, os, random, time

gameDifficulty = 1
targetMinimumDistance = 10.0
targetMaximumDistance = 45.0
trajectoryColour = 'cyan'

# Earth max distance - 41, Moon max distance ~ 245, Mars max distance ~ 108
planetGravities = [['earth', 9.81, 1, 'blue'], ['venus', 8.87, 2, 'yellow'], ['mars', 3.71, 4, 'red'], ['moon', 1.62, 6, 'white']]
planet = 0
gravitationalAcceleration = planetGravities[planet][1]
resolutionModifier = planetGravities[planet][2]
planetColour = planetGravities[planet][3]

experimentalEnabled = False

# https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
fgStyle = [['black',30],['red',31],['green',32],['yellow',33],['blue',34],['magenta',35],['cyan',36],['white',37],['default',39]]

# CODE TOOLS

def textStyles(text, textColor, textBright, bold):

    formatText = '\x1b['

    # Bold
    if bold == True: formatText += '1'

    # Text Foreground Colour
    textBrightMod = 0
    if textBright == True and textColor != 'default': textBrightMod = 60
    for i in range(len(fgStyle)):
        if fgStyle[i][0] == textColor and fgStyle[i][0] != 'default':
            if formatText == '\x1b[': formatText += str(fgStyle[i][1] + textBrightMod)
            else: formatText += ';' + str(fgStyle[i][1] + textBrightMod)
            break

    return f'{formatText}m{text}\x1b[0m'

def valueClamp(x, min, max):
    if x < min: return min
    elif x > max: return max
    else: return x

def isFloat(x):
    try:
        float(x)
        return True
    except: return False

# GRAPHING LOGIC

def generateCoordinates(initialVelocity, launchAngle, gravitationalAcceleration, initialHeight, xStep, yStep, targetRange):
    # Projectile motion initial values
    t = 0
    x = 0
    y = initialHeight
    graphHeight = initialHeight
    
    coordinates = []
    
    coordinates.append([round(x*2)/2,round(y*2)/2])
    while round(y*2)/2 >= 0:
        # Projectile motion vector equations
        x += 1*xStep
        t = x/(initialVelocity*math.cos(launchAngle))
        y = (-gravitationalAcceleration*math.pow(t,2))/2 + initialVelocity * t * math.sin(launchAngle) + initialHeight

        # Makes sure only appends if y value is positive or 0

        if round(y*(1/yStep))/(1/yStep) >= 0:
            coordinates.append([round(x*(1/xStep))/(1/xStep),round(y*(1/yStep))/(1/yStep)])
        
        # Keeps track of maximum graphed y value allowing for dynamic range in graph csv file
        if graphHeight < round(y*(1/yStep))/(1/yStep):
            graphHeight = round(y*(1/yStep))/(1/yStep)
    
    # Makes sure always graphs an intercept
    if coordinates[-1][1] != 0: coordinates.append([coordinates[-1][0]+xStep,0])

    # Checks if the target is further away than the projectile and sets the graphWidth to the target coordinates if needed
    if len(coordinates) > targetRange[1]:
        graphWidth = len(coordinates)
    else:
        graphWidth = targetRange[1]

    return coordinates, int(graphWidth), int(graphHeight*(1/yStep)+1)

def createGraphingSpace(fileName, coordinatesList, graphWidth, graphHeight, xStep, yStep, targetRange, hitTarget, loadMode):
    graph = []
    outputGraph = []
    graphCoordinatesList = []

    for n in range(graphHeight):
        rowOutput = []
        for m in range(graphWidth):
            rowOutput.append(0)
        graph.append(rowOutput)

    graphCoordinatesList = []
    for i in range(len(coordinatesList)):
        graphCoordinatesList.append([int(coordinatesList[i][0]*(1/xStep)),int(coordinatesList[i][1]*(1/yStep))])

    for i in range(len(graphCoordinatesList)):
        # Plot parabola in csv file
        graph[graphCoordinatesList[i][1]][graphCoordinatesList[i][0]] = 1

    for i in range(len(graph)):
        # Y axis graphic formatting
        if graph[i][0] == 0: graph[i][0] = 3

    for i in range(len(graph[0])):
        # X axis graphic formatting
        if graph[0][i] == 0: graph[0][i] = 4

        # Intercept graphic formatting
        elif graph[0][i] == 1 and i != 0 and hitTarget == False:
            graph[0][i] = 2
        
        elif graph[0][i] == 1 and i != 0 and hitTarget == True:
            graph[0][i] = 7
    
    graph[0][0] = 5

    # Displays the target range, making sure not to overwrite the projectile if it has landed
    for i in range(len(graph[0])):
        if graph[0][i] == 4 and targetRange[0] <= i <= targetRange[1]:
            graph[0][i] = 6

    # Flips the graph for easier outputting
    for i in range(len(graph)): outputGraph.append(graph[len(graph)-i-1])

    # CSV for possible save states
    if loadMode == 'csv':
        with open(fileName, 'w', newline="") as file:
            csvwriter = csv.writer(file)
            csvwriter.writerows(outputGraph)
    
    return outputGraph

def renderGraphFromArray(array, graphStyle, graphHeight, yStep):
    rowNum = 1
    
    for y in range(len(array)):
        rowOutput =  ' ' * ((len(str(yStep))+1)-len(str(graphHeight*yStep - rowNum*yStep))) + f'{graphHeight*yStep - rowNum*yStep}'
        for i in range(len(array[y])): rowOutput += graphStyle[array[y][i]]
        print(rowOutput)
        rowNum += 1

def renderGraphFromCSV(filename, graphStyle, graphHeight, yStep): # CSV possibly for save states
    
    with open(filename, newline='') as csvFile:
        reader_obj = csv.reader(csvFile)
        rowNum = 1
        
        for row in reader_obj:
            # Convert csv values back to integers
            for i in range(len(row)):
                row[i] = int(row[i])

            # Formatting output
            rowOutput =  ' ' * ((len(str(yStep))+1)-len(str(graphHeight*yStep - rowNum*yStep))) + f'{graphHeight*yStep - rowNum*yStep}'
            for i in range(len(row)): rowOutput += graphStyle[row[i]]
            print(rowOutput)
            rowNum += 1

def generateTargetRange(xStep):
    targetSize = 6 - gameDifficulty
    targetDistance = round(random.uniform(targetMinimumDistance, targetMaximumDistance-targetSize)*(1/xStep))/(1/xStep)
    targetRange = [targetDistance*(1/xStep), targetDistance*(1/xStep) + targetSize]
    return targetRange

def render(initialVelocity, launchAngle, initialHeight, xStep, yStep, loadMode, targetRange, hitTarget):
    
    # 0 - Spaces, 1 - Trajectory, 2 - Projectile Miss, 3 - Y Axis, 4 - X Axis, 5 - Corner, 6 - Target, 7 - Projectile Hit
    graphStyle = [' ', textStyles('*',trajectoryColour,True,True), textStyles('V','red',True,True), textStyles('┃', planetColour, False, True), textStyles('━', planetColour, False, True), textStyles('┗', planetColour, False, True), textStyles('━','green',True,True), textStyles('V','green',True,True)]

    os.system('clear')
    print(textStyles('PROJECTILE MOTION GAME\n----------------------','default',True,True))
    print(textStyles(f'YOUR SHOT', 'default', True, True))
    print(textStyles(f'PLANET: {planetGravities[planet][0].upper()}\n', 'default', True, True))

    coordinatesList, graphWidth, graphHeight = generateCoordinates(initialVelocity, launchAngle, gravitationalAcceleration, initialHeight, xStep, yStep, targetRange)
    outputGraph = createGraphingSpace('Assessment T2/graph.csv', coordinatesList, graphWidth, graphHeight, xStep, yStep, targetRange, hitTarget, loadMode)
    
    # CSV possibly for save states
    if loadMode == 'csv':
        renderGraphFromCSV('Assessment T2/graph.csv', graphStyle, graphHeight, yStep)
    elif loadMode == 'arr':
        renderGraphFromArray(outputGraph, graphStyle, graphHeight, yStep)
    else:
        exit()

# GAME

def getUserInputs(xStep, yStep, targetRange, hitTarget):

    # INITIAL VELOCITY INPUT

    initialVelocity = ''
    while initialVelocity == '':
        initialVelocity = input('\nMAX SPEED: 20m/s, MIN SPEED: 5m/s\n\x1b[1mInitial Velocity\x1b[0m (m/s): ')
        if isFloat(initialVelocity) == True:
            initialVelocity = valueClamp(float(initialVelocity), 5, 20)
        elif initialVelocity.lower() == 'menu':
            mainMenu()
            break
        elif initialVelocity.lower() == 'help':
            print(textStyles('This input will be the speed of your projectile when it is fired\nThe higher the velocity the further it will go', 'blue', True, True))
            initialVelocity = ''
        else:
            print(textStyles('Invalid input - ENTER A NUMBER BETWEEN 5 AND 20', 'red', True, True) + "\nIf you want to return to the homepage type 'menu'\nIf you need help type 'help'")
            initialVelocity = ''

    # LAUNCH ANGLE INPUT

    launchAngle = ''
    while launchAngle == '':
        launchAngle = input('\nMAX ANGLE: 75°, MIN ANGLE: 20°\n\x1b[1mLaunch Angle\x1b[0m (degrees): ')
        if isFloat(launchAngle) == True:
            launchAngle = math.radians(valueClamp(float(launchAngle), 20, 75))
        elif launchAngle.lower() == 'menu':
            mainMenu()
            break
        elif launchAngle.lower() == 'help':
            print(textStyles('This will be the angle of your projectile from the ground\nThe higher the angle, the higher up you will shoot\nThe lower the angle, the flatter you will shoot', 'blue', True, True))
            launchAngle = ''
        else:
            print(textStyles('Invalid input - ENTER A NUMBER BETWEEN 20 AND 75', 'red', True, True) + "\nIf you want to return to the homepage type 'menu'\nIf you need help type 'help'")
            launchAngle = ''

    # Option for better implementation down the track
    # initialHeight = float(input('\nMAX INITIAL HEIGHT: 10m\nInitial height (m): '))

    initialHeight = 0

    # ---------------------------- #
    # CHECK IF HIT TARGET

    landingXCoordinate = (math.pow(initialVelocity,2)*math.cos(launchAngle)*math.sin(launchAngle) + initialVelocity*math.cos(launchAngle)*math.sqrt(math.pow(initialVelocity,2)*math.pow(math.sin(launchAngle),2)+2*gravitationalAcceleration*initialHeight))/gravitationalAcceleration
    

    if targetRange[0] <= round(landingXCoordinate*(1/xStep))/(1/xStep)*(1/xStep) <= targetRange[1]: hitTarget = True
    
    # ---------------------------- #
    render(initialVelocity, launchAngle, initialHeight, xStep, yStep, 'arr', targetRange, hitTarget)

    print(' ' * (len(str(round(landingXCoordinate,2)))-len(str(round(landingXCoordinate)))) + ' '*int(landingXCoordinate*(1/xStep)) + str(round(landingXCoordinate*(1/xStep))/(1/xStep)))

    print(f'\nThe target lies at between {targetRange[0]*xStep} and {targetRange[1]*xStep} metres from the origin\nYour projectile landed approximately {round(landingXCoordinate*(1/xStep))/(1/xStep)} metres from the origin')

    return hitTarget

def gameLoop():
    playAgain = 'y'
    tips = ['A 45 degree launch angle gives you the maximum range', 'Use the information under the graph to help judge your next shot', 'You can type menu at any time to return to the main menu', 'Change your settings by typing menu', 'Going over the max input will just do the max in the given range']

    while playAgain == 'y':
        
        # ADJUST FOR PLANET GRAVITIES
        xStep, yStep = 0.25*resolutionModifier, 0.25*resolutionModifier
        targetRange = generateTargetRange(xStep)

        hitTarget = False
        tryCount = 0

        os.system('clear')
        print(textStyles('PROJECTILE MOTION GAME\n----------------------','default',True,True))
        print(textStyles('USER INPUTS\n', 'default', True, True))
        print(textStyles('OBJECTIVE: HIT THE ', 'default', True, True) + textStyles('GREEN ', 'green', True, True) + textStyles('TARGET', 'default', True, True))
        if tryCount == 0:
            print("Type 'menu' to return to the main menu")
            print("Type 'help' for help on what to input")
            print(textStyles("\nGuess your first shot to find out more about the target!", 'default', True, True))

        while hitTarget == False:
            if tryCount > 0:
                time.sleep(2), print(textStyles('\nUnlucky, have another go', 'red', True, True))
                time.sleep(2), print(textStyles(f'Tip: {tips[random.randint(0,len(tips)-1)]}!\n', 'blue', True, True))
                time.sleep(1)
            tryCount += 1
            hitTarget = getUserInputs(xStep, yStep, targetRange, hitTarget)

        playAgain = input(f"\n{textStyles('Good Game', 'green', True, True)}, you got it in {tryCount} tries!\nWould you like to play again? (Y/N) ").lower()
        if playAgain.lower() == 'n':
            mainMenu()
            break

def helpMenu():
    os.system('clear')
    print(textStyles('PROJECTILE MOTION GAME\n----------------------','default',True,True))
    print(textStyles('HELP', 'default', True, True))

    time.sleep(1)

    print(textStyles('\nObjective:', 'default', True, True))
    print('Your objective is to try to hit the target, it is signified by green on the shot map')
    print('Your first shot will be a guess, from this you will gain information about the target')
    print('Keep adjusting your values until you hit the target')

    time.sleep(5)

    print(textStyles('\nInputs:', 'default', True, True))
    print('When playing the game, you will be asked to input some values')
    print('You will be given a maximum and minimum value, your value has to fall in between this range')
    print('In the input line there will also be a set of brackets, this indicates the unit you are dealing with')
    print('If you need help at any point in the input stage, simply type ' + "'help'" + ' for some information about the input')

    time.sleep(5)

    returnToMenu = input("\nWhen you have finished reading enter 'menu' and you will return to the main menu\n> ")
    while returnToMenu.lower() != 'menu': returnToMenu = input("When you have finished reading enter 'menu' and you will return to the main menu\n> ")
    mainMenu()

def settingsMenu():
    global trajectoryColour, gameDifficulty, targetMinimumDistance

    os.system('clear')
    print(textStyles('PROJECTILE MOTION GAME\n----------------------','default',True,True))
    print(textStyles('SETTINGS\n', 'default', True, True))

    print(f'1. Game Difficulty          ({gameDifficulty})')
    print(f'2. Trajectory Colour        ({textStyles(trajectoryColour.capitalize(), trajectoryColour, True, True)})')

    settingsChoice = ''
    
    while settingsChoice == '':
        print("\nTo return to menu type 'menu'")
        settingsChoice = input('Enter an option (1-2): ')

        if isFloat(settingsChoice) == True:
            settingsChoice = int(settingsChoice)

            if settingsChoice == 1:
                gameDifficulty = valueClamp(int(input(f'\nEnter a new difficulty (1-5): ')), 1, 5)
                settingsMenu()
                break
            
            elif settingsChoice == 2:
                oldTrajectoryColour = trajectoryColour
                trajectoryColour = input('\nChoose your trajectory colour\nRed\nGreen\nYellow\nBlue\nMagenta\nCyan\nWhite\nChoose from the options above: ').lower()
                
                validColour = False

                for i in range(len(fgStyle)):
                    if fgStyle[i][0] == trajectoryColour and validColour == False:
                        validColour = True
                
                if validColour == False: trajectoryColour = oldTrajectoryColour
                settingsMenu()
                break
        
        elif settingsChoice == 'menu': mainMenu()
        
        else:
            settingsChoice = ''

def experimentalMenu(planetGravities):

    global experimentalEnabled, planet, gravitationalAcceleration,  resolutionModifier, targetMinimumDistance, targetMaximumDistance, planetColour
    
    os.system('clear')
    print(textStyles('PROJECTILE MOTION GAME\n----------------------','red',True,True))
    print(textStyles('EXPERIMENTAL\n', 'red', True, True))

    if experimentalEnabled == False:
        enableExperimentalFeatures = input('ARE YOU SURE YOU WANT TO ENABLE EXPERIMENTAL FEATURES (Y/N)\n').lower()
        if enableExperimentalFeatures == 'y':
            experimentalEnabled = True
            experimentalMenu(planetGravities)
        elif enableExperimentalFeatures == 'n':
            mainMenu()
        else:
            experimentalMenu(planetGravities)

    if experimentalEnabled == True:
        print(f'Planet Gravity ({planetGravities[planet][0].capitalize()})')
        # print(f'2. Initial Height (INDEV)')

        planetChoice = ""
        while planetChoice == "":
            print()
            
            for i in range(len(planetGravities)):
                print(f"{i+1}. {planetGravities[i][0].capitalize()}" + ' '*(8-len(planetGravities[i][0])) + f"({planetGravities[i][1]}m/s²)")
            print("\nTo return to menu type 'menu'")
            planetChoice = input('What planet gravity would you like? ')
            
            if isFloat(planetChoice) == True:
                planetChoice = int(planetChoice)
                if planetChoice <= len(planetGravities):
                    planet = planetChoice-1
                    gravitationalAcceleration = planetGravities[planet][1]
                    targetMinimumDistance = 10 * (9.81/gravitationalAcceleration)
                    targetMaximumDistance = 40 * (9.81/gravitationalAcceleration) + 6 - gameDifficulty
                    resolutionModifier = planetGravities[planet][2]
                    planetColour = planetGravities[planet][3]

                    experimentalMenu(planetGravities)
                    break
            
            elif planetChoice == 'menu': mainMenu()
            else:
                planetChoice = ""
        
def mainMenu():
    splashTextDictionary = ['As seen on TV!', 'Coming soon!', 'Keyboard compatible!', 'Not on steam!', 'Text!', 'Bug free?', 'Now with difficulty!', 'Now in 2D!', 'Projectiles included!', 'Scientific!', '¡umop-apisdn', 'Get experimental?', 'Try the experiments!', 'Is it an A?', '100%?']
    splashText = splashTextDictionary[random.randint(0,len(splashTextDictionary)-1)]

    os.system('clear')
    print(textStyles(' ____  ____   ___      _ _____ ____ _____ ___ _     _____   __  __  ___ _____ ___ ___  _   _    ____    _    __  __ _____\n|  _ \|  _ \ / _ \    | | ____/ ___|_   _|_ _| |   | ____| |  \/  |/ _ \_   _|_ _/ _ \| \ | |  / ___|  / \  |  \/  | ____|\n| |_) | |_) | | | |_  | |  _|| |     | |  | || |   |  _|   | |\/| | | | || |  | | | | |  \| | | |  _  / _ \ | |\/| |  _|\n|  __/|  _ <| |_| | |_| | |__| |___  | |  | || |___| |___  | |  | | |_| || |  | | |_| | |\  | | |_| |/ ___ \| |  | | |___\n|_|   |_| \_\\\\___/ \___/|_____\____| |_| |___|_____|_____| |_|  |_|\___/ |_| |___\___/|_| \_|  \____/_/   \_\_|  |_|_____|', 'cyan', True, True))
    
    # SPLASH TEXT
    print(textStyles((122-len(splashText))*' ' + splashText, 'yellow', True, False))
    
    print(textStyles(122*'-' + '\n', 'default', True, True))
    print(54*' ' + textStyles('PMG - MAIN MENU\n' + 54*' ' + '---------------\n', 'default', True, True))

    print(54*' ' + '1. Play')
    print(54*' ' + '2. Help')
    print(54*' ' + '3. Settings')
    print(54*' ' + textStyles('4. Experimental (INDEV)', 'red', True, True))
    print(54*' ' + '5. Exit\n')

    menuOption = int(input('Enter an option (1-5): '))

    if menuOption == 1: gameLoop()
    if menuOption == 2: helpMenu()
    if menuOption == 3: settingsMenu()
    if menuOption == 4: experimentalMenu(planetGravities)
    if menuOption == 5: os.system('clear'),exit()
    else: mainMenu()

mainMenu()