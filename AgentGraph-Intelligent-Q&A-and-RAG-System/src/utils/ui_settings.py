import gradio as gr


class UISettings:
    """
    Utility class for managing UI settings.
    """
    @staticmethod
    def feedback(data: gr.LikeData):
        """
        Process user feedback on the generated response.

        Parameters:
            data (gr.LikeData): Gradio LikeData object containing user feedback.
        """
        if data.liked:
            print("You upvoted this response: " + data.value)
        else:
            print("You downvoted this response: " + data.value)
