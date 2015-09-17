from bitarray import bitarray

class DataSetMapper:

    def __init__(self, p_dataset, num_classes, p_dataset_classes):
        self.m_num_classes = num_classes
        self.m_num_instances = p_dataset.shape[0]
        for i in range (0, p_dataset.shape[1]):
            l_current = {}
            att_values = p_dataset[:,i]

            for j in range (0, len(att_values)):
                l_current[att_values] = bitarray([False] * self.m_num_instances)

            self.m_values_map.append(l_current)

        self.set_fill_values_map(p_dataset)

    def get_bit_set(self, attr_order, value_order_or_value):
        return self.m_values_map[attr_order][value_order_or_value]

    def get_bit_set_and_check(self, attr_order, value_order_or_value):
        if value_order_or_value not in self.m_values_map[attr_order]:
            self.m_values_map[attr_order][value_order_or_value] = bitarray([False] * self.m_num_instances)
        return self.m_values_map[attr_order][value_order_or_value]

    # nominal_categories = list of nominal categories
    # [cat1, cat2, cat3, etc...]
    def add_nominal(self, p_dataset, p_dataset_classes, num_classes, attribute, nominal_categories):
        current = None
        l_missed = []

        distribution = [[0 for x in range(num_classes)] for x in range(len(nominal_categories))]

        for i in range(0, self.m_num_instances):
            current = p_dataset[i]

            #this is what is done if the instance doesn't have a value for the attribute
            #however this is incompatible with sk-learn
            #    l_missed.append(i)
            #    continue

            curr_val = nominal_categories.index(current[attribute])
            curr_class = p_dataset_classes[i]

            distribution[curr_class][curr_val] += 1
            self.get_bit_set(attribute, curr_val)[i] = True

        decisions_for_unknowns = 0 for x in range(num_classes)

        for i_class in range(0, num_classes):
            decisions_for_unknowns[i_class] = distribution[i_class].index(max(distribution[i_class]))

        for i in range(0, len(l_missed)):
            current = p_dataset[l_missed[i]]
            decision = p_dataset_classes[i]
            current[attribute] = decisions_for_unknowns[decision]
            self.get_bit_set(attribute, decisions_for_unknowns[decision])[l_missed[i]] = True


    def add_numeric(self, p_dataset, p_dataset_classes, num_classes, attribute):
        current = None
        l_missed = []
        occurrences = [0 for x in range(num_classes)]
        values = [0.0 for x in range(num_classes)]

        for i_instance in range(0, len(p_dataset)):
            current = p_dataset[i_instance]
            #this is what is done if the instance doesn't have a value for the attribute
            #however this is incompatible with sk-learn
            #    l_missed.append(i)
            #    continue

            curr_val = current[attribute]
            curr_class = p_dataset_classes[i_instance]

            self.get_bit_set(attribute, cur_val)[i] = True
            occurrences[curr_class] += 1
            vals[curr_class] += curr_val

        for i in range(0, len(vals)):
            if occurrences[i] != 0:
                vals[i] /= occurrences[i]

        for i in range(0, len(l_missed)):
            current = p_dataset[l_missed[i]]
            decision = p_dataset_classes[l_missed[i]]
            current[attribute] = vals[decision]
			self.get_bit_set_and_check(attribute, vals[decision])[l_missed[i]] = True

    # dataset_attr_type = attribute-sized list with True if attribute is nominal
    # in same order as in p_dataset
    # nominal_categories = attribute-sized list with an empty value for numeric
    # attributes and list with discrete categories for nominal attributes
    def fill_values_map(self, p_dataset, p_dataset_classes, num_classes, dataset_attr_type, nominal_categories):
        current = None
        for a in range(0, p_dataset.shape[1]):
            if not dataset_attr_type[a]:
                self.add_numeric(p_dataset, p_dataset_classes, num_classes, a)
                continue
            elif dataset_attr_type[a]:
                self.add_nominal(p_dataset, p_dataset_classes, num_classes, a, nominal_categories[a])
                continue

            for i_instance in range(0, self.m_num_instances):
                current = p_dataset[i_instance]

                #this is what is done if the instance doesn't have a value for the attribute
                #however this is incompatible with sk-learn
                #    continue

                get_bit_set(a, current[a])[i_instance] = True
