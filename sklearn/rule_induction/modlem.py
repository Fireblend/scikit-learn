import numpy as np
import copy
from sklearn.base import BaseEstimator, ClassifierMixin
from selection_criterion import LaplaceEstimator
import selection_criterion as sc
import classification_strategies
import classification_strategies.m_estimate_strategy as m_estimate_strategy
import classification_strategies.strategy as strategy
from dataset_mapper import DataSetMapper
import rule
import numerical_class_border
import condition

global LAPLACE_ESTIMATOR

class Modlem(BaseEstimator, ClassifierMixin):
    """Predicts the majority class of its training data."""

    def __init__(self, dataset_attr_type=None, nominal_categories=None):
        LAPLACE_ESTIMATOR = 1
        pass

    def fit(self, X, y):
        self.m_data = copy.deepcopy(X)
        self.m_data_classes = copy.deepcopy(y)
        self.m_num_classes = len(np.unique(self.m_data_classes))

        #TODO/POLISH: remove instances without classes if any

        #TODO/POLISH: add option to change criterion
        self.m_criterion = LaplaceEstimator(y.shape[0])

        rules = []
        self.m_possible_conditions = []

        for instance_index in range(0, len(self.m_data_classes)):
            self.m_data[instance_index].append(m_data_classes[instance_index])

        self.m_dataset_mapper = DataSetMapper(self.m_data, self.m_num_classes, self.m_data_classes, self.dataset_attr_type, self.nominal_categories)

        approximate_classes()
        generate_conditions()

        self.m_current_rule_coverage = bitarray([False]*self.m_data.shape[0])
        self.m_current_rule_positive_coverage = bitarray([False]*self.m_data.shape[0])
        covered_from_concept = bitarray([False]*self.m_data.shape[0])

        self.class_index = self.m_data.shape[1];

        for consequent in range(0, self.m_num_classes):
            self.m_positives = self.m_dataset_mapper.get_bit_set_and_check(self.class_index, consequent)
            covered_from_concept ^= covered_from_concept

            while bitarray.count(covered_from_concept) < bitarray.count(self.m_positives):
                self.m_current_rule_coverage = bitarray([True]*self.m_data.shape[0])

                for x in range(0, len(self.m_current_rule_coverage)):
                    if self.m_current_rule_coverage[x]:
                        if covered_from_concept[x]:
                            self.m_current_rule_coverage[x] = False

                self.m_current_rule_positive_coverage ^= self.m_current_rule_positive_coverage
                self.m_current_rule_positive_coverage |= self.m_positives

                for x in range(0, len(self.m_current_rule_positive_coverage)):
                    if self.m_current_rule_positive_coverage[x]:
                        if covered_from_concept[x]:
                            self.m_current_rule_positive_coverage[x] = False

                clean_usage()

                rule = Rule(self.m_data, consequent)

                while True:
                    self.m_criterion.set_worst_eval()
                    best = best_condition()

                    if best.get_evaluation() == m_criterion.get_worst_eval():
                        break

                    rule.extend(copy.deepcopy(best))

                    self.m_current_rule_coverage &= best.get_coverage()
                    self.m_current_rule_positive_coverage &= best.get_coverage()

                    mark_as_used(best)
                    if bitarray.count(self.m_current_rule_coverage) <=  bitarray.count(self.m_current_rule_positive_coverage):
                        break

                rule.drop_redundant_conditions(self.m_positives)

                if rule.get_size() == 0:
                    break

                rule.merge_conditions()
                rule.calculate_coverage(self.m_dataset_mapper)
                rules.append(rule)

                current_rule_positive_coverage = deepcopy(self.m_positives)
                current_rule_positive_coverage &= rule.get_coverage()
                covered_from_concept |= current_rule_positive_coverage

            remove_redundant_rules(rules, consequent)

        self.m_classification_strategy = Strategy.create()
        generate_output(rules)

        self.m_data = None
        self.m_possible_conditions = None
        self.m_dataset_mapper = None

        return self

    def predict(self, X):
        return self.m_classification_strategy.classify_instance(X)

    def get_params(self, deep=True):
    # suppose this estimator has parameters "alpha" and "recursive"
        return {}

    def set_params(self, **parameters):
        for parameter, value in parameters.items():
            self.setattr(parameter, value)
        return self

    def approximate_classes(self):
        if self.m_rules_type == NORMAL_APPROXIMATION:
            return

        for i in range (0, self.m_data.shape[0]):
            consequent = self.m_data_classes[i]
            curr_coverage = self.m_dataset_mapper.get_bit_set(self.class_index, consequent)

            for j in range (i+1, self.m_data.shape[0]):

                if curr_coverage[j] or (not compare(i,j)):
                    continue

                if self.m_rules_type == UPPER_APPROXIMATION:
                    curr_coverage[j] = True
                    self.m_dataset_mapper.get_bit_set(self.class_index, self.m_data_classes[j])[i] = True
                elif self.m_rules_type == LOWER_APPROXIMATION:
                    curr_coverage[i] = False
                    self.m_dataset_mapper.get_bit_set(self.class_index, self.m_data_classes[j])[j] = False

    def best_condition(self):
        best = Condition.create_nominal_condition(-1, [],  bitarray() ,"None")
        best.set_evaluation(self.m_criterion.get_worst_eval())
        best.set_positives_nr(0)

        for attributeIndex in range (0, len(self.m_possible_conditions)):

            if len(self.m_possible_conditions[attributeIndex]) == 0:
                continue

            if isinstance(self.m_data[0][attributeIndex], float):
                best = best_numerical(attributeIndex, best)

            elif isinstance(self.m_data[0][attributeIndex], int):
                best = best_nominal(attributeIndex, best)


    def best_nominal(self, attribute, best):
        candidate = Condition.create_nominal_condition(attribute, [], bitarray([True]*self.m_data.shape[0]), attribute)
        candidate.set_evaluation(self.m_criterion.get_worst_eval())

        current = None

        while True:
            current = copy.deepcopy(candidate)

            rule_conditions = self.m_possible_conditions[attribute]
            for i in range(0, len(rule_conditions)):
                element = rule_conditions[i]
                if element.is_used():
                    continue
                if candidate.contains(element):
                    continue

                merged = copy.deepcopy(candidate)
                merged.extend(element)
                merged.or_op(element.get_coverage())

                self.m_criterion.evaluate(merged, self.m_current_rule_coverage, self.m_current_rule_positive_coverage)
                if(self.m_criterion.compare(merged, current)):
                    current = merged

            if not self.m_criterion.compare(current, candidate):
                break

            candidate = current

        return select_better(candidate, best)


    def best_numerical(self, attribute, best):
        current1 = None
        current2 = None

        for i in range(0, len(self.m_possible_conditions[attribute]),2):
            current1 = self.m_possible_conditions.get(attribute).get(i)
            current2 = self.m_possible_conditions.get(attribute).get(i+1)

            is_lesser_cond_intersected = self.m_available_intervals_for_numerical[attribute].is_intersected(current1.get_interval())
            is_greater_equal_cond_intersected = self.m_available_intervals_for_numerical[attribute].is_intersected(current2.get_interval())

            if not (is_lesser_cond_intersected and is_greater_equal_cond_intersected):
                continue

            candidate = self.m_criterion.evaluate(curren1, current2, self.m_current_rule_coverage, self.m_current_rule_positive_coverage)
            best = select_better(candidate, best)

            if(best.get_evaluation() == self.m_criterion.best()):
                break

        return best

    def clean_usage(self):
        for i in range (0, len(self.m_possible_conditions)):
            if isinstance(self.m_data[0][i], int):
                for condition in self.m_possible_conditions[i]:
                    condition.set_used(not bitarray.count(condition.get_coverage() & self.m_current_rule_positive_coverage) > 0)

        self.m_available_intervals_for_numerical = Interval(self.m_data.shape[1])
        for i in range (0, len(self.m_available_intervals_for_numerical)):
            self.m_available_intervals_for_numerical[i] = Interval(-float("inf"), True, float("inf"), true)

    def compare(self, left, right):
        for attribute in range(0, self.m_data.shape[1]):
            if (self.m_data[left][attribute] != self.m_data[right][attribute]):
                return false
        return true

    def generate_conditions(self):
        for attribute in range (0, self.m_data.shape[1]):
            if(isinstance(self.m_data[0][attribute], float)):
                generate_numerical(attribute)
            elif(isinstance(self.m_data[0][attribute], int)):
                generate_nominal(attribute)

    def generate_nominal(self, attribute):
        conditions = []
        condition = None

        attribute_values = set(self.m_data[:,attribute])
        for i in range (0, len(attribute_values)):
            condition = Condition.create_nominal_condition(attribute, [float(i)], copy.deepcopy(self.m_dataset_mapper.get_bit_set_and_check(attribute, i)), attribute)

            if bitarray.count(condition.get_coverage()) == 0:
                continue

            conditions.append(condition)

        self.m_possible_conditions.append += conditions


    def generate_numerical(self, attribute):
        values = self.m_data[:,attribute]
        sorted_indexes = np.argsort(values)
        values = np.sort(values)

        points = []
        temp = NumericalClassBorder(values[sorted_indexes[0]])
        temp.add(self.m_data_classes[sorted_indexes[0]])

        points.append(temp)

        for i in range(1, self.m_data.shape[0]):
            index = sorted_indexes[i]
            value = values[index]
            consequent = self.m_data_classes[index]

            if(temp.m_value != value):
                temp = NumericalClassBorder(value)
                points.append(temp)

            temp.add(consequent)

        mask = bitarray([False] * len(self.m_data.shape[0]))
        neg_mask = bitarray([False] * len(self.m_data.shape[0]))

        conditions = []
        attribute_keys = self.m_dataset_mapper.get_keys_for_attribute(attribute)

        for i in range(1, len(points)):
            less_key = float("inf")
            current_key = float(points[i].m_value)
            previous_key = float(points[i-1].m_value)

            for key in attribute_keys:
                less_key = key
                if not (less_key < current_key):
                    break

                mask |= self.m_dataset_mapper.get_bit_set(attribute, less_key)

            if points[i-1].m_has_ambiguous_consequent or points[i].m_has_ambiguous_consequent or points[i-1].m_consequent != points[i].m_consequent:
                border = (previous_key + current_key) / 2.0

                neg_mask.setAll(True)
                neg_mask ^= mask

                interval1 = Interval(-float("inf"), true, border, false)
                interval2 = Interval(border, true, float("inf"), true)
                condition1 = Condition.create_numeric_condition(attribute, interval1, copy.deepcopy(mask))
                condition2 = Condition.create_numeric_condition(attribute, interval2, copy.deepcopy(neg_mask))

                conditions.append(condition1)
                conditions.append(condition2)

            mask |= self.m_dataset_mapper(attribute, less_key)

        self.m_possible_conditions.append(conditions)

    def generate_output(self, rules):
        i = 1
        for rule in rules:
            covered = bitarray.count(rule.get_coverage())
            positive_coverage = rule.get_class_coverage()[int(rule.get_consequent)]

            covered_positives = float( float(positive_coverage) / float(bitarray.count(m_dataset_mapper.get_bit_set(self.m_data.shape[1], rule.get_consequent()))))

            self.m_string += "Rule " + i + ". " + rule.to_string() + "   (" \
                + positive_coverage + "/"+ covered + ", " \
                +  '%.2f' % (coveredPositives * 100) + "%)\n"

            i += 1
            self.m_string += "\nNumber of rules: " + len(rules) + "\n"

    def mark_as_used(self, p_best):
        attribute = p_best.get_attribute()

        if isinstance(m_data[0][attribute], float):
            condition = p_best
            self.m_available_intervals_for_numerical[attribute] = self.m_available_intervals_for_numerical[attribute].intersect(condition.get_interval())

        for attribute in range(0, len(self.m_possible_conditions)):
            if isinstance(self.m_data[0][attribute], int):
                for condition in self.m_possible_conditions[attribute]:
                    if (not condition.is_used()) and (not bitarray.count(condition.get_coverage() & self.m_current_rule_positive_coverage) > 0):
                        condition.set_used(True)

    def remove_redundant_rules(self, rules, p_consequent):
        temporary_coverage = None

        for i in range(0, len(rules)):
            if rules[i].get_consequent == p_consequent:
                temporary_coverage = bitarray([False] * self.m_data.shape[0])
                for j in range(0, len(rules)):
                    if rules[j].get_consequent() != p_consequent or i == j:
                        continue

                    temporary_coverage |= rules[j].get_coverage()

                temporary_coverage &= self.m_positives

                if bitarray.count(self.m_positives) == bitarray.count(temporary_coverage):
                    del rules[i]
                    continue

    def select_better(self, candidate, best):
        if candidate.get_evaluation() == best.get_evaluation():
            if candidate.get_positives_nr() > best.get_positives_nr():
                best = candidate

        elif self.m_criterion.compare(candidate, best):
            best = candidate

        return best
