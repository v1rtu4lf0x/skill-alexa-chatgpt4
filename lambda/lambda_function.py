import logging
import ask_sdk_core.utils as ask_utils
import openai
from openai import OpenAI
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

# Set your OpenAI API key
client = OpenAI(
    api_key="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",
)
#openai.api_key = "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"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

messages = [{"role": "system", "content": "resposta em pt-br"}]

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Bem vindo ao Chat 'Gepetê Quatro'! Qual a sua pergunta?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class GptQueryIntentHandler(AbstractRequestHandler):
    """Handler for Gpt Query Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GptQueryIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        query = handler_input.request_envelope.request.intent.slots["query"].value
        response = generate_gpt_response(query)

        return (
                handler_input.response_builder
                    .speak(response)
                    .ask("Alguma outra pergunta?")
                    .response
            )

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors."""
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Desculpe, não consegui obter uma resposta para esta pergunta. Tente perguntar de outra forma."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Saindo do modo Chat Gepetê."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

def generate_gpt_response(query):
    try:
        messages.append(
            {"role": "user", "content": query},
        )
        response = client.chat.completions.create(
            #model="gpt-4",
            model="gpt-3.5-turbo",
            messages=messages,
            #max_tokens=1000,
            max_tokens=2048,
            n=1,
            stop=None,
            temperature=0
            #request_timeout=7
        )
        #reply = response['choices'][0]['message']['content'].strip()
        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply.strip()})
        return reply
    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GptQueryIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
