from bitarray import bitarray
import numpy
from abc import ABCMeta, abstractmethod
from ..externals import six
from copy import deepcopy

CONDITIONAL_ENTROPY = 0
LAPLACE_ESTIMATOR = 1

def create (type, num_classes):
    if type == CONDITIONAL_ENTROPY:
        return ConditionalEntropy()
    else:
        return LaplaceEstimator(num_classes)

class SelectionCriterion(six.with_metaclass(ABCMeta)):
    def get_worst_eval():
        return self.m_worst_val

    def prepare_selector_coverage(first, uncovered_examples):
        coverage = deepcopy(first.get_coverage())
        coverage = coverage & uncovered_examples
        return coverage

    @abstractmethod
    def best(self):
        pass

    @abstractmethod
    def compare(self, first, second):
        pass

    @abstractmethod
    def evaluate(self, first, second, uncovered_examples, p_positive):
        pass

    @abstractmethod
    def evaluate(self, first, uncovered_examples, p_positive):
        pass

    @abstractmethod
    def set_worst_eval(self, uncovered_examples, positive):
        pass

class ConditionalEntropy(SelectionCriterion):

    def __init__(self):
        self.m_worst_val = float("inf")
        self.m_positive_cardinalities = [0,0]

    def best(self):
        return 0.0

    def compare(self, first, second):
        return first.get_evaluation() < second.get_evaluation()

    def evaluate(self, first, second, uncovered_examples, p_positive):
        coverage1 = self.prepare_selector_coverage(first, uncovered_examples)
        coverage2 = self.prepare_selector_coverage(second, uncovered_examples)

        first.set_evaluation(self.calculate(coverage1, coverage2, p_positive))
        second.set_evaluation(first.get_evaluation())
        first.set_positives_nr(self.m_positive_cardinalities[0])
        second.set_positives_nr(self.m_positive_cardinalities[1])

        if coverage1.count() >= coverage2.count():
            return first
        return second


    def evaluate(self, first, uncovered_examples, p_positive):
        subset1 = self.prepare_selector_coverage(first, uncovered_examples)

        subset2 = bitarray([True] * len(first.get_coverage()))
        subset2 = subset2 ^ subset1
        subset2 = subset2 & uncovered_examples

        first.set_evaluation(self.calculate(subset1, subset2, p_positive))
        first.set_positives_nr(self.m_positive_cardinalities[0])

    def set_worst_eval(self, uncovered_examples, positive):
        pos = positive.count()+0.0
        all_pos = uncovered_examples.count()+0.0

        self.m_worst_val = get_entropy(pos/all_pos, (all_pos-pos)/all_pos)

    def calculate(self, set1, set2, p_positive):
        cardinality1 = set1.count()
        cardinality2 = set2.count()

        if cardinality1 == 0 or cardinality2 == 0:
            return self.m_worst_val

        total_card = cardinality1+cardinality2

        set1 = set1 & p_positive
        self.m_positive_cardinalities[0] = set1.count()
        result = self.conditional_entropy(total_card, cardinality1, self.m_positive_cardinalities[0])

        set2 = set2 & p_positive
        self.m_positive_cardinalities[1] = set2.count()
        result += self.conditional_entropy(total_card, cardinality2, self.m_positive_cardinalities[1])

        return result

    def conditional_entropy(self, total_number_in_set, condition_coverage, positive_coverage):
        negative_coverage = condition_coverage - positive_coverage
        return condition_coverage / total_number_in_set * \
                self.get_entropy(positive_coverage/condition_coverage, negative_coverage/condition_coverage)

    def entropy(self, probability):
        if probability == 0:
            return 0
        return -probability * numpy.log2(probability)

    def get_entropy(self, prob1, prob2):
        return self.entropy(prob1) + self.entropy(prob2)


class LaplaceEstimator(SelectionCriterion):

    def __init__(self, num_classes):
        self.m_num_classes = num_classes
        self.m_worst_val = 0

    def best(self):
        return 1.0

    def compare(self, first, second):
        return first.get_evaluation() > second.get_evaluation()

    def evaluate(self, first, second, uncovered_examples, p_positive):
        coverage1 = self.evaluate(first, uncovered_examples)
        coverage2 = self.evaluate(second, uncovered_examples)

        if(self.compare(first, second)):
            return first
        return second


    def evaluate(self, first, uncovered_examples, p_positive):
        subset1 = self.prepare_selector_coverage(first, uncovered_examples)
        first.set_evaluation(self.calculate(subset1, p_positive))
        first.set_positives_nr(self.m_positive_cardinality)

    def set_worst_eval(self, uncovered_examples, positive):
        pos = positive.count()+0.0
        all_pos = uncovered_examples.count()+0.0

        self.m_worst_val = estimate(pos, all_pos)

    def calculate(self, set1, p_positive):
        total_card = set1.count()

        set1 = set1 & p_positive
        self.m_positive_cardinality = set1.count()

        if self.m_positive_cardinality == 0:
            return 0.0

        return self.estimate(self.m_positive_cardinality, total_card)

    def estimate(self, positive, all_pos):
        return (positive + 1.0) / (all_pos + self.m_num_classes)
