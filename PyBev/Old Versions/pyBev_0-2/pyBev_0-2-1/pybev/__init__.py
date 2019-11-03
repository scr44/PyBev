from . import metricsobj
from . import datecheck
from . import mapping
from . import colcomp
import threading
import time
    
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