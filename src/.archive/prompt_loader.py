class PromptLoader():
    def __init__(self, base_path: str):
          self.base_path = base_path

    def load_prompt(self, file: str) -> str:
        """
        Loads the orchestrator prompt from a predefined file.

        Args:
            type: The type of prompt to load: "system", "human"

        Returns:
            The content of the orchestrator prompt as a string.

        Raises:
            Prints an error message if the file is not found or another exception occurs.
        """

        full_path = f"{self.base_path}/{file}"

        try:
            with open(full_path, "r", encoding="utf-8") as file:
                prompt = file.read()
        except FileNotFoundError:
            print(f"Error: The file '{full_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

        return prompt