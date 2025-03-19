from odoo import models, fields, api, exceptions

class ProjectProject(models.Model):
    _inherit = 'project.project'

    def copy(self, default=None):
        """ Replica el proyecto correctamente y elimina tareas con '(copia)' en el nombre """
        default = dict(default or {})

        # Crear la copia del proyecto
        new_project = super(ProjectProject, self).copy(default)

        # Mapeo para asociar tareas originales con sus copias
        task_mapping = {}

        # Copiar todas las tareas del proyecto original
        for task in self.task_ids:
            new_task = task.copy({
                'project_id': new_project.id,  # Asignar la tarea al nuevo proyecto
                'parent_id': False  # Evitar problemas de referencia con subtareas
            })
            task_mapping[task.id] = new_task.id  # Guardar la relación tarea original -> tarea copiada

        # Asignar correctamente las subtareas
        for task in self.task_ids:
            if task.child_ids:
                new_task = self.env['project.task'].browse(task_mapping[task.id])
                new_task.write({
                    'child_ids': [(6, 0, [task_mapping[child.id] for child in task.child_ids if child.id in task_mapping])]
                })

        # Eliminar tareas que contienen "(copia)" en el nombre
        tasks_to_delete = self.env['project.task'].search([
            ('project_id', '=', new_project.id),
            ('name', 'ilike', '(copia)')
        ])
        tasks_to_delete.unlink()

        return new_project

    @api.model_create_multi
    def create(self, vals_list):
        """ Evita agregar tareas a proyectos frizados """
        for vals in vals_list:
            if 'project_id' in vals:
                project = self.env['project.project'].browse(vals['project_id'])
                if project.is_frozen:
                    raise exceptions.ValidationError("No puedes agregar tareas a un proyecto frizado.")
        return super(ProjectProject, self).create(vals_list)
