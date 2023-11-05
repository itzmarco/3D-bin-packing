from ..constants import RotationType
from ..auxiliary_methods import intersect, set_decimal_places
from .item import Item
import numpy as np

import copy

DEFAULT_NUMBER_OF_DECIMALS = 0
ORIGIN = [0, 0, 0]


class Bin:

	def __init__(self, part_no, dim, max_weight, corner=0, put_type=1):
		""" """
		self.part_no = part_no
		self.width = dim[0]
		self.height = dim[1]
		self.depth = dim[2]
		self.max_weight = max_weight
		self.corner = corner
		self.items = []
		self.fit_items = np.array([[0, dim[0], 0, dim[1], 0, 0]])
		self.unfitted_items = []
		self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS
		self.fix_point = False
		self.check_stable = False
		self.support_surface_ratio = 0
		self.put_type = put_type
		# used to put gravity distribution
		self.gravity = []

	def format_numbers(self, number_of_decimals):
		self.width = set_decimal_places(self.width, number_of_decimals)
		self.height = set_decimal_places(self.height, number_of_decimals)
		self.depth = set_decimal_places(self.depth, number_of_decimals)
		self.max_weight = set_decimal_places(self.max_weight, number_of_decimals)
		self.number_of_decimals = number_of_decimals

	def string(self):
		return "%s(%sx%sx%s, max_weight:%s) vol(%s)" % (
			self.part_no, self.width, self.height, self.depth, self.max_weight,
			self.get_volume()
		)

	def get_volume(self):
		return set_decimal_places(
			self.width * self.height * self.depth, self.number_of_decimals
		)

	def get_total_weight(self):
		total_weight = 0

		for item in self.items:
			total_weight += item.weight

		return set_decimal_places(total_weight, self.number_of_decimals)

	def put_item(self, item, pivot):
		""" put item in bin_ """
		fit = False
		valid_item_position = item.position
		item.position = pivot
		rotate = RotationType.ALL if item.updown else RotationType.not_updown
		for r in range(0, len(rotate)):
			item.rotation_type = r
			dimension = item.get_dimension()
			if (
					self.width < pivot[0] + dimension[0] or
					self.height < pivot[1] + dimension[1] or
					self.depth < pivot[2] + dimension[2]
			):
				continue

			fit = True

			for current_item_in_bin in self.items:
				if intersect(current_item_in_bin, item):
					fit = False
					break

			if fit:
				# cal total weight
				if self.get_total_weight() + item.weight > self.max_weight:
					fit = False
					return fit

				# fix point float prob
				if self.fix_point:

					w, h, d = dimension
					x, y, z = float(pivot[0]), float(pivot[1]), float(pivot[2])

					for _ in range(3):
						# fix height
						y = self.check_height([x, x + float(w), y, y + float(h), z, z + float(d)])
						# fix width
						x = self.check_width([x, x + float(w), y, y + float(h), z, z + float(d)])
						# fix depth
						z = self.check_depth([x, x + float(w), y, y + float(h), z, z + float(d)])

					# check stability on item
					# rule :
					# 1. Define a support ratio, if the ratio below the support surface does not exceed this ratio,
					#       compare the second rule.
					# 2. If there is no support under any vertices of the bottom of the item, then fit = False.
					if self.check_stable:
						# Calculate the surface area of the item.
						item_area_lower = int(dimension[0] * dimension[1])
						# Calculate the surface area of the underlying support.
						support_area_upper = 0
						for i in self.fit_items:
							# Verify that the lower support surface area is greater than the upper support surface
							# area * support_surface_ratio.
							if z == i[5]:
								x1 = set([j for j in range(int(x), int(x + int(w)))]) \
								     & set([j for j in range(int(i[0]), int(i[1]))])
								x2 = set([j for j in range(int(y), int(y + int(h)))]) \
								     & set([j for j in range(int(i[2]), int(i[3]))])
								area = len(x1) * len(x2)
								support_area_upper += area

						# If not, get four vertices of the bottom of the item.
						if support_area_upper / item_area_lower < self.support_surface_ratio:
							four_vertices = [[x, y], [x + float(w), y], [x, y + float(h)], [x + float(w), y + float(h)]]
							#  If any vertices is not supported, fit = False.
							c = [False, False, False, False]
							for i in self.fit_items:
								if z == i[5]:
									for jdx, j in enumerate(four_vertices):
										if (i[0] <= j[0] <= i[1]) and (i[2] <= j[1] <= i[3]):
											c[jdx] = True
							if not all(c):
								item.position = valid_item_position
								fit = False
								return fit

					self.fit_items = np.append(
						self.fit_items,
						np.array([[x, x + float(w), y, y + float(h), z, z + float(d)]]),
						axis=0
					)
					item.position = [set_decimal_places(x), set_decimal_places(y), set_decimal_places(z)]

				if fit:
					self.items.append(copy.deepcopy(item))

			else:
				item.position = valid_item_position

			return fit

		else:
			item.position = valid_item_position

		return fit

	def check_depth(self, unfix_point):
		""" fix item position z """
		z_ = [[0, 0], [float(self.depth), float(self.depth)]]
		for j in self.fit_items:
			# create x set
			x_bottom = set([i for i in range(int(j[0]), int(j[1]))])
			x_top = set([i for i in range(int(unfix_point[0]), int(unfix_point[1]))])
			# create y set
			y_bottom = set([i for i in range(int(j[2]), int(j[3]))])
			y_top = set([i for i in range(int(unfix_point[2]), int(unfix_point[3]))])
			# find intersection on x set and y set.
			if len(x_bottom & x_top) and len(y_bottom & y_top):
				z_.append([float(j[4]), float(j[5])])
		top_depth = unfix_point[5] - unfix_point[4]
		# find diff set on z_.
		z_ = sorted(z_, key=lambda z_: z_[1])
		for j in range(len(z_) - 1):
			if z_[j + 1][0] - z_[j][1] >= top_depth:
				return z_[j][1]
		return unfix_point[4]

	def check_width(self, unfix_point):
		""" fix item position x """
		x_ = [[0, 0], [float(self.width), float(self.width)]]
		for j in self.fit_items:
			# create z set
			z_bottom = set([i for i in range(int(j[4]), int(j[5]))])
			z_top = set([i for i in range(int(unfix_point[4]), int(unfix_point[5]))])
			# create y set
			y_bottom = set([i for i in range(int(j[2]), int(j[3]))])
			y_top = set([i for i in range(int(unfix_point[2]), int(unfix_point[3]))])
			# find intersection on z set and y set.
			if len(z_bottom & z_top) and len(y_bottom & y_top):
				x_.append([float(j[0]), float(j[1])])
		top_width = unfix_point[1] - unfix_point[0]
		# find diff set on x_bottom and x_top.
		x_ = sorted(x_, key=lambda x_: x_[1])
		for j in range(len(x_) - 1):
			if x_[j + 1][0] - x_[j][1] >= top_width:
				return x_[j][1]
		return unfix_point[0]

	def check_height(self, unfix_point):
		"""fix item position y """
		y_ = [[0, 0], [float(self.height), float(self.height)]]
		for j in self.fit_items:
			# create x set
			x_bottom = set([i for i in range(int(j[0]), int(j[1]))])
			x_top = set([i for i in range(int(unfix_point[0]), int(unfix_point[1]))])
			# create z set
			z_bottom = set([i for i in range(int(j[4]), int(j[5]))])
			z_top = set([i for i in range(int(unfix_point[4]), int(unfix_point[5]))])
			# find intersection on x set and z set.
			if len(x_bottom & x_top) and len(z_bottom & z_top):
				y_.append([float(j[2]), float(j[3])])
		top_height = unfix_point[3] - unfix_point[2]
		# find diff set on y_bottom and y_top.
		y_ = sorted(y_, key=lambda y_: y_[1])
		for j in range(len(y_) - 1):
			if y_[j + 1][0] - y_[j][1] >= top_height:
				return y_[j][1]

		return unfix_point[2]

	def add_corner(self):
		"""add container corner"""
		if self.corner:
			corner = set_decimal_places(self.corner)
			corner_list = []
			for i in range(8):
				a = Item(
					part_no='corner{}'.format(i),
					name='corner',
					typeof='cube',
					dims=(corner, corner, corner),
					weight=0,
					level=0,
					load_bear=0,
					updown=True,
					color='#000000')

				corner_list.append(a)
			return corner_list

	def put_corner(self, info, item):
		"""put corner in bin_ """
		# fit = False
		x = set_decimal_places(self.width - self.corner)
		y = set_decimal_places(self.height - self.corner)
		z = set_decimal_places(self.depth - self.corner)
		pos = [ORIGIN, [0, 0, z], [0, y, z], [0, y, 0], [x, y, 0], [x, 0, 0], [x, 0, z], [x, y, z]]
		item.position = pos[info]
		self.items.append(item)

		corner = [
			float(item.position[0]),
			float(item.position[0]) + float(self.corner), float(item.position[1]),
			float(item.position[1]) + float(self.corner), float(item.position[2]),
			float(item.position[2]) + float(self.corner)
		]

		self.fit_items = np.append(self.fit_items, np.array([corner]), axis=0)
		return

	def clear_bin(self):
		"""clear item which in bin_"""
		self.items = []
		self.fit_items = np.array(
			[
				[0, self.width, 0, self.height, 0, 0]
			]
		)