from scipy import ndimage
from matplotlib import pyplot as plt
from PIL.Image import frombytes
import cv2
import numpy as np

'''
    Toolkit for image process
    with the method from cv2,plt,np
    个人工具包，对一些需要调用多次函数的
    过程打包，主要用于图像的处理和输出，
    使用的库为cv2,matplotlib,PIL,numpy
'''
cv_series= 0

def cv_show(*from_imgs, name="'L': next, 'A': back, 'E': exit"):
    """ Basic usage:cv_show(cv2_img),
        show a image with default name "Unnamed".
    """
    global cv_series
    cv_series+= 1
    i= 0
    while True:
        cv2.imshow(name + " - " + str(i+cv_series), from_imgs[i])
        if cv2.waitKey(0) == ord('l'):
            i+= 1
            cv2.destroyAllWindows()
        elif cv2.waitKey(0) == ord('a'):
            i-= 1
            cv2.destroyAllWindows()
        elif cv2.waitKey(0) == ord('e'):
            cv2.destroyAllWindows()
            break
        if i>=len(from_imgs):i=0
        elif i<0:i=len(from_imgs)-1


def cv_resize(from_img,max=800):
    """ Basic usage:cv_show(cv2_img),
        the maximum height/width of the image is limited to 800px
        if only has one argument.
    """
    if from_img.shape[0] <= max and from_img.shape[1] <= max:return 1, from_img
    ratio=max/from_img.shape[0] if from_img.shape[0]>from_img.shape[1] else max/from_img.shape[1]
    return ratio, cv2.resize(from_img, None, fx=ratio, fy=ratio)  # resize since image is huge


def cv_BoxPoints(rect):
    """
    """
    box= cv2.boxPoints(rect)
    #box = cv2.cv.BoxPoints(rect)  # for OpenCV 2.x
    box= [np.int0(box)]
    return box


def plt_show(*from_imgs):
    """ Basic usage:plt_show(cv2_img),
        show a image with default name "Unnamed".
    """

    row_a= int(np.sqrt(len(from_imgs)))
    col_a= int(len(from_imgs)/row_a) + len(from_imgs)%row_a
    if row_a>col_a:
        ratio_a= row_a/col_a
        row_b= row_a-1
        col_b= int(len(from_imgs)/row_b) + len(from_imgs)%row_b
        ratio_b= row_b/col_b if row_b>col_b else col_b/row_b
    elif row_a<col_a:
        ratio_a= col_a/row_a
        col_b= col_a-1
        row_b= int(len(from_imgs)/col_b) + len(from_imgs)%col_b
        ratio_b= row_b/col_b if row_b>col_b else col_b/row_b
    else:
        row_b, col_b=row_a, col_a
        ratio_a=ratio_b=1
    row= row_a if ratio_a<ratio_b else row_b
    col= col_a if ratio_a<ratio_b else col_b

    plt_series = 0
    for from_img in from_imgs:
        plt_series+= 1
        plt.subplot(row,col,plt_series)
        plt.title(str(plt_series))
        plt.imshow(from_img)
        #plt.axis('off')
        #plt.tight_layout()
    plt.show()


def bytearray_toimg(*datas,show=1):
    """ Basic usage:bytearray_toimg(np_array),
        convert a numpy array to image and show it
        if the last argument is set to 1 by default or by user.
        This function accept multiple arrays, show
        all of them or return the first one converted.
    """
    if show==1:
        for data in datas:
            frombytes(mode='1', size=data.shape[::-1], data=np.packbits(data, axis=1)).show()
    else:
        for data in datas:
            return frombytes(mode='1',size=data.shape[::-1],data=np.packbits(data,axis=1))


def del_isolatedot(square,nearby_ratio = 1/1000,white_ratio = 0.7,colour_ratio=1):
    """ Basic usage:del_isolatedot(cv2_img),
        find isolated black dots surrounded by white dots
        and fill this area with white,
        notice that cv2_img should be gray
        and both three ratios should be positive integer
        which is less than or equal to 1.

        USELESS BY NOW, but the experience learnt from here is useful.
    """
    square=np.copy(square)
    # black = 0
    white = 255
    nearby = int(max(min(square.shape[0] * nearby_ratio, square.shape[1] * nearby_ratio), 1))
    colournearby=int(max(min(nearby*colour_ratio,nearby),1))
    # the ratio that white pixel should take
    white_value = int(white * (nearby * 2 + 1) ** 2 * white_ratio)
    i = j = 0
    for x in range(nearby, square.shape[0], colournearby * 2):
        for y in range(nearby, square.shape[1], colournearby * 2):
            i += 1
            if np.sum(square[x - nearby:x + nearby + 1, y - nearby:y + nearby + 1]) >= white_value:
                j+=1
                square[x - colournearby:x + colournearby + 1, y - colournearby:y + colournearby + 1] = white
    print(j,"/",i)
    return square



