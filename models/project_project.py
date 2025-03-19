from odoo import models

class ProjectProject(models.Model):
    _inherit = 'project.project'

    def copy(self, default=None):
        default = dict(default or {})
        new_project = super(ProjectProject, self).copy(default)

        # Diccionario para mapear las tareas originales con sus copias
        task_mapping = {}

        # Primero, duplicamos las tareas principales y las guardamos en el diccionario
        for task in self.task_ids.filtered(lambda t: not t.parent_id):
            new_task = task.copy({'project_id': new_project.id})
            task_mapping[task.id] = new_task.id

        # Luego, duplicamos las subtareas y las vinculamos correctamente
        for task in self.task_ids.filtered(lambda t: t.parent_id):
            new_task = task.copy({
                'project_id': new_project.id,
                'parent_id': task_mapping.get(task.parent_id.id),  # Mapea la nueva tarea padre
            })
            task_mapping[task.id] = new_task.id

        return new_project
