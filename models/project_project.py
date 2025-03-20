from odoo import models, fields, api, exceptions

class ProjectProject(models.Model):
    _inherit = 'project.project'

    def copy(self, default=None):
        """ Replica el proyecto correctamente sin que la copia se cree frizada """
        default = dict(default or {})

        # 🔹 Evitar que el nuevo proyecto se copie como frizado
        default.setdefault('is_frozen', False)

        # Crear la copia del proyecto
        new_project = super(ProjectProject, self).copy(default)

        if new_project.is_frozen:
            new_project.write({'is_frozen': False})

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
                new_task = self.env['project.task'].browse(task_mapping.get(task.id))
                if new_task:
                    new_task.write({
                        'child_ids': [(6, 0, [
                            task_mapping[child.id] for child in task.child_ids if child.id in task_mapping
                        ])]
                    })
        # **🔹 Programar eliminación de tareas '(copia)' después de que la transacción se complete**
        # self.env.after_commit(lambda: self._eliminar_tareas_copia(new_project.id))
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
