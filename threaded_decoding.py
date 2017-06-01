from WebcamVideoStream import *
from PIL import Image
import textwrap
from image_decoding import *
import pygame, sys
from pygame.locals import *
import time
import cv2

# get the current time in millisecont
current_time = lambda: int(round(time.time() * 1000))

def take_shots(capture_interval=110, n_tons=2, coding=0, rows=3, columns=5):
    N_COLORS = n_tons**3
    pygame.init()
    pygame.mouse.set_visible(False)
    
    RESOLUTION = (1280, 720)
    USABLE_SIZE = (RESOLUTION[0]//3, RESOLUTION[1]//3)
    USABLE_RECT = USABLE_SIZE*2
    CROP = (USABLE_SIZE[1], 2*USABLE_SIZE[1], USABLE_SIZE[0], 2*USABLE_SIZE[0])

    cam = WebcamVideoStream(src=0, width=RESOLUTION[0], height=RESOLUTION[1]).start()
    bad_images = 340//capture_interval
        
    display = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    FILENAME = 'shots/pic'
    
    preparation = 1
    run = 1
    grand_final = 1

    while preparation:
        # Display preview to aim screen
        cv2_im = cam.read()
        cv2_im = cv2.cvtColor(cv2_im,cv2.COLOR_BGR2RGB)
        cv2_im = cv2_im[CROP[0]:CROP[1],CROP[2]:CROP[3]]
        PIL_image = Image.fromarray(cv2_im)
        string_image = PIL_image.tobytes('raw', "RGB")
        pygame_image = pygame.image.fromstring(string_image, USABLE_SIZE, "RGB")
        display.blit(pygame_image, USABLE_SIZE)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_s:
                pygame.time.delay(1000)# you have 1 sec to remove hands of canal
                pygame.time.set_timer(USEREVENT, capture_interval)
                preparation = 0
                display.fill((0,0,0))
                pygame.display.flip()
            if event.type == KEYDOWN and event.key == K_q:
                preparation = 0
                run = 0
                cam.stop()
                pygame.quit()

    images = []
    times = []

    previous_time = 0

    while run:
        time = current_time()
        loop_time = time % capture_interval

        if loop_time < previous_time:
            image = cam.read()
            images.append(image)
            times.append(time)
        previous_time = loop_time

        for event in pygame.event.get():
            if (event.type == KEYDOWN):
                run = 0
                cam.stop()

    # add every image into a PIL list
    PIL_images = []
    for image in images[bad_images:]:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image[CROP[0]:CROP[1],CROP[2]:CROP[3]]
        PIL_image = Image.fromarray(image, 'RGB')
        PIL_images.append(PIL_image)
    
    try:
        # decode the images into a string
        decoded_text = decodeImage(PIL_images, N_COLORS, coding, rows, columns)

        # save the decoded message in a file
        with open("output.txt", "w") as text_file:
            print(decoded_text, text_file)
    
        # print the decoded message in terminal
        print(decoded_text)

        # Display the decoded message in the screen as soon as it is decoded
        text_to_display =  decoded_text.replace('\r', ' ').replace('\n', ' ')
        lines = textwrap.wrap(text_to_display, 100)
        display.fill((255, 255, 255))
        myfont = pygame.font.SysFont("ubuntu", 22, True)
        text_rect = pygame.Rect(50, 50, 50, 1500)
        while lines:
            line = lines[0]
            lines.pop(0)

            label = myfont.render(line, 10, (41, 83, 80))
            display.blit(label, text_rect)
            text_rect.centery += 30
        pygame.display.flip()

        # displays the message until we push on "q"
        while grand_final:
            for event in pygame.event.get():
                if (event.type == KEYDOWN and event.key == K_q):
                    grand_final = 0

    except Exception as e:
        for i in range(len(PIL_images)):
            PIL_images[i].save(FILENAME+str(i+1)+'.png')
            if(i != 0):
                print("Interval", str(i-1)+"-"+str(i)+": "+str(times[i]-times[i-1]))
        print("Error:", e)
    pygame.quit()
    
config_safe = (110, 2, 10, 3, 5)
config1 = (110, 2, 30, 4, 6)
config_test = (40, 2, 30, 4, 6)

# take_shots(capture_interval=110, n_tons=2, coding=0, rows=3, columns=5)      
take_shots(*config_test)
