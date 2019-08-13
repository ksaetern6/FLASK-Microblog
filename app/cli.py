from app import app
import os
import click

##
# @name: translate()
# @desc: name of command 'translate' comes from the function and the
#       help messages come from the docstring """ """
# @deco: app.cli.group()
##
@app.cli.group()
def translate():
    """Translation and localization commands."""
    pass

##
# @name: update
# @desc: update runs 2 command line codes and checks if they return O, if they do
#       then a runtime error is raised. update also combines extract and update
#       of pybabel into one command. After the update messages.pot is deleted
# @deco: translate.command()
##
@translate.command()
def update():
    """Update all languages."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel update -i messages.pot -d app/translations'):
        raise RuntimeError('update command failed')
    os.remove('messages.pot')

##
# @name: compile
# @desc: compile CLI for pybabel
# @deco: translate.command()
##
@translate.command()
def compile():
    """Compile all languages"""
    if os.system('pybabel compile -d app/translations'):
        raise RuntimeError('compile command failed')

##
# @name: init
# @desc: uses click.argument decorator to pass value provided 'lang' to
#       a handler function as an argument, then uses the argument in the init command.
# @deco: translate.command()
#        click.argument('lang')
##
@translate.command()
@click.argument('lang')
def init(lang):
    """Initialize a new language"""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system(
        'pybabel init -i messages.pot -d app/translations -l ' + lang):
        raise RuntimeError('init command failed')
    os.remove('messages.pot')

