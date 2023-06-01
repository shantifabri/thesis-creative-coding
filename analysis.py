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


# anylise_cloc("./analysis/cloc_created_skip_unique.csv",
#              "./analysis/cloc_hearted_skip_unique.csv", 'JavaScript')
# anylise_cloc("./analysis/cloc_created_skip_unique.csv",
#              "./analysis/cloc_hearted_skip_unique.csv", 'Arduino Sketch')


def load_json(filename):
    with open(filename, encoding="utf8") as f:
        data = json.load(f)
    return data


def json_serializer(value):
    if isinstance(value, set):
        return list(value)
    return value


def write_dict(dict, filename):
    with open(filename, 'w') as file:
        file.write(json.dumps(dict, default=json_serializer))


df_demo = load_json("../cr_report_demo.json")  # 6  --- len(df["reports"])
df_demo2 = load_json("../cr_report_demo_2.json")  # 7  --- len(df["reports"])
# df = load_json("../cr_report_created_half1.json") # 6010
# df = load_json("../cr_report_created_half2.json") # 6112
# df = load_json("../cr_report_hearted_half1.json") # 3311
# df = load_json("../cr_report_hearted_half2.json") # 8341


def analyse_cr(data):
    reports = data["reports"]

    stats = {
        "sketches_setup_draw": 0,   # see if file has those 2 funcs  --  done
        "funcs_setup": 0,           # count total of "setup" funcs  --  done
        "funcs_draw": 0,            # count total of "draw" funcs  --  done
        "n_files": len(reports),    # count all files -- done
        "funcs": [],                # [[sketchname,func["name"],func["params"],func["sloc"]["logical"]]]
        "sketches": set(),          # unique sketches -- done
        "files_names": set(),       # unique file names -- done
        "func_names": set(),        # unique functions names  --  done
        # {sketch: [[filename, sloc, [name of funcs]]]} -- done
        "files": {},
        "sloc_logical": {'max': 0,
                         'min': 1000,
                         'sum': 0,
                         'file_avg': 0,
                         'func_avg': data["loc"]}
    }

    # each report represents a file
    for report in reports:
        txt = report["path"]
        x = txt.rfind("\\")
        filename = txt[x+1:]
        stats["files_names"].add(filename)  # add file name
        txt = txt[:x]
        y = txt.rfind("\\")
        sketchname = txt[y+1:]
        stats["sketches"].add(sketchname)  # add sketch name

        # file SLOC
        sloc_log_file = report["aggregate"]["sloc"]["logical"]
        stats["sloc_logical"]["sum"] += sloc_log_file

        if sloc_log_file > stats["sloc_logical"]["max"]:
            stats["sloc_logical"]["max"] = sloc_log_file

        if sloc_log_file < stats["sloc_logical"]["min"]:
            stats["sloc_logical"]["min"] = sloc_log_file

        # file gral info
        if sketchname in stats["files"]:
            stats["files"][sketchname].append([filename, sloc_log_file, []])
        else:
            stats["files"][sketchname] = [[filename, sloc_log_file, []]]

        # funcs info
        draw, setup = 0, 0
        for func in report["functions"]:
            func_name = func["name"]
            stats["files"][sketchname][-1][-1].append(func_name)
            stats["func_names"].add(func_name)
            stats["funcs"].append(
                [sketchname, func_name, func["params"], func["sloc"]["logical"]])

            if func_name == "draw":
                draw = 1
                stats["funcs_draw"] += 1

            elif func_name == "setup":
                setup = 1
                stats["funcs_setup"] += 1

        if draw and setup:
            stats["sketches_setup_draw"] += 1

    stats["sloc_logical"]["file_avg"] = stats["sloc_logical"]["sum"]/stats["n_files"]

    return stats

# see if paths repeat - counter of files per sketch - path up till last \\
# get highest and lowest of indexes


stats = analyse_cr(df_demo2)

print(stats)

write_dict(stats, "myfile.json")

print("ssss ------------------------")
ss = load_json("./myfile.json")
print(ss)

def analyse_cr_stats(stats):
    # get loc's (max, min, sum for avg) ---->  get how many close to it
    # how many funcs per project, max, min, avg
    pass


# df = pd.DataFrame(stats)
# print(df)
