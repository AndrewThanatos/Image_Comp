#!/usr/bin/python3


#IMPORT
from PIL import Image
import numpy as np
import math
import os
import sys
import time


#MAIN CONST
N = 900
M = 900
REL = 150


#Image size
ImgSize = (N, M)


#check points
PeacesX = int(N / REL)
PeacesY = PeacesX
SizeX = int (N / PeacesX)
SizeY = int (M / PeacesY)
Elem = SizeX * SizeY


def preprocess_image(image_name) :
    '''
        Input: name of image
        Output: BW image with size(N * M)

        1. Load image
        2. Change it to Black-and-White
        3. And resize to ImgSize
    '''

    return Image.open(image_name).convert('L').resize(ImgSize)


def img_to_array(img):
    '''
        Input: image
        Output: array the same size as image every element of witch is in range(0 - 255)

        Change image to numpy 2d array
    '''

    return np.array(img)


def crop_image(img_array, lower_percentile=5, upper_percentile=95, fix_ratio=False):
    """
        Input: array
        Output: same or smaller array

        Crops an img_array, removing featureless border regions.
    """
    # row-wise differences
    rw = np.cumsum(np.sum(np.abs(np.diff(img_array, axis=1)), axis=1))
    # column-wise differences
    cw = np.cumsum(np.sum(np.abs(np.diff(img_array, axis=0)), axis=0))

    # compute percentiles
    upper_column_limit = np.searchsorted(cw,
                                            np.percentile(cw, upper_percentile),
                                            side='left')
    lower_column_limit = np.searchsorted(cw,
                                            np.percentile(cw, lower_percentile),
                                            side='right')
    upper_row_limit = np.searchsorted(rw,
                                        np.percentile(rw, upper_percentile),
                                        side='left')
    lower_row_limit = np.searchsorted(rw,
                                        np.percentile(rw, lower_percentile),
                                        side='right')

    # if img_array is nearly featureless, use default region
    if lower_row_limit > upper_row_limit:
        lower_row_limit = int(lower_percentile/100.*img_array.shape[0])
        upper_row_limit = int(upper_percentile/100.*img_array.shape[0])
    if lower_column_limit > upper_column_limit:
        lower_column_limit = int(lower_percentile/100.*img_array.shape[1])
        upper_column_limit = int(upper_percentile/100.*img_array.shape[1])

    # if fix_ratio, return both limits as the larger range
    if fix_ratio:
        if (upper_row_limit - lower_row_limit) > (upper_column_limit - lower_column_limit):
            lower_column_limit = lower_row_limit
            upper_column_limit = upper_row_limit
        else:
            lower_row_limit = lower_column_limit
            upper_row_limit = upper_column_limit

    # otherwise, proceed as normal
    return img_array[lower_row_limit:upper_row_limit, lower_column_limit:upper_column_limit]


def mean_array(arr):
    '''
        Input: array
        Output: array of size(PeaceX, PeaceY)

        Make arr smaller 
    '''
    n = PeacesX
    m = PeacesY
    new_arr = np.zeros((m, n))
    for i in range(m):
        for j in range(n):
            new_arr[i][j] = arr[i*SizeX:(i+1)*SizeX, j*SizeY:(j+1)*SizeY].sum() / Elem
            
    return np.array(new_arr)   


def check(x):
    """
        Input: float number
        Output: int number in range(-2 - 2)

        -2..2	 0	Indentical
        -50..-3	-1	Darker
        < -50	-2	Very dark
        3..50	 1	Bright
        >50	     2	Very Bright
    """


    if (x >= -2) & (x <= 2): return 0
    if (x >= -50) & (x < -2): return -1
    if (x <= 50) & (x > 2): return 1
    if x > 50: return 2
    if x < -50: return -2


def normalize_and_threshold(arr):
    '''
        Input: array size of (m, n) 
        Output: array size of (3*m, 3*n)

        Normalizes difference matrix in place
        array[
            [0, -2, 2, 0]
            [1, -1, 1, -2]
            [-1, -1, 1, 2]
            [0, 0, 0, 0]
            ]
    '''
        
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

            new_arr[i-1][j] = check(new_arr[i-1][j])
            new_arr[i+1][j] = check(new_arr[i+1][j])
            new_arr[i][j-1] = check(new_arr[i][j-1])
            new_arr[i][j+1] = check(new_arr[i][j+1])
            new_arr[i-1][j-1] = check(new_arr[i-1][j-1])
            new_arr[i-1][j+1] = check(new_arr[i-1][j+1])
            new_arr[i+1][j-1] = check(new_arr[i+1][j-1])
            new_arr[i+1][j+1] = check(new_arr[i+1][j+1])

    for i in range(3, m*3+3, 3):
        for j in range(3, n*3+3, 3):
            new_arr[i][j] = 0

    return(new_arr[3:m*3+1, 3:n*3+1])


def mean_error(arr1, arr2):
    '''
        Input: two same size arrays
        Output: float number in range(0 - 1)

        Count mean square error
    '''
    all_sum = math.sqrt(((arr1 - arr2)*(arr1 - arr2)).sum())
    first_sum = math.sqrt((arr1*arr1).sum())
    second_sum = math.sqrt((arr2*arr2).sum())

    # print('-------------')
    # print(all_sum)
    # print(first_sum)
    # print(second_sum)

    return  all_sum / (first_sum + second_sum)

        
def Complete(image_name):
    '''
        Input: name of image
        Output: array of difference

        Make all needed changes to image to compare it
    '''
    img = preprocess_image(image_name)
    arr = img_to_array(img)
    arr = crop_image(arr)
    new_arr = mean_array(arr)
    comp_arr = normalize_and_threshold(new_arr)

    #print(Fn.detect(np.array(Image.open('4.jpg'))))
    #Image.fromarray(crop_image(arr)).show()
    # img.show()
    # Image.fromarray(new_arr).show()
    # print(new_arr)
    # print(new_arr.shape)
    # print(arr)
    # print(arr.shape)
    # print(comp_arr)
    # print(comp_arr.shape)

    return comp_arr


def input_check(argv):
    '''
        Check if what input and is it correct
    '''
    if len(argv) == 1 and (argv[0] == '--help' or argv[0] == 'h'):
        print('''usage: solution.py [-h] --path PATH

First test task on images similarity.

optional arguments:
  -h, --help            show this help message and exit
  --path PATH           folder with images
'''
)
        return None

    if len(argv) == 2 and (argv[0] == '--path' or argv[1] == 'PATH'):
        return argv[1]
    print('usage: solution.py [-h] --path PATH\nsolution.py: error: the following arguments are required: --path')
    return None



def main(argv):

    # d = mean_error(Complete('4_similar.jpg'), Complete('4.jpg'))
    # print(d)
    path = input_check(argv)
    if path == None:
        return
    k = 1
    for i in os.listdir(path):
        for j in os.listdir(path)[k:]:
            if (i.endswith('.jpg') or i.endswith('.jpeg')) and (j.endswith('.jpg') or j.endswith('.jpeg')):
                if mean_error(Complete(i), Complete(j)) < 0.3:
                    print ('{} {}'.format(i, j))
                    # if i[4:12] == j[4:12]: print(' --- True')
                    # else: print(' --- False')
                    # print(mean_error(Complete(i), Complete(j)))
                    
        k += 1

if __name__ == "__main__":
    main(sys.argv[1:])

