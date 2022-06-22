import click

@click.command()
@click.option('--name','-n',help="Name of the person to say hello to", required=True, prompt="Your name, please?\n")
# @click.argument('number')
def getStart(name):
    '''
    This prints "CLI Created!!! Hello {name}!"
    '''
    print("CLI Created!!! Hello " + name + "!")
