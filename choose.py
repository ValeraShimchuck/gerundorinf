import random


class Choose:
    def __init__(self, questions: list):
        self.chance_for_question = {}  # val -> float
        self.questions = questions
        self.current_question = None
        self.order = {}  # val -> int
        self.blacklisted_questions = {}  # val -> int
        self.statistics = {}  # val -> int
        self.setup_chances()

    def setup_chances(self):
        questions_size = len(self.questions)
        chance_per_question = 100 / questions_size
        for question in self.questions:
            self.chance_for_question[question] = chance_per_question

    def normalize_chances(self):
        total_chance = 0
        for value in self.chance_for_question.values():
            total_chance += value
        deviation = 100 - total_chance
        if abs(deviation) < 0.01:
            return
        random_key = random.choice(list(self.chance_for_question.keys()))
        self.chance_for_question[random_key] += deviation

    def add_chance(self, key, chance):
        original_chance = chance
        current_key_value = self.chance_for_question[key]
        if chance < 0:
            chance = current_key_value * (chance / 100)
        else:
            chance = (100 - current_key_value) * (chance / 100)
        non_chosen_chance_modifier = chance / (len(self.questions) - 1)
        # if 100 - current_key_value < chance:
        for other_key in self.chance_for_question.keys():
            if other_key == key:
                self.chance_for_question[key] += chance
            else:
                self.chance_for_question[other_key] -= non_chosen_chance_modifier
        self.normalize_chances()
        # print("key", key, "chance change", original_chance, "post chance", chance, "value",
        #      self.chance_for_question[key], "prev value", current_key_value)

    def next_question_modern(self):
        random_value = random.uniform(0, 100)
        min_value = 0
        # print("chosen value:", random_value)
        for key, value in self.chance_for_question.items():
            max_value = min_value + value
            # print("min", min_value, "max", max_value, "value", value)
            if min_value <= random_value < max_value:
                self.current_question = key
                return
            min_value = max_value
        raise RuntimeError("wtf")

    def get_statistics(self, key):
        value = self.statistics.get(key)
        if value is None:
            value = 0
        return value

    def add_statistics(self, key):
        value = self.get_statistics(key)
        value += 1
        self.statistics[key] = value

    def filter_questions(self):
        questions = self.questions.copy()
        for value in self.order.keys():
            questions.remove(value)

        for value in self.blacklisted_questions.keys():
            questions.remove(value)
        return questions

    def move_next(self):
        next_value = None
        for key, value in self.order.copy().items():
            value = value - 1
            if value == 0:
                if next_value is not None:
                    raise RuntimeError("wtf")
                next_value = key
                self.order.pop(key)
            else:
                self.order[key] = value

        for key, value in self.blacklisted_questions.copy().items():
            value = value - 1
            if value == 0:
                self.blacklisted_questions.pop(key)
            else:
                self.blacklisted_questions[key] = value
        return next_value

    def next_question(self):
        questions = self.filter_questions()
        possible_next_value = self.move_next()
        if possible_next_value is not None:
            self.current_question = possible_next_value
        else:
            self.current_question = random.choice(questions)
