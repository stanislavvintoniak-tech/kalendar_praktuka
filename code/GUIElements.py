import csv
import datetime as dt
import os
import tkinter as tk
from collections import OrderedDict
from functools import partial
from tkinter import messagebox, PhotoImage, ttk
from tkinter.font import Font, nametofont

from tkcalendar import Calendar

from .TimeLogic import DateCalc, TimeConvert, TimeCalc
from .ValidateWidget import DateInput, IntEntry, ValidatedCombobox, TimeEntry, RequiredEntry

import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))

class LabelInput(ttk.Frame):

    def __init__(self, parent, label: str = '', input_class=ttk.Entry, input_var=None, input_args=None, label_args=None,
                 **kwargs):
        super().__init__(parent, **kwargs)

        input_args = input_args or {}
        label_args = label_args or {}
        self.variable = input_var

        if input_class in (ttk.Checkbutton, ttk.Button, ttk.Radiobutton):
            input_args["text"] = label
            input_args["variable"] = input_var

            self.button = input_class(self, **input_args)
            self.button.grid(row=0, column=0, sticky=(tk.W + tk.E))

        else:
            self.label = ttk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))
            input_args["textvariable"] = input_var

            self.input = input_class(self, **input_args)
            self.input.grid(row=0, column=1, sticky=(tk.W + tk.E))

        self.columnconfigure(0, weight=1)
        self.error = getattr(self.input, 'error', tk.StringVar())
        self.error_label = ttk.Label(
            self, textvariable=self.error, justify='right', **label_args, )
        self.error_label.grid(
            row=1, column=0, sticky='ew', columnspan=2)

    def grid(self, sticky=(tk.E + tk.W), **kwargs) -> None:

        super().grid(sticky=sticky, **kwargs)

    def get(self) -> str:

        try:
            if self.variable:
                return self.variable.get()
            elif isinstance(self.input, tk.Text):
                return self.input.get('1.0', tk.END)
            else:
                return self.input.get()

        except (TypeError, tk.TclError):
            return ''

    def set(self, value, *args, **kwargs) -> None:

        if isinstance(self.variable, tk.BooleanVar):
            self.variable.set(bool(value))
        elif type(self.input) in (ttk.Checkbutton, ttk.Radiobutton):
            if value:
                self.input.select()
            else:
                self.input.deselect()
        elif isinstance(self.input, tk.Text):
            self.input.delete('1.0', tk.END)
            self.input.insert('1.0', value)
        elif self.variable:
            self.variable.set(value, *args, **kwargs)
        else:  
            self.input.delete(0, tk.END)
            self.input.insert(0, value)

