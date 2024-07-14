import pexpect
import argparse
import importlib
from pathlib import Path
from pygments.styles.vim import VimStyle
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import style_from_pygments_cls
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.application.current import get_app
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.key_binding import KeyBindings


parser = argparse.ArgumentParser(description='単純なコンソールを、洗練された REPL に変換します')
parser.add_argument('command', help='The command to run, e.g.: R, python, agscript')
parser.add_argument('cmd_prompt', help='Prompt of the original shell, e.g.: "> " for R, "aggressor> " for agscript')
parser.add_argument('-m', '--multiline', action='store_true', help='Support mutiline mode? Use Alt-Enter to send command when enabled')
parser.add_argument('-s', '--syntax-lexer', default='pygments.lexers.perl.PerlLexer', help='Syntax highlighting lexer')
parser.add_argument('-c', '--cmd-history-file', default="~/.local/share/repl-history", help='Command history file path used for autocompletion')
parser.add_argument('-w', '--working-dir', default='./', help='The working directory of the REPL')
args = parser.parse_args()


def load_lexer(clsname: str):
    """Load Pygments (syntax highlighting) Lexer class by name

    Args:
      Pygments lexer class name

    Find available lexers at [Pygments Lexer List](https://pygments.org/docs/lexers/)

    Returns:
      Pygments lexer class object

    Example:
      load_lexer('pygments.lexers.perl.PerlLexer')
    """
    modname = clsname.rsplit('.', 1)[0]
    clsname = clsname.rsplit('.', 1)[1]
    print(f'Syntaxhervorhebungsklasse {clsname} aus Modul {modname} laden.\n')
    lexmod = importlib.import_module(modname)
    return PygmentsLexer(getattr(lexmod, clsname))


def prompt_continuation(width, line_number, is_soft_wrap):
    """Set continuation symbol in multiline mode

    Here the default value '.' is used.
    """
    return '.' * width


def run(session, cmd_prompt, ml, synlexer):
    """Run commands

    Args:
      session: prompt session;
      cmd_prompt: string, command prompt of the underlying REPL
      ml: boolean;
      lexer: syntax highlight lexer;

    Returns:
      Texts user input
    """
    bindings = KeyBindings()

    @bindings.add('f4')
    def _(event):
        " Toggle between Emacs and Vi mode. "
        app = event.app

        if app.editing_mode == EditingMode.VI:
            app.editing_mode = EditingMode.EMACS
        else:
            app.editing_mode = EditingMode.VI

    @bindings.add('c-d')
    def _(event):
        " Exit when `c-d` is pressed. "
        event.app.exit()

    def bottom_toolbar():
        " Display the current input mode. "
        text = 'Vi' if get_app().editing_mode == EditingMode.VI else 'Emacs'
        return [
            ('class:toolbar', ' [F4] %s ' % text)
        ]

    return session.prompt(cmd_prompt,
                          multiline=ml,
                          prompt_continuation=prompt_continuation,
                          lexer=synlexer,
                          style=style_from_pygments_cls(VimStyle),
                          auto_suggest=AutoSuggestFromHistory(),
                          key_bindings=bindings,
                          bottom_toolbar=bottom_toolbar)

def main():
    p = pexpect.spawn(args.command, cwd=args.working_dir)
    print(f'Willkommen beim REPL Enhancer\n私はアプリケーション {args.command} の代理人です\n')
    hist_file_path = Path(args.cmd_history_file).expanduser()
    if not hist_file_path.parent.exists():
        hist_file_path.parent.mkdir(parents=True)
    print(f'Save/load command history from {args.cmd_history_file}.')
    sn = PromptSession(history=FileHistory(hist_file_path))
    lexer = load_lexer(args.syntax_lexer)

    while True:
        p.expect(args.cmd_prompt)
        print(p.before.decode('utf-8').strip())
        answer = run(sn, args.cmd_prompt, args.multiline, lexer)
        if (answer is None) or (answer == 'exit'):
            break
        p.sendline(answer)

    print('Tạm biệt.')
    p.close()


if __name__ == '__main__':
    main()
