from PIL import Image
import numpy as np
import math
import os

#MAIN CONST
N = 1600
M = 900
REL = 20

#Image size
ImgSize = (N, M)

#Check points
PeacesX = int(N / REL)
PeacesY = int (M / REL)
SizeX = int (N / PeacesX)
SizeY = int (M / PeacesY)
Elem = SizeX * SizeY



#Make image normal
def ImgNormalization(str) :
    return Image.open(str).convert('L').resize(ImgSize)

def ImgToArray(img):
    return np.array(img)

def ArrayAverage(arr):
    n = PeacesX
    m = PeacesY
    new_arr = np.zeros((m, n))
    for i in range(m):
        for j in range(n):
            new_arr[i][j] = arr[i*SizeX:(i+1)*SizeX, j*SizeY:(j+1)*SizeY].sum() / Elem
            
    return np.array(new_arr)

def Check(x):
    if (x >= -2) & (x <= 2): return 0
    if (x >= -50) & (x < -2): return -1
    if (x <= 50) & (x > 2): return 1
    if x > 50: return 2
    if x < -50: return -2

def ArrayDif(arr):
    n = PeacesX
    m = PeacesY
    new_arr = np.zeros((m*3+4, n*3+4))
    
    for i in range(m):
        for j in range(n):
            new_arr[i*3 + 3][j*3 + 3] = arr[i, j]

    for i in range(3, m*3+3, 3):
        for j in range(3, n*3+3, 3):
            new_arr[i-1][j] = new_arr[i][j] - new_arr[i-3][j]
            new_arr[i+1][j] = new_arr[i][j] - new_arr[i+3][j]
            new_arr[i][j-1] = new_arr[i][j] - new_arr[i][j-3]
            new_arr[i][j+1] = new_arr[i][j] - new_arr[i][j+3]
            new_arr[i-1][j-1] = new_arr[i][j] - new_arr[i-3][j-3]
            new_arr[i-1][j+1] = new_arr[i][j] - new_arr[i-3][j+3]
            new_arr[i+1][j-1] = new_arr[i][j] - new_arr[i+3][j-3]
            new_arr[i+1][j+1] = new_arr[i][j] - new_arr[i+3][j+3]

            new_arr[i-1][j] = Check(new_arr[i-1][j])
            new_arr[i+1][j] = Check(new_arr[i+1][j])
            new_arr[i][j-1] = Check(new_arr[i][j-1])
            new_arr[i][j+1] = Check(new_arr[i][j+1])
            new_arr[i-1][j-1] = Check(new_arr[i-1][j-1])
            new_arr[i-1][j+1] = Check(new_arr[i-1][j+1])
            new_arr[i+1][j-1] = Check(new_arr[i+1][j-1])
            new_arr[i+1][j+1] = Check(new_arr[i+1][j+1])

    for i in range(3, m*3+3, 3):
        for j in range(3, n*3+3, 3):
            new_arr[i][j] = 0

    return(new_arr[3:m*3+1, 3:n*3+1])

def Dif(arr1, arr2):
    all_sum = math.sqrt(((arr1 - arr2)*(arr1 - arr2)).sum())
    first_sum = math.sqrt((arr1*arr1).sum())
    second_sum = math.sqrt((arr2*arr2).sum())

    # print('-------------')
    # print(all_sum)
    # print(first_sum)
    # print(second_sum)

    return  all_sum / (first_sum + second_sum)

        
def Complete(str):
    img = ImgNormalization(str)
    arr = ImgToArray(img)
    new_arr = ArrayAverage(arr)
    comp_arr = ArrayDif(new_arr)
    # img.show()
    # Image.fromarray(new_arr).show()
    # print(new_arr)
    # print(new_arr.shape)
    # print(arr)
    # print(arr.shape)
    # print(comp_arr)
    # print(comp_arr.shape)

    return comp_arr



d = Dif(Complete('4.jpg'), Complete('4_similar.jpg'))
path = '.'

# for i in os.listdir(path):
#     for j in os.listdir(path):
#         if i.endswith('.jpg') & j.endswith('.jpg'):
#             if Dif(Complete(i), Complete(j)) < 0.3:
#                 print ('{} {}'.format(i, j))





print (d)
