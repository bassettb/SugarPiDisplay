from enum import Enum
class Trend(Enum):
	NONE = 0
	DoubleUp = 1
	SingleUp = 2
	FortyFiveUp = 3
	Flat = 4
	FortyFiveDown = 5
	SingleDown = 6
	DoubleDown = 7
	NotComputable = 8
	RateOutOfRange = 9

	