"""
Created on Sat Nov  2 14:59:05 2019

@author: Utkarsh
"""

import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import cv2
global p

def gaussian_kernel(size, sigma=1):
    size = int(size)  //2
    x, y = np.mgrid[-size:size+1, -size:size+1]
    normal = 1 / (2.0 * np.pi * sigma**2)
    g =  np.exp(-((x**2 + y**2) / (2.0*sigma**2))) * normal
    return g
def sobel_filters(img):
    Kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], np.float32)
    Ky = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], np.float32)
    
    Ix = ndimage.filters.convolve(img, Kx)
    Iy = ndimage.filters.convolve(img, Ky)
    
    G = np.hypot(Ix, Iy)
    G = G / G.max() * 255
    theta = np.arctan2(Iy, Ix)
    
    return (G, theta)
def non_max_suppression(img, D):
    M, N = img.shape
    Z = np.zeros((M,N), dtype=np.int32)
    angle = D * 180. / np.pi
    angle[angle < 0] += 180
    for i in range(1,M-1):
        for j in range(1,N-1):
                q = 255
                r = 255
               #angle 0
                if (0 <= angle[i,j] < 22.5) or (157.5 <= angle[i,j] <= 180):
                    q = img[i, j+1]
                    r = img[i, j-1]
                #angle 45
                elif (22.5 <= angle[i,j] < 67.5):
                    q = img[i+1, j-1]
                    r = img[i-1, j+1]
                #angle 90
                elif (67.5 <= angle[i,j] < 112.5):
                    q = img[i+1, j]
                    r = img[i-1, j]
                #angle 135
                elif (112.5 <= angle[i,j] < 157.5):
                    q = img[i-1, j-1]
                    r = img[i+1, j+1]
                if (img[i,j] >= q) and (img[i,j] >= r):
                    Z[i,j] = img[i,j]
                else:
                    Z[i,j] = 0
    return Z
def threshold(img, lowThreshold, highThreshold):
    M, N = img.shape
    res = np.zeros((M,N), dtype=np.int32)
    weak = 25
    strong = 255
    strong_i, strong_j = np.where(img >= highThreshold)
    zeros_i, zeros_j = np.where(img < lowThreshold)
    weak_i, weak_j = np.where((img <= highThreshold) & (img >= lowThreshold))
    res[strong_i, strong_j] = strong
    res[weak_i, weak_j] = weak
    return res,weak,strong

def hysteresis(img, weak, strong=255):
    M, N = img.shape  
    for i in range(1, M-1):
        for j in range(1, N-1):
            if (img[i,j] == weak):
                try:
                    if ((img[i+1, j-1] == strong) or (img[i+1, j] == strong) or (img[i+1, j+1] == strong)
                        or (img[i, j-1] == strong) or (img[i, j+1] == strong)
                        or (img[i-1, j-1] == strong) or (img[i-1, j] == strong) or (img[i-1, j+1] == strong)):
                        img[i, j] = strong
                    else:
                        img[i, j] = 0
                except IndexError as e:
                    pass
    return img
def plot(image,noisy_image):
    plt.subplot(121),plt.imshow(image, cmap = 'gray')
    plt.title("ORIGINAL")
    plt.subplot(122),plt.imshow(noisy_image, cmap= 'gray')
    plt.title("CANNY EDGES")
    plt.show()
def canny(low,high):
    a,b,c=threshold(p,low,high)
    d=hysteresis(a,b,c)
    
    print(d.dtype)
    f=cv2.imread('Lanes.jpg',0)
    plot(f,d)
    
img=cv2.imread('.images/Lanes.jpg',0)
img=np.asarray(img,np.float64)   
g=gaussian_kernel(5,1)
img=ndimage.convolve(img, g)
x,y=sobel_filters(img)
p=non_max_suppression(x,y)

    


fig=plt.figure()
fig.subplots_adjust(bottom=0.3)
ax1=fig.add_subplot(121)
ax2=fig.add_subplot(122)

#axes= fig.add_axes([0.1,0.7,0.15,0.15])
axes_slider= fig.add_axes([0.15,0.1,0.7,0.01])
axes_slider1= fig.add_axes([0.15,0.2,0.7,0.01])
slider1=Slider(axes_slider,"Lower Threashold",0,255,valinit=20)
slider2=Slider(axes_slider1,"Higher Threashold",0,255,valinit=32)
canny(20,32)
def update(val):
	canny(slider1.val,slider2.val)
slider1.on_changed(update)
slider2.on_changed(update)
plt.show()
