from init import *
from draw import *
import time

t1 = time.perf_counter()
res_conn = draw_image(img, res, conns, pins, N, n, m, L_min)
t2 = time.perf_counter()

print(f'Finished in {t2-t1} seconds')
