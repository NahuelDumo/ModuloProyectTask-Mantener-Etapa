from odoo import models, fields

class ProjectProject(models.Model):
    _inherit = 'project.project'

    def copy(self, default=None):
        default = dict(default or {})
        new_project = super(ProjectProject, self).copy(default)

        for task in self.task_ids:
            task.copy({'stage_id': task.stage_id.id, 'project_id': new_project.id})

        return new_project
