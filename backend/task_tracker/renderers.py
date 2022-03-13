from rest_framework.renderers import JSONRenderer


class CustomRenderer(JSONRenderer):
    """
    For converting response data into format:
    {
        "success": <True/False>,
        "msg": "<message>",
    }
    """
    message_201 = "Created!"
    message_200 = "Success"
    message_400 = "Incorrect parameters"
    message_401 = "Failed to authenticate"
    message_403 = "Forbidden"
    default_message = "Some error occured"

    def get_response_data(self, data, status_code):
        success = status_code < 400
        message = getattr(self, "message_%s" % status_code, self.default_message)
        show_data = status_code in (200, 400)
        response = {
            "success": success,
        }
        if message:
            response["msg"] = message
        if show_data:
            response["data"] = data
        return response

    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context['response'].status_code
        response = self.get_response_data(data, status_code)
        return super(CustomRenderer, self).render(response, accepted_media_type, renderer_context)


class TeamRenderer(CustomRenderer):
    message_201 = "Team created successfully"


class TaskRenderer(CustomRenderer):
    message_201 = "Task created successfully"
