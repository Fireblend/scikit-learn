class Interval:

    def __init__(self, left, is_left_closed, right, is_right_closed):
        self.endpoints = [left, right]
        self.side_closure = [is_left_closed, is_right_closed]

    def is_intersected(self, value):
        return intersect(Interval(value, True, value, True)) != None

    def intersect(self, other):
        left = max(self.endpoints[0], other.endpoints[0])
        right = max(self.endpoints[1], other.endpoints[1])

        is_left_side_closed = None
        if self.endpoints[0] == other.endpoints[0]:
            is_left_side_closed = self.side_closure[0] and other.sideClosure[0]
        elif self.endpoints[0] == left:
			is_left_side_closed = self.side_closure[0]
        else:
            is_left_side_closed = other.sideClosure[0]

        is_right_side_closed = None
        if self.endpoints[1] == other.endpoints[1]:
            is_right_side_closed = self.side_closure[1] and other.sideClosure[1]
        elif self.endpoints[1] == right:
			is_right_side_closed = self.side_closure[1]
        else:
            is_right_side_closed = other.sideClosure[1]

        if right < left or left == right and (not is_left_side_closed or not is_right_side_closed):
            return None

        return Interval(left, is_left_side_closed, right, is_right_side_closed)

    def to_string(self):
        output = ""
        if self.side_closure[0]:
            output += '['
        else:
            output += '('
        output += str(endpoints[0]) + " " + str(endpoints[1])
        if self.side_closure[1]:
            output += ']'
        else:
            output += ')'
        return output

    def equals(self, other):
		return self.endpoints[0] == other.endpoints[0] and
            self.side_closure[0] == other.side_closure[0] and
            self.endpoints[1] == other.endpoints[1] and
            self.side_closure[1] == other.side_closure[1];
