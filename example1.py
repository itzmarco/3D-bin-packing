import time

from py3dbp.agents.bin import Bin
from py3dbp.agents.item import Item
from py3dbp.agents.packer import Packer
from py3dbp.agents.painter import Painter

start = time.time()

'''

This example is used to demonstrate the mixed packing of cube and cylinder.

'''

# init packing function
packer = Packer()
#  init bin_
box = Bin('example1', (5.6875, 10.75, 15.0), 70.0, 0, 0)
packer.add_bin(box)
#  add item
packer.add_item(Item('50g [powder 1]', 'test', 'cube', (2, 2, 4), 1, 1, 100, True, 'red'))
packer.add_item(Item('50g [powder 2]', 'test', 'cube', (2, 2, 4), 2, 1, 100, True, 'blue'))
packer.add_item(Item('50g [powder 3]', 'test', 'cube', (2, 2, 4), 3, 1, 100, True, 'gray'))
packer.add_item(Item('50g [powder 4]', 'test', 'cube', (2, 2, 4), 3, 1, 100, True, 'orange'))
packer.add_item(Item('50g [powder 5]', 'test', 'cylinder', (2, 2, 4), 3, 1, 100, True, 'lawngreen'))
packer.add_item(Item('50g [powder 6]', 'test', 'cylinder', (2, 2, 4), 3, 1, 100, True, 'purple'))
packer.add_item(Item('50g [powder 7]', 'test', 'cylinder', (1, 1, 5), 3, 1, 100, True, 'yellow'))
packer.add_item(Item('250g [powder 8]', 'test', 'cylinder', (4, 4, 2), 4, 1, 100, True, 'pink'))
packer.add_item(Item('250g [powder 9]', 'test', 'cylinder', (4, 4, 2), 5, 1, 100, True, 'brown'))
packer.add_item(Item('250g [powder 10]', 'test', 'cube', (4, 4, 2), 6, 1, 100, True, 'cyan'))
packer.add_item(Item('250g [powder 11]', 'test', 'cylinder', (4, 4, 2), 7, 1, 100, True, 'olive'))
packer.add_item(Item('250g [powder 12]', 'test', 'cylinder', (4, 4, 2), 8, 1, 100, True, 'darkgreen'))
packer.add_item(Item('250g [powder 13]', 'test', 'cube', (4, 4, 2), 9, 1, 100, True, 'orange'))

# calculate packing 
packer.pack(
    bigger_first=True,
    distribute_items=False,
    fix_point=True,
    check_stable=True,
    support_surface_ratio=0.75,
    number_of_decimals=0
)

# print result
b = packer.bins[0]
volume = b.width * b.height * b.depth
print(":::::::::::", b.string())

print("FITTED ITEMS:")
volume_t = 0
volume_f = 0
unfitted_name = ''
for item in b.items:
    print("part_no : ", item.part_no)
    print("color : ", item.color)
    print("position : ", item.position)
    print("rotation type : ", item.rotation_type)
    print("W*H*D : ", str(item.width) + '*' + str(item.height) + '*' + str(item.depth))
    print("volume : ", float(item.width) * float(item.height) * float(item.depth))
    print("weight : ", float(item.weight))
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
print('residual volumn : ', float(volume) - volume_t)
print('unpack item : ', unfitted_name)
print('unpack item volumn : ', volume_f)
print("gravity distribution : ", b.gravity)
stop = time.time()
print('used time : ', stop - start)

# draw results
painter = Painter(b)
fig = painter.plot_box_and_items(
    title=b.part_no,
    alpha=0.2,
    write_num=False,
    fontsize=5
)
fig.show()
