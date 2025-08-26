import os
import click
from getAttributes import getElements
from toCSV import toCSV
from cleanData import *
from Time import *
from stats import *
from Koordinates import *
from Map import *
from Persons import *

@click.group()
def cli():
    "Creates a folder with all relevant subfolders for the scan"
    pass

@cli.command()
@click.option('--path', prompt='Project directory', type=click.Path(), help='Path to the project directory.')
def new_project(path):
    "Create a new project folder with necessary subfolders."
    csv_dir = os.path.join(path, "CSV")
    count_dir = os.path.join(path, "Counts")

    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(count_dir, exist_ok=True)

    click.echo(f"Project created at: {path}")
    click.echo(f"CSV folder: {csv_dir}")
    click.echo(f"Counts folder: {count_dir}")

@cli.command()
@click.option('--source', prompt='XML source folder', type=click.Path(exists=True), help='Folder containing XML files.')
@click.option('--project', prompt='Project folder', type=click.Path(exists=True), help='Project directory to save CSVs.')
def import_xml(source, project):
    "reads all XML files of a surveillance and saves them as a CSV file in the project"
    if not os.path.isfile(os.path.join(project,"elements.txt")):
        # auto-detect and prompt
        all_elements = getElements(source)
        click.echo("Available elements found:")
        for i, el in enumerate(all_elements):
            click.echo(f"{i + 1}: {el}")

        choices = click.prompt("Enter comma-separated numbers of elements to include", type=str)
        indices = [int(x.strip()) - 1 for x in choices.split(",")]
        selected = [all_elements[i] for i in indices]
        
        with open(os.path.join(project, "elements.txt"), "w") as f:
            for el in selected:
                f.write(f"{el}\n")
    else:
        with open(os.path.join(project, "elements.txt"), "r") as f:
            selected = [line.strip() for line in f if line.strip()]

    csv_dir = os.path.join(project, "CSV")
    os.makedirs(csv_dir, exist_ok=True)

    toCSV(source, csv_dir, selected, "</ResponseRecord>")
    click.echo(f"CSV files created in: {csv_dir}")


@cli.command()
@click.option('--project', prompt='Project folder', type=click.Path(exists=True), help='Project directory.')
def remove_double(project):
    "Removes entries that appear multiple times in the CSV files"
    csv_dir = os.path.join(project, "CSV")
    elements_path = os.path.join(project, "elements.txt")

    with open(elements_path, "r") as f:
        elements = [line.strip() for line in f if line.strip()]

    removedouble(csv_dir, elements)
    click.echo(f"Duplicates removed from CSV files in: {csv_dir}")


@cli.command()
@click.option('--project', prompt='Project folder', type=click.Path(exists=True), help='Project directory.')
@click.option('--field', prompt='Field to clean', help='The element (column) to remove empty entries from.')
def remove_empty(project, field):
    "Removes entries that have no value for a specific attribute"
    csv_dir = os.path.join(project, "CSV")
    elements_path = os.path.join(project, "elements.txt")

    with open(elements_path, "r") as f:
        elements = [line.strip() for line in f if line.strip()]

    if field not in elements:
        click.echo(f"'{field}' not found in elements.txt. Available fields: {', '.join(elements)}")
        return

    removeWithout(csv_dir, elements, field)
    click.echo(f"Removed entries with empty '{field}' from CSV files in: {csv_dir}")


@cli.command()
@click.option('--project', prompt='Project folder', type=click.Path(exists=True), help='Project directory.')
@click.option('--field', prompt='Field to analyze', help='The element to calculate mean, median, and mode for.')
def mean(project, field):
    "Calculates average, median, and modal value for an attribute"
    csv_dir = os.path.join(project, "CSV")
    elements_path = os.path.join(project, "elements.txt")

    with open(elements_path, "r") as f:
        elements = [line.strip() for line in f if line.strip()]

    if field not in elements:
        click.echo(f"'{field}' not found in elements.txt. Available fields: {', '.join(elements)}")
        return

    avg, median, mode = Mean(elements, field, csv_dir)

    click.echo(f"Statistics for '{field}':")
    click.echo(f"Mean   : {avg}")
    click.echo(f"Median : {median}")
    click.echo(f"Mode   : {mode}")


