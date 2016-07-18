
class NumericalClassBorder:
    def __init__(self, p_value):
        self.m_value = p_value
        self.m_has_ambiguous_consequent = False
        self.m_consequent = None

    def add(self, p_consequent):
        if self.m_consequent != None:
            if p_consequent == self.m_consequent:
                return

            self.m_has_ambiguous_consequent = True
            return

        self.m_consequent = p_consequent
