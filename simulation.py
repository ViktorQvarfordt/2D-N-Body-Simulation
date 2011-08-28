#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Viktor Qvarfordt (viktor.qvarfordt@gmail.com)"
__date__ = "2011-06-16"

import pyglet
from pyglet.window import mouse, key
#from pyglet.gl import *

# This also imports most of the math stuff
from my_pyglet_functions import *

from random import uniform
from cmath import phase

# list-like type but more powerful,
# using this to keep track of the trails
from collections import deque


################################################################
#       General configurations
################################################################


# Universal constants
G = 2.8e3 # Universal constant of gravitation

# Global control variables
steps = 100
exists_pause = False
exists_gravity = True
exists_collision = True
exists_edge_bounce = False

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
        """
        Sets up planet attributes:
        pos, vel, acc, radius, mass, color, trail, is_fixed, label.
        """
        self.pos = window.width/2. + window.height/2.*1j
        self.vel = 0
        self.acc = 0

        self.radius = 20
        self.mass = self.radius**2*pi

        self.color = (uniform(.5,1), uniform(.5,1), uniform(.5,1))
        
        # An empty deque type, list-like.
        self.trail = deque(maxlen=100)

        self.is_fixed = False

        self.label = pyglet.text.Label(
            text=str(self.vel), x=self.pos.real, y=self.pos.imag)

    def set_acc(self, body):
        """
        Adjusts the acceleration variable for self with respect to body
        according to the gravitational force exerted between them.
        """
        argument = phase(body.pos-self.pos)
        distance = abs(body.pos-self.pos)
        # There is no gravity if bodies are inside each other.
        # Normally this never tests as false,
        # collision will already have happened.
        if distance > 10:
            #  F = G*m1*m2/d^2
            # a1 = F/m1 =>
            # a1 = G*m2/d^2
            accModulus = G * body.mass / (distance**2.0) # scalar
            # updating acceleration
            self.acc += rect(accModulus, argument)

    def edge_bounce(self, elasticity=1):
        """
        Bounce of the window edge.
        Adjusting body.vel so that: incidence angle = departure angle
        Takes collission elasticity into account.
        Pushes back bodies that are located (partially or fully)
        outside the window edges.
        """
        velAbs = abs(self.vel)
        velArg = phase(self.vel)
        # Left edge
        if self.pos.real - self.radius < 0:
            self.vel = rect(velAbs*elasticity, pi - velArg)
            self.pos += self.radius - self.pos.real
        # Right edge
        elif self.pos.real + self.radius > window.width:
            self.vel = rect(velAbs*elasticity, pi - velArg)
            self.pos += window.width - (self.pos.real + self.radius) 
        # Bottom edge
        elif self.pos.imag - self.radius < 0:
            self.vel = rect(velAbs*elasticity, 2*pi - velArg)
            self.pos += (self.radius - self.pos.imag)*1j
        # Top edge
        elif self.pos.imag + self.radius > window.height:
            self.vel = rect(velAbs*elasticity, 2*pi - velArg)
            self.pos += (window.height - (self.pos.imag + self.radius))*1j

    def eulerStandard(self, dt):
        # y_{n+1} = y_n + hy'(n)
        self.pos += self.vel * dt
        self.vel += self.acc * dt
        
    def eulerSymplectic(self, dt):
        # y_{n+1} = y_n + hy'(n+1)
        self.vel += self.acc * dt
        self.pos += self.vel * dt

    def verlet(self, dt):
        self.pos += self.vel*dt + self.acc*dt**2/2.0
        self.vel += self.acc*dt
    
    ###

    def get_dx(self, dt, v):
        dx = v * dt
        return dx

    def get_dv(self, dt, a):
        dv = a * dt
        return dv
    
    def rk2(self, dt):
        dx1 = self.get_dx(dt, self.vel)
        dx2 = self.get_dx(2*dt, self.vel + dt*dx1)
        self.pos += (1/3.) * (dx1 + dx2)

        dv1 = self.get_dv(0, self.acc)
        dv2 = self.get_dv(dt, self.acc + dt*dv1)
        self.vel += (1/3.) * (dv1 + dv2)

    ###

    def update(self):
        # self.mass = self.radius**2*pi
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
# massCenter = Circle()
# massCenter.radius = 5

# Container for all planet objects
planets = []


# myLabel = pyglet.text.Label(
#     text='Hello', x=planets[0].pos.real, y=planets[0].pos.imag)
infoLabel = pyglet.text.Label(
    anchor_x='right', anchor_y='top', multiline=True, width=500)
