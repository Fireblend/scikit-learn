from abc import ABCMeta, abstractmethod

from ...externals import six
from ...rule_induction import dataset_mapper
from ...rule_induction import rule
import numpy as np
from sklearn.preprocessing import normalize

def build_strategy(strategy, dataset, rules, matching_mode, datasetmapper, dataset_classes):
    if strategy == M_ESTIMATE:
        return MEstimateStrategy(dataset, rules, matching_mode, datasetmapper, dataset_classes)

class Strategy(six.with_metaclass(ABCMeta)):
    FULL_MATCHING = 1
    PARTIAL_MATCHING_OFF = 2

    m_abstaining_info = FULL_MATCHING

    def __init__(self, dataset, rules, abstaining_status, datasetmap, num_classes):
        self.m_abstaining_info = abstaining_status
        self.m_data = dataset
        self.m_dataset_map = datasetmap
        self.m_rules = rules
        self.m_num_classes = num_classes

        self.partials = [[0.0] * num_classes] * num_classes
        self.multiples = [[0.0] * num_classes] * num_classes
        self.number_of_simples = 0
        self.number_of_multiples = 0
        self.number_of_partials = 0

    def classify_instance(instance):
        distribution = self.distribution_for_instance(instance)
        return self.classify_instance_distro(distribution)

    def classify_instance_distro(distribution):
        result = None
        if 0 != sum(distrubution):
            result = index(max(distribution))
        return result

    def distribution_for_instance(instance, instance_class_value):
        distribution = [0.0]*self.m_num_classes
        covered_classes = bitarray([False] * self.m_num_classes)
        covering_rules = bitarray([False] * len(self.m_rules))

        for i in range (0, len(self.m_rules)):
            if self.m_rules[i].covers(instance):
                covering_rules[i] = True
                covered_classes[int(self.m_rules[i].get_consequent())]

        if bitarray.count(covered_classes) == 1:
            rule = self.m_rules[Strategy.utils_next_set_bit(covering_rules, 0)]
            distribution[int(rule.get_consequent())] = 1.0
            self.number_of_simples += 1

        elif bitarray.count(covered_classes) > 1 and (self.m_abstaining_info == FULL_MATCHING or self.m_abstaining_info == PARTIAL_MATCHING_OFF):
            self.multiple(distribution, covering_rules)

            decision = int(self.classify_instance(distribution))
            self.multiples[ int( instance_class_value )][decision] += 1.0
            self.number_of_multiples += 1

        elif bitarray.count(covered_classes) == 0 and self.m_abstaining_info == FULL_MATCHING:
            self.partial(distribution, instance)

            decision = int(self.classify_instance(distribution))
            self.partials[ int( instance_class_value )][decision] += 1.0
            self.number_of_partials += 1

        if ( sum(distribution) != 0):
            distribution = Strategy.utils_normalize_sum(distribution)

        return distribution

    @abstractmethod
    def multiple(self, result, covering_rules):
        pass

    @abstractmethod
    def partial(self, result, covering_rules):
        pass

    def utils_next_set_bit(bit_array, position):
        for i in range(position, len(bit_array)):
            if bit_array[i]:
                return i
        return -1

    def utils_normalize_sum(doubles):
        Strategy.utils_normalize(doubles, sum(doubles))

    def utils_normalize(doubles, sum):
        for i in range (0, len(doubles)):
            doubles[i] /= sum
