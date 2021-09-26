import random
import xlwt 
from xlwt import Workbook

class SameXValue(Exception):
    pass

class HullCompError(Exception):
    pass

def min_max_points(points,index_to_compare):
    # assume that the first points are the min and the max
    min_value = points[0][index_to_compare]
    min_index = 0
    max_value = points[0][index_to_compare]
    max_index = 0
    for i in range(0,len(points)):
        if points[i][index_to_compare] < min_value:
            min_value = points[i][index_to_compare]
            min_index = i
        
        if points[i][index_to_compare] > max_value:
            max_value = points[i][index_to_compare]
            max_index = i
    
    return points[min_index], points[max_index]


def sort(points, start_index,end_index,index_to_compare):
    
    if(start_index != end_index):
        # temporary memory - once it is in order, it will be commited to the main array
        temp = [0] * (end_index - start_index + 1)
        midindex = (end_index + start_index ) // 2

        # after these two lines, the subarrays [start,mid], [mid+1,end]
        # are in order
        sort(points, start_index,midindex,index_to_compare)
        sort(points, midindex + 1,end_index,index_to_compare)
        
        # store the objects in the right order in the temp variable
        # then we replace the order
        count = 0
        i = start_index
        j = midindex + 1
        while( i <= midindex and j <= end_index):
            # comparing with respect to the first coordinate
            if points[i][index_to_compare] <= points[j][index_to_compare]:
                temp[count] = points[i]
                i += 1
                count += 1
            else:
                temp[count] = points[j]
                j += 1
                count += 1
        
        # these checks are mututally exclusive
        # count stores the index of the next cell to be used
        if(i <= midindex):
            temp[count:] = points[i:midindex+1]
        if(j <= end_index):
            temp[count:] = points[j:end_index+1] # the error was here

        # commit the temp variable
        points[start_index:end_index+1] = temp[:]
        
    else:
        pass


def find_split_index(points,min_value,index_to_compare):
    '''
    Assumes that the given list is sorted with respect to the y axis.
    Applies binary search to find the smallest value largest than min_value
    '''
    low_index = 0
    high_index = len(points)-1
    
    while high_index - low_index > 1:
        midindex = (high_index + low_index) // 2
        y_value = points[midindex][index_to_compare]
        
        if y_value < min_value:
            low_index = midindex
        else:
            high_index = midindex
    
    if high_index - low_index == 1:
        if points[low_index][index_to_compare] >= min_value:
            return low_index
        else:
            return high_index
    else:
        return low_index
    



def convex_hull(points):
    '''
    The input is an unordered set of points stored as a tuple (x,y)
    '''
    N = len(points)
    sort(points,0,N-1,0) # sort points with respect to x
    
    '''
    # changes the order of the given data structure
    point_min_x, point_max_x = min_max_points(points)
    min_y = min(point_min_x[1], point_max_x[1]) # between these two points find the max value
    
    
    sort(points,0,N-1,1) # sorting with respect to y
    split_index = split(points,min_y)
    # split the points into top and bottom
    
    bottom_points = points[0:split_index-2]
    top_points = points[split_index: N-1]
    sort(bottom_points,0,len(bottom_points)-1,0) # sort all the values below min_y with respect to x
    sort(top_points,0,len(top_points)-1,0) # sort all the values below min_y with respect to x
    '''

    try:
        points_in_top_hull = top_hull(points)
    except HullCompError:
        print('Error: failed to compute the top hull')
    
    try:
        points_in_bottom_hull = bottom_hull(points)
    except HullCompError:
        print('Error: failed to compute the bottom hull')
    

    points_in_bottom_hull = points_in_bottom_hull[1:len(points_in_bottom_hull)-1]

    # has the added property that points are in clockwise order and the first element is the leftmost element
    return points_in_top_hull + points_in_bottom_hull[::-1] # [1:len(points_in_bottom_hull)-1]


def top_hull(points):
    
    # assume every point belongs to the top hull
    top_hull_points = points[:]

    # trivial case - the algorithm I use requires more than two points
    # cannot be less than one but anyway
    if(len(points) <= 2):
        return top_hull_points

    #print('Start of top hull algorithm')
    i = 0
    while True:
        try:
            # only happens when a deletion is made an i is pointing to the first element of the list
            if i == -1:
                i = 0

            x1,y1 = top_hull_points[i]
            x2,y2 = top_hull_points[i+1]
            x3,y3 = top_hull_points[i+2]

            y_prime = point_slope_line_eval(x1,y1,x2,y2,x3)
    
            if(y3 < y_prime):
                # do nothing. The point belongs to the top hull
                i += 1
            else:
                top_hull_points.remove(top_hull_points[i+1])
                i -= 1 # careful about a negative index

        except IndexError:
            # this will happen when i + 2 is out of range. All points checked
            # nothing whent wrong
            break
        except SameXValue:
            top_hull_points.remove(top_hull_points[i+1])
            i -= 1
                
    
    #print('Top hull complete')
    return top_hull_points

def bottom_hull(points):
    
    # assume every point belongs to the top hull
    bottom_hull_points = points[:]

    # trivial case - the algorithm I use requires more than two points
    # cannot be less than one but anyway
    N = len(points)
    if(N <= 2):
        return bottom_hull_points

    #print('Start of bottom hull algorithm')
    i = N - 1
    count = 0
    while True:
        try:
            #print(i)
            x1,y1 = bottom_hull_points[i]
            # to prevent looping -> looks like the try except is not necessary, but just in case
            if i-1 < 0:
                break
            x2,y2 = bottom_hull_points[i-1]
            x3,y3 = bottom_hull_points[i-2]

            #print(bottom_hull_points[i],bottom_hull_points[i-1],bottom_hull_points[i-2])

            y_prime = point_slope_line_eval(x1,y1,x2,y2,x3)

            if(y3 > y_prime):
                # do nothing. The point belongs to the bottom hull
                i -= 1
            else:
                #print('delete ',bottom_hull_points[i-1])
                bottom_hull_points.remove(bottom_hull_points[i-1])
                #print(bottom_hull_points)
                #i += 1 # no need to update, python adjusts this - a conveninet coincidence
        except IndexError:
            # this only happens when i is poiting to the last element in the list
            i -= 1
            #continue

        except SameXValue:
            #print('delete ',bottom_hull_points[i-1])
            bottom_hull_points.remove(bottom_hull_points[i-1])
            #i += 1 # no need to update, python adjusts this - a conveninet coincidence


    
    #print('Bottom hull complete')
    return bottom_hull_points
        

def point_slope_line_eval(x1,y1,x2,y2,x):
    try:
        return (y2-y1)/(x2-x1)*(x-x1)+y1
    except ZeroDivisionError:
        raise SameXValue('Two points have the same x value')




print('-------------------------------------------------------')

# Workbook is created 
wb = Workbook()

sizes = [10,10,10,100,100,1000]
count = 1
for e in sizes:
    sheet = wb.add_sheet('Polygon ' + str(count))
    L = [0]*e
    for i in range(0,e):
        x = random.uniform(-e,e)
        y = random.uniform(-e,e)
        L[i] = (x,y)
        sheet.write(i,0,x)
        sheet.write(i,1,y)
    
    sort(L,0,len(L)-1,0)
    L2 = convex_hull(L)
    for i in range(0,len(L2)):
        x,y = L2[i]
        sheet.write(i,3,x)
        sheet.write(i,4,y)
    x,y = L2[0]
    sheet.write(i+1,3,x)
    sheet.write(i+1,4,y)

    count += 1

wb.save('convex_hull.xls')
