from PIL import Image
import numpy as np
import math
import os

#MAIN CONST
N = 900
M = 900
REL = 40

#Image size
ImgSize = (N, M)

#Check points
PeacesX = int(N / REL)
PeacesY = PeacesX
SizeX = int (N / PeacesX)
SizeY = int (M / PeacesY)
Elem = SizeX * SizeY


def preprocess_image(image_name) :
    '''
        Load img_array and change it to Black-and-White
    '''

    return Image.open(image_name).convert('L').resize(ImgSize)


def img_to_array(img):
    '''
        Change image to numpy 2d array
    '''

    return np.array(img)


def crop_image(img_array, lower_percentile=5, upper_percentile=95, fix_ratio=False):
    """
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

        
def Complete(image_name):
    img = preprocess_image(image_name)
    arr = img_to_array(img)
    arr = crop_image(arr)
    new_arr = ArrayAverage(arr)
    comp_arr = ArrayDif(new_arr)
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



d = Dif(Complete('15_modification.jpg'), Complete('15.jpg'))
path = '.'


# for i in os.listdir(path):
#     for j in os.listdir(path):
#         if i.endswith('.jpg') & j.endswith('.jpg'):
#             if Dif(Complete(i), Complete(j)) < 0.3:
#                 print ('{} {}'.format(i, j))


print(d)