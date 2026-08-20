from numbergame.game import UI, Signal


class CLI(UI):

    def get_guess(self, prompt: str) -> str:
        return input(prompt)

    def provide_feedback(self, signal: Signal, prompt: str) -> None:
        self.echo(prompt)

    def echo(self, message: str) -> None:
        print(message)
