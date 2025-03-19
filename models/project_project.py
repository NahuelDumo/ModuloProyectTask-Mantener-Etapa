from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    def copy(self, default=None):
        """ Crea una réplica exacta del proyecto SIN tocar el original """
        default = dict(default or {})

        # Copiar el proyecto
        new_project = super(ProjectProject, self).copy(default)

        # Diccionario para mapear tareas originales con sus copias
        task_mapping = {}

        # Copiar cada tarea asociándola al nuevo proyecto y mantener sus datos
        for task in self.task_ids:
            new_task = task.copy({
                'project_id': new_project.id,  # Asociar la nueva tarea al nuevo proyecto
                'parent_id': False  # Inicialmente sin padre para evitar problemas de referencia
            })
            task_mapping[task.id] = new_task.id  # Guardar referencia entre original y copia

        # Ajustar las relaciones de subtareas en la copia
        for task in self.task_ids:
            if task.child_ids:
                copied_task = self.env['project.task'].browse(task_mapping[task.id])
                copied_task.write({
                    'child_ids': [(6, 0, [task_mapping[child.id] for child in task.child_ids if child.id in task_mapping])]
                })

        return new_project