class Window(tk.Frame):

    def __init__(self, parent, user_name: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user: str = user_name

        self.labelframe_color = (
            {'background': "#f8a51b"},
            {"background": "#03a45e"}
        )

        self.style = ttk.Style()
        self.style.configure(
            'label_style_0.TLabel',
            **self.labelframe_color[0]
        )
        self.style.configure(
            "label_style_1.TLabel",
            **self.labelframe_color[1]
        )

        button_font = Font(
            family='Slabo 27px',
            size=11,
            weight='bold',
            slant='roman',
            underline=False,
            overstrike=False
        )

        default_font = nametofont('TkTextFont')
        default_font.config(
            family="ds-digital",
            weight='normal',
            size=15
        )
        text_field = Font(
            family="Fira Code",
            size=15,
            weight='normal',
            slant='roman'
        )
        self.style.configure(
            'text_field.TEntry',
            font=text_field,
        )
        self.style.configure(
            'text_field.TCombobox',
            font=text_field,
        )

        label_font = Font(
            family='Catamaran SemiBold',
            size=11,
            weight='normal',
            slant='roman',
        )
        frame_l_font = Font(
            family="Arvo",
            size=15,
            weight='normal',
            slant='italic',
        )
        process_font = Font(
            family='Cascadia Code Bold',
            size=13,
            slant='roman'
        )
        self.style.configure(
            "process.TButton",
            font=process_font,
            foreground="#4169e1",
        )

        self.file_name = os.path.join(
            os.path.expanduser('~'), "Documents",
            f"{self.user}-calendar.csv"
        )

        mainframe = ttk.Frame(self)


        self.widgets = OrderedDict()

        logo_pic = PhotoImage(
            file=r"assets/SmallCalendar.png")
        self.widgets['logo'] = tk.Label(
            mainframe,
            image=logo_pic,
            background="#4884e4"
        )

        self.widgets['logo'].image = logo_pic
        self.widgets['logo'].grid(
            row=0, column=0, sticky='news')

        self.widgets['feature_frame'] = tk.Frame(mainframe)

        today_date = dt.date.today()
        self.add_calendar = Calendar(
            self.widgets['feature_frame'],
            selectmode='none',
            year=today_date.year,
            month=today_date.month,
            day=today_date.day,
            font=label_font,
            selectforeground='#191970',
            normalforeground="#FDFEFF",
            normalbackground="#343434",
            disabledselectbackground="#343434",
            weekendforeground="#66ff00",
            weekendbackground="#343434",
            othermonthforeground="#eeeade",
            othermonthbackground="#404040",
            othermonthwebackground="#404040",
            othermonthweforeground="#eeeade",

        )
        self.add_calendar.grid(row=1, column=0, sticky='news', ipadx=130,
                               ipady=80, )

        self.widgets['date_calculator'] = tk.Button(
            mainframe,
            text="Калькулятор дат",
            command=self.place_date_calculator,
            bg="#0066b4", fg="#ffd500",
            font=button_font
        )
        self.widgets['date_calculator'].grid(
            row=1, column=0, sticky='news')

        self.date_calculator_widgets = OrderedDict()

        self.date_calculator_widgets['time_bw_date_label'] = (
            tk.LabelFrame(self.widgets['feature_frame'],
                          text="День (дні) між двома датами",
                          foreground='red',
                          font=frame_l_font),
            OrderedDict()
        )
        self.date_calculator_widgets['time_bw_date_label'][1]["start_date"] = LabelInput(
            self.date_calculator_widgets['time_bw_date_label'][0],
            "Початкова дата",
            input_class=DateInput,
            input_var=tk.StringVar(),
            input_args={"locale": 'en_US', "date_pattern": 'yyyy-MM-dd'},
            label_args={'font': label_font, "style": 'label_style_0.TLabel'}
        )
        self.date_calculator_widgets['time_bw_date_label'][1]["end_date"] = LabelInput(
            self.date_calculator_widgets['time_bw_date_label'][0],
            "Дата закінчення",
            input_class=DateInput,
            input_var=tk.StringVar(),
            input_args={"locale": 'en_US', "date_pattern": 'yyyy-MM-dd'},
            label_args={'font': label_font, "style": 'label_style_0.TLabel'}
        )
        self.date_calculator_widgets['time_bw_date_label'][1]['output'] = LabelInput(
            self.date_calculator_widgets['time_bw_date_label'][0],
            "Кількість днів між датами",
            input_var=tk.StringVar(),
            input_args={'state': 'disabled'},
            label_args={'font': label_font, "style": 'label_style_0.TLabel'}
        ),
        self.date_calculator_widgets['time_bw_date_label'][1]["submit"] = ttk.Button(
            self.date_calculator_widgets['time_bw_date_label'][0],
            text="пуск",
            command=partial(self.submit, 1.1),
            style='process.TButton'
        )

        self.date_calculator_widgets['date_after_period'] = (
            tk.LabelFrame(
                self.widgets['feature_frame'],
                text="Дата після закінчення певного періоду часу —".title(),
                font=frame_l_font,
                foreground="#172e7c"
            ),
            OrderedDict()
        )
        self.date_calculator_widgets['date_after_period'][1]['date'] = LabelInput(
            self.date_calculator_widgets['date_after_period'][0],
            "Початкова дата",
            input_class=DateInput,
            input_var=tk.StringVar(),
            input_args={"locale": 'en_US', "date_pattern": 'yyyy-MM-dd'},
            label_args={'font': label_font, "style": 'label_style_1.TLabel'}
        )
        self.date_calculator_widgets['date_after_period'][1]['increment'] = (
            LabelInput(
                self.date_calculator_widgets['date_after_period'][0],
                "Період",
                input_class=IntEntry,
                input_var=tk.StringVar(),
                label_args={'font': label_font,
                            "style": 'label_style_1.TLabel'}
            ),
            LabelInput(
                self.date_calculator_widgets['date_after_period'][0],
                "Одиниця",
                input_class=ValidatedCombobox,
                input_var=tk.StringVar(),
                input_args={"values": [
                    "day(s)", "week(s)", "month(s)", "year(s)"]},
                label_args={'font': label_font,
                            "style": 'label_style_1.TLabel'}
            )
        )
        self.date_calculator_widgets['date_after_period'][1]['output'] = LabelInput(
            self.date_calculator_widgets['date_after_period'][0],
            "Дата після крапки",
            input_var=tk.StringVar(),
            input_args={'state': 'disabled'},
            label_args={'font': label_font, "style": 'label_style_1.TLabel'}
        )
        self.date_calculator_widgets['date_after_period'][1]['submit'] = ttk.Button(
            self.date_calculator_widgets['date_after_period'][0],
            text="пуск",
            style='process.TButton',
            command=partial(self.submit, 1.2)
        )

        self.widgets['time_calculator'] = tk.Button(
            mainframe,
            text="Калькулятор часу",
            command=self.place_time_calculator,
            bg="#0066b4", fg="#ffd500",
            font=button_font

        )
        self.widgets['time_calculator'].grid(row=2, column=0, sticky='news')
        self.time_calculator_widgets = OrderedDict()

        self.time_calculator_widgets['time_difference'] = (
            tk.LabelFrame(
                self.widgets['feature_frame'],
                text="Різниця в часі між двома часовими мітками".title(),
                foreground='red',
                font=frame_l_font),
            OrderedDict()
        )
        self.time_calculator_widgets['time_difference'][1]['start_time'] = LabelInput(
            self.time_calculator_widgets['time_difference'][0],
            "Початковий час",
            input_class=TimeEntry,
            input_var=tk.StringVar(),
            label_args={'font': label_font, "style": 'label_style_0.TLabel'}
        )
        self.time_calculator_widgets['time_difference'][1]['end_time'] = LabelInput(
            self.time_calculator_widgets['time_difference'][0],
            "Кінець часу",
            input_class=TimeEntry,
            input_var=tk.StringVar(),
            label_args={'font': label_font, "style": 'label_style_0.TLabel'}
        )
        self.time_calculator_widgets['time_difference'][1]['output'] = LabelInput(
            self.time_calculator_widgets['time_difference'][0],
            "Різниця в часі",
            input_var=tk.StringVar(),
            input_args={'state': 'disabled'},
            label_args={'font': label_font, "style": 'label_style_0.TLabel'}
        )
        self.time_calculator_widgets['time_difference'][1]['submit'] = ttk.Button(
            self.time_calculator_widgets['time_difference'][0],
            text="пуск",
            style='process.TButton',
            command=partial(self.submit, 2.1)
        )

        self.time_calculator_widgets['time_after_increment'] = (
            tk.LabelFrame(
                self.widgets['feature_frame'],
                text="Час після значення приросту".title(),
                font=frame_l_font,
                foreground="#172e7c",
            ),
            OrderedDict()
        )
        self.time_calculator_widgets['time_after_increment'][1]['time'] = LabelInput(
            self.time_calculator_widgets['time_after_increment'][0],
            "Час",
            input_class=TimeEntry,
            input_var=tk.StringVar(),
            label_args={'font': label_font, "style": 'label_style_1.TLabel'}
        )
        self.time_calculator_widgets['time_after_increment'][1]['seconds_to_increment'] = (
            LabelInput(
                self.time_calculator_widgets['time_after_increment'][0],
                "Збільшити значення",
                input_class=IntEntry,
                input_var=tk.StringVar(),
                label_args={'font': label_font,
                            "style": 'label_style_1.TLabel'}
            ),
            LabelInput(
                self.time_calculator_widgets['time_after_increment'][0],
                "Одиниця",
                input_class=ValidatedCombobox,
                input_var=tk.StringVar(),
                input_args={"values": ["sec", "min", "hrs"]},
                label_args={'font': label_font,
                            "style": 'label_style_1.TLabel'}
            )
        )
        self.time_calculator_widgets['time_after_increment'][1]['output'] = LabelInput(
            self.time_calculator_widgets['time_after_increment'][0],
            "Час виведення",
            input_var=tk.StringVar(),
            input_args={'state': 'disabled'},
            label_args={'font': label_font,
                        "style": 'label_style_1.TLabel'}
        )
        self.time_calculator_widgets['time_after_increment'][1]['submit'] = ttk.Button(
            self.time_calculator_widgets['time_after_increment'][0],
            text='пуск',
            style='process.TButton',
            command=partial(self.submit, 2.2)
        )

        self.widgets['unit_conversion'] = tk.Button(
            mainframe,
            text="Перетворення одиниць виміру",
            command=self.place_unit_convert,
            bg="#0066b4", fg="#ffd500",
            font=button_font

        )
        self.widgets['unit_conversion'].grid(row=3, column=0, sticky='news')
        self.unit_conversion_widgets = OrderedDict()

        self.unit_conversion_widgets['Conversion'] = (
            tk.LabelFrame(
                self.widgets['feature_frame'],
                text="Перетворити час з однієї одиниці виміру в іншу".title(),
                font=frame_l_font,
                foreground='red',
            ),
            OrderedDict()
        )
        self.unit_conversion_widgets['Conversion'][1]['input_time'] = (
            LabelInput(
                self.unit_conversion_widgets['Conversion'][0],
                "Число",
                input_class=IntEntry,
                input_var=tk.StringVar(),
                label_args={'font': label_font,
                            "style": 'label_style_0.TLabel'}
            ),
            LabelInput(
                self.unit_conversion_widgets['Conversion'][0],
                "Одиниця",
                input_var=tk.StringVar(),
                input_args={"values": ["sec", "min",
                                       "hour", "day(s)", "week(s)", "year(s)"]},
                input_class=ValidatedCombobox,
                label_args={'font': label_font,
                            "style": 'label_style_0.TLabel'}
            )
        )
        self.unit_conversion_widgets['Conversion'][1]['output'] = (
            LabelInput(
                self.unit_conversion_widgets['Conversion'][0],
                "Вихідне числове значення",
                input_var=tk.StringVar(),
                input_args={'state': 'disabled'},
                label_args={'font': label_font,
                            "style": 'label_style_0.TLabel'},
            ),
            LabelInput(
                self.unit_conversion_widgets['Conversion'][0],
                "Одиниця",
                input_var=tk.StringVar(),
                input_args={"values": ["sec", "min",
                                       "hour", "day(s)", "week(s)", "year(s)"]},
                input_class=ValidatedCombobox,
                label_args={'font': label_font,
                            "style": 'label_style_0.TLabel'}
            )
        )
        self.unit_conversion_widgets['Conversion'][1]['submit'] = ttk.Button(
            self.unit_conversion_widgets['Conversion'][0],
            text='пуск',
            style='process.TButton',
            command=partial(self.submit, 3.1)
        )

        self.widgets['new_events'] = tk.Button(
            mainframe,
            text="Нова подія",
            command=self.place_new_event,
            bg="#0066b4", fg="#ffd500",
            font=button_font

        )
        self.widgets['new_events'].grid(row=4, column=0, sticky='news')
        self.new_events_widgets = OrderedDict()

        self.new_events_widgets['new_event'] = (
            tk.LabelFrame(
                self.widgets['feature_frame'],
                text="Створити нову подію".title(),
                font=frame_l_font,
                foreground='red',
            ),
            OrderedDict()
        )
        self.new_events_widgets['new_event'][1]['name'] = LabelInput(
            self.new_events_widgets['new_event'][0],
            "Назва події",
            input_var=tk.StringVar(),
            input_args={'style': 'text_field.TEntry'},
            label_args={'font': label_font, "style": 'label_style_0.TLabel'}
        )
        self.new_events_widgets['new_event'][1]['type'] = LabelInput(
            self.new_events_widgets['new_event'][0],
            "Тип події",
            ValidatedCombobox,
            tk.StringVar(),
            {"values": ["Birthday", "Marriage Anniversary",
                        "Appointment", "Meeting", "N/A"], 'style': 'text_field.TCombobox'},
            label_args={'font': label_font, "style": 'label_style_0.TLabel'}
        )
        self.new_events_widgets['new_event'][1]['date'] = LabelInput(
            self.new_events_widgets['new_event'][0],
            "Дата заходу",
            input_class=DateInput,
            input_var=tk.StringVar(),
            input_args={"locale": 'en_US', "date_pattern": 'yyyy-MM-dd'},
            label_args={'font': label_font, "style": 'label_style_0.TLabel'}
        )
        self.new_events_widgets['new_event'][1]['timings'] = (
            LabelInput(
                self.new_events_widgets['new_event'][0],
                "Початковий час заходу",
                input_class=TimeEntry,
                input_var=tk.StringVar(),
                label_args={'font': label_font,
                            "style": 'label_style_0.TLabel'}
            ),
            LabelInput(
                self.new_events_widgets['new_event'][0],
                "Час закінчення події",
                input_class=TimeEntry,
                input_var=tk.StringVar(),
                label_args={'font': label_font,
                            "style": 'label_style_0.TLabel'}
            )
        )
        self.new_events_widgets['new_event'][1]['recurring'] = LabelInput(
            self.new_events_widgets['new_event'][0],
            "Це регулярна подія?",
            ValidatedCombobox,
            tk.StringVar(),
            {"values": ["Yes", "No"], 'style': 'text_field.TCombobox'},
            label_args={'font': label_font, "style": 'label_style_0.TLabel'}
        )
        self.new_events_widgets['new_event'][1]['submit'] = ttk.Button(
            self.new_events_widgets['new_event'][0],
            text="пуск",
            style='process.TButton',
            command=partial(self.submit, 4.0)
        )

        # Feature #5: Show Calendar
        self.widgets['show_calendar'] = tk.Button(
            mainframe,
            text="Показати календар за роком/місяцем",
            command=self.place_show_calendar,
            bg="#0066b4", fg="#ffd500",
            font=button_font

        )
        self.widgets['show_calendar'].grid(row=5, column=0, sticky='news')
        self.show_calendar_widgets = OrderedDict()

        self.show_calendar_widgets['calendar'] = (
            tk.LabelFrame(
                self.widgets['feature_frame'],
                text="Вікно календаря",
                font=frame_l_font,
                foreground='red',
            ),
            OrderedDict()
        )

        self.show_calendar_widgets['calendar'][1]['calendar_win'] = Calendar(
            self.show_calendar_widgets['calendar'][0],
            selectmode='day',
            year=today_date.year,
            month=today_date.month,
            day=today_date.day,
            background="#5c88c5",
            font=label_font,
            selectforeground='#191970',
            normalforeground="#FDFEFF",
            normalbackground="#343434",
            disabledselectbackground="#343434",
            weekendforeground="#66ff00",
            weekendbackground="#343434",
            othermonthforeground="#eeeade",
            othermonthbackground="#404040",
            othermonthwebackground="#404040",
            othermonthweforeground="#eeeade",
        )

        self.widgets['show_current_events'] = tk.Button(
            mainframe,
            text='Показати події',
            command=self.place_show_event,
            bg="#0066b4", fg="#ffd500",
            font=button_font

        )
        self.widgets['show_current_events'].grid(
            row=6, column=0, sticky='news')
        self.show_current_events_widgets = OrderedDict()

        self.style.configure("tree_style.Treeview", highlightthickness=0, bd=0, font=(
            'Arvo', 10)) 
        self.style.configure("tree_style.Treeview.Heading", font=(
            'Catamaran SemiBold', 12, 'bold'))  
        self.style.layout("tree_style.Treeview", [
            ('tree_style.Treeview.treearea', {'sticky': 'news'})])  

        self.column_defs = {
            '#0': {'label': 'Row', 'anchor': tk.W, 'width': 40},
            'name': {'label': 'Name', 'width': 150, 'stretch': True},
            'type': {'label': 'Type', 'width': 90, 'stretch': True},
            'date': {'label': 'Date', 'width': 90},
            'recurring': {'label': 'Recurring', 'width': 70},
            'start_timing': {'label': "Start Time", 'width': 90},
            'end_timing': {'label': "End Time", 'width': 90},
        }
        self.default_width = 100
        self.default_minwidth = 10
        self.deafault_anchor = tk.CENTER

        self.show_current_events_widgets['csv_tree'] = (
            ttk.Frame(
                self.widgets['feature_frame'],
            ),
            OrderedDict()
        )
        self.show_current_events_widgets['csv_tree'][1]['tree'] = ttk.Treeview(
            self.show_current_events_widgets['csv_tree'][0],
            columns=list(self.column_defs.keys())[1:],
            selectmode='browse',
            style='tree_style.Treeview',
        )
        self.show_current_events_widgets['csv_tree'][1]['tree'].columnconfigure(
            0, weight=1
        )
        self.show_current_events_widgets['csv_tree'][1]['tree'].rowconfigure(
            0, weight=1
        )

        for name, definition in self.column_defs.items():
            label = definition.get('label', '')
            anchor = definition.get('anchor', self.deafault_anchor)
            minwidth = definition.get(
                'minwidth',
                self.default_minwidth
            )
            width = definition.get('width', self.default_width)
            stretch = definition.get('stretch', False)
            self.show_current_events_widgets['csv_tree'][1]['tree'].heading(
                name, text=label, anchor=anchor)
            self.show_current_events_widgets['csv_tree'][1]['tree'].column(
                name,
                anchor=anchor,
                minwidth=minwidth,
                width=width,
                stretch=stretch
            )

        self.show_current_events_widgets['csv_tree'][1]['scrollbar_x'] = ttk.Scrollbar(
            self.show_current_events_widgets['csv_tree'][0],
            orient=tk.HORIZONTAL,
            command=self.show_current_events_widgets['csv_tree'][1]['tree'].xview
        )
        self.show_current_events_widgets['csv_tree'][1]['scrollbar_y'] = ttk.Scrollbar(
            self.show_current_events_widgets['csv_tree'][0],
            orient=tk.VERTICAL,
            command=self.show_current_events_widgets['csv_tree'][1]['tree'].yview
        )

        self.show_current_events_widgets['csv_tree'][1]['tree'].configure(
            xscrollcommand=self.show_current_events_widgets['csv_tree'][1]['scrollbar_x'].set,
            yscrollcommand=self.show_current_events_widgets['csv_tree'][1]['scrollbar_y'].set
        )

        mainframe.grid(row=0, sticky=(tk.S + tk.N))
        self.widgets['feature_frame'].grid(
            row=0, column=1, rowspan=7, columnspan=3, padx=30)

        if self.user == 'guest':
            self.widgets['show_current_events'].config(state='disabled')
            self.widgets['new_events'].config(state='disabled')

    def place_date_calculator(self):

        self._constructor(
            self.date_calculator_widgets,
            self.widgets['feature_frame']
        )

    def place_time_calculator(self):

        self._constructor(
            self.time_calculator_widgets,
            self.widgets['feature_frame']
        )

    def place_unit_convert(self):

        self._constructor(
            self.unit_conversion_widgets,
            self.widgets['feature_frame']
        )

    def place_new_event(self):

        self._constructor(
            self.new_events_widgets,
            self.widgets['feature_frame']
        )

    def place_show_calendar(self):

        self._constructor(
            self.show_calendar_widgets,
            self.widgets['feature_frame']
        )

        if os.path.exists(self.file_name):
            with open(self.file_name) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.show_calendar_widgets['calendar'][1]['calendar_win'].calevent_create(
                        dt.datetime.strptime(row['date'], '%Y-%m-%d'),
                        row['name'],
                        row['type']
                    )

    def place_show_event(self):

        if os.path.exists(self.file_name):

            Window.destroyer(self.widgets['feature_frame'])
            self.widgets['feature_frame'].config(width=500)

            self.show_current_events_widgets['csv_tree'][1]['scrollbar_x'].pack(
                side=tk.RIGHT, fill=tk.Y
            )
            self.show_current_events_widgets['csv_tree'][1]['scrollbar_x'].pack(
                side=tk.BOTTOM, fill=tk.X
            )
            self.show_current_events_widgets['csv_tree'][1]['tree'].pack()
            self.show_current_events_widgets['csv_tree'][0].grid(row=0)

            if os.path.exists(self.file_name):
                with open(self.file_name) as file:
                    reader = csv.DictReader(file)
                    data = list(reader)

            self.populate(data)
        else:
            message = f"No event has been created by {self.user}"
            messagebox.showerror(
                title="CSV file not found",
                message=message
            )

    def populate(self, rows):

        for row in self.show_current_events_widgets['csv_tree'][1]['tree'].get_children():
            self.show_current_events_widgets['csv_tree'][1]['tree'].delete(row)

        valuekeys = list(self.column_defs.keys())[1:]
        for row_num, row_data in enumerate(rows):
            values = [row_data[key] for key in valuekeys]
            self.show_current_events_widgets['csv_tree'][1]['tree'].insert(
                '', 'end', iid=str(row_num), text=str(row_num + 1), values=values)

        if len(rows) > 0:
            self.show_current_events_widgets['csv_tree'][1]['tree'].focus_set()
            self.show_current_events_widgets['csv_tree'][1]['tree'].selection_set(
                0)
            self.show_current_events_widgets['csv_tree'][1]['tree'].focus('0')

    def submit(self, feature_id: float):

        widget_dict = {
            1: self.date_calculator_widgets,
            2: self.time_calculator_widgets,
            3: self.unit_conversion_widgets,
            4: self.new_events_widgets,
        }

        main_feat_id: int = int(feature_id)
        sub_feat_id: int = int(str(feature_id)[-1])

        req_dict = list(widget_dict[main_feat_id].values())[
            sub_feat_id - 1][-1]

        req_data = self.get(req_dict)

        try:
            if main_feat_id == 1:
                if isinstance(req_dict['output'], tuple):
                    self.date_calc(
                        sub_feat_id,
                        req_dict['output'][0],
                        **req_data
                    )
                else:
                    self.date_calc(
                        sub_feat_id,
                        req_dict['output'],
                        **req_data
                    )
            elif main_feat_id == 2:
                if isinstance(req_dict['output'], tuple):
                    self.time_calc(
                        sub_feat_id,
                        req_dict['output'][0],
                        **req_data
                    )
                else:
                    self.time_calc(
                        sub_feat_id,
                        req_dict['output'],
                        **req_data
                    )
            elif main_feat_id == 3:
                self.unit_converter(req_data, req_dict['output'][0])

            elif main_feat_id == 4:
                if self.create_new_event(req_data):
                    messagebox.showinfo(
                        title="Event Created Successfully",
                        message=f"The event is successfully created to {self.file_name}"
                    )
                else:
                    messagebox.showerror(
                        title="Event not created",
                        message="The event could not be created for some reason."
                    )
        except Exception:
            messagebox.showerror(
                title="Error Occurred",
                message="Invalid input. Try again."
            )

    def unit_converter(self, data: dict, to_update_in):

        calc_obj = TimeConvert(
            float(data['input_time'][0]),
            data['input_time'][1],
            data['output'][1]
        )
        output = calc_obj.output()

        to_update_in.set(f"{output}")

    def create_new_event(self, data: dict) -> bool:

        if self.user == 'guest':
            return False

        start_time, end_time = data.pop('timings')
        data['start_timing'] = start_time
        data['end_timing'] = end_time

        newfile: bool = not os.path.exists(self.file_name)

        with open(self.file_name, 'a', newline='') as fn:
            csv_writer = csv.DictWriter(fn, fieldnames=data.keys())
            if fn.writable():
                if newfile:
                    csv_writer.writeheader()
                csv_writer.writerow(data)
                return True

    @staticmethod
    def get(where_from: dict) -> dict:

        data = {}
        for key, widget in where_from.items():
            try:
                data[key] = widget.get()
            except AttributeError:
                data[key] = list()
                try:
                    for wid in widget:
                        data[key].append(wid.get())
                except Exception:
                    continue

                continue
        data.pop('submit')

        return data

    def date_calc(self, feature_code: int, to_update_in, **kwargs):

        calc_obj = DateCalc()

        if feature_code == 1:
            to_update_in.set(
                f"{calc_obj.day_calculator(start_date=kwargs['start_date'], end_date=kwargs['end_date'])}"
            )  

        elif feature_code == 2:
            to_update_in.set(
                f"{calc_obj.date_increment(kwargs['date'], int(kwargs['increment'][0]), kwargs['increment'][1])}"
            )  

    def time_calc(self, feature_code: int, to_update_in, **kwargs):

        calc_obj = TimeCalc()

        if feature_code == 1:
            seconds = calc_obj.time_gap(
                start_time=kwargs['start_time'], end_time=kwargs['end_time'])
            hour, left_sec = divmod(seconds, 3600)
            minute, sec = divmod(left_sec, 60)
            to_update_in.set(
                f"{hour} hours(s) {minute} minute(s) {sec} second(s)"
            )  

        elif feature_code == 2:
            to_update_in.set(
                f"{calc_obj.time_increment(kwargs['time'], int(kwargs['seconds_to_increment'][0]), kwargs['seconds_to_increment'][1])}"
            )  

    def _constructor(self, what_to_construct: dict, frame_to_clear: tk.Frame):

        Window.destroyer(frame_to_clear)

        sub_feature_label_row = 0  
        for container_obj, feature_widgets in what_to_construct.values():

            container_obj.config(
                **self.labelframe_color[sub_feature_label_row])
            container_obj.grid(row=sub_feature_label_row,
                               column=0, sticky="news")

            sub_feature_label_row += 1

            _sub_feature_field_row, _sub_feature_field_column = 0, 0

            for object_to_grid in feature_widgets.values():
                try:
                    if isinstance(object_to_grid, (ttk.Combobox, LabelInput)):
                        object_to_grid.grid(
                            row=_sub_feature_field_row,
                            column=_sub_feature_field_column,
                            sticky='ew',
                            pady=(10, 0),
                        )
                        object_to_grid.set('')
                    elif isinstance(object_to_grid, Calendar):
                        object_to_grid.grid(
                            row=_sub_feature_field_row,
                            column=_sub_feature_field_column,
                            pady=(10, 0),
                            ipadx=100,
                            ipady=60,
                        )
                    else:
                        object_to_grid.grid(
                            row=_sub_feature_field_row,
                            column=_sub_feature_field_column,
                            sticky='ew',
                            pady=(10, 0),
                            ipady=5,
                            ipadx=5,
                            columnspan=2,
                        )
                except AttributeError:

                    unit_column = 0

                    for obj in object_to_grid:
                        obj.grid(
                            row=_sub_feature_field_row,
                            column=unit_column,
                            sticky='news',
                            pady=(10, 0)
                        )

                        if type(obj) in (ttk.Combobox, LabelInput):
                            obj.set('')
                        unit_column += 1
                finally:

                    _sub_feature_field_row += 1

    @staticmethod
    def destroyer(frame: tk.Frame):


        for child_widgets in frame.winfo_children():
            child_widgets.grid_forget()


class LoginPage(tk.Frame):

    def __init__(self, which_login: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.style = ttk.Style()
        self.style.configure(
            'label.TLabel',
            background="#f8a51b"
        )
        default_font = nametofont('TkTextFont')
        default_font.config(
            family="ds-digital",
            weight='normal',
            size=15
        )
        self.text_field = Font(
            family="Fira Code",
            size=15,
            weight='normal',
            slant='roman'
        )
        self.style.configure(
            'text.TEntry',
            font=self.text_field,
        )

        self.label_font = Font(
            family='Catamaran SemiBold',
            size=11,
            weight='normal',
            slant='roman',
        )
        self.frame_l_font = Font(
            family="Arvo",
            size=15,
            weight='normal',
            slant='italic',
        )
        self.process_font = Font(
            family='Cascadia Code Bold',
            size=13,
            slant='roman'
        )
        self.style.configure(
            "processor.TButton",
            font=self.process_font,
            foreground="#4169e1",
        )

        # list of all widgets
        self.widgets = dict()

        self.login_frame = tk.LabelFrame(
            self,
            text=f"{which_login.split('_')[0].title()} Login",
            font=self.frame_l_font,
            foreground='red',
            background="#f8a51b")
        self.login_frame.grid(row=0, column=0, sticky=(tk.W + tk.E))

        self.file_name = os.path.join(
            os.path.expanduser('~'), "Documents",
            "users.csv"
        )

        if which_login == 'new_user_login':
            self.new_user_login()
        elif which_login == 'existing_user_login':
            self.existing_user_login()
        elif which_login == 'guest_login':
            self.guest_login()

    def existing_user_login(self):

        self.widgets['user_id'] = LabelInput(
            self.login_frame,
            "ваш ID",
            input_class=RequiredEntry,
            label_args={'font': self.label_font, 'style': 'label.TLabel'},
            input_var=tk.StringVar(),

        )
        self.widgets['user_id'].grid(row=0, column=0, columnspan=2)

        self.widgets['password'] = LabelInput(
            self.login_frame,
            "Пароль",
            input_class=RequiredEntry,
            input_var=tk.StringVar(),
            label_args={'font': self.label_font, "style": "label.TLabel"}
        )
        self.widgets['password'].grid(row=1, column=0, columnspan=2)

        self.widgets['submit'] = ttk.Button(
            self.login_frame,
            text="далі",
            style="processor.TButton",
            command=partial(self.read_user, self.widgets)
        )
        self.widgets['submit'].grid(row=2, column=0, columnspan=2)

    def new_user_login(self):

        self.widgets['name'] = LabelInput(
            self.login_frame,
            "Ім'я користувача",
            input_class=RequiredEntry,
            input_var=tk.StringVar(),
            label_args={'font': self.label_font, 'style': 'label.TLabel'}
        )
        self.widgets['name'].grid(row=0, column=0, columnspan=2)

        self.widgets['birth_date'] = LabelInput(
            self.login_frame,
            "Дата народження",
            input_class=DateInput,
            input_args={"locale": 'en_US', "date_pattern": 'yyyy-MM-dd'},
            input_var=tk.StringVar(),
            label_args={'font': self.label_font, 'style': 'label.TLabel'}
        )
        self.widgets['birth_date'].grid(row=1, column=0, columnspan=2)

        self.widgets['user_id'] = LabelInput(
            self.login_frame,
            "Ваш ID",
            input_class=RequiredEntry,
            input_var=tk.StringVar(),
            label_args={'font': self.label_font, 'style': 'label.TLabel'}
        )
        self.widgets['user_id'].grid(row=2, column=0, columnspan=2)

        self.widgets['password'] = LabelInput(
            self.login_frame,
            "Пароль",
            input_class=RequiredEntry,
            input_var=tk.StringVar(),
            label_args={'font': self.label_font, 'style': 'label.TLabel'}
        )
        self.widgets['password'].grid(row=3, column=0, columnspan=2)

        self.widgets['submit'] = ttk.Button(
            self.login_frame,
            text="далі",
            style='processor.TButton',
            command=partial(self.save_user, self.widgets)
        )
        self.widgets['submit'].grid(row=4, column=0, columnspan=2)

    def guest_login(self):

        self.switch_to_main_application('guest')

    def switch_to_main_application(self, user_name: str):

        Window.destroyer(self)

        app = Window(self, user_name)
        app.grid(row=0, padx=10)

    def read_user(self, widgets_dict):

        data = Window.get(widgets_dict)
        if os.path.exists(self.file_name):
            with open(self.file_name, 'r') as users_csv:
                reader = csv.DictReader(users_csv)
                for row in reader:
                    if row['user_id'] == data['user_id'] and row['password'] == data['password']:
                        self.switch_to_main_application(row['name'])
        else:
            messagebox.showerror(
                "user.csv file not found",
                "Create a user first using *New user option*"
            )

    def save_user(self, widgets_dict):

        data = Window.get(widgets_dict)

        newfile: bool = not os.path.exists(self.file_name)

        used_usernames = list()
        with open(self.file_name, 'a+', newline='') as fn:
            if fn.readable():
                fn.seek(0)
                csv_read = csv.DictReader(fn)
                for row in csv_read:
                    used_usernames.append(row['user_id'])

                if data['user_id'] in used_usernames:
                    messagebox.showerror(
                        "Can't create user",
                        f"{data['user_id']} already exists in database.\n"
                        "Please choose a different one."
                    )
                    return
            csv_writer = csv.DictWriter(fn, fieldnames=data.keys())
            if newfile:
                csv_writer.writeheader()
            csv_writer.writerow(data)
            self.switch_to_main_application(data['name'])


class Welcome(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.widgets = dict()

        self.button_style = ttk.Style()

        self.button_frame = ttk.Frame(self)

        self.widgets['user_login'] = ttk.Button(
            self.button_frame,
            text="Якщо ви вже зареєстрований користувач, натисніть тут",
            style='welcome.TButton',
            command=partial(self.login, "existing_user_login")
        )
        self.widgets['user_login'].grid(
            sticky=tk.E, row=0, column=0, padx=(10, 20), ipadx=10, ipady=10)

        self.widgets['guest_login'] = ttk.Button(
            self.button_frame,
            text='Вхід для гостей',
            style='welcome.TButton',
            command=partial(self.login, "guest_login")
        )
        self.widgets['guest_login'].grid(
            sticky=tk.W, row=0, column=1, padx=(10, 20), ipadx=10, ipady=10)

        self.widgets['new_user'] = ttk.Button(
            self.button_frame,
            text="Новий користувач, натисніть тут, щоб зареєструватися",
            style='welcome.TButton',
            command=partial(self.login, "new_user_login")
        )
        self.widgets['new_user'].grid(
            sticky=tk.E, row=0, column=2, padx=(10, 20), ipadx=10, ipady=10)

        self.button_style.configure(
            'welcome.TButton',
            font=Font(
                family='Helvetica Rounded',
                size=20,
                weight='bold',
                slant='italic'
            )
        )

        self.button_frame.grid(
            row=0, column=2, sticky=(tk.W + tk.E), columnspan=2)

    def login(self, which_user: str):
        self.destroy()
        login = LoginPage(which_user)
        login.grid(row=1, padx=10)


class MainApplication(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Calendar Application")
        self.geometry("900x800")

        icon = PhotoImage(file=r"assets/calendar.png")
        self.iconphoto(False, icon)

        main_heading = Font(
            family="Gill Sans MT Shadow",
            size=40,
            weight='bold',
            slant='roman',
        )

        self.greet = ttk.Label(
            self,
            text="Календар",
            font=main_heading,
            justify='right',
            wraplength=800,
            background='#0085f9',
            relief="ridge",
        )
        self.greet.grid(row=0, sticky=(
                tk.W + tk.E), padx=50, pady=(5, 20), ipadx=50)

        self.welcomeframe = Welcome(self)
        self.welcomeframe.grid(row=1, padx=10, pady=(100, 0))
