from dataclasses import dataclass


@dataclass
class DialogPart:
    caster: str
    dialogs: str


def parse_dialog_file(file_path='assets/overlay/dialogs/dialogs.txt'):
    """
    Lit le fichier de dialogues et renvoie un dictionnaire des dialogues.
    Le format du fichier est: identifiant#speaker1#texte1#speaker2#texte2...
    """
    dialogs = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split('#')
                if len(parts) < 3:  # Au minimum: id, speaker, texte
                    continue

                dialog_id = parts[0]
                dialog_parts = []

                # Traiter les paires (speaker, texte)
                i = 1
                while i < len(parts) - 1:
                    speaker = parts[i]
                    dialog_text = parts[i + 1]
                    dialog_parts.append(DialogPart(speaker, dialog_text))
                    i += 2

                dialogs[dialog_id] = dialog_parts
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier de dialogues: {e}")

    return dialogs


def dialogs_data():
    """
    Renvoie le dictionnaire de tous les dialogues.
    """
    return parse_dialog_file()