@cli.command()
@click.option('--project', prompt='Project folder', type=click.Path(exists=True), help='Project directory.')
@click.option('--field', prompt='Field to analyze', help='The field to get top N values from.')
@click.option('--n', default=3, show_default=True, type=int, help='Number of top values to show.')
@click.option('--mode', type=click.Choice(['min', 'max']), prompt='Show min or max values?', help='Whether to show min or max values.')
def min_max(project, field, n, mode):
    "returns the n largest or smallest values of an attribute"
    csv_dir = os.path.join(project, "CSV")
    elements_path = os.path.join(project, "elements.txt")

    with open(elements_path, "r") as f:
        elements = [line.strip() for line in f if line.strip()]

    if field not in elements:
        click.echo(f"'{field}' not found in elements.txt. Available fields: {', '.join(elements)}")
        return

    what = 1 if mode == "min" else 2
    results = getMinMax(what, n, elements, field, csv_dir)

    click.echo(f"Top {n} {mode.upper()} values for '{field}':")
    for i, val in enumerate(results, 1):
        click.echo(f"  {i}. {val}")



@cli.command()
@click.option('--project', prompt='Project folder', type=click.Path(exists=True), help='Project directory.')
@click.option('--field', prompt='Field to count', help='The field to count occurrences of.')
def counts(project, field):
    "lists all values that an attribute has and shows how often they occur"
    csv_dir = os.path.join(project, "CSV")
    count_dir = os.path.join(project, "Counts")
    elements_path = os.path.join(project, "elements.txt")
    output_file = os.path.join(count_dir, f"{field}.csv")

    with open(elements_path, "r") as f:
        elements = [line.strip() for line in f if line.strip()]

    if field not in elements:
        click.echo(f"'{field}' not found in elements.txt. Available fields: {', '.join(elements)}")
        return

    if not os.path.isfile(output_file):
        counter = calc(csv_dir, elements, field)
        array = counter.most_common()
        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([field, "count"])
            writer.writerows(array)

    temp_elements = [field, "count"]
    avg, median, mode = Mean(temp_elements, "count", count_dir)

    with open(output_file, "r") as f:
        row_count = sum(1 for row in f if row.strip()) - 1

    click.echo(f"Counted {row_count} unique values for field '{field}':")
    click.echo(f"Mean   : {avg}")
    click.echo(f"Median : {median}")
    click.echo(f"Mode   : {mode}")


@cli.command()
@click.option('--project', prompt='Project folder', type=click.Path(exists=True), help='Project directory.')
@click.option('--start-field', prompt='Start time field', help='Field that contains the start timestamp.')
@click.option('--end-field', prompt='End time field', help='Field that contains the end timestamp.')
def time_range(project, start_field, end_field):
    "shows when the first entry began, the last one ended and the time that passed in between"
    csv_dir = os.path.join(project, "CSV")
    elements_path = os.path.join(project, "elements.txt")

    with open(elements_path, "r") as f:
        elements = [line.strip() for line in f if line.strip()]

    for field in (start_field, end_field):
        if field not in elements:
            click.echo(f"'{field}' not found in elements.txt. Available fields: {', '.join(elements)}")
            return

    start, stop, difference = getTimeRange(csv_dir, elements, start_field, end_field)

    click.echo(f"Time Range:")
    click.echo(f"First Entry : {start}")
    click.echo(f"Last Entry  : {stop}")
    click.echo(f"Difference  : {difference}")


