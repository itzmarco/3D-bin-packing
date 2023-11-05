import time

from py3dbp.agents.bin import Bin
from py3dbp.agents.item import Item
from py3dbp.agents.packer import Packer
from py3dbp.agents.painter import Painter

start = time.time()

'''

This example can be used to compare the fix_point function with and without the fix_point function.

'''

# init packing function
packer = Packer()

# Evergreen Real Container (20ft Steel Dry Cargo Container)
# Unit cm/kg
box = Bin(
    part_no='example0',
    dim=(589.8, 243.8, 259.1),
    max_weight=28080,
    corner=15,
    put_type=0
)

packer.add_bin(box)

# dyson DC34 (20.5 * 11.5 * 32.2 ,1.33kg)
# 64 pcs per case ,  82 * 46 * 170 (85.12)
for i in range(5): 
    packer.add_item(Item(
        part_no='Dyson DC34 Animal{}'.format(str(i + 1)),
        name='Dyson', 
        typeof='cube',
        dims=(170, 82, 46),
        weight=85.12,
        level=1,
        load_bear=100,
        updown=True,
        color='#FF0000')
    )

# washing machine (85 * 60 *60 ,10 kG)
# 1 pcs per case, 85 * 60 *60 (10)
for i in range(10):
    packer.add_item(Item(
        part_no='wash{}'.format(str(i + 1)),
        name='wash',
        typeof='cube',
        dims=(85, 60, 60),
        weight=10,
        level=1,
        load_bear=100,
        updown=True,
        color='#FFFF37'
    ))

# 42U standard cabinet (60 * 80 * 200 , 80 kg)
# one per box, 60 * 80 * 200 (80)
for i in range(5):
    packer.add_item(Item(
        part_no='Cabinet{}'.format(str(i + 1)),
        name='cabinet',
        typeof='cube',
        dims=(60, 80, 200),
        weight=80,
        level=1,
        load_bear=100,
        updown=True,
        color='#842B00')
    )

# Server (70 * 100 * 30 , 20 kg) 
# one per box , 70 * 100 * 30 (20)
for i in range(10):
    packer.add_item(Item(
        part_no='Server{}'.format(str(i + 1)),
        name='server',
        typeof='cube',
        dims=(70, 100, 30),
        weight=20,
        level=1,
        load_bear=100,
        updown=True,
        color='#0000E3')
    )


# calculate packing
packer.pack(
    bigger_first=True,
    distribute_items=False,
    fix_point=False,  # Try switching fix_point=True/False to compare the results
    check_stable=False,
    support_surface_ratio=0.75,
    number_of_decimals=0
)

# print result
for box in packer.bins:

    volume = box.width * box.height * box.depth
    print(":::::::::::", box.string())

    print("FITTED ITEMS:")
    volume_t = 0
    volume_f = 0
    unfitted_name = ''

    # '''
    for item in box.items:
        print("part_no : ", item.part_no)
        print("type : ", item.name)
        print("color : ", item.color)
        print("position : ", item.position)
        print("rotation type : ", item.rotation_type)
        print("W*H*D : ", str(item.width) + '*' + str(item.height) + '*' + str(item.depth))
        print("volume : ", float(item.width) * float(item.height) * float(item.depth))
        print("weight : ", float(item.weight))
        volume_t += float(item.width) * float(item.height) * float(item.depth)
        print("***************************************************")
    print("***************************************************")
    # '''
    print("UNFITTED ITEMS:")
    for item in box.unfitted_items:
        print("part_no : ", item.part_no)
        print("type : ", item.name)
        print("color : ", item.color)
        print("W*H*D : ", str(item.width) + '*' + str(item.height) + '*' + str(item.depth))
        print("volume : ", float(item.width) * float(item.height) * float(item.depth))
        print("weight : ", float(item.weight))
        volume_f += float(item.width) * float(item.height) * float(item.depth)
        unfitted_name += '{},'.format(item.part_no)
        print("***************************************************")
    print("***************************************************")
    print('space utilization : {}%'.format(round(volume_t / float(volume) * 100, 2)))
    print('residual volume : ', float(volume) - volume_t)
    print('unpack item : ', unfitted_name)
    print('unpack item volume : ', volume_f)
    print("gravity distribution : ", box.gravity)
    # '''
    stop = time.time()
    print('used time : ', stop - start)

    # draw results
    painter = Painter(box)
    fig = painter.plot_box_and_items(
        title=box.part_no,
        alpha=0.2,
        write_num=True,
        fontsize=10
    )

fig.show()
