from bitarray import bitarray
import copy
from strategy import Strategy

class MEstimateStrategy(Strategy):
    def __init__(self, dataset, rules, abstaining_status, datasetmap, num_classes, dataset_classes):
        Strategy.__init__(self, dataset, rules, abstaining_status, datasetmap, num_classes)

        self.m_class_cardinality = [0]*len(num_classes)

        for i in range(0, num_classes):
            self.m_class_cardinality[i] = bitarray.count(self.m_dataset_map.get_bit_set(dataset.shape[1], i))

        self.m_rule_distribution = new [0.0] * len(rules)

        for i in range(0, len(rules)):
            self.m_rule_distribution[i] = rule_estimation(copy.deepcopy(rules[i].get_coverage()), rules[i].get_consequent())


    def multiple(self, distribution, covering_rules):
        i = Strategy.utils_next_set_bit(covering_rules, 0)
        while True:
            i = covering_rules.next_set_bit

            dec = int(m_rules[i].get_consequent())
            distribution[dec] = mac(self.m_rule_distribution[i], distribution[dec])

            i = Strategy.utils_next_set_bit(covering_rules, i+1)
            if i < 0:
                break

    def partial(self, distribution, instance):
        for rule in self.m_rules:
            if rule.get_matching_number(instance) == 0:
                continue

            dec = int(rule.get_consequent())
            res = rule_estimation(rule.get_partial_rule_coverage(instance), dec)
            distribution[dec] = max(distribution[dec], res)


    def rule_estimation(self, rule_coverage, consequent):
        apriori = m_class_cardinality[consequent]/self.m_data.shape[0]

        coverage_size = bitarray.count(rule_coverage)
        rule_coverage = rule_coverage & self.m_dataset_map.get_bit_set(self.m_data.shape[1], consequent)
        pos_coverage = bitarray.count(rule_coverage)

        return (pos_coverage + 3 * apriori)/(coverage_size + 3)
