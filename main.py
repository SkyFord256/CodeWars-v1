import sys
import pygame
from pygame.sprite import Group
import numpy as np
import cv2
import time

from base import Base
from collectible import Collectible
import script
#resources library

class Game():

        
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1200,800))
        #self.score = pygame.display.set_mode((400, 800))
        #self.scoreboard = pygame.display.set_caption("Code Wars")
        self.fps_controller = pygame.time.Clock()
        self.dim = (40,40)
        self.resources = self.create_map()
        self.resources[19][9] = 0
        self.resources[19][29] = 0
        self.GlobalRobotCount = 0
        self.explosion = pygame.image.load("explode.png")


        self.collectibles = []
        
        self.PositionToRobot = {}
        for i in range(self.dim[0]):
            Z = []
            for j in range(self.dim[1]):
                Z.append(Collectible(self.screen, i*20, j*20, self.resources[j][i]))
            self.collectibles.append(Z)
        
        

        self.__bluebots = Group()
        self.__redbots = Group()
        self.robots = np.zeros(self.dim)
        # 0 in self.robots means no robots
        # 1 means one robot of red team
        # 2 means one robot of blue team
        # 3 means base for team red
        # 4 means base for team blue

        self.__redbase = Base(self.screen, 180, 380, 'red', self.__redbots, self.robots,self)
        self.__bluebase = Base(self.screen, 580, 380, 'blue', self.__bluebots, self.robots,self)
        self.PositionToRobot[(9,19)] = {self.__redbase:True}
        self.PositionToRobot[(29,19)] = {self.__bluebase:True}
        self.update_score()

        for j in range(3):
            self.__redbase.create_robot('')
            self.__bluebase.create_robot('')

    def run_game(self):
        iter = 0
        while True:
            iter+=1
            self.screen.fill((60,60,60))
<<<<<<< HEAD
            self.__redbase.create_robot('')
            self.__bluebase.create_robot('')
            moves = {}
            for robo in self.__redbots:
                n = robo.next_move()
                moves[robo] = n
            for robo in self.__bluebots:
                n = robo.next_move()
                moves[robo] = n
            for robo, n in moves.items():
=======
            self.collect()
            script.ActOperator(self.__bluebase)
            script.ActOperator(self.__redbase)
            for robo in self.__redbots:
                n = script.ActRobot(robo)
                if n == 1:
                    robo.move_up()
                elif n == 2:
                    robo.move_right()
                elif n == 3:
                    robo.move_down()
                elif n == 4:
                    robo.move_right()
            for robo in self.__bluebots:
                n = script.ActRobot(robo)
