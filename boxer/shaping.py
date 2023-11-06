"""
various utility functions for shaping signals
"""


def remap( input, start1, stop1, start2, stop2):
	"""
	remap a value from a range to a new range

	unclamped, for `input` values outside of `start1` or `end1`,
	the output values will be outside of `start2` or `end2`

	Arguments:
		`input` : `Any`
			input value
		
		`start1` : `Any`
			"from" range start value

		`end1` : `Any`
			"from" range end value

		`start2` : `Any`
			"to" range start value

		`end2` : `Any`
			"to" range end value

	"""
	return start2 + (stop2 - start2) * ((input - start1) / (stop1 - start1))