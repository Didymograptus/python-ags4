#!/usr/bin/env python

import click
from python_ags4 import AGS4
from rich.console import Console
import pkg_resources
import os

# Create rich console for pretty printing
console = Console()

# Get path to standard AGS4 dictionary
path_to_standard_dictionary = pkg_resources.resource_filename('python_ags4', 'Standard_dictionary_v4_1.ags')


@click.group()
def main():
    '''A tool to read, write, and check AGS4 files.
    '''
    pass


@main.command()
@click.argument('input_file', type=click.File('r'))
@click.argument('output_file', type=click.File('w', lazy=False))
# The lazy=False option is used in order to catch errors in the output file path before starting the program
@click.option('-f', '--format_columns', default="true",
              help='Format numeric data based on TYPE values if converting from .xlsx to .ags (true [default] or false)')
@click.option('-d', '--dictionary', type=click.File('r'), default=None,
              help="Path to AGS4 dictionary file. Numeric data will be formatted based on TYPE values from this file if converting from .xlsx to .ags.")
def convert(input_file, output_file, format_columns, dictionary):
    '''Convert .ags file to .xlsx file or vice versa.

    INPUT_FILE   Path to input file. The file should be either .ags or .xlsx

    OUTPUT_FILE  Path to output file. The file should be either .ags or .xlsx

    e.g.
   
    Linux/Mac: ags4_cli convert ~/temp/data.ags ~/temp/data.xlsx

    Windows:   ags4_cli convert c:\Temp\data.ags c:\Temp\data.xlsx

    '''

    input_file = input_file.name
    output_file = output_file.name

    if input_file.endswith('.ags') & output_file.endswith('.xlsx'):
        console.print(f'[green]Opening file... [bold]{input_file}[/bold][/green]')
        console.print(f'[green]Exporting data to... [bold]{output_file}[/bold][/green]')
        print('')

        AGS4.AGS4_to_excel(input_file, output_file)

        console.print('\n[green]File conversion complete! :heavy_check_mark:[/green]\n')

    elif input_file.endswith('.xlsx') & output_file.endswith('.ags'):
        console.print(f'[green]Opening file... [bold]{input_file}[/bold][/green]')
        console.print(f'[green]Exporting data to... [bold]{output_file}[/bold][/green]')
        print('')

        # Process optional arguments
        format_numeric_columns = format_columns.lower() in ['true', 'yes']

        if dictionary is not None:
            dictionary = dictionary.name

        # Call export function
        AGS4.excel_to_AGS4(input_file, output_file, format_numeric_columns=format_numeric_columns,
                           dictionary=dictionary)

        console.print('\n[green]File conversion complete! :heavy_check_mark:[/green]\n')

    elif (input_file.endswith('.ags') & output_file.endswith('.ags')) | (input_file.endswith('.xlsx') & output_file.endswith('.xlsx')):
        file_type = input_file.split('.')[-1]
        console.print(f'[yellow]Both input and output files are of the same type (i.e. [bold].{file_type}[/bold]). No conversion necessary.[/yellow]')

    else:
        console.print('[red]ERROR: Invalid filenames.[/red]')
        console.print('[red]Try "ags4_cli convert --help" to see help and examples.[/red]')



@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output_file', type=click.Path(writable=True), default=None,
              help="Path to save error log")
@click.option('-d', '--dictionary', type=click.Path(exists=True), default=path_to_standard_dictionary,
              help="Path to AGS4 dictionary file.")
def check(input_file, dictionary, output_file):
    '''Check .ags file for error based AGS4 rules.

    INPUT_FILE   Path to .ags file to be checked
    '''

    if input_file.endswith('.ags'):
        console.print(f'[green]Opening file... [bold]{input_file}[/bold][/green]')
        console.print('')

        with console.status("[bold green]Checking file...") as status:
            ags_errors = AGS4.check_file(input_file, standard_AGS4_dictionary=dictionary)

        # Dictionay evaluates to False if empty
        if bool(ags_errors) is False:
            console.print('\n[green]File check complete! No errors found. :heavy_check_mark:[/green]\n')

        else:
            # Count number of entries in error log
            error_count = 0
            for key, val in ags_errors.items():
                error_count += len(val)

            # Print errors to screen if list is short enough.
            if error_count < 100:
                print_to_screen(ags_errors)

                console.print(f'\n[yellow]File check complete! {error_count} errors found![/yellow]')

                if output_file is not None:
                    save_to_file(output_file, ags_errors, input_file, error_count)
                    console.print(f'\n[yellow]Error report saved in {output_file}.[/yellow]\n')

            else:
                console.print(f'\n[yellow]File check complete! {error_count} errors found![/yellow]')
                console.print('\n[yellow]Error report too long to print to screen.[/yellow]')

                if output_file is None:
                    output_dir = os.path.dirname(input_file)
                    output_file = os.path.join(output_dir, 'error_log.txt')

                save_to_file(output_file, ags_errors, input_file, error_count)

                console.print(f'\n[yellow]Error report saved in {output_file}[/yellow]\n')

    else:
        console.print('[red]ERROR: Only .ags files are accepted as input.[/red]')


def print_to_screen(ags_errors):
    '''Print error report to screen.'''
    for key in ags_errors:
        console.print(f'''[underline]{key}[/underline]:''')
        for entry in ags_errors[key]:
            console.print(f'''  Line {entry['line']}\t [bold]{entry['group'].strip('"')}[/bold]\t {entry['desc']}''')
        console.print('')


def save_to_file(output_file, ags_errors, input_file, error_count):
    '''Save error report to file.'''

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        f.write(f'Input file: {input_file}\n')
        f.write(f'{error_count} errors found!\n')
        f.write('\n')

        for key in ags_errors:
            f.write(f'{key}:\n')
            for entry in ags_errors[key]:
                f.write(f'''  Line {entry['line']}\t {entry['group'].strip('"')}\t {entry['desc']}\n''')
            f.write('\n')


if __name__ == '__main__':
    main()
