from odoo import models, fields, api, exceptions

class ProjectProject(models.Model):
    _inherit = 'project.project'

    def copy(self, default=None):
        """ Copia proyectos plantillas desfrizándolos temporalmente para permitir la duplicación. """
        default = dict(default or {})
        default.setdefault('is_frozen', False)  # La copia nunca debe estar frizada

        # 🔹 Guardar estado original del proyecto antes de copiar
        was_frozen = self.is_frozen

        # 🔹 **Desfrizar temporalmente la plantilla**
        if was_frozen:
            self.write({'is_frozen': False})

        try:
            # 🔹 **Crear la copia del proyecto**
            new_project = super(ProjectProject, self).copy(default)
            new_project.write({'is_frozen': False})  # Asegurar que la copia no esté frizada

            task_mapping = {}

            # 🔹 **Copiar todas las tareas del proyecto original**
            for task in self.task_ids:
                new_task = task.with_context({'allow_frozen_project': True}).copy({
                    'project_id': new_project.id,
                    'parent_id': False
                })
                task_mapping[task.id] = new_task.id

            # 🔹 **Asignar correctamente las subtareas**
            for task in self.task_ids:
                if task.child_ids:
                    new_task = self.env['project.task'].browse(task_mapping.get(task.id))
                    if new_task:
                        new_task.write({
                            'child_ids': [(6, 0, [
                                task_mapping[child.id] for child in task.child_ids if child.id in task_mapping
                            ])]
                        })

        finally:
            # 🔹 **Volver a frizar el proyecto original**
            if was_frozen:
                self.write({'is_frozen': True})

        return new_project

class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model_create_multi
    def create(self, vals_list):
        """ Evita agregar tareas a proyectos frizados, salvo si viene de una copia """
        if not self.env.context.get('allow_frozen_project', False):
            for vals in vals_list:
                if 'project_id' in vals:
                    project = self.env['project.project'].browse(vals['project_id'])
                    if project.is_frozen:
                        raise exceptions.ValidationError("No puedes agregar tareas a un proyecto frizado.")
        
        return super(ProjectTask, self).create(vals_list)
