from . import metricsobj as mo
from . import datecheck as dc
from . import mapping as mp
from . import colcomp as cc
import datetime as dtt
# import threading
# import time
#
# 
# def loading_dots(f,loading_text='Loading'):
#     thread = threading.Thread(target=f)
#     thread.start()
#     
#     dot_count = 0
#     while thread.is_alive():
#         dots = '.'*(dot_count+1)
#         print('%s%s%s' %(loading_text,dots,' '*3),end='\r')
#         dot_count = (dot_count + 1) % 3
#         time.sleep(.1)
#     thread.join()
#     print('%s%s Done' %(loading_text,'.'*3))

# def loading_dots(f,loading_text='Loading'):
#     thread = threading.Thread(target=f)
#     thread.start()
#     
#     print('%s' %loading_text,end=''),
#     while thread.is_alive():
#         print('.',end=''),
#         time.sleep(1)
#     thread.join()
#     print(' Done')
def panel_selection():
    while True:
        panel = input("""Please select a panel:
1. BevAl
2. Non-Flash
3. WIP
(Defaults to BevAl)\n""") or '1'
        if (panel == '1' or panel=='BevAl'):
            panel = 'Beval'
            break
        elif (panel == '2' or panel=='Non-Flash'):
            panel = 'NonFlash'
            break
        else:
            print('Unrecognized panel, please choose another.\n')
            continue
    mcap_path = [0,0]
    mcap_path[0] = 'Z:\\'+dtt.datetime.today().strftime('%m%d%Y_QC_Completed_') + panel + '.txt'
    mcap_path[1] = panel
    return mcap_path