#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Viktor Qvarfordt (viktor.qvarfordt@gmail.com)"
__date__ = "2011-04-21"

import pyglet
from pyglet.window import mouse
from pyglet.window import key
from pyglet.gl import *
from pyglet import clock

from my_pyglet_functions import * # this also imports most of the math stuff

from random import uniform
from cmath import phase

# list-like type but more powerful, using this to keep track of the trails
from collections import deque


################################################################
#       Configurations
################################################################


# Universal constants
G = 6.674e-11 # Universal constant of gravitation

# Global control variables
steps = 100.
exists_pause = False
exists_gravity = True
exists_collision = True
exists_edgeBounce = False
exists_solarSystem = False

exists_clear = True

draw_trail = True
draw_vectors = True

time = 0

window = pyglet.window.Window(width=800, height=800, resizable=True)


################################################################
#       Classes
################################################################


class Planet():
    def __init__(self,label=None):
        self.pos = window.width/2. + window.height/2.*1j
        self.vel = 0
        self.acc = 0

        self.radius = 20
        self.mass = self.radius**2*pi

        self.color = (uniform(.5,1), uniform(.5,1), uniform(.5,1))
        # self.color = (1,1,1)
        
        self.trail = deque(maxlen=100)

        # internal control variables
        self.is_fixed = False

        self.label = pyglet.text.Label(text=str(self.vel), x=self.pos.real, y=self.pos.imag)

    def setAcc(self, body):
        """
        Adjusts the acceleration variable for self with respect to body
        according to the gravitational force exerted between them.
        """
        # 1.496e11 meters per 200 pixels
        # => sun -> earch = 200 pixels
        distanceScale = 1.496e11/200
        argument = phase(body.pos-self.pos)
        distance = abs(body.pos*distanceScale-self.pos*distanceScale)
        print distance
        if distance > 10: # there is no gravity if bodies are inside each other
            #  F = G*m1*m2/d^2
            # a1 = F/m1
            #    =>
            # a1 = G*m2/d^2
            accModulus = G * body.mass / (distance**2.0) # scalar

            # updating acceleration
            self.acc += rect(accModulus, argument)

    def verlet(self, dt):
        self.pos += self.vel*dt + self.acc*dt**2/2.0
        self.vel += self.acc*dt

    def update(self):
        self.label.x = self.pos.real
        self.label.y = self.pos.imag

    def draw(self):
        # Planet
        glColor3f(self.color[0], self.color[1], self.color[2])
        circle(self.pos, self.radius)
        # Trail
        if draw_trail:
            trail(self.trail)
        # velocity & acceleration
        if draw_vectors:
            glColor3f(0,0,1)
            line(self.pos, self.pos + 1/4.*self.vel, 2)
            glColor3f(1,0,0)
            line(self.pos, self.pos + 1/8.*self.acc, 2)
        # Label
        self.label.draw()


class Line():
    def __init__(self):
        self.start = 0
        self.end = 0
    def draw(self):
        line(self.start, self.end)


class Circle():
    def __init__(self):
        self.pos = 100+100j
        self.radius = 20
        self.active = False
    def draw(self):
        if self.active:
            circle(self.pos, self.radius)


################################################################
#       Objects
################################################################


myLine = Line()
myCircle = Circle()

# Container for all planet objects
planets = []
# Sun
a = Planet()
a.color = (1,1,0)
a.is_fixed = True
a.pos = window.width/2.0+window.height/2.0*1j
a.mass = 1.9891e30
a.radius = 50
planets.append(a)
# Tellus
a = Planet()
a.color = (0,0,1)
a.pos = window.width/2.0+window.height/2.0*1j + 200j
a.vel = 

# myLabel = pyglet.text.Label(text='Hello', x=planets[0].pos.real, y=planets[0].pos.imag)
infoLabel = pyglet.text.Label(anchor_x='right', anchor_y='top', multiline=True, width=500)
infoLabel.document.set_style(0, len(infoLabel.text), dict(align='right'))


################################################################
#       Hooks
################################################################


@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.RIGHT:
        newPlanet = Planet()
        newPlanet.pos = x + y*1j
        planets.append(newPlanet)
    elif button == mouse.LEFT:
        myLine.start = x+y*1j
        myLine.end = myLine.start
        myCircle.active = True
        myCircle.pos = x+y*1j

@window.event
def on_mouse_release(x, y, button, modifiers):
    if button == mouse.LEFT:
        newPlanet = Planet()
        newPlanet.pos = myLine.start
        newPlanet.vel = myLine.end - myLine.start
        newPlanet.mass = 1e30
        planets.append(newPlanet)
        myCircle.active = False
        
        myLine.start = 0
        myLine.end = 0

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if buttons == 1: # 1::lmb 4::rmb
        myLine.end = x+y*1j

@window.event
def on_key_press(symbol, modifiers):
    # Toggle pause on/off
    if symbol == key.P:
        global exists_pause
        if exists_pause:
            exists_pause = False
        else:
            exists_pause = True
    # Toggle gravity on/off
    if symbol == key.G:
        global exists_gravity
        if exists_gravity:
            exists_gravity = False
        else:
            exists_gravity = True
    # Toggle vectors on/off
    if symbol == key.V:
        global draw_vectors
        if draw_vectors:
            draw_vectors = False
        else:
            draw_vectors = True
    # Toggle trails on/off
    if symbol == key.T:
       global draw_trail
       if draw_trail:
           draw_trail = False
       else:
           draw_trail = True
            
@window.event
def on_text(text):
    if text == "C":
        global exists_clear
        if exists_clear:
            exists_clear = False
        else:
            exists_clear = True
    # Change number of Euler steps
    global steps
    if text == "1":
        steps = 1.
    if text == "2":
        steps = 20.
    if text == "3":
        steps = 50.
    if text == "4":
        steps = 100.
    if text == "5":
        steps = 500.
    if text == "6":
        steps = 1000.



################################################################
#       Runtime
################################################################


def update(dt):
    if not exists_pause:
        # Preform the calculations $steps times per visual update.
        dt = dt / steps
        for count in range(int(steps)):
            for p1 in planets:
                p1.acc = 0
                for p2 in planets:
                    # Checks so that the planets havent been removed (in a collision) and are still in the list.
                    if p1 != p2 and p1 in planets and p2 in planets:
                        if exists_gravity:
                            p1.setAcc(p2)
                
                if not p1.is_fixed:
                    p1.verlet(dt)
                p1.update()
    
    infoLabel.text = "Active planets: %d\nEuler steps: %d\nGravity: %s\nCollision: %s\nEdge bounce: %s" %(len(planets), steps, exists_gravity, exists_collision, exists_edgeBounce)
    infoLabel.x = window.width
    infoLabel.y = window.height
            




# Is this anything more than FPS cap?
pyglet.clock.schedule_interval(update, 1/60.0) # update at 60Hz

fps_display = pyglet.clock.ClockDisplay()
glClearColor(0,0,0,1)
@window.event
def on_draw():
    if exists_clear:
        window.clear()

    # Drawing all planets
    for p in planets:
        if draw_trail:
            p.trail.append(p.pos)
        elif p.trail:
            p.trail = []
        p.draw()

    glColor3f(1,1,1)
    myLine.draw()
    myCircle.draw()

    glColor3f(1,1,0)

    infoLabel.draw()
    fps_display.draw()

pyglet.app.run()