@cli.command()
@click.option('--project', prompt='Project folder', type=click.Path(exists=True), help='Project directory.')
@click.option('--start-field', prompt='Start time field', help='Field that contains the start timestamp.')
@click.option('--end-field', prompt='End time field', help='Field that contains the end timestamp.')
def heatmap(project, start_field, end_field):
    "creates a heat map with the distribution of entries over days and their hours"
    csv_dir = os.path.join(project, "CSV")
    elements_path = os.path.join(project, "elements.txt")

    with open(elements_path, "r") as f:
        elements = [line.strip() for line in f if line.strip()]

    for field in (start_field, end_field):
        if field not in elements:
            click.echo(f"'{field}' not found in elements.txt. Available fields: {', '.join(elements)}")
            return

    getheatmap(csv_dir, elements, start_field, end_field)
    click.echo("Heatmap generated.")


@cli.command()
@click.option('--project', prompt='Project folder', type=click.Path(exists=True), help='Project directory.')
@click.option('--latitude-field', prompt='Latitude field', help='Field name for latitude.')
@click.option('--longitude-field', prompt='Longitude field', help='Field name for longitude.')
@click.option('--format', type=click.Choice(['1', '2']), prompt='Coordinate format (1=Decimal Degrees, 2=Degrees Decimal Minutes)', help='Coordinate format: (1=Decimal Degrees, 2=Degrees Decimal Minutes).')
def add_coordinates(project, latitude_field, longitude_field, format):
    "creates a list with all coordinates from the dataset"
    csv_dir = os.path.join(project, "CSV")
    elements_path = os.path.join(project, "elements.txt")
    output_file = os.path.join(project, "Koordinates.csv")

    with open(elements_path, "r") as f:
        elements = [line.strip() for line in f if line.strip()]

    for field in (latitude_field, longitude_field):
        if field not in elements:
            click.echo(f"'{field}' not found in elements.txt. Available fields: {', '.join(elements)}")
            return

    koordformat = int(format)
    counter = getKoordinates(csv_dir, elements, latitude_field, longitude_field, koordformat)

    if not os.path.isfile(output_file):
        with open(output_file, "w", newline="") as f:
            f.write("Latitude,Longitude,Original Latitude,Original Longitude,count\n")

    with open(output_file, "a", newline="") as f:
        for key, count in counter.items():
            line = f"{key},{count}\n"
            f.write(line)

    click.echo(f"Coordinates added to {output_file}")


@cli.command()
@click.option('--project', prompt='Project folder', type=click.Path(exists=True), help='Project directory.')
def create_map(project):
    "creates an interactive HTML map with all coordinates from the coordinate list"
    createMap(project)
    click.echo(f"Coordinates added to {os.path.join(project, 'Map.html')}")

@cli.command()
@click.option('--project', prompt='Project folder', type=click.Path(exists=True), help='Project directory.')
@click.option('--element', prompt='Field testing for uniqueness', help='This is the Attribute to be tested for mapping.')
@click.option('--compairto', prompt='Attribute to map on Key Attribute', help='This is the Attribute to be tested for mapping.')
def testkeys(project, element, compairto):
    """Compares two possible keys to find which one is suitable."""
    elements_path = os.path.join(project, "elements.txt")
    csv_dir = os.path.join(project, "CSV")
    
    with open(elements_path, "r") as f:
        elements = [line.strip() for line in f if line.strip()]
    
    for field in (element, compairto):
        if field not in elements:
            click.echo(f"'{field}' not found in elements.txt. Available fields: {', '.join(elements)}")
            return

    click.echo(hasMultiple(csv_dir, elements, element, compairto))
    click.echo(hasMultiple(csv_dir, elements, compairto, element))


