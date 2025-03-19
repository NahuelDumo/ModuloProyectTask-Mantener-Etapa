from odoo import models

class ProjectTask(models.Model):
    _inherit = 'project.task'

    def copy(self, default=None):
        default = dict(default or {})
        # Mantener la misma etapa en la tarea duplicada
        default['stage_id'] = self.stage_id.id
        return super(ProjectTask, self).copy(default)
