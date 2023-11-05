from ..constants import Axis
import numpy as np

import copy

DEFAULT_NUMBER_OF_DECIMALS = 0
ORIGIN = [0, 0, 0]


class Packer:

	def __init__(self):
		self.bins = []
		self.items = []
		self.unfit_items = []
		self.total_items = 0
		self.binding = []

	# self.apex = []

	def add_bin(self, bin_):
		return self.bins.append(bin_)

	def add_item(self, item):
		self.total_items = len(self.items) + 1
		return self.items.append(item)

	@staticmethod
	def pack_2_bin(
			bin_,
			item,
			fix_point,
			check_stable,
			support_surface_ratio
	):
		""" pack item to bin_ """
		fitted = False
		bin_.fix_point = fix_point
		bin_.check_stable = check_stable
		bin_.support_surface_ratio = support_surface_ratio

		# first put item on (0,0,0) , if corner exist ,first add corner in box.
		if bin_.corner and not bin_.items:
			corner_lst = bin_.add_corner()
			for i, ci in enumerate(corner_lst):
				bin_.put_corner(i, ci)

		elif not bin_.items:
			response = bin_.put_item(item, item.position)

			if not response:
				bin_.unfitted_items.append(item)
			return

		for axis in range(0, 3):
			items_in_bin = bin_.items
			for ib in items_in_bin:
				pivot = [0, 0, 0]
				w, h, d = ib.get_dimension()
				if axis == Axis.WIDTH:
					pivot = [ib.position[0] + w, ib.position[1], ib.position[2]]
				elif axis == Axis.HEIGHT:
					pivot = [ib.position[0], ib.position[1] + h, ib.position[2]]
				elif axis == Axis.DEPTH:
					pivot = [ib.position[0], ib.position[1], ib.position[2] + d]

				if bin_.put_item(item, pivot):
					fitted = True
					break
			if fitted:
				break
		if not fitted:
			bin_.unfitted_items.append(item)

	def sort_binding(self):
		""" sorted by binding"""
		b, front, back = [], [], []
		for i, bi in enumerate(self.binding):
			b.append([])
			for item in self.items:
				if item.name in bi:
					b[i].append(item)
				elif item.name not in self.binding:
					if len(b[0]) == 0 and item not in front:
						front.append(item)
					elif item not in back and item not in front:
						back.append(item)

		min_c = len(min(b, key=len))

		sort_bind = []
		for i in range(min_c):
			for bj in b:
				sort_bind.append(bj[i])

		for i in b:
			for j in i:
				if j not in sort_bind:
					self.unfit_items.append(j)

		self.items = front + sort_bind + back

	def put_order(self):
		"""Arrange the order of items"""
		for i in self.bins:
			# open-top container
			if i.put_type == 2:
				i.items.sort(key=lambda item: item.position[0], reverse=False)
				i.items.sort(key=lambda item: item.position[1], reverse=False)
				i.items.sort(key=lambda item: item.position[2], reverse=False)
			# general container
			elif i.put_type == 1:
				i.items.sort(key=lambda item: item.position[1], reverse=False)
				i.items.sort(key=lambda item: item.position[2], reverse=False)
				i.items.sort(key=lambda item: item.position[0], reverse=False)
			else:
				pass
		return

	@staticmethod
	def gravity_center(bin_):
		"""
		Deviation Of Cargo gravity distribution
		"""
		w = int(bin_.width)
		h = int(bin_.height)

		area1 = [set(range(0, w // 2 + 1)), set(range(0, h // 2 + 1)), 0]
		area2 = [set(range(w // 2 + 1, w + 1)), set(range(0, h // 2 + 1)), 0]
		area3 = [set(range(0, w // 2 + 1)), set(range(h // 2 + 1, h + 1)), 0]
		area4 = [set(range(w // 2 + 1, w + 1)), set(range(h // 2 + 1, h + 1)), 0]
		area = [area1, area2, area3, area4]

		for i in bin_.items:
			x_st, y_st = map(int, i.position[:2])
			x_ed, y_ed = x_st, y_st
			if i.rotation_type == 0:
				x_ed += i.width
				y_ed += i.height
			elif i.rotation_type == 1:
				x_ed += i.height
				y_ed += i.width
			elif i.rotation_type == 2:
				x_ed += i.height
				y_ed += i.depth
			elif i.rotation_type == 3:
				x_ed += i.depth
				y_ed += + i.height
			elif i.rotation_type == 4:
				x_ed += + i.depth
				y_ed += + i.width
			elif i.rotation_type == 5:
				x_ed += i.width
				y_ed += i.depth

			x_set = set(range(x_st, int(x_ed) + 1))
			y_set = set(range(y_st, int(y_ed) + 1))

			# cal gravity distribution
			for j, aj in enumerate(area):
				if x_set.issubset(aj[0]) and y_set.issubset(aj[1]):
					aj[2] += int(i.weight)
					break
				# include x and !include y
				elif x_set.issubset(aj[0]) and (not y_set.issubset(aj[1])) and len(y_set & aj[1]):
					y = len(y_set & aj[1]) / (y_ed - y_st) * int(i.weight)
					aj[2] += y
					if j >= 2:
						area[j - 2][2] += (int(i.weight) - x)
					else:
						area[j + 2][2] += (int(i.weight) - y)
					break
				# include y and !include x
				elif (not x_set.issubset(aj[0])) and y_set.issubset(aj[1]) and len(x_set & aj[0]):
					x = len(x_set & aj[0]) / (x_ed - x_st) * int(i.weight)
					area[j][2] += x
					if j >= 2:
						area[j - 2][2] += (int(i.weight) - x)
					else:
						area[j + 2][2] += (int(i.weight) - x)
					break
				# !include x and !include y
				elif (not x_set.issubset(aj[0])) and (not y_set.issubset(aj[1])) \
						and len(y_set & aj[1]) and len(x_set & aj[0]):
					all_ = (y_ed - y_st) * (x_ed - x_st)
					y = len(y_set & area[0][1])
					y_2 = y_ed - y_st - y
					x = len(x_set & area[0][0])
					x_2 = x_ed - x_st - x
					area[0][2] += x * y / all_ * int(i.weight)
					area[1][2] += x_2 * y / all_ * int(i.weight)
					area[2][2] += x * y_2 / all_ * int(i.weight)
					area[3][2] += x_2 * y_2 / all_ * int(i.weight)
					break

		r = [area[0][2], area[1][2], area[2][2], area[3][2]]
		result = []
		for i in r:
			result.append(round(i / sum(r) * 100, 2))
		return result

	def pack(
			self,
			bigger_first=False,
			distribute_items=True,
			fix_point=True,
			check_stable=True,
			support_surface_ratio=0.75,
			binding=None,
			number_of_decimals=DEFAULT_NUMBER_OF_DECIMALS
	):
		"""pack master func """
		if binding is None:
			binding = list()
		# set decimals
		for bj in self.bins:
			bj.format_numbers(number_of_decimals)

		for item in self.items:
			item.format_numbers(number_of_decimals)
		# add binding attribute
		self.binding = binding
		# Bin : sorted by volume
		self.bins.sort(key=lambda b: b.get_volume(), reverse=bigger_first)
		# Item : sorted by volume -> sorted by load_bear -> sorted by level -> binding
		self.items.sort(key=lambda i: i.get_volume(), reverse=bigger_first)
		# self.items.sort(key=lambda item: item.getMaxArea(), reverse=bigger_first)
		self.items.sort(key=lambda i: i.load_bear, reverse=True)
		self.items.sort(key=lambda i: i.level, reverse=False)
		# sorted by binding
		if binding:
			self.sort_binding()

		for idx, bin_ in enumerate(self.bins):
			# pack item to bin_
			for item in self.items:
				self.pack_2_bin(bin_, item, fix_point, check_stable, support_surface_ratio)

			if binding:
				# resorted
				self.items.sort(key=lambda i: i.get_volume(), reverse=bigger_first)
				self.items.sort(key=lambda i: i.load_bear, reverse=True)
				self.items.sort(key=lambda i: i.level, reverse=False)
				# clear bin_
				bin_.items = []
				bin_.unfitted_items = self.unfit_items
				bin_.fit_items = np.array([[0, bin_.width, 0, bin_.height, 0, 0]])
				# repacking
				for item in self.items:
					self.pack_2_bin(bin_, item, fix_point, check_stable, support_surface_ratio)

			# Deviation Of Cargo Gravity Center
			self.bins[idx].gravity = self.gravity_center(bin_)

			if distribute_items:
				for b_item in bin_.items:
					no = b_item.part_no
					for item in self.items:
						if item.part_no == no:
							self.items.remove(item)
							break

		# put order of items
		self.put_order()

		if self.items:
			self.unfit_items = copy.deepcopy(self.items)
			self.items = []
	# for item in self.items.copy():
	#     if item in bin_.unfitted_items:
	#         self.items.remove(item)