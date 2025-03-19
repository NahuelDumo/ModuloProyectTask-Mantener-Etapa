from odoo import models, fields, api, exceptions

class ProjectProject(models.Model):
    _inherit = 'project.project'

    is_frozen = fields.Boolean(string="Proyecto Frizado", default=False)

    def copy(self, default=None):
        """ Crea una réplica exacta del proyecto SIN modificar el original """
        default = dict(default or {})
        default['is_frozen'] = False  # El nuevo proyecto NO debe estar frizado

        # Crear la copia del proyecto
        new_project = super(ProjectProject, self).copy(default)

        task_mapping = {}

        # Copiar cada tarea y asignarla al nuevo proyecto
        for task in self.task_ids:
            new_task = task.copy({
                'project_id': new_project.id,
                'parent_id': False  # Evitamos problemas de referencia
            })
            task_mapping[task.id] = new_task.id

        # Mantener relaciones de subtareas
        for task in self.task_ids:
            if task.child_ids:
                copied_task = self.env['project.task'].browse(task_mapping[task.id])
                copied_task.write({
                    'child_ids': [(6, 0, [task_mapping[child.id] for child in task.child_ids if child.id in task_mapping])]
                })

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