@cli.command()
@click.option('--project', prompt='Project folder', type=click.Path(exists=True), help='Project directory.')
def personlist(project):
    "creates a list of all the people who appear in the data"
    csv_dir = os.path.join(project, "CSV")

    Persons = ProfileList(project,csv_dir, False, False,0)

    for person in Persons:
        locations = set()
        for msisdn in person.mSISDNList:
            loc = LocatePhoneNumber(msisdn)
            locations.add(loc)
            person.location = ";".join(sorted(locations)) if locations else ""

    with open(os.path.join(project,"PersonenListe.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["PersonID","Entries", "iMSIs", "iMEIs", "mSISDNs","nationality"])  # header
        for idx, person in enumerate(Persons, start=1):
            writer.writerow([
                idx,
                person.line_count,
                ";".join(person.iMSIList),
                ";".join(person.iMEIList),
                ";".join(person.mSISDNList),
                person.location
        ])
            
    with open(os.path.join(project,"badNumbers.txt"), "w", newline="") as f:
        f.writelines(badNumbers)

    print(f"Saved merged person list to {os.path.join(project, "personenliste.csv")}")

@cli.command()
@click.option('--project', prompt='Project folder', type=click.Path(exists=True), help='Project directory.')
def count_nations(project):
    "counts for the nationalities inside the Personlist"
    with open(os.path.join(project,"PersonenListe.csv"), "r") as f:

        data = []

        csvFile = csv.reader(f, delimiter=",")
        next(csvFile, None)
        for line in csvFile:
            value = line[5]

            if value:
                data.append(value)
            elif line[4]:
                data.append("badNumber")
            else:
                data.append("noNumber")
                    
        counter = Counter(data)


    array = counter.most_common()
    with open(os.path.join(project,"Counts","nationalities.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["nationality", "count"])
        writer.writerows(array)

@cli.command()
@click.option('--firstproject', prompt='first Project folder', type=click.Path(exists=True), help='Project directory.')
@click.option('--secondproject', prompt='second Project folder', type=click.Path(exists=True), help='Project directory.')
@click.option('--element', prompt='element to be checked', help='element to check for existing values in two projects')
def check_cross_project(firstproject,secondproject,element):
    "Checks whether values of an attribute occur in multiple projects"

    csv_dir_firstproject = os.path.join(firstproject, "CSV")
    csv_dir_secondproject = os.path.join(secondproject, "CSV")

    elements_path_firstproject = os.path.join(firstproject, "elements.txt")
    elements_path_secondproject = os.path.join(secondproject, "elements.txt")

    with open(elements_path_firstproject, "r") as f:
        firstelements = [line.strip() for line in f if line.strip()]

    with open(elements_path_secondproject, "r") as f:
        secondelements = [line.strip() for line in f if line.strip()]

    firstset = getUnique(csv_dir_firstproject,firstelements,element)
    secondset = getUnique(csv_dir_secondproject,secondelements,element)

    result = firstset.intersection(secondset)

    if not bool(result):
        click.echo("There are no values that exist in both projects")
    else:
        click.echo("there are " + str(len(result))+ " values existing in both projects")
        click.echo(result)

@cli.command()
@click.option('--project', prompt='Project folder', type=click.Path(exists=True), help='Project directory.')
@click.option('--longsequence', type=click.Choice(['yes', 'no']), prompt='cut sequence in time periods?', help='Whether to cut the sequence in time periods or not')
def movement_sequence(project,longsequence):
    "creates a movement pattern for each person in the dataset"
    csv_dir = os.path.join(project, "CSV")

    if longsequence == "yes":
        empty = click.prompt("Symbol for empty periods", type=str)
        time = click.prompt("length of a time period in minutes", type=int)
        SequenceList = ProfileList(project,csv_dir, True,True,empty,time)
    else:
        SequenceList = ProfileList(project,csv_dir, True,False,"X",60)

    with open(os.path.join(project,"Bewegungsmuster.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["PersonID","Sequence"])  # header
        for idx, person in enumerate(SequenceList, start=1):

            if longsequence == "yes":
                sequence = "|".join(person.sequences)
            else: 
                sequence = ""
                last = None
                for v in person.visits:
                    loc = v["location"]
                    if loc != last:
                        sequence += loc
                    last = loc  

            writer.writerow([
                idx,
                sequence
            ])
    
if __name__ == '__main__':
    cli()


