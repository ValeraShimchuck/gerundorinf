import tkinter as tk
import random
import requests
from tkinter import messagebox
from urllib.parse import quote
from choose import Choose

window = tk.Tk()
prevQuestion = ""
answer_was_right = None
prevRightAnswer = ""


def read_data(file_name):
    with open("files/" + file_name, "r", encoding='utf-8') as file:
        return file.read().split(',')


questions_dict = {
    'bareinf': read_data("bareinf.txt"),
    'gerund': read_data("gerund.txt"),
    'toinf': read_data("toinf.txt"),
    'gerorinfdif': read_data("gerorinfdif.txt"),
    "gerorinfsame": read_data("gerorinfsame.txt")
}
answer_view_dict = {
    'bareinf': 'bare infinitive',
    'gerund': 'gerund',
    'toinf': 'to infinitive',
    'gerorinfdif': 'gerund or infinitive, but meanings are different',
    "gerorinfsame": 'gerund or infinitive, meanings are same'
}
questions = []
for value in questions_dict.values():
    for item in value:
        if item not in questions:
            questions.append(item)
choose = Choose(questions)


def clear_view():
    for widget in window.winfo_children():
        widget.destroy()

    for col in range(window.grid_size()[0]):
        window.grid_columnconfigure(col, weight=0)

    for row in range(window.grid_size()[1]):
        window.grid_rowconfigure(row, weight=0)


def stretch_text(text):
    button_text = tk.StringVar()
    button_text.set(text)
    return button_text


right_answer_text = stretch_text("")
right_answer_label = None
question_text = stretch_text("")


def next_question():
    # choose.next_question()
    choose.next_question_modern()
    question_text.set(choose.current_question)


def change_view(next_view_fun):
    clear_view()
    next_view_fun()


def answer_on_question(answer):
    right_answers = []
    for key, item_list in questions_dict.items():
        if choose.current_question in item_list:
            right_answers.append(key)
    right_answers_view = ""
    for index, other_answer in enumerate(right_answers):
        if index != 0:
            right_answers_view += ', '
        right_answers_view += answer_view_dict[other_answer]
    if answer is not None and answer in right_answers:
        right_answer_text.set("Right! " + choose.current_question + " is " + right_answers_view + ".")
        right_answer_label.configure(bg="green")
        choose.add_statistics(choose.current_question)
        if choose.get_statistics(choose.current_question) % 3 == 0:
            choose.blacklisted_questions[choose.current_question] = 20
            # modern
            choose.add_chance(choose.current_question, -50)

    else:
        right_answer_text.set("Wrong! " + choose.current_question + " is " + right_answers_view + ".")
        right_answer_label.configure(bg="red")
        choose.statistics[choose.current_question] = 0
        choose.order[choose.current_question] = 3
        # modern
        choose.add_chance(choose.current_question, 20)

    next_question()


def send_translate_request():
    url = "https://api.mymemory.translated.net/get?langpair=en|uk&q=" + quote(choose.current_question, safe=':/')
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['responseData']['translatedText']
    else:
        return "error: " + str(response.status_code) + " ".join(response.json())


def translate_info():
    messagebox.showinfo("Translate", send_translate_request())


def quiz_view():
    global right_answer_label
    for i in range(3):
        window.columnconfigure(i, weight=1)
        window.rowconfigure(i, weight=1)
    window.rowconfigure(3, weight=1)
    window.rowconfigure(4, weight=1)
    right_answer_label = tk.Label(window, textvariable=right_answer_text)
    right_answer_label.grid(row=0, column=0, columnspan=3, sticky="nsew")
    right_answer_label.configure(justify="center")
    next_question()

    question_label = tk.Label(window, textvariable=question_text)
    question_label.grid(row=1, column=0, sticky="nsew", columnspan=3)
    question_label.configure(justify="center")

    idk_button = tk.Button(window, textvariable=stretch_text("idk"), command=lambda: answer_on_question(None))
    gerund_button = tk.Button(window, textvariable=stretch_text("-ing"), command=lambda: answer_on_question("gerund"))
    toinf_button = tk.Button(window, textvariable=stretch_text("to inf"), command=lambda: answer_on_question("toinf"))
    bareinf_button = tk.Button(window, textvariable=stretch_text("inf without to"),
                               command=lambda: answer_on_question("bareinf"))
    gerorinfsame_button = tk.Button(window, textvariable=stretch_text("both are same"),
                                    command=lambda: answer_on_question("gerorinfsame"))
    gerorinfdif_button = tk.Button(window, textvariable=stretch_text("both are different"),
                                   command=lambda: answer_on_question("gerorinfdif"))

    idk_button.grid(row=2, column=0, sticky="nsew")
    gerund_button.grid(row=2, column=1, sticky="nsew")
    toinf_button.grid(row=2, column=2, sticky="nsew")
    bareinf_button.grid(row=3, column=0, sticky="nsew")
    gerorinfsame_button.grid(row=3, column=1, sticky="nsew")
    gerorinfdif_button.grid(row=3, column=2, sticky="nsew")

    translate_button = tk.Button(window, textvariable=stretch_text("translate"), command=lambda: translate_info())
    translate_button.grid(row=4, column=0, columnspan=3, sticky="nsew")


def start_view():
    window.columnconfigure(0, weight=1)
    window.rowconfigure(0, weight=1)
    button = tk.Button(window, text="start", command=lambda: quiz_view())
    button.grid(row=0, column=0, sticky="nsew")


if __name__ == "__main__":
    window.geometry("400x400")
    window.title("Gerund or Infinitive?")
    start_view()
    window.mainloop()