def isCornerTooDark(img, limit=0.8, area=2):
    '''
    If corners of the image that was after thresh_gray-ed
    is too dark, the best solution is to reduce the thresh level.
    '''
    #default (also recommended) one is 1/4
    area=1/(area+2)
    img_x, img_y=img.shape[0], img.shape[1]

    # black = 0
    white = 255
    length_x=int(area*img_x)
    length_y=int(area*img_y)
    #图形说明见f2.png
    #mx^2+ny^2=1
    #numpy解二元一次方程
    known_pos=[[img_x, img_y - length_y],   # 相邻的两个交点
               [img_x - length_x, img_y]]
    m, n=np.linalg.solve([[known_pos[0][0]**2, known_pos[0][1]**2],
                          [known_pos[1][0]**2, known_pos[1][1]**2]],
                         [1,1])*5
    #通过同时平移椭圆和矩形，使得矩形的左下端位于(0,0)得到的
    #函数计算得到椭圆区域，并反转取值，得到黑色遮罩区域
    #但是注意遮罩True表示区域
    outside_ellipse=np.fromfunction(lambda x,y :m*(x-img_x/2)**2+n*(y-img_y/2)**2<=1,
                                    [img_x, img_y])
    #prints(img_x,img_y,m,n,outside_ellipse)

    #不同过滤值下的图片
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert to grayscale
    thresh_gray=[]
    corner_area=[]
    j=0
    #150~190
    for i in range(160,200,10):
        retval, temp = cv2.threshold(gray, thresh=i, maxval=white, type=cv2.THRESH_BINARY)
        thresh_gray.append(temp)
        corner_area.append(np.ma.array(thresh_gray[j],mask=outside_ellipse))
        prints(corner_area[j].mean()/white)
        j+=1

    plt_show(*corner_area)






def prints(*datas):
    for data in datas:
        print(data)
        print("="*20)


def corner_points(points):
    """
    Transform a random quadrilateral to a rectangle
    Accept a four-points array generated by cv2.approxPolyDP
    and return the arranged one with same format.

    min--> 0-a-1
           d\   \b
             3-c-2 <--max
    """
    distances=[cv2.norm(points[x]) for x in range(0, 4)]
    transform_distance=[]
    points_index=[0, 1, 2, 3]
    arrange_points_index=[0]*4

    arrange_points_index[0]=distances.index(min(distances))  # find the "0" point
    arrange_points_index[2]=distances.index(max(distances))  # find the "2" point
    points_index.remove(arrange_points_index[0])
    points_index.remove(arrange_points_index[2])
    if np.absolute(points[points_index[0]][0][0]-points[distances.index(min(distances))][0][0]) > \
            np.absolute(points[points_index[1]][0][0]-points[distances.index(min(distances))][0][0]):
        # find the "1" point <-- points_index[0], "3" point <-- points_index[1]
        arrange_points_index[1]=points_index[0]
        arrange_points_index[3]=points_index[1]
    else:
        arrange_points_index[3]=points_index[0]
        arrange_points_index[1]=points_index[1]

    line_length=[cv2.norm(points[arrange_points_index[0]][0],points[arrange_points_index[1]][0]),  # 0-a-1
                cv2.norm(points[arrange_points_index[1]][0], points[arrange_points_index[2]][0]),  # 1-b-2
                cv2.norm(points[arrange_points_index[2]][0], points[arrange_points_index[3]][0]),  # 2-c-3
                cv2.norm(points[arrange_points_index[3]][0], points[arrange_points_index[0]][0])]  # 3-d-0
    test= cv2.norm(points[arrange_points_index[3]][0], points[arrange_points_index[0]][0])
    x= int(line_length[0] if line_length[0] > line_length[2] else line_length[2])
    y= int(line_length[1] if line_length[1] > line_length[3] else line_length[3])

    # original format is counterclockwise
    transform_distance.append([[0, 0]])
    transform_distance.append([[0, y]])
    transform_distance.append([[x, y]])
    transform_distance.append([[x, 0]])

    return np.array(transform_distance)

