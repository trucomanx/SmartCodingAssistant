import os
import subprocess
import tempfile
import shutil

def is_git_in_path():
    """
    Checks if 'git' is available in the system PATH.

    Returns:
        bool: True if 'git' is in PATH, False otherwise.
    """
    return shutil.which("git") is not None

def is_meld_in_path():
    """
    Checks if 'meld' is available in the system PATH.

    Returns:
        bool: True if 'meld' is in PATH, False otherwise.
    """
    return shutil.which("meld") is not None


def get_git_base_dir(path):
    """
    Returns the base directory (root) of the GIT repository that contains the path provided.

    Parameters:
    path (str): Way to a directory inside (or potentially inside) of a Git repository.

    Returns:
    str or None: Absolute path to the root of the git repository if found, otherwise None.
    """
    try:
        resultado = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path,
            capture_output=True,
            text=True,
            check=True
        )
        return resultado.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def show_message(func_msg=None, msg=""):
    """
    Shows a message, either through a personalized function or directly at the terminal.

    Parameters:
    func_msg (Callable or None): Personalized message display function. If None, uses print ().
    msg (str): Message to be displayed.
    """
    if func_msg is None:
        print(msg)
    else:
        func_msg(msg)


def meld_head_vs_current(dir_path, func_msg=None):
    """
    Compares modified files in the working directory with the Git HEAD version using Meld.

    Creates a temporary copy of the files in the HEAD version, and opens Meld to compare with the current files,
    keeping Meld open after the function finishes executing.

    Parameters:
    dir_path (str): Path to a directory within a Git repository.
                    func_msg (callable or None): Function to display messages. If None, uses print().

    Returns:
    str or None: Path to the temporary directory containing the HEAD files if there are modifications,
                or None if there are no modifications or an error occurs.
    """
    if not os.path.isdir(dir_path):
        show_message(func_msg, "PATH is not a directory")
        return None

    path_projeto = get_git_base_dir(dir_path)

    if path_projeto is None:
        show_message(func_msg, "The directory is not a git repository")
        return None

    if not os.path.isdir(os.path.join(path_projeto, ".git")):
        show_message(func_msg, "The directory is not a git repository")
        return None

    try:
        # Obtém arquivos modificados
        resultado = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=path_projeto,
            capture_output=True,
            text=True,
            check=True
        )
        arquivos_modificados = resultado.stdout.strip().split("\n")
        arquivos_modificados = [f for f in arquivos_modificados if f]

        if not arquivos_modificados:
            show_message(func_msg, "Nenhuma modificação encontrada.")
            return None

        # Cria diretório temporário apenas para HEAD
        dir_head = tempfile.mkdtemp(prefix="HEAD_")

        for arq in arquivos_modificados:
            caminho_head = os.path.join(dir_head, arq)
            os.makedirs(os.path.dirname(caminho_head), exist_ok=True)
            try:
                conteudo = subprocess.check_output(["git", "show", f"HEAD:{arq}"], cwd=path_projeto)
                with open(caminho_head, "wb") as f:
                    f.write(conteudo)
            except subprocess.CalledProcessError:
                show_message(func_msg, f"Erro ao extrair HEAD:{arq}")

        # Abre meld (não bloqueante)
        subprocess.Popen(["meld", dir_head, path_projeto])

        return dir_head

    except subprocess.CalledProcessError as e:
        show_message(func_msg, f"Erro ao executar comando Git: {e}")
        return None

if __name__ == "__main__":
    # Exemplo de uso
    PATH = "/home/fernando/Proyectos/PROGRAMACION/GITHUB-SMART/SMART-NEWS-ORGANIZER/SmartNewsOrganizer"
    meld_head_vs_current(PATH)

    # Testando a função get_git_base_dir com diferentes subdiretórios
    print(get_git_base_dir(PATH + "/src"))
    print(get_git_base_dir(PATH + "/.."))

