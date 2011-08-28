import pyglet
from pyglet.window import mouse
from pyglet.window import key
from pyglet.gl import *

from cmath import exp as cexp
from cmath import polar, rect, phase
from math import *

# all positions in the 2d plane are represented by complex numbers 

def triangle(pos, side, ang=0):
    r = side/(2*cos(pi/6))

    p1 = pos + rect(r, 7*pi/6 + ang)
    p2 = pos + rect(r, pi/2 + ang)
    p3 = pos + rect(r, -pi/6 + ang)

    glBegin(GL_TRIANGLES)
    glColor3f(0,1,0,1)
    glVertex2f(p1.real, p1.imag)
    glColor3f(1,0,0,1)
    glVertex2f(p2.real, p2.imag)
    glColor3f(0,0,1,1)
    glVertex2f(p3.real, p3.imag)
    glEnd()

#def hollowTriangle

def rectangle(pos, width):
    x1 = pos.real - width/2
    y1 = pos.imag - width/2
    x2 = pos.real + width/2
    y2 = pos.imag + width/2

    glRectf(x1, y1, x2, y2)


def line(w, z, width=1):
    glLineWidth(width)
    glBegin(GL_LINES)
    glVertex2f(z.real, z.imag)
    glVertex2f(w.real, w.imag)
    glEnd()

def trail(coordinates, width=2):
    glLineWidth(width)
    glBegin(GL_LINE_STRIP)
    for p in coordinates:
        glVertex2f(p.real, p.imag)
    glEnd()

#def arrow(w, z, width):
#    glLineWidth(width)
#    glBegin(GL_LINES)
#    glVertex2f(z.real, z.imag)
#    glVertex2f(w.real, w.imag)
#    glEnd()
#
#    glBegin(GL_TRIANGLES)
#    glVertex2f(w.real, w.imag)

def circle(pos, radius):
    """
    We want a pixel perfect circle. To get one,
    we have to approximate it densely with triangles.
    Each triangle thinner than a pixel is enough
    to do it. Sin and cosine are calculated once
    and then used repeatedly to rotate the vector.
    I dropped 10 iterations intentionally for fun.
    """
    x = pos.real
    y = pos.imag

    # iterations = int(2*radius*pi)
    iterations = 8
    s = sin(2*pi / iterations)
    c = cos(2*pi / iterations)

    dx, dy = radius, 0

    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for i in range(iterations+1):
        glVertex2f(x+dx, y+dy)
        dx, dy = (dx*c - dy*s), (dy*c + dx*s)
    glEnd()

def hollow_circle(pos, radius, width):
    x = pos.real
    y = pos.imag
    
    # iterations = int(2*pi*radius)
    iterations = 8
    s = sin(2*pi / iterations)
    c = cos(2*pi / iterations)

    dx, dy = radius, 0

    glLineWidth(width)
    glBegin(GL_LINE_STRIP)
    for i in range(iterations+1):
        glVertex2f(x+dx, y+dy)
        dx, dy = (dx*c - dy*s), (dy*c + dx*s)
    glEnd()

