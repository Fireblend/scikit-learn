from abc import ABCMeta, abstractmethod

from ..externals import six

class Condition(six.with_metaclass(ABCMeta)):

    @abstractmethod
    def __init__(self, p_attribute, p_coverage, attr_name):
        self.m_attribute = p_attribute
        self.m_coverage = p_coverage
        self.m_attr_name = attr_name

    def covers(self, p_instance):
        value = p_instance[self.m_attribute]
        return covers_impl(value)

    @abstractmethod
    def covers_impl(self, value):
        pass

    def get_attribute(self):
        return self.m_attribute

    def get_coverage(self):
        return self.m_coverage

    def get_evaluation(self):
        return self.m_evaluation

    def get_positives_nr(self):
        return self.m_positives_nr

    @abstractmethod
    def merge(self, condition):
        pass

    def set_evaluation(self, p_evaluation):
        self.m_evaluation = p_evaluation

    def set_positives_nr(self, positives_nr):
        self.m_positives_nr = positives_nr

    @abstractmethod
    def to_string(self, data):
        pass

    def create_numeric_condition(attribute, interval, mask):
        return NumericCondition(attribute, interval, mask)

    def create_nominal_condition(attribute, interval, mask):
        return NominalCondition(attribute, interval, mask)
