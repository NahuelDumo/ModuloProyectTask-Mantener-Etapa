from odoo import models

class ProjectProject(models.Model):
    _inherit = 'project.project'

    def copy(self, default=None):
        default = dict(default or {})
        new_project = super(ProjectProject, self).copy(default)

        # Asegurar que las tareas del nuevo proyecto conserven su etapa
        for task in new_project.task_ids:
            task.write({'stage_id': task._origin.stage_id.id})

        return new_project
