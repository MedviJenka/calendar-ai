import asyncio
from api import AssistantFnc
from dotenv import load_dotenv
from dataclasses import dataclass
from livekit.plugins import openai, silero
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm, JobProcess

load_dotenv()


@dataclass
class App:

    name: str

    def prewarm(self, proc: JobProcess):
        proc.userdata["vad"] = silero.VAD.load()
        return proc.userdata["vad"]

    async def entrypoint(self, ctx: JobContext) -> None:
        initial_ctx = llm.ChatContext().append(
            role="system",
            text=(
                "You are a voice assistant created by LiveKit. Your interface with users will be voice. "
                "You should use short and concise responses, and avoiding usage of un-pronouncable punctuation."
            ),
        )
        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
        fnc_ctx = AssistantFnc()

        assistant = VoiceAssistant(
            vad=self.prewarm(JobProcess()),  # silero.VAD.load(),
            stt=openai.STT(),
            llm=openai.LLM(),
            tts=openai.TTS(),
            chat_ctx=initial_ctx,
            fnc_ctx=fnc_ctx,
        )
        assistant.start(ctx.room)

        await asyncio.sleep(.1)
        await assistant.say(source=f"hey {self.name}, how can i assist you?", allow_interruptions=True)


app = App(name='jenia ha gever')
if __name__ == "__main__":
    try:
        cli.run_app(WorkerOptions(entrypoint_fnc=app.entrypoint))
    finally:
        import os
        os.system('py -m main start')