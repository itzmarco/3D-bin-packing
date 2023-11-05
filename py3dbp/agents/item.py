from ..constants import RotationType
from ..auxiliary_methods import set_decimal_places

DEFAULT_NUMBER_OF_DECIMALS = 0
ORIGIN = [0, 0, 0]


class Item:

	def __init__(
			self,
			part_no,
			name,
			typeof,
			dims,
			weight,
			level: int,
			load_bear: int,
			updown: bool,
			color
	):
		self.part_no = part_no
		self.name = name
		self.typeof = typeof
		self.width = dims[0]
		self.height = dims[1]
		self.depth = dims[2]
		self.weight = weight
		# Packing Priority level ,choose 1-3
		self.level = level
		# load-bear
		self.load_bear = load_bear
		# Upside down? True or False
		self.updown = updown if typeof == 'cube' else False
		# Draw item color
		self.color = color
		self.rotation_type = 0
		self.position = ORIGIN
		self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS

	def format_numbers(self, number_of_decimals):
		self.width = set_decimal_places(self.width, number_of_decimals)
		self.height = set_decimal_places(self.height, number_of_decimals)
		self.depth = set_decimal_places(self.depth, number_of_decimals)
		self.weight = set_decimal_places(self.weight, number_of_decimals)
		self.number_of_decimals = number_of_decimals

	def string(self):
		return "%s(%sx%sx%s, weight: %s) pos(%s) rt(%s) vol(%s)" % (
			self.part_no, self.width, self.height, self.depth, self.weight,
			self.position, self.rotation_type, self.get_volume()
		)

	def get_volume(self):
		return set_decimal_places(self.width * self.height * self.depth, self.number_of_decimals)

	def get_max_area(self):
		a = sorted([self.width, self.height, self.depth], reverse=True) if self.updown \
			else [self.width, self.height, self.depth]

		return set_decimal_places(a[0] * a[1], self.number_of_decimals)

	def get_dimension(self):
		""" rotation type """
		if self.rotation_type == RotationType.RT_WHD:
			dimension = [self.width, self.height, self.depth]
		elif self.rotation_type == RotationType.RT_HWD:
			dimension = [self.height, self.width, self.depth]
		elif self.rotation_type == RotationType.RT_HDW:
			dimension = [self.height, self.depth, self.width]
		elif self.rotation_type == RotationType.RT_DHW:
			dimension = [self.depth, self.height, self.width]
		elif self.rotation_type == RotationType.RT_DWH:
			dimension = [self.depth, self.width, self.height]
		elif self.rotation_type == RotationType.RT_WDH:
			dimension = [self.width, self.depth, self.height]
		else:
			dimension = []

		return dimension