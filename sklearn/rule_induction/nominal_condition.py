class NominalCondition(Condition):

    def __init__(self, p_attribute, values, p_coverage, attr_name):
        Condition.__init__(self, p_attribute, p_coverage, attr_name)
        self.m_values = set(values)
        self.m_usage = false

    def contains(self, condition):
        for value in condition.m_values:
            if value not in self.m_values:
                return False
        return True

    def is_used(self):
        return self.m_usage

    def set_used(self, used):
        self.m_usage = used

    def extend(self, condition):
        self.m_values = self.m_values.union(condition.m_values)

    def covers_impl(self, value):
        return self.contains(value)

    def merge(self, condition):
        return condition

    def to_string(self, data):
        output = "(" + self.m_attr_name + " in {"
        for v in m_values:
            output = output + ", " + str(p_attribute[v])
        output = output + "})"
        return output
