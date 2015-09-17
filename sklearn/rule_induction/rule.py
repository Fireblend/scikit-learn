from bitarray import bitarray

class Rule:

    def __init__(self, dataset, target, current_class_value,
                num_classes, num_instances):
        self.m_data = dataset
        self.m_target = target
        self.m_consequent = current_class_value
        self.m_conditions = []
        self.m_coverage = bitarray([True] * len(m_data.len))
        self.m_class_coverage = [0] * num_classes
        self.m_num_instances = num_instances
        self.m_num_classes = num_classes


    def calculate_coverage(self, data_set_mapper):
        self.m_coverage = bitarray([True] * len(self.m_coverage.len))
        for condition in self.m_conditions:
            self.m_coverage = self.m_coverage & condition.get_coverage()

        for i in range(0, self.m_num__classes):
            copy = data_set_mapper.get_bit_set(target, i)
            copy = copy & self.m_coverage
            self.m_class_coverage[i] = copy.count()

    def covers(self, instance):
        return self.get_matching_number(instance) == len(self.m_conditions)

    def drop_redundant_conditions(self, positive_examples):
        i = 0
        while i < len(self.m_conditions):
            new_coverage = bitarray([True] * self.m_num_instances)

            for j in range(0, len(self.m_conditions)):
                if i == j:
                    continue
                new_coverage = new_coverage & self.m_conditions[j].get_coverage()

            cardinality = new_coverage.count()
            new_coverage = new_coverage & positive_examples

            if new_coverage.count() == cardinality:
                del self.m_conditions[i]
            else:
                i++

    def extend(self, rule_condition):
        self.m_conditions.append(rule_condition)

    def get_class_coverage(self):
        return self.m_class_coverage

    def get_conditions(self):
        return self.m_conditions

    def get_consequent(self):
        return self.m_consequent

    def get_coverage(self):
        return self.m_coverage

    def get_matching_number(self, instance):
        result = 0
        for condition in self.m_conditions:
            if condition.covers( instance ):
                result++
        return result

    def get_partial_rule_coverage(self, instance):
        rule_coverage = bitarray([True] * self.m_num_instances)

        for condition in self.m_conditions:
            if condition.covers(instance) :
                rule_coverage = rule_coverage & condition.get_coverage()
        return rule_coverage

    def has_antds(self):
        return len(self.m_conditions) != 0

    def merge_conditions(self):
        for j in range(0, len(self.m_conditions)):
            old = m_conditions[j]
            for i in range(j+1, len(self.m_conditions)):
                selector = self.m_conditions[i]
                if selector.get_attribute() == old.get_attribute():
                    self.m_conditions[j] = old.merge(selector)
                    del self.m_conditions[i]
                else:
                    i++

    def get_size(self):
        return len(self.m_conditions)

    def to_string(self):
        end = " => ( class = " + str(self.m_target[self.m_consequent]) + ")"

        if len(self.m_conditions) == 0:
            return "{}" + end

        output = ""
        i = 0

        while True:
            output = output + self.m_conditions[i].to_string(self.m_data)
            i++
            if i == len(self.m_conditions):
                break
            output = output + "&"

        return output + ends
