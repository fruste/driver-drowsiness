import os
import datetime
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from IPython.display import Markdown, display

def load_blinks(subject, cond):
    path = '../eye_openess_features/' + subject + '/' + cond + '/'
    all_status_rates = []
    all_wrong_frames = []

    lst = os.listdir(path)
    num_parts = int(len(lst) / 2)
    for num in range(1, num_parts+1):
        status_rates = list(np.load(path + "status_rates_part" + str(num) + ".npy"))
        wrong_frames = list(np.load(path + "wrong_frames_part" + str(num) + ".npy"))

        all_status_rates = all_status_rates + status_rates
        all_wrong_frames = all_wrong_frames + wrong_frames
    return all_status_rates, all_wrong_frames

# Finds eye-blinks given a sequence of values and a treshhold.
def find_blinks(values, treshhold):
    blink = False
    blinks = []
    blink_count = 0
    for i, val in enumerate(values):
        if val < treshhold:
            if blink == False:
                blink_count +=1
                start = i
            blink = True
        else:
            if blink == True:
                end = i - 1
                #calculate duration of blink, and include in tuple
                duration = end - start + 1
                blinks.append((start, end, duration))
                #print("Blinking period: " + str(start) + " - " + str(end))
            blink = False
    return blinks, blink_count

# Extracts features in a segment from given blinks
def blinks_segment(blink_starts, blink_durs, video_len, segment_len):
    # the amount of frames at the end that are not taken into account
    rest = video_len % segment_len
    num_frames = video_len - rest
    blink_counts = []
    average_durs = []
    
    blink_count = 0
    dur_count = 0
    
    # a blink is counted to a segment,when the blink starts in that segment
    for frame in range(num_frames):
        # if frame % 30000 == 0:
        #     print(frame)
        # only happens at the end of a segment
        if frame % segment_len == 0 and frame != 0:
            #print('new_segment', frame)
            blink_counts.append(blink_count)
            if dur_count > 0:
                avg_dur = dur_count / blink_count
            else:
                avg_dur = 0
            average_durs.append(avg_dur)
            blink_count = 0 
            dur_count = 0
        # happens when a blink starts
        if frame in blink_starts:
            frame_index = blink_starts.index(frame)
            blink_count += 1
            dur_count += blink_durs[frame_index]
            
    return blink_counts, average_durs

def run_analysis(status_rates, wrong_frames, treshhold, segment_length):
    blinks, count = find_blinks(status_rates, treshhold)
    #print("Number of blinks: ", len(blinks))

    blink_starts = list(np.array(blinks)[:,0])
    blink_durs = list(np.array(blinks)[:,2])

    blink_counts, average_durs = blinks_segment(blink_starts, blink_durs, len(status_rates), segment_length)
    print("Number of segments", len(blink_counts))
    #print("Mean blink count per segment", np.mean(blink_counts))
    #print("Mean blink duration per segment", np.mean(average_durs))
    return blink_counts, average_durs