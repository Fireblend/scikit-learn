class NumericCondition(Condition):

    def __init__(self, p_attribute, interval, p_coverage, attr_name):
        Condition.__init__(self, p_attribute, p_coverage, attr_name)
        self.m_interval = interval

    def get_interval(self):
        return self.m_interval

    def covers_impl(self, value):
        return self.m_interval.is_intersected(value)

    def merge(self, condition):
        interval = self.m_interval.intersect(condition.get_interval())
        self.m_coverage = self.get_coverage() & condition.get_coverage()
        return self

    def to_string(self, data):
        output = "(" + self.m_attr_name + " in " + interval.to_string() + ")"
        return output
