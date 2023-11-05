import time

from py3dbp.agents.bin import Bin
from py3dbp.agents.item import Item
from py3dbp.agents.packer import Packer
from py3dbp.agents.painter import Painter

start = time.time()

'''

Check stability on item - first rule
1. Define a support ratio, if the ratio below the support surface does not exceed this ratio, compare the second rule. 

'''

# init packing function
packer = Packer()
#  init bin_
box = Bin('example5', (5, 4, 3), 100, 0, 0)
#  add item
# Item('item part_no', (W,H,D), Weight, Packing Priority level, load bear, Upside down or not , 'item color')
packer.add_bin(box)
packer.add_item(
    Item(
        part_no='Box-3',
        name='test',
        typeof='cube',
        dims=(2, 5, 2), weight=1, level=1, load_bear=100,
        updown=True, color='pink'
    )
)
packer.add_item(
    Item(
        part_no='Box-3',
        name='test',
        typeof='cube',
        dims=(2, 3, 2), weight=1, level=2, load_bear=100,
        updown=True,
        color='pink'
    )
)  # Try switching dim=(2, 2, 2) and (2, 3, 2) to compare the results
packer.add_item(
    Item(
        part_no='Box-4',
        name='test',
        typeof='cube',
        dims=(5, 4, 1), weight=1, level=3, load_bear=100,
        updown=True,
        color='brown'
    )
)

# calculate packing 
packer.pack(
    bigger_first=True,
    distribute_items=False,
    fix_point=True,
    check_stable=True,
    support_surface_ratio=0.75,
    number_of_decimals=0
)

# put order
packer.put_order()

# print result
for b in packer.bins:
    volume = b.width * b.height * b.depth
    print(":::::::::::", b.string())

    print("FITTED ITEMS:")
    volume_t = 0
    volume_f = 0
    unfitted_name = ''
    for item in b.items:
        print("part_no: ", item.part_no)
        print("color: ", item.color)
        print("position: ", item.position)
        print("rotation type: ", item.rotation_type)
        print("W*H*D: ", str(item.width) + '*' + str(item.height) + '*' + str(item.depth))
        print("volume: ", float(item.width) * float(item.height) * float(item.depth))
        print("weight: ", float(item.weight))
        volume_t += float(item.width) * float(item.height) * float(item.depth)
        print("***************************************************")
    print("***************************************************")
    print("UNFITTED ITEMS:")
    for item in b.unfitted_items:
        print("part_no : ", item.part_no)
        print("color : ", item.color)
        print("W*H*D : ", str(item.width) + '*' + str(item.height) + '*' + str(item.depth))
        print("volume : ", float(item.width) * float(item.height) * float(item.depth))
        print("weight : ", float(item.weight))
        volume_f += float(item.width) * float(item.height) * float(item.depth)
        unfitted_name += '{},'.format(item.part_no)
        print("***************************************************")
    print("***************************************************")
    print('space utilization : {}%'.format(round(volume_t / float(volume) * 100, 2)))
    print('residual volume: ', float(volume) - volume_t)
    print('unpack item: ', unfitted_name)
    print('unpack item volume: ', volume_f)
    print("gravity distribution: ", b.gravity)
    stop = time.time()
    print('used time : ', stop - start)

    # draw results
    painter = Painter(b)
    fig = painter.plot_box_and_items(
        title=b.part_no,
        alpha=0.8,
        write_num=False,
        fontsize=10
    )

fig.show()
