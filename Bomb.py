conf = {
  'AISLES': 7,
  'BOMB_POWER': 3,
  'ZONE_SPEED': 0.5,
  'GRAVITY_FORCE': 0.0005,
  'ROTATION_SPEED': 0.005,
  'PLAYER_TERMINAL_VEL': 0.5,
  'FIELD_HEIGHT': 700,
  'FIELD_WIDTH': 1400,
  'SKY_HEIGHT': 70,
  'WATER_HEIGHT': 100,
  'WATER_FORCE': 0.002,
  'FIRING_COOLDOWN': 75,
  'BULLET_SPEED': 0.8,
  'BULLET_LIFESPAN': 500,
  'BULLET_GENERATOR_FIRING_COOLDOWN': 300,
  'PLAYER_HP': 3,
}

class BombEnv():
  def __init__(self):

    # Repeated outside reset() so the syntax highlighter doesn't freak out
    self.playerDict = {}
    self.bombGeneratorDict = {}
    self.bombList = []
    self.actionLog = None
    self.t = 0
    self.done = False

    # Used as player ID across playerDict, observations, etc.
    self.playerCount = 0

    self.reset()

  # Helper for adding a player mid-run (returns player ID)
  def addPlayer(self, x=None, y=None):
    player = Player(x, y, self.playerCount, self)
    self.playerDict[self.playerCount] = player
    self.playerCount += 1
    return self.playerCount - 1

  def addBulletGenerator(self, x=None, y=None):
    bulletGenerator = BulletGenerator(x, y, self)
    self.bulletGeneratorDict[len(self.bulletGeneratorDict)] = bulletGenerator

  def step(self, actions):
    self.actionLog = actions
    self.t += 1

    # Increase speed with multiple passes
    for i in range(20):
      for id in self.playerDict:
        if (self.playerDict[id].hp > 0):
          if str(id) in actions:
            self.playerDict[id].update(actions[str(id)])
          else:
            self.playerDict[id].update([0, 0, 0, 0])

      for id in self.bulletGeneratorDict:
        self.bulletGeneratorDict[id].update()

      for i in range(len(self.bulletList)):

        # Need this check since list size can update while iterating
        if i < len(self.bulletList):
          self.bulletList[i].update()

    return {
      'done': self.done
    }

  def reset(self):
    self.playerDict = {}
    self.bulletList = []
    self.actionLog = None
    self.t = 0
    self.done = False
    self.playerCount = 0

    self.addPlayer(200, 200)
    self.addPlayer(500, 200)
    # self.addBulletGenerator(400, 400)

    return {
      'done': self.done
    }
  
  def draw(self, screen):
    screen.fill((0, 0, 0))
    sky_color = pygame.Color('#40455c')
    pygame.draw.rect(screen, sky_color,(0, 0, conf['FIELD_WIDTH'], conf['SKY_HEIGHT']))
    water_color = pygame.Color('#253478')
    pygame.draw.rect(screen, water_color,(0, conf['FIELD_HEIGHT'] - conf['WATER_HEIGHT'], conf['FIELD_WIDTH'], conf['WATER_HEIGHT']))
    self.playerDict[0].draw(screen)

    for bullet in self.bulletList:
      bullet.draw(screen)