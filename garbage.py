import numpy as np
import pygame

conf = {
  'PLAYER_RADIUS': 15,
  'BULLET_RADIUS': 5,
  'INPUT_FORCE': 0.001,
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

class LuftEnv():
  def __init__(self):

    # Repeated outside reset() so the syntax highlighter doesn't freak out
    self.playerDict = {}
    self.bulletGeneratorDict = {}
    self.bulletList = []
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

# Base class for object on the cylindrical field
class OnCylinder:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def update(self):
    if (self.x > conf['FIELD_WIDTH']):
      self.x = self.x - conf['FIELD_WIDTH']
    elif (self.x < 0):
      self.x = self.x + conf['FIELD_WIDTH']

class Player(OnCylinder):
  def __init__(self, x, y, player_id, env):
    super().__init__(x, y)
    self.vx = 0
    self.vy = 0
    self.ax = 0
    self.ay = 0
    self.theta = 0
    self.env = env
    self.hp = conf['PLAYER_HP']
    self.cooldown = conf['FIRING_COOLDOWN']
    self.player_id = player_id

  # action = [thrust, rotate_left, rotate_right, fire]
  def update(self, action):
    self.ax = 0
    self.ay = conf['GRAVITY_FORCE']

    if (action[0]):
      self.ay = conf['INPUT_FORCE'] * np.sin(self.theta)
      self.ax = conf['INPUT_FORCE'] * np.cos(self.theta)
    if (action[1]):
      self.theta -= conf['ROTATION_SPEED']
    if (action[2]):
      self.theta += conf['ROTATION_SPEED']

    # Apply water or sky force
    if (self.y > conf['FIELD_HEIGHT'] - conf['WATER_HEIGHT']):
      self.ay -= conf['WATER_FORCE']
    elif (self.y < conf['SKY_HEIGHT']):
      self.ay += conf['WATER_FORCE'] - conf['GRAVITY_FORCE']

    self.vx += self.ax
    self.vy += self.ay

    # Clip to max player velocity
    c = np.sqrt(np.square(self.vx) + np.square(self.vy))
    if (c > conf['PLAYER_TERMINAL_VEL']):
      f = c / conf['PLAYER_TERMINAL_VEL']
      self.vx /= f
      self.vy /= f

    # Update position and wrap on cylinder
    self.x += self.vx
    self.y += self.vy
    super().update()

    # Handle firing + cooldown
    if (self.cooldown > 0):
      self.cooldown -= 1
    if (action[3] and self.cooldown == 0):
      self.cooldown = conf['FIRING_COOLDOWN']
      Bullet(self.x, self.y, self.theta, self.player_id, self.env)

  def draw(self, screen):
    player_color = '#c22b5b'
    color = pygame.Color(player_color)
    x = int(np.round(self.x))
    y = int(np.round(self.y))
    pygame.draw.circle(screen, color, (x, y), conf['PLAYER_RADIUS'])

    # Draw dir indicator
    indicator_color = pygame.Color('#42e0ff')
    x = 30 * np.cos(self.theta)
    y = 30 * np.sin(self.theta)
    toX = self.x + x
    toY = self.y + y
    pygame.draw.line(screen, indicator_color, (self.x, self.y), (toX, toY), 2)

  def hit(self):
    self.hp -= 1

class Bullet(OnCylinder):
  def __init__(self, x, y, theta, player_id, env):
    super().__init__(x, y)
    self.vx = conf['BULLET_SPEED'] * np.cos(theta)
    self.vy = conf['BULLET_SPEED'] * np.sin(theta)
    self.lifespan = conf['BULLET_LIFESPAN']
    self.env = env
    self.player_id = player_id
    self.env.bulletList.append(self)

  def update(self):
    self.x += self.vx
    self.y += self.vy
    self.lifespan -= 1
    super().update()

    # Decrement player life if hit
    # TODO: only check neighboring regions
    for id in self.env.playerDict:
      if id != self.player_id:
        player = self.env.playerDict[id]
        if np.absolute(self.x - player.x) < conf['BULLET_RADIUS'] + conf['PLAYER_RADIUS']:
          if np.absolute(self.y - player.y) < conf['BULLET_RADIUS'] + conf['PLAYER_RADIUS']:
            player.hit()
            self.env.bulletList.remove(self)

    # Clear if out of bounds
    if (self.y > conf['FIELD_HEIGHT'] or self.y < 0 or self.lifespan < 1):
      self.env.bulletList.remove(self)
      return 

  def draw(self, screen):
    player_color = pygame.Color('#ff61df')
    x = int(np.round(self.x))
    y = int(np.round(self.y))
    pygame.draw.circle(screen, player_color, (x, y), conf['BULLET_RADIUS'])

class BulletGenerator(OnCylinder):
  def __init__(self, x, y, env):
    super().__init__(x, y)
    self.vx = 0
    self.vy = 0
    self.ax = 0
    self.ay = 0
    self.theta = 0
    self.env = env
    self.cooldown = conf['BULLET_GENERATOR_FIRING_COOLDOWN']

  def update(self):
    self.ax = 0
    self.ay = 0

    # Apply water or sky force
    if (self.y > conf['FIELD_HEIGHT'] - conf['WATER_HEIGHT']):
      self.ay -= conf['WATER_FORCE']
    elif (self.y < conf['SKY_HEIGHT']):
      self.ay += conf['WATER_FORCE'] - conf['GRAVITY_FORCE']

    self.vx += self.ax
    self.vy += self.ay

    # Update position and wrap on cylinder
    self.x += self.vx
    self.y += self.vy
    super().update()

    # Handle firing + cooldown
    if (self.cooldown > 0):
      self.cooldown -= 1
    if (self.cooldown == 0):
      self.theta = np.random.randint(0, 7);
      self.cooldown = conf['BULLET_GENERATOR_FIRING_COOLDOWN']
      Bullet(self.x, self.y, self.theta, -1, self.env)

'''
env = LuftEnv()
env.reset()

# Set up the drawing window
pygame.init()
screen = pygame.display.set_mode([conf['FIELD_WIDTH'], conf['FIELD_HEIGHT']])

# Run until the user asks to quit
running = True
while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

  action = [0, 0, 0, 0]
  keys = pygame.key.get_pressed()  #checking pressed keys
  if keys[pygame.K_w]:
    action[0] = 1
  if keys[pygame.K_a]:
    action[1] = 1
  if keys[pygame.K_d]:
    action[2] = 1
  if keys[pygame.K_j]:
    action[3] = 1
  
  env.step({ 0: action })
  env.draw(screen)

  pygame.display.flip()

pygame.quit()
'''