>>>>>>> 0acac2e546af771338c796bc2a53c62937208c45
                if n == 1:
                    robo.move_up()
                elif n == 2:
                    if robo.type == "blue":
                        robo.move_left()
                    else:
                        robo.move_right()
                elif n == 3:
                    if robo.type == "blue":
                        robo.move_left()
                    else:
                        robo.move_right()
                elif n == 4:
                    robo.move_down()
            self.collect()
            for i in range(0,self.dim[0]):
                for j in range(0,self.dim[1]):
                    self.collectibles[i][j].blitme()  
            self.__bluebase.blitme()
            self.__redbase.blitme()
            collisions  = self.check_collisions()
            self.updateRoboMap()
            self.__bluebots.draw(self.screen)
            self.__redbots.draw(self.screen)
            for b in collisions.keys():
                self.screen.blit(self.explosion, b.rect)
            #print(self.PositionToRobot)
            self.update_score()
            pygame.display.flip()
            self.check_events()
            if iter % 10 == 0:
                self.replenish()
            
            
            self.fps_controller.tick(2)

    def updateRoboMap(self):
        self.robots = np.zeros((self.dim[1],self.dim[0])).astype(int)
        for key in self.PositionToRobot.keys():
            value = self.PositionToRobot[key]
            entr = 0
            for v in value:
                if v==self.__redbase:
                    entr = 3
                    break
                if v==self.__bluebase:
                    entr = 4
                    break
                if v.type=="red":
                    entr = 1
                else:
                    entr = 2
            self.robots[key[1]][key[0]] = entr
    
    def check_events(self):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
    
    def check_collisions(self):
        removals = pygame.sprite.groupcollide(self.__bluebots, self.__redbots, False, False)
        #print(removals)
        to_kill = set()
        for b, r_list in removals.items():
            #print(id(b))
            for r in r_list:
                #print(id(r))
                if b.selfElixir > r.selfElixir:
                    b.selfElixir -= r.selfElixir
                    self.robots[r.rect.y//20][r.rect.x//20] = 2
                    to_kill.add(r)
                    self.__redbase.TotalTeamElixir -= r.selfElixir
                    self.__bluebase.TotalTeamElixir -= r.selfElixir
                    r.selfElixir = 0
                elif b.selfElixir < r.selfElixir:
                    self.robots[r.rect.y//20][r.rect.x//20] = 1
                    r.selfElixir -= b.selfElixir
                    to_kill.add(b)
                    self.__bluebase.TotalTeamElixir -= b.selfElixir
                    self.__bluebase.TotalTeamElixir -= b.selfElixir
                    b.selfElixir = 0
                else:
                    self.robots[r.rect.y//20][r.rect.x//20] = 0
                    to_kill.add(r)
                    to_kill.add(b)
                    self.__redbase.TotalTeamElixir -= r.selfElixir
                    self.__bluebase.TotalTeamElixir -= b.selfElixir
                    r.selfElixir = 0
                    b.selfElixir = 0
        for a in to_kill:
                del self.PositionToRobot[(a.rect.x//20, a.rect.y//20)][a]
                a.kill()
        return removals


    def create_map(self):
        """Take info about collectibles and create the map"""
        im = cv2.imread("test_img3.jpg", cv2.IMREAD_GRAYSCALE)
        im = cv2.resize(im, (40,40))
        im = np.array(im)
        im = im - np.full((40,40), 127)
        im = (im/127)*50
        return np.array(im)

    def replenish(self):
        for i in range(0,self.dim[0]):
            for j in range(0,self.dim[1]):
                # if self.collectibles[i][j].initPoints > 1e-5:
                #     self.collectibles[i][j].points = min(self.collectibles[i][j].initPoints, self.collectibles[i][j].points*1.3)
                if self.collectibles[i][j].initPoints < -1e-5:
                    self.collectibles[i][j].points = max(self.collectibles[i][j].initPoints, self.collectibles[i][j].points*1.3)
                self.resources[j][i] = self.collectibles[i][j].points
                self.collectibles[i][j].setColor()


    def collect(self):
        
        for key in self.PositionToRobot.keys():
            value = self.PositionToRobot[key]
            if self.robots[key[1]][key[0]] == 1 or self.robots[key[1]][key[0]] == 2:
                V = self.resources[key[1]][key[0]]/(2*len(value))
                for v in value:
                    v.addResource(V)
                self.resources[key[1]][key[0]] /= 2
                self.collectibles[key[0]][key[1]].points = self.resources[key[1]][key[0]]
                self.collectibles[key[0]][key[1]].setColor()


                


    def update_score(self):
        """Update scores in the scoreboard"""
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("Score Board", True, (255,255,255))
        titlerect = title.get_rect()
        titlerect.x = 900
        titlerect.y = 50
        self.screen.blit(title, titlerect)
        head_font = pygame.font.SysFont(None, 40)
        norm_font = pygame.font.SysFont(None, 32)
        blue_head = head_font.render("Blue Team", False, (130,130,255))
        self.screen.blit(blue_head, (830, 130))
        blue_total = norm_font.render("Total Elixir :" + str(round(self.__bluebase.TotalTeamElixir,2)), False, (230,230,230))
        blue_self = norm_font.render("Self Elixir : " + str(self.__bluebase.SelfElixir), False, (230,230,230))
        blue_robots = norm_font.render("No. of Robots: " +str(len(self.__bluebots)), False, (230,230,230))
        blue_virus = norm_font.render("Total Virus: " + str(round(self.__bluebase.TotalVirus, 2)), False, (230,230,230))
        self.screen.blit(blue_total, (850, 170))
        self.screen.blit(blue_self, (850, 210))
        self.screen.blit(blue_robots, (850, 250))
        self.screen.blit(blue_virus, (850, 290))

        red_head = head_font.render("Red Team", False, (255,130,130))
        self.screen.blit(red_head, (830, 400))
        red_total = norm_font.render("Total Elixir :" + str(round(self.__redbase.TotalTeamElixir,2)), False, (230,230,230))
        red_self = norm_font.render("Self Elixir : " + str(self.__redbase.SelfElixir), False, (230,230,230))
        red_robots = norm_font.render("No. of Robots: " +str(len(self.__redbots)), False, (230,230,230))
        red_virus = norm_font.render("Total Virus: " + str(round(self.__redbase.TotalVirus, 2)), False, (230,230,230))
        self.screen.blit(red_total, (850, 440))
        self.screen.blit(red_self, (850, 480))
        self.screen.blit(red_robots, (850, 520))
        self.screen.blit(red_virus, (850, 560))

        print("Red Team: ")
        print("Total Elixir: "+ str(self.__redbase.TotalTeamElixir))
        print("Self ELixir: " + str(self.__redbase.SelfElixir))
        print("No. of Robots: " + str(len(self.__redbots)))
        

    def game_over(self):
        """Check conditions of game over"""
        if self.__redbase.SelfElixir <= 0:
            print( "Blue Wins")
            sys.exit(0)
        elif self.__bluebase.SelfElixir <= 0:
            print("Red Wins")
            sys.exit(0)
            
    

game = Game()
game.run_game()