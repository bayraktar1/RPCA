"""
Dogukan Bayraktar
Python Version 3.9.7
Creates three separate GTF files containing the three,
two and no matches from the GffCompare tracking file.
"""
from collections import defaultdict


def categorize_tracking(tracking_file):
    """
    Gets transcript id's for each match in the tracking file and sorts
    them into three dictionaries.

    :param tracking_file: tracking file from GffCompare
    :return: tcons_xxx (key): [transcript_id,
                               transcripts_id,
                               transcript_id] (value)
    """
    with open(tracking_file, 'r') as tracking:
        three_match, two_match, no_match = {}, {}, {}
        for line in tracking:
            line = line.split()
            # section containing the transcript match information
            transcripts = line[4::]
            transcript_ids = []

            count = 0
            for transcript in transcripts:
                # No transcript present in position
                if transcript == '-':
                    count += 1
                    transcript_id = transcript
                # transcript present
                else:
                    transcript_id = transcript.split('|')[1]
                transcript_ids.append(transcript_id)

            # 1 transcript was not present
            if count == 1:
                two_match[line[0]] = transcript_ids
            # 2 transcripts were not present
            elif count == 2:
                no_match[line[0]] = transcript_ids
            # all transcripts are present
            else:
                three_match[line[0]] = transcript_ids
    return three_match, two_match, no_match


def gtf(file):
    """
    Reads in GTF file and puts transcripts with its exons in a
    dictionary.
    :param file: GTF file.
    :return: Key: Transcript_id Value: Lines that contain the id.
    """
    gtf_dict = defaultdict(list)
    with open(file) as GTF:
        for line in GTF:
            # skip comments
            if line.startswith("#"):
                continue
            # skip genes
            if line.split()[2] == "gene":
                continue
            transcript_id = line.split()[11][1:-2]
            gtf_dict[transcript_id].append(line.strip('\n'))
    return gtf_dict


def write(tracking_dict, oxford, flair, talon, outfile):
    """
    Creates new sorted GTF file containing all matched transcripts.
    :param tracking_dict: Dictionary with transcript id's
    :param oxford: GTF file in dictionary by transcript id
    :param flair: GTF file in dictionary by transcript id
    :param talon: GTF file in dictionary by transcript id
    :param outfile: name of outfile
    :return: -
    """
    with open(outfile, 'w') as out:
        for tcons_id, transcipt_ids, in tracking_dict.items():
            # transcript order: q1 oxford, q2 flair, q3 talon
            # writes out one of the three transcripts
            if transcipt_ids[0] != '-':
                for line in oxford[transcipt_ids[0]]:
                    out.write(f'{line} match_id "{tcons_id}";\n')
            # if no oxford transcript, write flair transcript
            elif transcipt_ids[1] != '-':
                for line in flair[transcipt_ids[1]]:
                    out.write(f'{line} match_id "{tcons_id}";\n')
            # if no oxford and flair transcript, write talon transcript
            else:
                for line in talon[transcipt_ids[2]]:
                    out.write(f'{line} match_id "{tcons_id}";\n')


def main():
    """
    Creates dictionaries from GTF files and tracking file and creates
    three sorted GTF files containing matched transcripts.
    :return:
    """
    tracking_three, tracking_two, tracking_one = categorize_tracking(snakemake.input.tracking)
    oxford = gtf(snakemake.input.oxford)
    flair = gtf(snakemake.input.flair)
    talon = gtf(snakemake.input.talon)
    write(tracking_three, oxford, flair, talon, snakemake.output.tracking_three)
    write(tracking_two, oxford, flair, talon, snakemake.output.tracking_two)
    write(tracking_one, oxford, flair, talon, snakemake.output.tracking_one)


main()
