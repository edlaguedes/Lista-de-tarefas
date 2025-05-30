import flet as ft
import sqlite3

class ToDo:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.window_width = 350
        self.page.window_height = 450
        self.page.window_resizable = False
        self.page.window_always_on_top = True
        self.page.title = 'LISTA DE TAREFAS'
        self.task = ''
        self.view = 'all'

        # Inicializa banco de dados
        self.db_execute("CREATE TABLE IF NOT EXISTS tasks(name TEXT, status TEXT)")
        self.results = self.db_execute('SELECT * FROM tasks')

        self.main_page()

    def db_execute(self, query, params=[]):
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute(query, params)
            con.commit()
            return cur.fetchall()

    def set_value(self, e):
        self.task = e.control.value

    def add(self, e, input_task):
        name = self.task
        status = 'incomplete'
        if name:
            self.db_execute('INSERT INTO tasks VALUES (?, ?)', [name, status])
            input_task.value = ''
            self.results = self.db_execute('SELECT * FROM tasks')
            self.update_task_list()

    def checked(self, e):
        task_name = e.control.label
        is_checked = e.control.value

        status = "complete" if is_checked else "incomplete"
        self.db_execute('UPDATE tasks SET status = ? WHERE name = ?', [status, task_name])

        if self.view == 'all':
            self.results = self.db_execute('SELECT * FROM tasks')
        else:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = ?', [self.view])
        self.update_task_list()

    def tasks_container(self):
             return ft.Container(
                height=self.page.height * 0.6,
                content=ft.Column(
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Checkbox(
                                    label=res[0],
                                    value=(res[1] == 'complete'),
                                    on_change=self.checked
                                ),
                                ft.IconButton(
                                    icon="delete",
                                    icon_color="red",
                                    data=res[0],  # passa o nome da tarefa para o botão
                                    on_click=self.delete_task
                                )
                            ]
                        ) for res in self.results
                    ],
                    scroll=ft.ScrollMode.ALWAYS
                )
            )

    def update_task_list(self):
        self.page.controls[-1] = self.tasks_container()
        self.page.update()

    def tabs_changed(self, e):
        index = e.control.selected_index
        if index == 0:
            self.view = 'all'
            self.results = self.db_execute('SELECT * FROM tasks')
        elif index == 1:
            self.view = 'incomplete'
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = "incomplete"')
        elif index == 2:
            self.view = 'complete'
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = "complete"')
        self.update_task_list()

    def main_page(self):
        input_task = ft.TextField(
            hint_text="Digite aqui uma tarefa",
            expand=True,
            on_change=self.set_value
        )

        input_bar = ft.Row(
            controls=[
                input_task,
                ft.FloatingActionButton(
                    icon="add",
                    on_click=lambda e: self.add(e, input_task)
                )
            ]
        )

        tabs = ft.Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[
                ft.Tab(text="Todos"),
                ft.Tab(text="Em andamento"),
                ft.Tab(text="Concluído")
            ]
        )

        tasks = self.tasks_container()

        self.page.add(input_bar, tabs, tasks)

    def delete_task(self, e):
        task_name = e.control.data  # pega o nome da tarefa do botão
        self.db_execute("DELETE FROM tasks WHERE name = ?", [task_name])
        self.results = self.db_execute('SELECT * FROM tasks')  # recarrega tarefas
        self.update_task_list()
# Inicialização do aplicativo
ft.app(target=ToDo)