infoLabel.document.set_style(0, len(infoLabel.text), dict(align='right'))



################################################################
#       Functions
################################################################
# This set of functions assumes their arguments to have
# arg.pos and arg.vel represented as complex numbers.


def start():
    exists_solarSystem = False
    a = Planet()
    a.pos = window.width/2. + window.height/2.*1j-100j
    a.vel = 100
    a.radius = 20
    planets.append(a)
    
    a = Planet()
    a.pos = window.width/2. + window.height/2.*1j+100j
    a.vel = -100
    a.radius = 20
    planets.append(a)

def body_collision(p1, p2):
    """
    A perfectly inelastic collision between p1 and p2.
    The larger body will consume the smaller.
    Momentum is conserved.
    """
    distance = abs(p2.pos - p1.pos)
    comb_radius = p1.radius + p2.radius
    momentum =  p1.mass*abs(p1.vel) + p2.mass*abs(p2.vel)

    # Collision will occur when planets are overlapping.
    if distance < comb_radius: 
        # Always let the larger body consume the smaller.
        if p1.mass > p2.mass:
            # Fuse masses.
            p1.mass = p1.mass + p2.mass
            # Change radius to reflect the new mass.
            # 1 mass unit = 1 pixel => mass = area => radius = sqrt(mass/pi)
            p1.radius = sqrt(p1.mass/pi)
            # Momentum: m1*v1 + m2*v2 = (m1+m2)*v_total
            # p1 is now the fused mass. so p1.vel is v_total
            p1.vel = (p1.mass*p1.vel + p2.mass*p2.vel) / (p1.mass + p2.mass)
            # The consumed planet is removed
            planets.remove(p2)
        else:  # p2 is the big one. or p1.mass == p2.mass.
            p2.mass = p1.mass + p2.mass
            p2.radius = sqrt(p2.mass/pi)
            p2.vel = (p2.mass*p2.vel + p1.mass*p1.vel) / (p2.mass + p1.mass)
            planets.remove(p1)

def body_bounce(body1, body2):
    """Incomplete"""
    pass

################################################################
#       Event hooks
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
    #if symbol == key.LSHIFT or symbol == key.RSHIFT:
    #    print "shift was pressed"

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
    # Clear all planets
    if symbol == key.SPACE:
        global planets
        planets = []
    # Toggle collision on/off
    if symbol == key.C:
        global exists_collision
        if exists_collision:
            exists_collision = False
        else:
            exists_collision = True
    # Spawn predefined planets
    if symbol == key.F1:
        start()
    # Toggle edge bounce on/off
    if symbol == key.B:
        global exists_edge_bounce
        if exists_edge_bounce:
            exists_edge_bounce = False
        else:
            exists_edge_bounce = True
        
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
        dt = float(dt / steps)
        for count in range(steps):
            for p1 in planets:
                p1.acc = 0
                for p2 in planets:
                    # Checks so that the planets haven't been removed
                    # (in a collision) and are still in the list.
                    if p1 != p2 and p1 in planets and p2 in planets:
                        if exists_gravity:
                            p1.set_acc(p2)
                        if exists_collision:
                            body_collision(p1, p2)
                
                if not p1.is_fixed:
                    if exists_edge_bounce:
                        p1.edge_bounce()
                    p1.verlet(dt)
                    #p1.rk2(dt)
                    p1.update()  # Taking care of labels.


    # # Stuff that needs no high precicion.
    # # Calculating the total momentum.
    # momentumTotal = 0
    # massTotal = 0
    # posTotal = 0
    # for planet in planets:
    #     momentumTotal += planet.mass*planet.vel
    #     massTotal += planet.mass
    #     posTotal += planet.pos*planet.mass
                
    #     momentumTotal = abs(momentumTotal)
                
    # # Mass center, incomplete.
    #     if len(planets) >= 2:
    #         massCenter.active = True
    #         massCenter.pos = posTotal / (len(planets)+massTotal)
    #     else:
    #         massCenter.active = False
                
    # infoLabel.text = 'Active planets: %d\nTotal momentum: %d' %(len(planets), momentumTotal)
    
    infoLabel.text = "Active planets: %d\nEuler steps: %d\nGravity: %s\nCollision: %s\nEdge bounce: %s" %(len(planets), steps, exists_gravity, exists_collision, exists_edge_bounce)
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

    # glColor3f(1,1,0)
    # massCenter.draw()

    infoLabel.draw()
    fps_display.draw()

pyglet.app.run()
