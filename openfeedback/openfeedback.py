import pkg_resources
from xblock.scorable import ScorableXBlockMixin
from xblock.core import XBlock
from xblock.fields import Scope, String, Boolean, List
from xblockutils.studio_editable import StudioEditableXBlockMixin
from web_fragments.fragment import Fragment
from xblockutils.resources import ResourceLoader
import time

loader = ResourceLoader(__name__)


def resource_string(path):
    """Handy helper for getting resources from our kit."""
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")


class OpenFeedbackXBlock(XBlock, ScorableXBlockMixin, StudioEditableXBlockMixin):
    display_name = String(display_name="display_name",
                          default="Feedback aberto",
                          scope=Scope.settings,
                          help="Nome do componente na plataforma")

    prompt = String(display_name="prompt",
                    default="Caso haja algo que aches que possamos fazer de forma diferente ou melhor, aproveita agora para nos dizeres.",
                    scope=Scope.settings,
                    help="Texto que aparece associado a esta caixa de texto de open feedback.")

    students_feedback = List(display_name="students_feedback",
                             scope=Scope.user_state_summary)

    student_submitted = Boolean(display_name="student_submitted",
                                default=False,
                                scope=Scope.user_state)

    editable_fields = ('display_name', 'prompt')

    def student_view(self, _context):
        """
            The view students see
        :param _context:
        :return:
        """
        data = {
            'prompt': self.prompt,
            'student_submitted': self.student_submitted,
            'xblock_id': self._get_xblock_loc()
        }
        if self.show_staff_grading_interface():
            data['is_course_staff'] = True
            data['submissions'] = self.students_feedback

        html = loader.render_django_template('templates/openfeedback.html', data)
        frag = Fragment(html)

        frag.add_javascript(resource_string("static/openfeedback.js"))
        frag.add_css(resource_string("static/openfeedback.css"))
        frag.initialize_js('OpenFeedbackXBlock', data)
        return frag

    @XBlock.json_handler
    def submit_feedback(self, data, _suffix):
        """
            Triggered when the user presses the submit button.
        :param data:
        :param _suffix:
        :return:
        """
        if not self.student_submitted and "student_feedback" in data and data["student_feedback"]:
            self.students_feedback.append({
                'feedback': data["student_feedback"],
                'timestamp': int(time.time())
            })
            self.student_submitted = True
            return {
                'result': 'success'
            }
        return {
            'result': 'error',
            'message': 'Apenas uma submissão por aluno.'
        }

    def _get_xblock_loc(self):
        """Returns trailing number portion of self.location"""
        return str(self.location).split('@')[-1]

    def show_staff_grading_interface(self):
        """
        Return if current user is staff and not in studio.
        """
        in_studio_preview = self.scope_ids.user_id is None
        return getattr(self.xmodule_runtime, 'user_is_staff', False) and not in_studio_preview
