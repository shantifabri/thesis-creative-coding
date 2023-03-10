import json
import pandas as pd


def load_cloc(filename):
    data = pd.read_csv(filename, index_col='language')
    return data


def write_csv(filename, dataframe):
    dataframe.to_csv(filename)


def anylise_cloc(filecreated, filehearted, language):

    df_created = load_cloc(filecreated)
    df_hearted = load_cloc(filehearted)

    tot_created = df_created.loc['SUM']['files']
    n_files_created = df_created.loc[language]['files']
    loc_created = df_created.loc[language]['code']
    lo_comms_created = df_created.loc[language]['comment']

    loc_per_file_created = round(loc_created/n_files_created, 2)
    lo_comms_per_file_created = round(lo_comms_created/n_files_created, 2)
    percent_files_created = round(
        (int(n_files_created) / int(tot_created)) * 100, 2)

    tot_hearted = df_hearted.loc['SUM']['files']
    n_files_hearted = df_hearted.loc[language]['files']
    loc_hearted = df_hearted.loc[language]['code']
    lo_comms_hearted = df_hearted.loc[language]['comment']

    loc_per_file_hearted = round(loc_hearted/n_files_hearted, 2)
    lo_comms_per_file_hearted = round(lo_comms_hearted/n_files_hearted, 2)
    percent_files_hearted = round(
        (int(n_files_hearted) / int(tot_hearted)) * 100, 2)

    data = [{'total files': tot_created,
             f'{language} files': n_files_created,
             f'% {language} files': percent_files_created,
             f'total loc {language}': loc_created,
             'avg loc per file': loc_per_file_created,
             f'total comments {language}': lo_comms_created,
             'avg comments per file': lo_comms_per_file_created},
            {'total files': tot_hearted,
             f'{language} files': n_files_hearted,
             f'% {language} files': percent_files_hearted,
             f'total loc {language}': loc_hearted,
             'avg loc per file': loc_per_file_hearted,
             f'total comments {language}': lo_comms_hearted,
             'avg comments per file': lo_comms_per_file_hearted}]

    # Lists of dictionaries and row index.
    df = pd.DataFrame(data, index=['created', 'hearted'])

    write_csv(f'./analysis/cloc_analysis_{language}.csv', df)


anylise_cloc("./analysis/cloc_created_skip_unique.csv",
             "./analysis/cloc_hearted_skip_unique.csv", 'JavaScript')
anylise_cloc("./analysis/cloc_created_skip_unique.csv",
             "./analysis/cloc_hearted_skip_unique.csv", 'Arduino Sketch')


def load_cr(filename):
    with open(filename, encoding="utf8") as f:
        data = json.load(f)
    return data

# df = load_cr("../cr_report_demo.json")  # 6  --- len(df["reports"])
# df = load_cr("../cr_report_created_half1.json") # 6010
# df = load_cr("../cr_report_created_half2.json") # 6112
# df = load_cr("../cr_report_hearted_half1.json") # 3311
# df = load_cr("../cr_report_hearted_half2.json") # 8341
